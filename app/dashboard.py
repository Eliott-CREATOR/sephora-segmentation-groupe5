"""
dashboard.py
─────────────────────────────────────────────────────────────────────────────
Rôle : interface Streamlit de démonstration du projet de segmentation
dynamique Sephora — Groupe 5, Case 2, BDD #7.

Pages disponibles :
    1. Personas          : profils des clusters avec radar charts et KPIs
    2. Migrations        : matrice de migration et Sankey diagram
    3. Simulation        : slider temporel Juil–Sep, visualisation en direct
    4. Valeur Business   : CLV, revenue at risk, recommandations actionnables
    5. Vue Client        : profil individuel et historique d'un client

Lancement :
    streamlit run app/dashboard.py
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, sys

# Accès au package src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Sephora — Segmentation Dynamique | Groupe 5",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_resource
def load_model_cached():
    try:
        from src.clustering import load_model
        return load_model()
    except Exception as e:
        return None, None

@st.cache_data
def load_features(path):
    if os.path.exists(path):
        return pd.read_csv(path, index_col="anonymized_card_code")
    return None

@st.cache_data
def load_personas():
    try:
        from src.utils import OUTPUTS_PATH
        path = os.path.join(OUTPUTS_PATH, "data", "persona_cards.json")
        if os.path.exists(path):
            import json
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return None

@st.cache_data
def load_migrations():
    try:
        from src.utils import OUTPUTS_PATH
        path = os.path.join(OUTPUTS_PATH, "data", "migrations.csv")
        if os.path.exists(path):
            return pd.read_csv(path, parse_dates=["date"])
    except Exception:
        pass
    return None

@st.cache_data
def load_business_kpis():
    try:
        from src.utils import OUTPUTS_PATH
        path = os.path.join(OUTPUTS_PATH, "data", "business_kpis.csv")
        if os.path.exists(path):
            return pd.read_csv(path)
    except Exception:
        pass
    return None


# ── Données ───────────────────────────────────────────────────────────────────
from src.utils import DATA_PATH, OUTPUTS_PATH, MODELS_PATH

FEAT_TRAIN_PATH = os.path.join(DATA_PATH, "customer_features_train.csv")
data_loaded = os.path.exists(FEAT_TRAIN_PATH)
feat_train = load_features(FEAT_TRAIN_PATH) if data_loaded else None
model, scaler = load_model_cached()
persona_cards = load_personas()
migrations = load_migrations()
biz_kpis = load_business_kpis()

PINK = "#FF0066"
BLACK = "#1A1A1A"
LGRAY = "#F5F5F5"


# ── En-tête ───────────────────────────────────────────────────────────────────
st.markdown(
    f"<h1 style='color:{BLACK}'>💄 Sephora × Albert School — BDD #7</h1>",
    unsafe_allow_html=True
)
st.caption(
    "Groupe 5 | Case 2 : Segmentation Dynamique des Clients & Détection de Migrations  "
    "| Jury : Youri ZAKHVATOV, Directeur Data Analytics & Reports"
)

if data_loaded and model is not None:
    n_clusters = model.n_clusters
    n_clients  = len(feat_train) if feat_train is not None else 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Clients analysés", f"{n_clients:,}")
    col2.metric("Clusters (K optimal)", f"{n_clusters}")
    col3.metric("Migrations détectées", f"{len(migrations):,}" if migrations is not None else "—")
    col4.metric("Période test", "Juil–Sep 2025")
else:
    st.warning(
        "Données non encore générées. "
        "Exécuter les notebooks 0 à 4 pour produire les fichiers dans `data/` et `outputs/`."
    )

st.divider()

# ── Navigation ────────────────────────────────────────────────────────────────
page = st.sidebar.radio(
    "Navigation",
    options=[
        "🧩 Personas",
        "🔀 Migrations",
        "⏱️ Simulation Temporelle",
        "💰 Valeur Business",
        "👤 Vue Client",
    ],
    index=0,
)

st.sidebar.divider()
st.sidebar.caption("BDD #7 — Sephora × Albert School")
st.sidebar.caption("Groupe 5 | Case 2 | Mars 2026")

if not data_loaded:
    st.info(
        "Pour activer le dashboard, déposer le CSV dans `data/` puis "
        "exécuter les notebooks 0 → 4 dans l'ordre."
    )
    st.stop()

# ── Pages ─────────────────────────────────────────────────────────────────────

# ════════════════════════════════════════════════════════════════════════════
if page == "🧩 Personas":
    st.header("🧩 Personas — Profils des Clusters")
    st.markdown(
        "Profils des clusters identifiés par MiniBatchKMeans, "
        "avec KPIs comparés à la **moyenne globale** (obligation Sephora)."
    )

    if feat_train is None or "cluster" not in feat_train.columns:
        st.warning("Exécuter notebooks 0 → 2 pour générer les clusters.")
        st.stop()

    from src.personas import profile_cluster, PERSONA_NAMES
    profile = profile_cluster(feat_train)

    # Sélecteur cluster
    cluster_options = sorted(feat_train["cluster"].unique())
    selected_cl = st.selectbox(
        "Sélectionner un cluster :",
        options=cluster_options,
        format_func=lambda c: f"Cluster {c} — {PERSONA_NAMES.get(int(c), '?')}"
    )

    row = profile.loc[selected_cl]
    name = PERSONA_NAMES.get(int(selected_cl), f"Cluster {selected_cl}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader(f"👤 {name}")
        n_cl = int(row["n_clients"])
        pct_cl = float(row["pct_clients"])
        st.metric("Taille", f"{n_cl:,} clients", f"{pct_cl:.1f}% de la base")

    with col2:
        global_mean = profile.select_dtypes(include=[np.number]).mean()
        st.metric("CA moyen", f"{row['monetary']:.0f} €",
                  f"{(row['monetary']-global_mean['monetary'])/global_mean['monetary']*100:+.1f}% vs moy.")
        st.metric("Panier moyen", f"{row['avg_basket']:.0f} €",
                  f"{(row['avg_basket']-global_mean['avg_basket'])/global_mean['avg_basket']*100:+.1f}% vs moy.")
        st.metric("Fréquence", f"{row['frequency']:.1f} tickets",
                  f"{(row['frequency']-global_mean['frequency'])/global_mean['frequency']*100:+.1f}% vs moy.")

    with col3:
        st.metric("Recency", f"{row['recency_days']:.0f} jours")
        st.metric("Discount rate", f"{row['discount_ratio']*100:.1f}%",
                  f"{(row['discount_ratio']-global_mean['discount_ratio'])*100:+.1f} pp vs moy.")
        if "icb_score" in row:
            st.metric("ICB Score", f"{row['icb_score']:.0f}/100")

    # Radar chart
    radar_path = os.path.join(OUTPUTS_PATH, "figures", f"3_radar_persona_{selected_cl}.png")
    if os.path.exists(radar_path):
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.image(radar_path, caption=f"Radar Chart — {name}", use_container_width=True)
        with col_r2:
            st.subheader("Recommandations Marketing")
            if persona_cards:
                card = next((c for c in persona_cards if c["cluster_id"] == int(selected_cl)), None)
                if card:
                    for rec in card["recommendations"]:
                        st.write(rec)
    else:
        st.info("Radar charts non générés — exécuter notebook 3.")

    # Tableau comparatif tous clusters
    st.subheader("Comparaison tous clusters vs moyenne globale")
    kpi_cols_disp = ["n_clients", "pct_clients", "monetary", "avg_basket",
                     "frequency", "recency_days", "discount_ratio"]
    kpi_cols_disp = [c for c in kpi_cols_disp if c in profile.columns]
    st.dataframe(profile[kpi_cols_disp].round(2), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
elif page == "🔀 Migrations":
    st.header("🔀 Migrations de Segments")
    st.markdown(
        "Matrice de transition et flux de clients entre segments "
        "sur la période Juillet–Septembre 2025."
    )

    if migrations is None or len(migrations) == 0:
        st.warning("Exécuter notebook 3 pour générer `outputs/data/migrations.csv`.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total migrations", f"{len(migrations):,}")
    col2.metric("Clients migrés", f"{migrations['client_id'].nunique():,}")
    col3.metric("Taux de migration",
                f"{migrations['client_id'].nunique() / len(feat_train) * 100:.1f}%")

    # Matrice heatmap
    heatmap_path = os.path.join(OUTPUTS_PATH, "figures", "3_migration_heatmap.png")
    sankey_path  = os.path.join(OUTPUTS_PATH, "figures", "3_sankey_migrations.html")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Matrice de Transition")
        if os.path.exists(heatmap_path):
            st.image(heatmap_path, use_container_width=True)
        else:
            from src.migration_detector import build_migration_matrix
            if model:
                matrix = build_migration_matrix(migrations.to_dict("records"), model.n_clusters)
                fig, ax = plt.subplots(figsize=(8, 6))
                im = ax.imshow(matrix.values, cmap="RdPu", aspect="auto")
                plt.colorbar(im, ax=ax)
                ax.set_xticks(range(len(matrix.columns)))
                ax.set_yticks(range(len(matrix.index)))
                ax.set_xticklabels(matrix.columns, rotation=45)
                ax.set_yticklabels(matrix.index)
                ax.set_title("Matrice de Migration")
                st.pyplot(fig)

    with col_m2:
        st.subheader("Direction des Migrations")
        dir_counts = migrations["direction"].value_counts()
        fig_dir, ax_dir = plt.subplots(figsize=(5, 4))
        colors_dir = [PINK, BLACK, "#CCCCCC"]
        ax_dir.bar(dir_counts.index, dir_counts.values,
                   color=colors_dir[:len(dir_counts)], alpha=0.85, edgecolor="white")
        ax_dir.set_title("Upgrades vs Downgrades vs Lateral")
        st.pyplot(fig_dir)

    # Sankey interactif (si disponible)
    if os.path.exists(sankey_path):
        st.subheader("Sankey Diagram — Flux de Migrations")
        with open(sankey_path) as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=550)

    # Timeline migrations
    st.subheader("Timeline des Migrations")
    mig_timeline = migrations.set_index("date").resample("W").size()
    fig_t, ax_t = plt.subplots(figsize=(12, 4))
    ax_t.plot(mig_timeline.index, mig_timeline.values, color=PINK, lw=2, marker="o", ms=4)
    ax_t.fill_between(mig_timeline.index, mig_timeline.values, alpha=0.2, color=PINK)
    ax_t.set_title("Nombre de migrations par semaine (Juil–Sep 2025)")
    ax_t.set_xlabel("Date")
    ax_t.set_ylabel("Nb migrations")
    plt.xticks(rotation=30)
    fig_t.tight_layout()
    st.pyplot(fig_t)


# ════════════════════════════════════════════════════════════════════════════
elif page == "⏱️ Simulation Temporelle":
    st.header("⏱️ Simulation Temporelle")
    st.markdown(
        "Visualisation en quasi-temps réel des changements de segment : "
        "déplacer le slider pour avancer dans le temps."
    )

    if migrations is None or len(migrations) == 0:
        st.warning("Exécuter notebook 3 pour générer les migrations.")
        st.stop()

    # Slider temporel
    min_date = migrations["date"].min().date() if "date" in migrations.columns else None
    max_date = migrations["date"].max().date() if "date" in migrations.columns else None

    if min_date and max_date:
        selected_date = st.slider(
            "Date de simulation",
            min_value=min_date,
            max_value=max_date,
            value=min_date,
            format="DD/MM/YYYY"
        )

        # Migrations jusqu'à la date sélectionnée
        mig_to_date = migrations[migrations["date"].dt.date <= selected_date]

        col1, col2, col3 = st.columns(3)
        col1.metric("Migrations cumulées", f"{len(mig_to_date):,}")
        col2.metric("Clients affectés", f"{mig_to_date['client_id'].nunique():,}")

        upgrades   = (mig_to_date["direction"] == "upgrade").sum()
        downgrades = (mig_to_date["direction"] == "downgrade").sum()
        col3.metric("Upgrades / Downgrades", f"{upgrades} / {downgrades}",
                    f"Ratio : {upgrades/(downgrades+1):.1f}x")

        # Évolution cumulative par direction
        if len(mig_to_date) > 0:
            fig_sim, ax_sim = plt.subplots(figsize=(12, 4))
            for direction, color in [("upgrade", PINK), ("downgrade", BLACK), ("lateral", "#CCCCCC")]:
                sub = mig_to_date[mig_to_date["direction"] == direction]
                if len(sub) > 0:
                    cumul = sub.set_index("date").resample("D").size().cumsum()
                    ax_sim.plot(cumul.index, cumul.values, color=color, lw=2,
                                label=f"{direction.capitalize()} ({len(sub)})")
            ax_sim.set_title(f"Migrations cumulées jusqu'au {selected_date}")
            ax_sim.set_xlabel("Date")
            ax_sim.set_ylabel("Nb migrations cumulées")
            ax_sim.legend()
            plt.xticks(rotation=30)
            fig_sim.tight_layout()
            st.pyplot(fig_sim)

        # Distribution clusters à la date sélectionnée
        if feat_train is not None and "cluster" in feat_train.columns:
            st.subheader(f"Distribution des clusters au {selected_date}")
            cluster_dist = feat_train["cluster"].value_counts().sort_index()

            # Appliquer les migrations jusqu'à la date
            current_cl = feat_train["cluster"].copy()
            for _, mig in mig_to_date.iterrows():
                cid = str(mig["client_id"])
                if cid in current_cl.index:
                    current_cl[cid] = mig["to_cluster"]

            dist_after = current_cl.value_counts().sort_index()
            dist_df = pd.DataFrame({
                "Avant (Jan-Juin)": cluster_dist,
                "Après migrations": dist_after
            }).fillna(0).astype(int)

            st.bar_chart(dist_df)


# ════════════════════════════════════════════════════════════════════════════
elif page == "💰 Valeur Business":
    st.header("💰 Valeur Business")
    st.markdown(
        "CLV estimée par segment, revenue at risk (clients dormants), "
        "et recommandations actionnables avec ROI estimé."
    )

    if feat_train is None or "cluster" not in feat_train.columns:
        st.warning("Exécuter notebooks 0 → 3.")
        st.stop()

    from src.utils import compute_clv
    from src.personas import PERSONA_NAMES

    # CLV
    feat_train["clv"] = feat_train.apply(
        lambda r: compute_clv(r.get("avg_basket", 0), r.get("frequency", 0),
                              r.get("tenure_days", 0)),
        axis=1
    )

    clv_df = feat_train.groupby("cluster").agg(
        clv_mean  = ("clv", "mean"),
        clv_total = ("clv", "sum"),
        n_clients = ("clv", "count"),
        ca_mean   = ("monetary", "mean"),
    ).round(0)
    clv_df["nom"] = [PERSONA_NAMES.get(int(c), f"Cluster {c}") for c in clv_df.index]

    st.subheader("CLV Estimée par Segment (3 ans, marge 35%)")
    col1, col2 = st.columns(2)
    with col1:
        fig_clv, ax_clv = plt.subplots(figsize=(8, 5))
        cluster_ids_clv = sorted(clv_df.index)
        colors_c = plt.cm.RdPu(np.linspace(0.3, 0.9, len(cluster_ids_clv)))
        ax_clv.bar(range(len(cluster_ids_clv)),
                   clv_df.loc[cluster_ids_clv, "clv_mean"],
                   color=colors_c, edgecolor="white", alpha=0.9)
        ax_clv.set_xticks(range(len(cluster_ids_clv)))
        ax_clv.set_xticklabels([f"C{c}" for c in cluster_ids_clv])
        ax_clv.axhline(clv_df["clv_mean"].mean(), color=BLACK, ls="--",
                       label=f"Moy: {clv_df['clv_mean'].mean():.0f}€")
        ax_clv.set_title("CLV Moyenne par Cluster (€)")
        ax_clv.legend()
        st.pyplot(fig_clv)

    with col2:
        st.dataframe(
            clv_df[["nom", "n_clients", "clv_mean", "clv_total", "ca_mean"]].rename(
                columns={"nom": "Persona", "n_clients": "Clients",
                         "clv_mean": "CLV moy (€)", "clv_total": "CLV tot (€)",
                         "ca_mean": "CA moy (€)"}
            ).astype({"Clients": int, "CLV moy (€)": int, "CA moy (€)": int}),
            use_container_width=True
        )

    # Revenue at risk
    st.subheader("Revenue at Risk — Clients Dormants (recency > 90j)")
    dormant = feat_train[feat_train["recency_days"] > 90]
    n_dorm = len(dormant)
    ca_dorm = dormant["monetary"].sum()

    col_d1, col_d2, col_d3 = st.columns(3)
    col_d1.metric("Clients dormants", f"{n_dorm:,}", f"{n_dorm/len(feat_train)*100:.1f}% de la base")
    col_d2.metric("CA à risque", f"{ca_dorm:,.0f} €")
    col_d3.metric("CA mensuel à risque", f"{ca_dorm/9:,.0f} €")

    # Visualisation figure outputs si disponible
    clv_fig_path = os.path.join(OUTPUTS_PATH, "figures", "4_clv_by_cluster.png")
    if os.path.exists(clv_fig_path):
        st.image(clv_fig_path, use_container_width=True)

    # Recommandations prioritaires
    st.subheader("Recommandations Actionnables — ROI Estimé")
    roi_data = {
        "Action": ["Réactivation dormants", "Upsell cross-axe", "Activation omnicanale"],
        "Clients ciblés": [n_dorm, int(len(feat_train) * 0.15), int(len(feat_train) * 0.12)],
        "CA potentiel (€)": [
            int(n_dorm * 0.15 * 80),
            int(len(feat_train) * 0.15 * 0.20 * 50),
            int(len(feat_train) * 0.12 * 0.10 * 40),
        ],
        "ROI estimé": ["24x", "8x", "5x"],
        "Canal": ["Email + SMS", "App push", "Email + App"],
    }
    st.dataframe(pd.DataFrame(roi_data), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
elif page == "👤 Vue Client":
    st.header("👤 Vue Client Individuel")
    st.markdown(
        "Rechercher un client par son identifiant pour visualiser son "
        "profil de segment, son historique et l'action marketing recommandée."
    )

    if feat_train is None:
        st.warning("Exécuter notebooks 0 → 2.")
        st.stop()

    from src.personas import PERSONA_NAMES

    # Recherche client
    client_id_input = st.text_input(
        "Identifiant client (anonymized_card_code) :",
        placeholder="Ex: 1234567890"
    )

    # Sélection aléatoire
    if st.button("Client aléatoire"):
        random_id = str(np.random.choice(feat_train.index))
        st.session_state["client_id"] = random_id
        client_id_input = random_id

    if "client_id" in st.session_state:
        client_id_input = st.session_state["client_id"]

    if client_id_input:
        client_id = str(client_id_input).strip()

        if client_id not in feat_train.index.astype(str):
            st.error(f"Client '{client_id}' non trouvé dans le feature store.")
        else:
            client_row = feat_train.loc[client_id]
            cluster_id = int(client_row.get("cluster", -1))
            persona_name = PERSONA_NAMES.get(cluster_id, f"Cluster {cluster_id}")

            st.subheader(f"Profil — Client {client_id[:20]}...")

            col1, col2, col3 = st.columns(3)
            col1.metric("Segment", f"Cluster {cluster_id}")
            col1.metric("Persona", persona_name)
            col2.metric("CA total", f"{client_row.get('monetary', 0):.0f} €")
            col2.metric("Panier moyen", f"{client_row.get('avg_basket', 0):.0f} €")
            col3.metric("Fréquence", f"{client_row.get('frequency', 0):.0f} tickets")
            col3.metric("Recency", f"{client_row.get('recency_days', 0):.0f} jours")

            # KPIs supplémentaires
            st.subheader("Profil Détaillé")
            kpi_client = {
                "Discount rate":      f"{client_row.get('discount_ratio', 0)*100:.1f}%",
                "% estore":           f"{client_row.get('pct_estore', 0)*100:.1f}%",
                "Omnicanal":          "✓ Oui" if client_row.get("is_omnichannel", 0) else "✗ Non",
                "Tenure (jours)":     f"{client_row.get('tenure_days', 0):.0f}j",
                "ICB Score":          f"{client_row.get('icb_score', 0):.0f}/100",
                "Marques distinctes": f"{client_row.get('unique_brands', 0):.0f}",
                "Axes distincts":     f"{client_row.get('unique_axes', 0):.0f}",
            }
            kpi_cols = st.columns(4)
            for i, (k, v) in enumerate(kpi_client.items()):
                kpi_cols[i % 4].metric(k, v)

            # Historique de migrations
            if migrations is not None and len(migrations) > 0:
                client_mig = migrations[migrations["client_id"] == client_id]
                if len(client_mig) > 0:
                    st.subheader(f"Historique de Migrations ({len(client_mig)} migrations)")
                    st.dataframe(client_mig[["date", "from_cluster", "to_cluster", "direction"]],
                                 use_container_width=True)
                else:
                    st.info("Ce client n'a pas migré de segment pendant la période Juil–Sep.")

            # Recommandation marketing
            st.subheader("Action Marketing Recommandée")
            if persona_cards:
                card = next((c for c in persona_cards if c["cluster_id"] == cluster_id), None)
                if card:
                    for rec in card["recommendations"]:
                        st.write(rec)
                else:
                    st.write(f"→ Activer le segment {cluster_id} selon les recommandations cluster.")
