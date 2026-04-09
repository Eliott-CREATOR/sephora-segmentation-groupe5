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

# ══════════════════════════════════════════════════════════════════════════════
# CHANTIER 1 — CORRECTION DU BIAIS DE SAISONNALITÉ
# Ajouté pour corriger l'inflation artificielle des migrations Q3 (Juil–Sep)
# due au pic naturel d'achats rentrée + préparation fêtes.
# ══════════════════════════════════════════════════════════════════════════════

SI_CLIP_MIN = 0.30   # évite la division par un SI trop proche de 0
SI_CLIP_MAX = 3.00   # évite une sur-correction sur des mois atypiques


def compute_seasonality_index(df_transactions: pd.DataFrame) -> dict[int, float]:
    """
    Calcule l'indice de saisonnalité mensuel sur l'ensemble des transactions.

    SI(m) = volume_CA_mensuel(m) / volume_CA_mensuel_moyen

    SI > 1 → mois inflationnaire (Jul–Sep rentrée/fêtes)
    SI < 1 → mois calme (Jan–Fév post-fêtes)
    SI = 1 → mois "plat" (référence)

    Parameters
    ----------
    df_transactions : DataFrame nettoyé contenant au minimum
        transactionDate (datetime) et salesVatEUR (float).

    Returns
    -------
    dict {mois_int (1-12): seasonality_index (float)}
        Valeurs clippées dans [SI_CLIP_MIN, SI_CLIP_MAX].

    Notes
    -----
    Calculer sur toutes les transactions disponibles (pas seulement train)
    pour que l'indice reflète la réalité saisonnière globale du dataset.
    """
    df = df_transactions.copy()
    df["_month"] = df["transactionDate"].dt.month

    monthly_ca = (
        df.groupby("_month")["salesVatEUR"]
        .sum()
        .rename("monthly_ca")
    )

    if len(monthly_ca) == 0:
        print("  [compute_seasonality_index] ⚠️  Aucune transaction — SI = 1 pour tous les mois")
        return {m: 1.0 for m in range(1, 13)}

    mean_ca = monthly_ca.mean()
    if mean_ca == 0:
        return {m: 1.0 for m in range(1, 13)}

    si_raw = (monthly_ca / mean_ca).to_dict()

    # Clip + compléter les mois absents du dataset avec SI=1 (neutre)
    si_index = {}
    for m in range(1, 13):
        raw = si_raw.get(m, 1.0)
        si_index[m] = float(np.clip(raw, SI_CLIP_MIN, SI_CLIP_MAX))

    print("  [compute_seasonality_index] Indices calculés :")
    for m, si in si_index.items():
        flag = "⚠️ " if si > 1.10 else ("📉" if si < 0.90 else "✓ ")
        print(f"    Mois {m:2d} : SI = {si:.3f}  {flag}")

    return si_index


def apply_seasonality_correction(
    df_transactions: pd.DataFrame,
    seasonality_index: dict[int, float],
) -> pd.DataFrame:
    """
    Corrige les montants monétaires par l'indice de saisonnalité du mois.

    Pour chaque transaction :
        salesVatEUR_adj  = salesVatEUR  / SI(mois)
        discountEUR_adj  = discountEUR  / SI(mois)
        net_spend_adj    = net_spend    / SI(mois)

    Cela ramène tous les montants en "équivalent mois plat" :
    une dépense de 200€ en septembre (SI=1.35) devient 148€ ajusté,
    comparable à un mois de référence.

    Ajoute aussi la colonne `seasonality_weight` par client :
        seasonality_weight(client) = moyenne pondérée des SI sur ses transactions
        → utilisé pour informer le dashboard (clients les plus affectés)

    Parameters
    ----------
    df_transactions : DataFrame nettoyé (sortie de fix_data_quality).
    seasonality_index : dict {mois_int: SI} (sortie de compute_seasonality_index).

    Returns
    -------
    pd.DataFrame avec colonnes supplémentaires :
        salesVatEUR_adj, discountEUR_adj, net_spend_adj, si_month, seasonality_weight

    Notes
    -----
    NE MODIFIE PAS les colonnes originales salesVatEUR / discountEUR.
    Les features corrigées sont buildées depuis les colonnes *_adj.
    """
    df = df_transactions.copy()

    # Mapper SI sur chaque transaction
    df["si_month"] = df["transactionDate"].dt.month.map(seasonality_index).fillna(1.0)

    # Correction des montants
    df["salesVatEUR_adj"] = df["salesVatEUR"] / df["si_month"]
    df["discountEUR_adj"] = df["discountEUR"].fillna(0) / df["si_month"]
    df["net_spend_adj"]   = df["net_spend"]   / df["si_month"]

    # Seasonality weight par client (moyenne des SI de ses transactions)
    sw = (
        df.groupby("anonymized_card_code")["si_month"]
        .mean()
        .rename("seasonality_weight")
    )
    df = df.join(sw, on="anonymized_card_code")

    # Diagnostique
    n_tx        = len(df)
    ca_before   = df["salesVatEUR"].sum()
    ca_after    = df["salesVatEUR_adj"].sum()
    pct_delta   = (ca_after - ca_before) / ca_before * 100 if ca_before > 0 else 0.0
    print(f"  [apply_seasonality_correction] {n_tx:,} transactions corrigées")
    print(f"    CA avant correction  : €{ca_before:,.0f}")
    print(f"    CA après correction  : €{ca_after:,.0f}  ({pct_delta:+.1f}%)")
    print("    → Les mois Q3 (Juil–Sep) sont déflatés, Q1 (Jan–Mar) sont gonflés")

    return df


