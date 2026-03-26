"""
clustering.py
─────────────────────────────────────────────────────────────────────────────
Rôle : entraîner, valider et sauvegarder le modèle de clustering
MiniBatchKMeans sur les profils clients agrégés.

Appelé par : notebooks/2_clustering.ipynb
Produit    : models/kmeans_model.pkl
             models/scaler.pkl
             outputs/figures/2_elbow_curve.png
             outputs/figures/2_silhouette_scores.png
             outputs/figures/2_umap_clusters.png
─────────────────────────────────────────────────────────────────────────────
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA

from src.utils import MODELS_PATH, OUTPUTS_PATH, RANDOM_SEED, set_global_style, save_figure

# Features numériques utilisées pour le clustering (exclut socio-demo)
CLUSTERING_FEATURES = [
    "recency_days", "frequency", "monetary",
    "avg_basket", "max_basket", "avg_items_per_basket", "discount_ratio",
    "unique_brands", "brand_entropy", "top_brand_share",
    "unique_axes", "axe_entropy", "top_axe_share",
    "pct_discounted_txn", "icb_score",
    "pct_estore", "nb_channels", "is_omnichannel",
    "pct_exclusive", "pct_selective", "pct_sephora",
    "tenure_days", "avg_days_between_purchases",
    "purchase_regularity", "trend_spend_monthly",
]

K_RANGE = range(4, 12)   # K=4 à K=11


# ── 1. Preprocessing ──────────────────────────────────────────────────────────

def preprocess(df: pd.DataFrame,
               scaler: StandardScaler = None,
               fit: bool = True):
    """
    Sélectionne les features numériques de clustering et standardise.

    Parameters
    ----------
    df      : DataFrame clients (index = anonymized_card_code)
    scaler  : scaler existant (si fit=False, utilisé pour transform)
    fit     : si True, fit un nouveau StandardScaler

    Returns
    -------
    X       : np.ndarray normalisé
    scaler  : StandardScaler fitté
    cols    : liste des colonnes utilisées
    """
    cols = [c for c in CLUSTERING_FEATURES if c in df.columns]
    X_raw = df[cols].fillna(0).values

    if fit or scaler is None:
        scaler = StandardScaler()
        X = scaler.fit_transform(X_raw)
    else:
        X = scaler.transform(X_raw)

    return X, scaler, cols


# ── 2. Trouver K optimal ──────────────────────────────────────────────────────

def find_optimal_k(X: np.ndarray,
                   k_range=K_RANGE,
                   random_state: int = RANDOM_SEED) -> dict:
    """
    Itère K=4→11, calcule Silhouette Score, Calinski-Harabasz et Inertia.

    Returns
    -------
    dict {
        'k_values': list,
        'inertias': list,
        'silhouette_scores': list,
        'calinski_scores': list,
        'davies_scores': list,
        'optimal_k': int  (max silhouette)
    }
    """
    results = {
        "k_values":         [],
        "inertias":         [],
        "silhouette_scores": [],
        "calinski_scores":  [],
        "davies_scores":    [],
    }

    for k in k_range:
        print(f"  [find_optimal_k] K={k}...")
        model = MiniBatchKMeans(
            n_clusters=k, random_state=random_state,
            n_init=10, batch_size=4096
        )
        labels = model.fit_predict(X)

        results["k_values"].append(k)
        results["inertias"].append(float(model.inertia_))
        results["silhouette_scores"].append(
            float(silhouette_score(X, labels, sample_size=min(10000, len(X)),
                                   random_state=random_state))
        )
        results["calinski_scores"].append(float(calinski_harabasz_score(X, labels)))
        results["davies_scores"].append(float(davies_bouldin_score(X, labels)))

    results["optimal_k"] = results["k_values"][
        int(np.argmax(results["silhouette_scores"]))
    ]
    print(f"  → K optimal (max Silhouette) = {results['optimal_k']}")
    return results


# ── 3. Entraînement ───────────────────────────────────────────────────────────

def train_model(X: np.ndarray, k: int,
                random_state: int = RANDOM_SEED) -> MiniBatchKMeans:
    """
    Entraîne MiniBatchKMeans avec k clusters.

    Returns
    -------
    MiniBatchKMeans fitté
    """
    print(f"[train_model] Entraînement MiniBatchKMeans K={k}...")
    model = MiniBatchKMeans(
        n_clusters=k, random_state=random_state,
        n_init=10, batch_size=4096, max_iter=300
    )
    model.fit(X)
    print(f"  → Inertia : {model.inertia_:.1f}")
    return model


# ── 4. Validation ─────────────────────────────────────────────────────────────

def validate_model(X: np.ndarray, labels: np.ndarray,
                   random_state: int = RANDOM_SEED) -> dict:
    """
    Rapport complet de validation.

    Returns
    -------
    dict avec silhouette, calinski_harabasz, davies_bouldin,
    cluster_sizes, cluster_pcts
    """
    sil = float(silhouette_score(X, labels,
                                  sample_size=min(10000, len(X)),
                                  random_state=random_state))
    ch  = float(calinski_harabasz_score(X, labels))
    db  = float(davies_bouldin_score(X, labels))

    unique, counts = np.unique(labels, return_counts=True)
    sizes = {int(k): int(v) for k, v in zip(unique, counts)}
    pcts  = {int(k): float(v / len(labels) * 100) for k, v in zip(unique, counts)}

    report = {
        "n_clusters":       int(len(unique)),
        "n_samples":        int(len(labels)),
        "silhouette":       sil,
        "calinski_harabasz": ch,
        "davies_bouldin":   db,
        "cluster_sizes":    sizes,
        "cluster_pcts":     pcts,
    }

    print(f"\n[validate_model] Rapport de validation :")
    print(f"  Silhouette Score   : {sil:.4f}  (↑ max 1.0 = parfait)")
    print(f"  Calinski-Harabasz  : {ch:.1f}  (↑ plus grand = mieux)")
    print(f"  Davies-Bouldin     : {db:.4f}  (↓ plus petit = mieux)")
    print(f"  Distribution clusters : {sizes}")
    return report


# ── 5. Sauvegarde ─────────────────────────────────────────────────────────────

def save_model(model: MiniBatchKMeans, scaler: StandardScaler) -> dict:
    """
    Sauvegarde models/kmeans_model.pkl + models/scaler.pkl via joblib.

    Returns
    -------
    dict {label: chemin}
    """
    os.makedirs(MODELS_PATH, exist_ok=True)
    paths = {}

    model_path  = os.path.join(MODELS_PATH, "kmeans_model.pkl")
    scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")

    joblib.dump(model,  model_path)
    joblib.dump(scaler, scaler_path)

    paths["model"]  = model_path
    paths["scaler"] = scaler_path

    print(f"[save_model] Modèle sauvegardé → {model_path}")
    print(f"[save_model] Scaler sauvegardé → {scaler_path}")
    return paths


# ── 6. Chargement ─────────────────────────────────────────────────────────────

def load_model() -> tuple:
    """
    Charge le modèle et le scaler sauvegardés.

    Returns
    -------
    (MiniBatchKMeans, StandardScaler)
    """
    model_path  = os.path.join(MODELS_PATH, "kmeans_model.pkl")
    scaler_path = os.path.join(MODELS_PATH, "scaler.pkl")

    assert os.path.exists(model_path),  f"Modèle introuvable : {model_path}"
    assert os.path.exists(scaler_path), f"Scaler introuvable : {scaler_path}"

    model  = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print(f"[load_model] Chargé : K={model.n_clusters}, scaler fitted")
    return model, scaler


# ── 7. Prédiction cluster ─────────────────────────────────────────────────────

def assign_cluster(feature_vector: np.ndarray,
                   model: MiniBatchKMeans,
                   scaler: StandardScaler) -> int:
    """
    Prédit le cluster pour un vecteur de features brutes.

    Parameters
    ----------
    feature_vector : 1D array de features (dans l'ordre CLUSTERING_FEATURES)
    model, scaler  : modèle et scaler chargés

    Returns
    -------
    int : numéro de cluster
    """
    fv = np.array(feature_vector, dtype=float).reshape(1, -1)
    fv_scaled = scaler.transform(fv)
    return int(model.predict(fv_scaled)[0])


# ── 8. Visualisations ─────────────────────────────────────────────────────────

def plot_elbow_curve(results: dict) -> str:
    """Génère et sauvegarde la courbe Elbow + Silhouette."""
    set_global_style()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    ks      = results["k_values"]
    optimal = results["optimal_k"]

    # Inertia (elbow)
    ax = axes[0]
    ax.plot(ks, results["inertias"], "o-", color="#FF0066", lw=2, ms=6)
    ax.axvline(optimal, ls="--", color="#1A1A1A", alpha=0.5, label=f"K={optimal}")
    ax.set_title("Inertia (Elbow Method)")
    ax.set_xlabel("K")
    ax.set_ylabel("Inertia")
    ax.legend()

    # Silhouette
    ax = axes[1]
    ax.plot(ks, results["silhouette_scores"], "o-", color="#FF0066", lw=2, ms=6)
    ax.axvline(optimal, ls="--", color="#1A1A1A", alpha=0.5, label=f"K={optimal}")
    ax.set_title("Silhouette Score")
    ax.set_xlabel("K")
    ax.set_ylabel("Score")
    ax.legend()

    # Calinski-Harabasz
    ax = axes[2]
    ax.plot(ks, results["calinski_scores"], "o-", color="#FF0066", lw=2, ms=6)
    ax.axvline(optimal, ls="--", color="#1A1A1A", alpha=0.5, label=f"K={optimal}")
    ax.set_title("Calinski-Harabasz Index")
    ax.set_xlabel("K")
    ax.set_ylabel("Index")
    ax.legend()

    fig.suptitle(f"Choix du K optimal — K={optimal} retenu", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return save_figure(fig, "2_elbow_curve.png")


def plot_clusters_pca(X: np.ndarray, labels: np.ndarray) -> str:
    """Projection PCA 2D des clusters."""
    set_global_style()
    pca = PCA(n_components=2, random_state=RANDOM_SEED)
    X2d = pca.fit_transform(X)

    fig, ax = plt.subplots(figsize=(10, 7))
    n_clusters = len(np.unique(labels))
    colors = plt.cm.tab10(np.linspace(0, 1, n_clusters))

    for i, (cl, color) in enumerate(zip(sorted(np.unique(labels)), colors)):
        mask = labels == cl
        ax.scatter(X2d[mask, 0], X2d[mask, 1],
                   c=[color], alpha=0.35, s=8, label=f"Cluster {cl}")

    ax.set_title(f"Clusters — Projection PCA 2D "
                 f"(variance expliquée : {pca.explained_variance_ratio_.sum()*100:.1f}%)")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.legend(markerscale=3, loc="best")
    fig.tight_layout()
    return save_figure(fig, "2_umap_clusters.png")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from src.utils import DATA_PATH

    feat_path = os.path.join(DATA_PATH, "customer_features_train.csv")
    df = pd.read_csv(feat_path, index_col="anonymized_card_code")

    X, scaler, cols = preprocess(df)
    print(f"Matrix shape : {X.shape}")

    k_results = find_optimal_k(X)
    plot_elbow_curve(k_results)

    model  = train_model(X, k=k_results["optimal_k"])
    labels = model.labels_

    report = validate_model(X, labels)
    paths  = save_model(model, scaler)

    plot_clusters_pca(X, labels)
    print("\nDone.")
