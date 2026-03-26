"""
personas.py
─────────────────────────────────────────────────────────────────────────────
Rôle : profiler chaque cluster issu du clustering et générer les fiches
personas utilisables par les équipes marketing Sephora.

Appelé par : notebooks/3_personas_migration.ipynb
Produit    : outputs/figures/3_radar_persona_*.png
             outputs/data/personas_profiles.csv
─────────────────────────────────────────────────────────────────────────────
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from src.utils import (DATA_PATH, OUTPUTS_PATH, RANDOM_SEED,
                       set_global_style, save_figure,
                       format_delta, compute_clv, SEPHORA_COLORS)

# 8 axes du radar chart (selon le brief)
RADAR_AXES = [
    "Budget",       # monetary normalisé
    "Fidélité",     # frequency normalisé
    "Diversité",    # brand_entropy normalisé
    "Premium",      # (pct_selective + pct_exclusive) / 2
    "Digital",      # pct_estore normalisé
    "Promo",        # discount_ratio normalisé
    "Skincare",     # % CA axe SKINCARE
    "Fragrance",    # % CA axe FRAGRANCE
]

# Noms des personas (calibrés sur les archétypes Sephora)
PERSONA_NAMES = {
    0: "La Beauty Addict Omnicanale",
    1: "L'Exploratrice GenZ",
    2: "La Loyaliste Parfum Premium",
    3: "La Pragmatique Skincare",
    4: "Le Client Dormant",
    5: "L'Opportuniste Promo",
    6: "Le Connaisseur Masculin",
    7: "La VIP Exclusive",
}


# ── 1. Profilage cluster ──────────────────────────────────────────────────────

def profile_cluster(features: pd.DataFrame,
                    raw_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Calcule les KPIs moyens de chaque cluster.

    Parameters
    ----------
    features : DataFrame avec colonne 'cluster' + toutes les features
    raw_df   : DataFrame brut optionnel (pour top marques, top axes)

    Returns
    -------
    DataFrame (index = cluster_id) avec KPIs moyens
    """
    assert "cluster" in features.columns, "Colonne 'cluster' manquante"

    kpi_cols = [
        "recency_days", "frequency", "monetary", "avg_basket",
        "discount_ratio", "pct_estore", "brand_entropy", "icb_score",
        "tenure_days", "is_omnichannel",
        "pct_exclusive", "pct_selective", "pct_sephora",
        "axe_entropy", "top_brand_share", "purchase_regularity",
    ]
    kpi_cols = [c for c in kpi_cols if c in features.columns]

    profile = features.groupby("cluster")[kpi_cols].mean()
    profile["n_clients"] = features.groupby("cluster").size()
    profile["pct_clients"] = profile["n_clients"] / len(features) * 100
    profile["total_ca"] = features.groupby("cluster")["monetary"].sum()

    # ICB moyen
    if "icb_score" in features.columns:
        profile["icb_mean"] = features.groupby("cluster")["icb_score"].mean()

    # Top axe dominant par cluster (si raw_df disponible)
    if raw_df is not None and "cluster" not in raw_df.columns:
        client_cluster = features["cluster"].reset_index()
        client_cluster.columns = ["anonymized_card_code", "cluster"]
        raw_with_cluster = raw_df.merge(client_cluster, on="anonymized_card_code", how="left")

        top_axe = (raw_with_cluster.groupby(["cluster", "Axe_Desc"])["salesVatEUR"]
                                   .sum()
                                   .reset_index()
                                   .sort_values("salesVatEUR", ascending=False)
                                   .groupby("cluster")["Axe_Desc"].first()
                                   .rename("top_axe"))
        top_brand = (raw_with_cluster.groupby(["cluster", "brand"])["salesVatEUR"]
                                     .sum()
                                     .reset_index()
                                     .sort_values("salesVatEUR", ascending=False)
                                     .groupby("cluster")["brand"].first()
                                     .rename("top_brand"))
        profile = profile.join(top_axe, how="left")
        profile = profile.join(top_brand, how="left")

    return profile


# ── 2. Delta vs moyenne globale ───────────────────────────────────────────────