def compute_rfm_corrected(df: pd.DataFrame) -> pd.DataFrame:
    """
    Variante de compute_rfm() utilisant les colonnes *_adj pour RFM.

    Identique à compute_rfm() mais remplace salesVatEUR par salesVatEUR_adj
    et discountEUR par discountEUR_adj.
    Appeler uniquement sur un df ayant passé par apply_seasonality_correction().

    Returns
    -------
    DataFrame indexé par anonymized_card_code — mêmes colonnes que compute_rfm().
    """
    if "salesVatEUR_adj" not in df.columns:
        raise ValueError(
            "Colonne 'salesVatEUR_adj' absente — "
            "appeler apply_seasonality_correction() avant compute_rfm_corrected()."
        )

    ref_date = REFERENCE_DATE

    last_txn  = df.groupby("anonymized_card_code")["transactionDate"].max()
    recency   = (ref_date - last_txn).dt.days.rename("recency_days")

    freq = (df.groupby("anonymized_card_code")["anonymized_Ticket_ID"]
              .nunique().rename("frequency"))

    # Monetary sur montants CORRIGÉS
    monetary = (df.groupby("anonymized_card_code")["salesVatEUR_adj"]
                  .sum().rename("monetary"))

    basket_stats = (
        df.groupby(["anonymized_card_code", "anonymized_Ticket_ID"])["salesVatEUR_adj"]
        .sum().reset_index()
    )
    avg_basket = (basket_stats.groupby("anonymized_card_code")["salesVatEUR_adj"]
                               .mean().rename("avg_basket"))
    max_basket = (basket_stats.groupby("anonymized_card_code")["salesVatEUR_adj"]
                               .max().rename("max_basket"))

    qty_per_ticket = (
        df.groupby(["anonymized_card_code", "anonymized_Ticket_ID"])["quantity"]
        .sum().reset_index()
    )
    avg_items = (qty_per_ticket.groupby("anonymized_card_code")["quantity"]
                                .mean().rename("avg_items_per_basket"))

    disc_total  = df.groupby("anonymized_card_code")["discountEUR_adj"].sum()
    spend_total = df.groupby("anonymized_card_code")["salesVatEUR_adj"].sum()
    discount_ratio = (
        (disc_total / spend_total.replace(0, np.nan))
        .rename("discount_ratio")
        .fillna(0)
    )

    rfm = pd.concat([recency, freq, monetary, avg_basket, max_basket,
                     avg_items, discount_ratio], axis=1)
    return rfm


