"""
feature_engineering.py
─────────────────────────────────────────────────────────────────────────────
Rôle : charger le CSV brut, corriger les anomalies de qualité, et agréger
les 400K lignes de transactions en 1 profil par client (64K lignes × 25+ features).

Pipeline :
    load_raw_data() → fix_data_quality() → compute_rfm() → compute_behavioral()
    → compute_channel() → compute_market() → compute_temporal()
    → build_feature_store() → save_features()

Appelé par : notebooks/0_cleaning_features.ipynb
─────────────────────────────────────────────────────────────────────────────
"""

import os
import numpy as np
import pandas as pd
from scipy import stats

from src.utils import DATA_PATH, RANDOM_SEED, shannon_entropy, validate_dataframe

# Nom du fichier CSV brut (à déposer dans data/)
RAW_CSV = "BDD#7_Database_Albert_School_Sephora.csv"

# Date de référence pour la recency (dernier jour du dataset = fin sept 2025)
REFERENCE_DATE = pd.Timestamp("2025-09-30")

# Split temporel : train = Jan–Juin, test = Juil–Sep
SPLIT_DATE = pd.Timestamp("2025-07-01")


# ── 1. Chargement ─────────────────────────────────────────────────────────────

def load_raw_data(path: str = None) -> pd.DataFrame:
    """
    Charge le CSV brut avec les bons types.

    - anonymized_card_code : string (évite la notation scientifique)
    - anonymized_Ticket_ID : string
    - transactionDate       : parsed en datetime (MM/DD/YYYY)
    """
    if path is None:
        path = os.path.join(DATA_PATH, RAW_CSV)

    print(f"[load_raw_data] Lecture : {path}")

    df = pd.read_csv(
        path,
        dtype={
            "anonymized_card_code":         str,
            "anonymized_Ticket_ID":         str,
            "anonymized_first_purchase_id": str,
            "materialCode":                 str,
            "materialCode_first_purchase":  str,
        },
        low_memory=False,
    )

    # Parse dates
    df["transactionDate"] = pd.to_datetime(
        df["transactionDate"], format="%m/%d/%Y", errors="coerce"
    )
    for date_col in ["first_purchase_dt", "subscription_date"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(
                df[date_col], format="%m/%d/%Y", errors="coerce"
            )

    print(f"  → {len(df):,} lignes | {df['anonymized_card_code'].nunique():,} clients uniques")
    return df


# ── 2. Corrections qualité ────────────────────────────────────────────────────

def fix_data_quality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Corrige les 5 anomalies documentées.

    1. Typo MAEK UP → MAKE UP dans Axe_Desc + Axe_Desc_first_purchase
    2. Valeurs manquantes age_category / age_generation → "Unknown"
    3. salesVatEUR / discountEUR / quantity → coerce, négatifs → 0
    4. gender 99999 → NaN
    5. Lignes sans transactionDate → drop
    """
    df = df.copy()

    # 1. Typo axe
    for col in ["Axe_Desc", "Axe_Desc_first_purchase"]:
        if col in df.columns:
            df[col] = df[col].str.strip().replace("MAEK UP", "MAKE UP")

    # 2. Age category
    for col in ["age_category", "age_generation"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").replace("", "Unknown")

    # 3. Numériques
    for col in ["salesVatEUR", "discountEUR", "quantity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)

    # 4. Gender 99999 → NaN
    if "gender" in df.columns:
        df["gender"] = df["gender"].replace(99999, np.nan)

    # 5. Drop dates manquantes
    n_before = len(df)
    df = df.dropna(subset=["transactionDate"])
    n_dropped = n_before - len(df)
    if n_dropped > 0:
        print(f"  [fix_data_quality] {n_dropped} lignes sans date supprimées")

    # Recalcul net spend
    df["net_spend"] = df["salesVatEUR"] - df["discountEUR"].fillna(0)

    print(f"  [fix_data_quality] Dataset nettoyé : {len(df):,} lignes")
    return df


# ── 3. RFM ────────────────────────────────────────────────────────────────────

def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les 3 métriques RFM + features dérivées basiques par client.

    Returns
    -------
    DataFrame indexé par anonymized_card_code avec :
        recency_days, frequency, monetary,
        avg_basket, max_basket, avg_items_per_basket, discount_ratio
    """
    ref_date = REFERENCE_DATE

    # Recency = jours depuis dernière transaction
    last_txn = df.groupby("anonymized_card_code")["transactionDate"].max()
    recency = (ref_date - last_txn).dt.days.rename("recency_days")

    # Frequency = nb tickets uniques
    freq = (df.groupby("anonymized_card_code")["anonymized_Ticket_ID"]
              .nunique().rename("frequency"))

    # Monetary = CA total
    monetary = (df.groupby("anonymized_card_code")["salesVatEUR"]
                  .sum().rename("monetary"))

    # Panier moyen & max
    basket_stats = (df.groupby(["anonymized_card_code", "anonymized_Ticket_ID"])["salesVatEUR"]
                      .sum().reset_index())
    avg_basket = (basket_stats.groupby("anonymized_card_code")["salesVatEUR"]
                               .mean().rename("avg_basket"))
    max_basket = (basket_stats.groupby("anonymized_card_code")["salesVatEUR"]
                               .max().rename("max_basket"))

    # Quantité moyenne par ticket
    qty_per_ticket = (df.groupby(["anonymized_card_code", "anonymized_Ticket_ID"])["quantity"]
                        .sum().reset_index())
    avg_items = (qty_per_ticket.groupby("anonymized_card_code")["quantity"]
                                .mean().rename("avg_items_per_basket"))

    # Discount ratio
    disc_total  = df.groupby("anonymized_card_code")["discountEUR"].sum()
    spend_total = df.groupby("anonymized_card_code")["salesVatEUR"].sum()
    discount_ratio = (disc_total / spend_total.replace(0, np.nan)).rename("discount_ratio").fillna(0)

    rfm = pd.concat([recency, freq, monetary, avg_basket, max_basket,
                     avg_items, discount_ratio], axis=1)
    return rfm


# ── 4. Comportemental ─────────────────────────────────────────────────────────

def compute_behavioral(df: pd.DataFrame) -> pd.DataFrame:
    """
    Features de diversité et fidélité marque / axe + ICB score.

    Returns
    -------
    DataFrame avec :
        unique_brands, brand_entropy, top_brand_share,
        unique_axes, axe_entropy, top_axe_share,
        pct_discounted_txn, icb_score
    """

    def _entropy_and_top(grp, value_col, amount_col):
        ca_by_val = grp.groupby(value_col)[amount_col].sum()
        entropy   = shannon_entropy(ca_by_val)
        top_share = float(ca_by_val.max() / ca_by_val.sum()) if ca_by_val.sum() > 0 else 0.0
        n_unique  = int(ca_by_val.shape[0])
        return n_unique, entropy, top_share

    records = []
    for client_id, grp in df.groupby("anonymized_card_code"):
        n_brands, b_ent, b_top = _entropy_and_top(grp, "brand", "salesVatEUR")
        n_axes,   a_ent, a_top = _entropy_and_top(grp, "Axe_Desc", "salesVatEUR")

        # % tickets avec discount
        txn_disc  = grp.groupby("anonymized_Ticket_ID")["discountEUR"].sum()
        pct_disc  = float((txn_disc > 0).mean())

        records.append({
            "anonymized_card_code": client_id,
            "unique_brands":        n_brands,
            "brand_entropy":        b_ent,
            "top_brand_share":      b_top,
            "unique_axes":          n_axes,
            "axe_entropy":          a_ent,
            "top_axe_share":        a_top,
            "pct_discounted_txn":   pct_disc,
        })

    beh = pd.DataFrame(records).set_index("anonymized_card_code")

    # ICB (Indice de Curiosité Beauté) — score 0-100
    for col in ["brand_entropy", "axe_entropy", "unique_brands"]:
        mx = beh[col].max()
        beh[f"_norm_{col}"] = beh[col] / mx if mx > 0 else 0.0

    beh["icb_score"] = (
        0.40 * beh["_norm_brand_entropy"] +
        0.30 * beh["_norm_axe_entropy"] +
        0.30 * beh["_norm_unique_brands"]
    ) * 100

    beh = beh.drop(columns=[c for c in beh.columns if c.startswith("_norm_")])
    return beh


# ── 5. Canal ──────────────────────────────────────────────────────────────────

def compute_channel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Features omnicanal.

    Returns
    -------
    DataFrame avec : pct_estore, nb_channels, is_omnichannel
    """
    channel_col = "store_type_app" if "store_type_app" in df.columns else "channel"

    ch = df.groupby("anonymized_card_code").agg(
        nb_channels=  (channel_col, "nunique"),
        total_txn=    ("anonymized_Ticket_ID", "nunique"),
    )

    estore_mask = df[channel_col].str.lower().str.contains("estore|online|e-store", na=False)
    estore_cnt  = (df[estore_mask]
                   .groupby("anonymized_card_code")["anonymized_Ticket_ID"]
                   .nunique()
                   .rename("estore_txn"))
    ch = ch.join(estore_cnt, how="left").fillna({"estore_txn": 0})
    ch["pct_estore"]    = (ch["estore_txn"] / ch["total_txn"].replace(0, np.nan)).fillna(0)
    ch["is_omnichannel"] = (ch["nb_channels"] >= 2).astype(int)

    return ch[["pct_estore", "nb_channels", "is_omnichannel"]]


# ── 6. Marché ─────────────────────────────────────────────────────────────────

def compute_market(df: pd.DataFrame) -> pd.DataFrame:
    """
    Positionnement marché : EXCLUSIVE / SELECTIVE / SEPHORA.

    Returns
    -------
    DataFrame avec : pct_exclusive, pct_selective, pct_sephora
    """
    ca_total = df.groupby("anonymized_card_code")["salesVatEUR"].sum()
    result   = pd.DataFrame(index=ca_total.index)

    for market_type in ["EXCLUSIVE", "SELECTIVE", "SEPHORA"]:
        sub    = df[df["Market_Desc"] == market_type]
        ca_sub = sub.groupby("anonymized_card_code")["salesVatEUR"].sum()
        col    = f"pct_{market_type.lower()}"
        result[col] = (ca_sub / ca_total.replace(0, np.nan)).fillna(0)

    return result


# ── 7. Temporel ───────────────────────────────────────────────────────────────

def compute_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Features temporelles : tenure, régularité, tendance.

    Returns
    -------
    DataFrame avec :
        tenure_days, avg_days_between_purchases,
        purchase_regularity, trend_spend_monthly
    """
    records = []

    for client_id, grp in df.groupby("anonymized_card_code"):
        dates      = grp.groupby("anonymized_Ticket_ID")["transactionDate"].min().sort_values()
        first_date = dates.min()
        last_date  = dates.max()
        tenure     = int((last_date - first_date).days)

        if len(dates) > 1:
            intervals    = np.diff(dates.values).astype("timedelta64[D]").astype(float)
            avg_interval = float(np.mean(intervals))
            std_interval = float(np.std(intervals))
        else:
            avg_interval = 0.0
            std_interval = 0.0

        # Tendance mensuelle (pente régression linéaire CA par mois)
        monthly = (grp.assign(month=grp["transactionDate"].dt.to_period("M"))
                      .groupby("month")["salesVatEUR"].sum())
        if len(monthly) >= 3:
            x = np.arange(len(monthly))
            slope, *_ = stats.linregress(x, monthly.values)
        else:
            slope = 0.0

        records.append({
            "anonymized_card_code":       client_id,
            "tenure_days":                max(tenure, 0),
            "avg_days_between_purchases": avg_interval,
            "purchase_regularity":        std_interval,
            "trend_spend_monthly":        float(slope),
        })

    return pd.DataFrame(records).set_index("anonymized_card_code")


# ── 8. Build feature store ────────────────────────────────────────────────────

def build_feature_store(df: pd.DataFrame,
                        include_socio: bool = True) -> pd.DataFrame:
    """
    Assemble toutes les features en 1 DataFrame par client (~25 features).

    Parameters
    ----------
    df            : DataFrame brut nettoyé (sortie de fix_data_quality)
    include_socio : si True, joint age_category, gender, status

    Returns
    -------
    DataFrame (index = anonymized_card_code)
    """
    print("[build_feature_store] Calcul RFM...")
    rfm  = compute_rfm(df)

    print("[build_feature_store] Calcul comportemental...")
    beh  = compute_behavioral(df)

    print("[build_feature_store] Calcul canal...")
    chan = compute_channel(df)

    print("[build_feature_store] Calcul marché...")
    mkt  = compute_market(df)

    print("[build_feature_store] Calcul temporel...")
    temp = compute_temporal(df)

    features = rfm.join(beh, how="left") \
                  .join(chan, how="left") \
                  .join(mkt, how="left") \
                  .join(temp, how="left")

    if include_socio:
        socio_cols = [c for c in
                      ["gender", "age_category", "age_generation", "status", "RFM_Segment_ID"]
                      if c in df.columns]
        if socio_cols:
            socio = (df[["anonymized_card_code"] + socio_cols]
                     .groupby("anonymized_card_code")
                     .agg({c: "last" for c in socio_cols}))
            features = features.join(socio, how="left")

    # Remplir NaN résiduels sur colonnes numériques
    num_cols = features.select_dtypes(include=[np.number]).columns
    features[num_cols] = features[num_cols].fillna(0)

    print(f"  → Feature store : {features.shape[0]:,} clients × {features.shape[1]} features")
    return features


# ── 9. Sauvegarde ─────────────────────────────────────────────────────────────

def save_features(features: pd.DataFrame,
                  split: bool = True,
                  raw_df: pd.DataFrame = None) -> dict:
    """
    Sauvegarde les features dans data/.

    Returns
    -------
    dict {label: chemin_absolu}
    """
    os.makedirs(DATA_PATH, exist_ok=True)
    paths = {}

    full_path = os.path.join(DATA_PATH, "customer_features.csv")
    features.to_csv(full_path)
    paths["full"] = full_path
    print(f"  [save_features] → {full_path}")

    if split and raw_df is not None:
        # Train : Jan–Juin
        df_train = fix_data_quality(raw_df[raw_df["transactionDate"] < SPLIT_DATE].copy())
        feat_train = build_feature_store(df_train)
        train_path = os.path.join(DATA_PATH, "customer_features_train.csv")
        feat_train.to_csv(train_path)
        paths["train"] = train_path
        print(f"  [save_features] → {train_path}")

        # Test transactions : Juil–Sep (pour replay migration)
        df_test = raw_df[raw_df["transactionDate"] >= SPLIT_DATE].copy()
        test_path = os.path.join(DATA_PATH, "transactions_test.csv")
        df_test.to_csv(test_path, index=False)
        paths["test_transactions"] = test_path
        print(f"  [save_features] → {test_path}")

    return paths


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df_raw   = load_raw_data()
    df_clean = fix_data_quality(df_raw)
    features = build_feature_store(df_clean)
    paths    = save_features(features, split=True, raw_df=df_raw)
    print("\nFichiers générés :")
    for k, v in paths.items():
        print(f"  {k:30s} → {v}")