def compute_delta_vs_global(profile: pd.DataFrame,
                             global_stats: pd.Series = None) -> pd.DataFrame:
    """
    Calcule le delta de chaque KPI par rapport à la moyenne globale.

    Returns
    -------
    DataFrame avec les colonnes delta_* en %
    """
    if global_stats is None:
        # Moyenne pondérée par taille de cluster
        num_cols = profile.select_dtypes(include=[np.number]).columns
        global_stats = (profile[num_cols]
                        .multiply(profile["n_clients"], axis=0)
                        .sum() / profile["n_clients"].sum())

    delta_df = pd.DataFrame(index=profile.index)
    for col in profile.select_dtypes(include=[np.number]).columns:
        if col in ["n_clients", "pct_clients", "total_ca"]:
            continue
        ref = global_stats.get(col, 0)
        if ref != 0:
            delta_df[f"delta_{col}_pct"] = (profile[col] - ref) / abs(ref) * 100
        else:
            delta_df[f"delta_{col}_pct"] = 0.0

    return pd.concat([profile, delta_df], axis=1)


# ── 3. Fiche persona structurée ───────────────────────────────────────────────

def generate_persona_card(cluster_id: int,
                           profile_row: pd.Series,
                           global_stats: pd.Series,
                           features: pd.DataFrame = None) -> dict:
    """
    Retourne un dict structuré par persona.

    Returns
    -------
    dict avec : nom, taille, KPIs, deltas, recommandations
    """
    n_clients = int(profile_row.get("n_clients", 0))
    monetary  = float(profile_row.get("monetary", 0))
    freq      = float(profile_row.get("frequency", 0))
    avg_bask  = float(profile_row.get("avg_basket", 0))
    recency   = float(profile_row.get("recency_days", 0))
    disc_rate = float(profile_row.get("discount_ratio", 0))
    pct_e     = float(profile_row.get("pct_estore", 0))
    tenure    = float(profile_row.get("tenure_days", 0))
    icb       = float(profile_row.get("icb_score", 0))

    # CLV estimée
    clv = compute_clv(avg_bask, freq, tenure)

    # Nom du persona
    name = PERSONA_NAMES.get(cluster_id, f"Persona {cluster_id}")

    # Recommandations marketing (basées sur le profil)
    recommendations = _generate_recommendations(profile_row, name)

    card = {
        "cluster_id":     cluster_id,
        "name":           name,
        "n_clients":      n_clients,
        "pct_clients":    float(profile_row.get("pct_clients", 0)),
        "total_ca":       float(profile_row.get("total_ca", monetary * n_clients)),
        "kpis": {
            "monetary_mean":   round(monetary, 2),
            "avg_basket":      round(avg_bask, 2),
            "frequency":       round(freq, 2),
            "recency_days":    round(recency, 1),
            "discount_ratio":  round(disc_rate, 4),
            "pct_estore":      round(pct_e, 4),
            "icb_score":       round(icb, 1),
            "clv_estimated":   round(clv, 2),
        },
        "deltas_vs_global": {
            "monetary":  format_delta(monetary, float(global_stats.get("monetary", monetary))),
            "avg_basket": format_delta(avg_bask, float(global_stats.get("avg_basket", avg_bask))),
            "frequency": format_delta(freq, float(global_stats.get("frequency", freq))),
            "recency":   format_delta(recency, float(global_stats.get("recency_days", recency))),
            "discount":  format_delta(disc_rate, float(global_stats.get("discount_ratio", disc_rate)),
                                       unit="pp", decimals=1),
        },
        "recommendations": recommendations,
    }
    return card


def _generate_recommendations(profile_row: pd.Series, persona_name: str) -> list:
    """Génère 3 recommandations marketing contextuelles."""
    recs = []

    disc_rate = float(profile_row.get("discount_ratio", 0))
    pct_e     = float(profile_row.get("pct_estore", 0))
    recency   = float(profile_row.get("recency_days", 0))
    freq      = float(profile_row.get("frequency", 0))
    icb       = float(profile_row.get("icb_score", 0))
    pct_excl  = float(profile_row.get("pct_exclusive", 0))
    pct_selec = float(profile_row.get("pct_selective", 0))

    # Activation canal
    if pct_e > 0.5:
        recs.append("🖥️  Push notifications app + email personnalisé (canal digital dominant)")
    elif pct_e < 0.1:
        recs.append("🏪  Animation en magasin : échantillons, beauty consultations exclusives")
    else:
        recs.append("🔀  Parcours omnicanal : réserver en app, retirer en magasin")

    # Promo / valeur
    if disc_rate > 0.20:
        recs.append("💰  Offres flash ciblées avec countdown — sensible aux promotions")
    elif pct_excl + pct_selec > 0.70:
        recs.append("👑  Programme Sephora Rouge VIP : accès early sale, lancements exclusifs")
    else:
        recs.append("🎁  Programme de fidélité gamifié : double points sur marques exclusives")

    # Réactivation / rétention / découverte
    if recency > 90:
        recs.append("⏰  Campagne réactivation : 'Vous nous manquez' + code promo à durée limitée")
    elif icb > 60:
        recs.append("✨  Curation 'Nouveautés pour vous' : algorithme de découverte de marques")
    elif freq < 2:
        recs.append("📧  Séquence email onboarding post-1er achat : cross-sell axe complémentaire")
    else:
        recs.append("🔄  Abonnement auto-réassort (skincare routine) : +2 commandes/an estimé")

    return recs[:3]