def build_corrected_feature_store(
    df_clean: pd.DataFrame,
    seasonality_index: dict[int, float] | None = None,
    include_socio: bool = True,
) -> pd.DataFrame:
    """
    Pipeline complet feature engineering avec correction saisonnalité.

    Enchaîne :
      apply_seasonality_correction → compute_rfm_corrected + features inchangées
      → joint final + colonne seasonality_weight

    Parameters
    ----------
    df_clean         : DataFrame nettoyé (sortie fix_data_quality).
    seasonality_index: dict {mois: SI}. Si None, calculé automatiquement.
    include_socio    : inclure les variables socio-démographiques.

    Returns
    -------
    DataFrame (index = anonymized_card_code) avec 26 colonnes
    (= 25 features originales + seasonality_weight).

    Notes
    -----
    La colonne seasonality_weight NE doit PAS être ajoutée à CLUSTERING_FEATURES
    dans clustering.py — elle sert uniquement à l'analyse et au dashboard.
    """
    print("[build_corrected_feature_store] Démarrage pipeline corrigé…")

    # Calcul SI si non fourni
    if seasonality_index is None:
        print("[build_corrected_feature_store] Calcul du seasonality index…")
        seasonality_index = compute_seasonality_index(df_clean)

    # Correction saisonnalité
    df_adj = apply_seasonality_correction(df_clean, seasonality_index)

    # RFM corrigé
    print("[build_corrected_feature_store] Calcul RFM corrigé…")
    rfm = compute_rfm_corrected(df_adj)

    # Features non-monétaires inchangées (calculées sur données originales)
    print("[build_corrected_feature_store] Calcul features comportementales…")
    beh  = compute_behavioral(df_clean)

    print("[build_corrected_feature_store] Calcul canal…")
    chan = compute_channel(df_clean)

    print("[build_corrected_feature_store] Calcul marché…")
    mkt  = compute_market(df_clean)

    print("[build_corrected_feature_store] Calcul temporel…")
    temp = compute_temporal(df_clean)

    # Seasonality weight (1 valeur par client)
    sw = (
        df_adj.groupby("anonymized_card_code")["si_month"]
        .mean()
        .rename("seasonality_weight")
    )

    features = (
        rfm.join(beh,  how="left")
           .join(chan, how="left")
           .join(mkt,  how="left")
           .join(temp, how="left")
           .join(sw,   how="left")
    )

    if include_socio:
        socio_cols = [c for c in
                      ["gender", "age_category", "age_generation", "status", "RFM_Segment_ID"]
                      if c in df_clean.columns]
        if socio_cols:
            socio = (
                df_clean[["anonymized_card_code"] + socio_cols]
                .groupby("anonymized_card_code")
                .agg({c: "last" for c in socio_cols})
            )
            features = features.join(socio, how="left")

    num_cols = features.select_dtypes(include=[np.number]).columns
    features[num_cols] = features[num_cols].fillna(0)

    print(
        f"  → Feature store corrigé : "
        f"{features.shape[0]:,} clients × {features.shape[1]} features"
    )
    print(f"  ✓ Colonnes : {list(features.columns)}")
    return features


def save_corrected_features(
    df_raw: pd.DataFrame,
    seasonality_index: dict[int, float] | None = None,
) -> dict[str, str]:
    """
    Génère et sauvegarde les features corrigées pour train (Jan–Jun) et test.

    Fichiers produits :
        data/customer_features_train_corrected.csv  (26 cols)
        data/seasonality_index.csv                   (12 lignes)

    Parameters
    ----------
    df_raw           : DataFrame brut (avant fix_data_quality).
    seasonality_index: si None, calculé depuis l'ensemble du dataset brut.

    Returns
    -------
    dict {label: chemin_absolu}
    """
    os.makedirs(DATA_PATH, exist_ok=True)
    paths = {}

    # Nettoyer une fois
    df_clean_full = fix_data_quality(df_raw)

    # Calculer SI sur l'ensemble (Jan–Sep) pour une référence complète
    if seasonality_index is None:
        print("[save_corrected_features] Calcul SI sur le dataset complet…")
        seasonality_index = compute_seasonality_index(df_clean_full)

    # Sauvegarder le SI pour traçabilité / audit jury
    si_df = pd.DataFrame(
        list(seasonality_index.items()),
        columns=["month", "seasonality_index"]
    ).sort_values("month")
    si_path = os.path.join(DATA_PATH, "seasonality_index.csv")
    si_df.to_csv(si_path, index=False)
    paths["seasonality_index"] = si_path
    print(f"  [save_corrected_features] → {si_path}")

    # Features corrigées sur Jan–Jun uniquement (train)
    df_train_clean = fix_data_quality(
        df_raw[df_raw["transactionDate"] < SPLIT_DATE].copy()
    )
    feat_train_corr = build_corrected_feature_store(
        df_train_clean, seasonality_index=seasonality_index
    )
    train_corr_path = os.path.join(DATA_PATH, "customer_features_train_corrected.csv")
    feat_train_corr.to_csv(train_corr_path)
    paths["train_corrected"] = train_corr_path
    print(f"  [save_corrected_features] → {train_corr_path}")

    # Validation croisée : nombre de migrations avant/après (approximation)
    n_clients = len(feat_train_corr)
    sw_mean   = feat_train_corr["seasonality_weight"].mean() if "seasonality_weight" in feat_train_corr.columns else 1.0
    print(f"\n  Validation :")
    print(f"    Clients dans le train corrigé : {n_clients:,}")
    print(f"    Seasonality weight moyen      : {sw_mean:.3f}")
    print("    ✓ Features corrigées prêtes pour re-entraînement MiniBatchKMeans")

    return paths


if __name__ == "__main__":
    df_raw   = load_raw_data()
    df_clean = fix_data_quality(df_raw)
    features = build_feature_store(df_clean)
    paths    = save_features(features, split=True, raw_df=df_raw)
    print("\nFichiers générés :")
    for k, v in paths.items():
        print(f"  {k:30s} → {v}")

    # Chantier 1 — features corrigées
    print("\n── Génération features corrigées (saisonnalité) ──")
    corr_paths = save_corrected_features(df_raw)
    for k, v in corr_paths.items():
        print(f"  {k:30s} → {v}")
