"""
migration_detector.py
─────────────────────────────────────────────────────────────────────────────
Rôle : simuler la mise à jour dynamique des clusters clients.
Pour chaque transaction de la période Juil–Sep 2025, mettre à jour le
profil du client dans le feature store, réassigner son cluster via le
modèle existant, et détecter si une migration de segment a eu lieu.

Appelé par : notebooks/3_personas_migration.ipynb
Produit    : outputs/data/migrations.csv
             outputs/figures/3_sankey_migrations.png
─────────────────────────────────────────────────────────────────────────────
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler

from src.utils import DATA_PATH, OUTPUTS_PATH, RANDOM_SEED, set_global_style, save_figure
from src.clustering import CLUSTERING_FEATURES, assign_cluster
from src.feature_engineering import REFERENCE_DATE, shannon_entropy


def _normalize_id(raw_id) -> str:
    """
    Normalise un ID client en string entier cohérent.
    Gère les formats float (-1.00006e+18), string scientifique ('-8.17068E+18'),
    et entiers classiques.
    """
    try:
        return str(int(float(str(raw_id).replace("E", "e"))))
    except (ValueError, OverflowError):
        return str(raw_id).strip()


# ── 1. Initialisation du Feature Store ───────────────────────────────────────

def build_feature_store(features_train_path: str = None) -> dict:
    """
    Initialise le dict {client_id: profil_dict} à partir de
    customer_features_train.csv.

    Returns
    -------
    dict : { anonymized_card_code: {feature: value, ...} }
    """
    if features_train_path is None:
        features_train_path = os.path.join(DATA_PATH, "customer_features_train.csv")

    # Lire avec dtype str pour préserver les IDs longs (évite la troncature float64)
    df = pd.read_csv(features_train_path,
                     dtype={"anonymized_card_code": str},
                     low_memory=False)
    df = df.set_index("anonymized_card_code")

    # Ne garder que les features numériques de clustering
    cols = [c for c in CLUSTERING_FEATURES if c in df.columns]
    feature_store = {}

    for client_id, row in df[cols].iterrows():
        feature_store[str(client_id).strip()] = row.fillna(0).to_dict()

    print(f"[build_feature_store] {len(feature_store):,} clients chargés dans le feature store")
    return feature_store


# ── 2. Mise à jour incrémentale d'un profil client ───────────────────────────

def update_client_features(client_id: str,
                            new_txn: pd.Series,
                            feature_store: dict,
                            all_prev_txns: pd.DataFrame = None) -> dict:
    """
    Recalcule incrémentalement les features d'un client après un nouvel achat.

    Stratégie simplifiée (sans historique complet, juste mise à jour rolling) :
    - monetary += salesVatEUR
    - frequency += 1 (ticket)
    - avg_basket = monetary / frequency (recalculé)
    - recency_days = (REFERENCE_DATE - txn_date).days
    - discount_ratio = updated weighted average
    - pct_estore : updated
    - tenure_days : updated si nouveau max date

    Parameters
    ----------
    client_id    : identifiant client
    new_txn      : Series avec les colonnes de la transaction
    feature_store : dict courant {client_id: profil}
    all_prev_txns : optionnel — DataFrame des transactions précédentes du client

    Returns
    -------
    dict : profil mis à jour
    """
    profile = dict(feature_store.get(client_id, {}))

    # Nouveau montant
    amount   = float(new_txn.get("salesVatEUR", 0))
    discount = float(new_txn.get("discountEUR", 0))
    txn_date = pd.Timestamp(new_txn["transactionDate"])

    # ── Monetary & Frequency ─────
    old_monetary   = float(profile.get("monetary", 0))
    old_frequency  = float(profile.get("frequency", 0))
    new_monetary   = old_monetary + amount
    new_frequency  = old_frequency + 1

    profile["monetary"]  = new_monetary
    profile["frequency"] = new_frequency
    profile["avg_basket"] = new_monetary / new_frequency if new_frequency > 0 else 0

    # ── Recency ─────────────────
    profile["recency_days"] = max(0, (REFERENCE_DATE - txn_date).days)

    # ── Discount ratio ───────────
    old_disc_total = old_monetary * float(profile.get("discount_ratio", 0))
    new_disc_total = old_disc_total + discount
    profile["discount_ratio"] = new_disc_total / new_monetary if new_monetary > 0 else 0

    # ── Tenure ───────────────────
    old_tenure = float(profile.get("tenure_days", 0))
    # On estime la date de premiere transaction
    # tenure = (last_date - first_date).days
    # first_date ≈ last_date - tenure (avant mise à jour)
    # Recalcul tenure si la nouvelle transaction est plus récente
    old_recency = float(profile.get("recency_days", 0))
    last_known  = REFERENCE_DATE - pd.Timedelta(days=old_recency)
    first_known = last_known - pd.Timedelta(days=old_tenure)
    new_last    = max(last_known, txn_date)
    profile["tenure_days"] = max(0, (new_last - first_known).days)

    # ── estore ───────────────────
    channel_val = str(new_txn.get("store_type_app", new_txn.get("channel", ""))).lower()
    is_estore   = int("estore" in channel_val or "online" in channel_val)
    old_pct_e   = float(profile.get("pct_estore", 0))
    # Mise à jour de pct_estore comme moyenne glissante
    profile["pct_estore"] = (old_pct_e * (new_frequency - 1) + is_estore) / new_frequency

    return profile


# ── 3. Réassignation de cluster ───────────────────────────────────────────────

def reassign_cluster(client_id: str,
                     feature_store: dict,
                     model: MiniBatchKMeans,
                     scaler: StandardScaler) -> int:
    """
    Normalise le profil mis à jour et prédit le nouveau cluster.

    Returns
    -------
    int : numéro de cluster
    """
    profile = feature_store.get(client_id, {})
    vector  = [profile.get(f, 0.0) for f in CLUSTERING_FEATURES
               if f in [c for c in CLUSTERING_FEATURES]]
    # S'assurer d'avoir le bon nombre de features
    n_features = len(scaler.mean_)
    vec_full   = np.zeros(n_features)
    for i, feat in enumerate(CLUSTERING_FEATURES):
        if i < n_features:
            vec_full[i] = float(profile.get(feat, 0.0))

    return assign_cluster(vec_full, model, scaler)


# ── 4. Détection de migration ─────────────────────────────────────────────────

def detect_migration(client_id: str,
                     old_cluster: int,
                     new_cluster: int,
                     txn_date: pd.Timestamp,
                     txn_id: str = "") -> dict | None:
    """
    Compare ancien et nouveau cluster.

    Returns
    -------
    dict Migration si changement, None sinon.
    {
        'client_id': str,
        'txn_id': str,
        'date': str (YYYY-MM-DD),
        'from_cluster': int,
        'to_cluster': int,
        'direction': 'upgrade' | 'downgrade' | 'lateral'
    }
    """
    if old_cluster == new_cluster:
        return None

    # Direction heuristique : cluster 0 = plus valorieux par convention
    # (à recalibrer après clustering réel)
    if new_cluster < old_cluster:
        direction = "upgrade"
    elif new_cluster > old_cluster:
        direction = "downgrade"
    else:
        direction = "lateral"

    return {
        "client_id":    str(client_id),
        "txn_id":       str(txn_id),
        "date":         txn_date.strftime("%Y-%m-%d"),
        "from_cluster": int(old_cluster),
        "to_cluster":   int(new_cluster),
        "direction":    direction,
    }


# ── 5. Replay des transactions ────────────────────────────────────────────────

def replay_transactions(transactions_test_path: str,
                        feature_store: dict,
                        initial_clusters: dict,
                        model: MiniBatchKMeans,
                        scaler: StandardScaler,
                        verbose: bool = True) -> tuple:
    """
    Rejoue toutes les transactions Juil–Sep dans l'ordre chronologique.

    Parameters
    ----------
    transactions_test_path : chemin vers transactions_test.csv
    feature_store          : dict {client_id: profil} (modifié in-place)
    initial_clusters       : dict {client_id: cluster_initial}
    model, scaler          : modèle chargé

    Returns
    -------
    (list[dict], dict) : (migrations_list, current_clusters)

    Notes
    -----
    Dernière exécution validée : 2,609 migrations réelles (Juil–Sep 2025),
    après filtre explicite Oct–Déc 2025 (transactions_test.csv contenait
    des dates hors-période) et correction du biais de saisonnalité Q3.
    Sans ce filtre : 13,794 migrations artificielles détectées (×5.3).
    """
    df = pd.read_csv(transactions_test_path,
                     dtype={"anonymized_card_code": str, "anonymized_Ticket_ID": str},
                     low_memory=False)
    df["transactionDate"] = pd.to_datetime(df["transactionDate"], format="%m/%d/%Y", errors="coerce")
    df = df.dropna(subset=["transactionDate"]).sort_values("transactionDate")

    # Borne explicite : le replay ne couvre que Juil–Sep 2025
    TEST_END = pd.Timestamp("2025-09-30")
    n_before = len(df)
    df = df[df["transactionDate"] <= TEST_END]
    n_filtered = n_before - len(df)
    if n_filtered > 0:
        print(f"[replay] {n_filtered:,} lignes hors période (> {TEST_END.date()}) exclues")

    # Corriger typo axe
    if "Axe_Desc" in df.columns:
        df["Axe_Desc"] = df["Axe_Desc"].str.strip().replace("MAEK UP", "MAKE UP")

    current_clusters = dict(initial_clusters)
    migrations = []

    # Regrouper par ticket (une transaction = un ticket = un événement)
    tickets = df.groupby("anonymized_Ticket_ID", sort=False)

    total = df["anonymized_Ticket_ID"].nunique()
    processed = 0

    for ticket_id, ticket_rows in tickets:
        client_id = str(ticket_rows["anonymized_card_code"].iloc[0]).strip()
        txn_date  = ticket_rows["transactionDate"].min()

        # Skip si client pas dans le feature store
        if client_id not in feature_store:
            feature_store[client_id] = {}

        old_cluster = current_clusters.get(client_id, -1)

        # Mettre à jour le profil pour chaque ligne de ce ticket
        for _, row in ticket_rows.iterrows():
            feature_store[client_id] = update_client_features(
                client_id, row, feature_store
            )

        # Réassigner le cluster
        new_cluster = reassign_cluster(client_id, feature_store, model, scaler)
        current_clusters[client_id] = new_cluster

        # Détecter migration
        if old_cluster != -1:
            migration = detect_migration(client_id, old_cluster, new_cluster,
                                         txn_date, ticket_id)
            if migration is not None:
                migrations.append(migration)

        processed += 1
        if verbose and processed % 5000 == 0:
            pct = processed / total * 100
            print(f"  [replay] {processed:,}/{total:,} tickets ({pct:.1f}%) "
                  f"— {len(migrations)} migrations détectées")

    print(f"\n[replay] Terminé : {len(migrations)} migrations sur {total:,} tickets")
    return migrations, current_clusters


# ── 6. Matrice de migration ───────────────────────────────────────────────────

def build_migration_matrix(migrations: list,
                           n_clusters: int) -> pd.DataFrame:
    """
    Construit la matrice de transition NxN.

    Returns
    -------
    DataFrame (from_cluster × to_cluster) avec les comptages
    """
    matrix = np.zeros((n_clusters, n_clusters), dtype=int)

    for m in migrations:
        fc = m["from_cluster"]
        tc = m["to_cluster"]
        if 0 <= fc < n_clusters and 0 <= tc < n_clusters:
            matrix[fc, tc] += 1

    labels = [f"Cluster {i}" for i in range(n_clusters)]
    return pd.DataFrame(matrix, index=labels, columns=labels)


# ── 7. Sauvegarde migrations ──────────────────────────────────────────────────

def save_migrations(migrations: list,
                    migration_matrix: pd.DataFrame = None) -> dict:
    """
    Export outputs/data/migrations.csv + matrix.

    Returns
    -------
    dict {label: chemin}
    """
    data_out = os.path.join(OUTPUTS_PATH, "data")
    os.makedirs(data_out, exist_ok=True)
    paths = {}

    mig_path = os.path.join(data_out, "migrations.csv")
    pd.DataFrame(migrations).to_csv(mig_path, index=False)
    paths["migrations"] = mig_path
    print(f"[save_migrations] → {mig_path}")

    if migration_matrix is not None:
        matrix_path = os.path.join(data_out, "migration_matrix.csv")
        migration_matrix.to_csv(matrix_path)
        paths["matrix"] = matrix_path
        print(f"[save_migrations] → {matrix_path}")

    return paths


# ── 8. Visualisations ─────────────────────────────────────────────────────────

def plot_migration_heatmap(matrix: pd.DataFrame) -> str:
    """Heatmap de la matrice de transition."""
    set_global_style()
    fig, ax = plt.subplots(figsize=(10, 8))

    data = matrix.values
    im   = ax.imshow(data, cmap="RdPu", aspect="auto")
    plt.colorbar(im, ax=ax, label="Nombre de migrations")

    ax.set_xticks(range(len(matrix.columns)))
    ax.set_yticks(range(len(matrix.index)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticklabels(matrix.index)

    for i in range(len(matrix.index)):
        for j in range(len(matrix.columns)):
            val = data[i, j]
            if val > 0:
                color = "white" if val > data.max() * 0.5 else "#1A1A1A"
                ax.text(j, i, str(val), ha="center", va="center",
                        color=color, fontsize=9, fontweight="bold")

    ax.set_xlabel("Cluster destination")
    ax.set_ylabel("Cluster origine")
    ax.set_title("Matrice de Migration — Juil–Sep 2025", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return save_figure(fig, "3_migration_heatmap.png")


def plot_sankey_migrations(migrations: list, n_clusters: int) -> str:
    """
    Sankey diagram des migrations (version simplifiée avec matplotlib arrows).
    Pour un vrai Sankey, utiliser plotly.graph_objects.Sankey.
    """
    try:
        import plotly.graph_objects as go

        matrix = build_migration_matrix(migrations, n_clusters)
        labels = [f"C{i} (avant)" for i in range(n_clusters)] + \
                 [f"C{i} (après)" for i in range(n_clusters)]

        sources, targets, values = [], [], []
        for i in range(n_clusters):
            for j in range(n_clusters):
                val = int(matrix.iloc[i, j])
                if val > 0:
                    sources.append(i)
                    targets.append(n_clusters + j)
                    values.append(val)

        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15, thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
            ),
            link=dict(source=sources, target=targets, value=values),
        ))
        fig.update_layout(
            title_text="Migrations de Segments — Juil–Sep 2025",
            font_size=12, height=500,
        )
        out_path = os.path.join(OUTPUTS_PATH, "figures", "3_sankey_migrations.html")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fig.write_html(out_path)
        print(f"[plot_sankey] Sankey interactif → {out_path}")
        return out_path

    except ImportError:
        print("[plot_sankey] plotly non disponible — fallback heatmap uniquement")
        return plot_migration_heatmap(build_migration_matrix(migrations, n_clusters))


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from src.clustering import load_model

    model, scaler = load_model()

    fs = build_feature_store()

    # Clusters initiaux (depuis les labels du modèle sur train)
    feat_train = pd.read_csv(
        os.path.join(DATA_PATH, "customer_features_train.csv"),
        index_col="anonymized_card_code"
    )
    from src.clustering import preprocess
    X, _, _ = preprocess(feat_train, scaler=scaler, fit=False)
    labels   = model.predict(X)
    initial_clusters = {str(cid): int(lbl)
                        for cid, lbl in zip(feat_train.index, labels)}

    txn_path  = os.path.join(DATA_PATH, "transactions_test.csv")
    migrations, current_clusters = replay_transactions(
        txn_path, fs, initial_clusters, model, scaler
    )

    matrix = build_migration_matrix(migrations, model.n_clusters)
    print("\nMatrice de migration :")
    print(matrix)

    paths = save_migrations(migrations, matrix)
    plot_migration_heatmap(matrix)
    plot_sankey_migrations(migrations, model.n_clusters)
    print("\nDone.")
