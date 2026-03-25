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

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Sephora — Segmentation Dynamique | Groupe 5",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── En-tête ───────────────────────────────────────────────────────────────────
st.title("💄 Sephora × Albert School — BDD #7")
st.caption(
    "Groupe 5 | Case 2 : Segmentation Dynamique des Clients & Détection de Migrations  "
    "| Jury : Youri ZAKHVATOV, Directeur Data Analytics & Reports"
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

# ── Pages ─────────────────────────────────────────────────────────────────────

if page == "🧩 Personas":
    st.header("🧩 Personas")
    st.markdown(
        "Profils des clusters identifiés par le modèle MiniBatchKMeans, "
        "avec radar charts et KPIs comparés à la moyenne globale."
    )
    st.info(
        "À connecter avec les données réelles — exécuter les notebooks "
        "0 à 2 pour générer `models/kmeans_model.pkl` et `data/customer_features.csv`."
    )

elif page == "🔀 Migrations":
    st.header("🔀 Migrations de Segments")
    st.markdown(
        "Matrice de transition et Sankey diagram des flux de clients "
        "entre segments sur la période Juillet–Septembre 2025."
    )
    st.info(
        "À connecter avec les données réelles — exécuter le notebook 3 "
        "pour générer `outputs/data/migrations.csv`."
    )

elif page == "⏱️ Simulation Temporelle":
    st.header("⏱️ Simulation Temporelle")
    st.markdown(
        "Visualisation en quasi-temps réel des changements de segment : "
        "déplacer le slider pour avancer dans le temps et observer les migrations."
    )
    st.info(
        "À connecter avec les données réelles — le slider rejoue les "
        "transactions de Juillet à Septembre 2025 chronologiquement."
    )

elif page == "💰 Valeur Business":
    st.header("💰 Valeur Business")
    st.markdown(
        "CLV estimée par segment, revenue at risk (clients dormants), "
        "et recommandations actionnables avec ROI estimé en euros."
    )
    st.info(
        "À connecter avec les données réelles — exécuter le notebook 4 "
        "pour générer `outputs/data/business_kpis.csv`."
    )

elif page == "👤 Vue Client":
    st.header("👤 Vue Client Individuel")
    st.markdown(
        "Rechercher un client par son identifiant pour visualiser son "
        "historique d'achats, l'évolution de son segment dans le temps "
        "et l'action marketing recommandée."
    )
    st.info(
        "À connecter avec les données réelles — entrer un `anonymized_card_code` "
        "présent dans `data/customer_features.csv`."
    )