# ── 4. Radar chart ────────────────────────────────────────────────────────────

def _compute_radar_values(profile_row: pd.Series,
                           global_max: dict,
                           raw_df_cluster: pd.DataFrame = None) -> np.ndarray:
    """Calcule les 8 valeurs normalisées [0–1] pour le radar chart."""
    vals = []

    # Budget (monetary normalisé)
    vals.append(min(1.0, float(profile_row.get("monetary", 0)) / max(global_max.get("monetary", 1), 1)))

    # Fidélité (frequency normalisé)
    vals.append(min(1.0, float(profile_row.get("frequency", 0)) / max(global_max.get("frequency", 1), 1)))

    # Diversité (brand_entropy normalisé)
    vals.append(min(1.0, float(profile_row.get("brand_entropy", 0)) / max(global_max.get("brand_entropy", 1), 1)))

    # Premium (pct_selective + pct_exclusive) / 2
    prem = (float(profile_row.get("pct_selective", 0)) + float(profile_row.get("pct_exclusive", 0))) / 2
    vals.append(min(1.0, prem))

    # Digital (pct_estore)
    vals.append(min(1.0, float(profile_row.get("pct_estore", 0))))

    # Promo (discount_ratio × 5 pour amplifier sur [0–1])
    vals.append(min(1.0, float(profile_row.get("discount_ratio", 0)) * 5))

    # Skincare orientation (pct CA axe skincare)
    # Utiliser axe_entropy comme proxy si raw_df non dispo
    vals.append(min(1.0, float(profile_row.get("_pct_skincare", 0.3))))

    # Fragrance orientation
    vals.append(min(1.0, float(profile_row.get("_pct_fragrance", 0.1))))

    return np.array(vals)


def plot_radar_chart(profile_row: pd.Series,
                     cluster_id: int,
                     global_max: dict,
                     global_mean_row: pd.Series = None) -> str:
    """
    Génère un radar chart à 8 axes pour un persona.

    Returns
    -------
    str : chemin de la figure sauvegardée
    """
    set_global_style()

    n_axes  = len(RADAR_AXES)
    angles  = np.linspace(0, 2 * np.pi, n_axes, endpoint=False).tolist()
    angles += angles[:1]  # fermer le polygone

    vals = _compute_radar_values(profile_row, global_max).tolist()
    vals += vals[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True},
                           facecolor=SEPHORA_COLORS["white"])
    ax.set_facecolor(SEPHORA_COLORS["lgray"])

    # Remplir la grille
    ax.plot(angles, vals, "o-", lw=2.5, color=SEPHORA_COLORS["pink"],
            zorder=3, ms=5)
    ax.fill(angles, vals, alpha=0.25, color=SEPHORA_COLORS["pink"])

    # Moyenne globale en comparaison (si fournie)
    if global_mean_row is not None:
        mean_vals = _compute_radar_values(global_mean_row, global_max).tolist()
        mean_vals += mean_vals[:1]
        ax.plot(angles, mean_vals, "--", lw=1.5, color=SEPHORA_COLORS["black"],
                alpha=0.5, label="Moyenne globale")

    # Axes labels
    ax.set_thetagrids(np.degrees(angles[:-1]), RADAR_AXES, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.50, 0.75, 1.0])
    ax.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=7, color="gray")
    ax.grid(True, alpha=0.3)

    name = PERSONA_NAMES.get(cluster_id, f"Cluster {cluster_id}")
    ax.set_title(f"{name}\n(Cluster {cluster_id})",
                 size=12, fontweight="bold", pad=20,
                 color=SEPHORA_COLORS["black"])

    if global_mean_row is not None:
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

    fig.tight_layout()
    return save_figure(fig, f"3_radar_persona_{cluster_id}.png")


# ── 5. ICB — Indice de Curiosité Beauté ──────────────────────────────────────

def compute_beauty_curiosity_index(features: pd.DataFrame) -> pd.Series:
    """
    Calcule le score ICB (Indice de Curiosité Beauté) 0–100 par client.
    (Version de validation / recalcul si icb_score absent)

    Returns
    -------
    pd.Series indexée par client_id
    """
    if "icb_score" in features.columns:
        return features["icb_score"]

    cols = ["brand_entropy", "axe_entropy", "unique_brands"]
    cols = [c for c in cols if c in features.columns]

    icb = pd.Series(0.0, index=features.index)
    for col in cols:
        mx = features[col].max()
        if mx > 0:
            icb += features[col] / mx * (100 / len(cols))

    return icb


# ── 6. Comparaison avec RFM Sephora ──────────────────────────────────────────

def compare_with_sephora_rfm(features: pd.DataFrame) -> pd.DataFrame:
    """
    Compare nos clusters avec les RFM_Segment_ID fournis par Sephora.

    Returns
    -------
    DataFrame : croisement cluster × RFM_Segment_ID avec effectifs
    """
    assert "cluster" in features.columns, "Colonne 'cluster' manquante"
    assert "RFM_Segment_ID" in features.columns, "Colonne 'RFM_Segment_ID' manquante"

    cross = pd.crosstab(features["cluster"],
                        features["RFM_Segment_ID"],
                        margins=True,
                        margins_name="Total")

    # Normalisation en %
    cross_pct = cross.div(cross["Total"], axis=0) * 100
    cross_pct = cross_pct.drop(columns=["Total"])
    cross_pct["Total_clients"] = cross["Total"]

    return cross_pct


# ── 7. Sauvegarde ─────────────────────────────────────────────────────────────

def save_personas(profile: pd.DataFrame,
                  persona_cards: list = None) -> dict:
    """
    Sauvegarde outputs/data/personas_profiles.csv + persona_cards.json.

    Returns
    -------
    dict {label: chemin}
    """
    data_out = os.path.join(OUTPUTS_PATH, "data")
    os.makedirs(data_out, exist_ok=True)
    paths = {}

    csv_path = os.path.join(data_out, "personas_profiles.csv")
    profile.to_csv(csv_path)
    paths["profiles"] = csv_path
    print(f"[save_personas] → {csv_path}")

    if persona_cards:
        import json
        json_path = os.path.join(data_out, "persona_cards.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(persona_cards, f, ensure_ascii=False, indent=2)
        paths["cards"] = json_path
        print(f"[save_personas] → {json_path}")

    return paths


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from src.clustering import load_model, preprocess

    # Charger les features + assigner les clusters
    feat = pd.read_csv(os.path.join(DATA_PATH, "customer_features_train.csv"),
                       index_col="anonymized_card_code")
    model, scaler = load_model()
    X, _, _ = preprocess(feat, scaler=scaler, fit=False)
    feat["cluster"] = model.predict(X)

    # Profil clusters
    profile = profile_cluster(feat)
    profile = compute_delta_vs_global(profile)
    print(profile[["n_clients", "pct_clients", "monetary",
                    "avg_basket", "frequency", "recency_days"]].round(2))

    # Cartes personas
    global_stats = profile.select_dtypes(include=[np.number]).mean()
    global_max   = profile.select_dtypes(include=[np.number]).max().to_dict()
    cards = []
    for cl in profile.index:
        card = generate_persona_card(cl, profile.loc[cl], global_stats, feat)
        cards.append(card)
        print(f"\n[Persona {cl}] {card['name']}")
        print(f"  {card['n_clients']:,} clients | CA moyen {card['kpis']['monetary_mean']:.0f} EUR")
        print(f"  Recommandations : {card['recommendations']}")

    # Radar charts
    for cl in profile.index:
        path = plot_radar_chart(profile.loc[cl], cl, global_max,
                                global_mean_row=global_stats)
        print(f"  Radar → {path}")

    # Comparaison RFM Sephora
    if "RFM_Segment_ID" in feat.columns:
        cross = compare_with_sephora_rfm(feat)
        print("\nComparaison clusters × RFM Sephora :")
        print(cross.round(1))

    save_personas(profile, cards)
    print("\nDone.")
