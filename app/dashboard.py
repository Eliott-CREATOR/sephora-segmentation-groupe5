"""
dashboard.py
─────────────────────────────────────────────────────────────────────────────
Sephora × Albert School — BDD #7 | Groupe 5 | Case 2
Dashboard CRM analytique — focus argent & actionnabilité

Pages :
    1. 💰 Command Center   : KPIs financiers + alertes churn + vs RFM statique
    2. 📡 Migrations Live  : slider temporel + action CRM par migration + savings
    3. 📈 Valeur Business  : CLV, scatter ROI, top-10 opportunités
    4. 🧩 Personas         : profils clusters + radar charts
    5. 👤 Vue Client       : profil individuel + historique + recommandation

Font : IBM Plex Mono / IBM Plex Sans
Palette : #000000 noir | #C9A84C or | #E63946 rouge | #2DC653 vert
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, sys, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Config page ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sephora CRM | Groupe 5",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ───────────────────────────────────────────────────────────────────
GOLD   = "#C9A84C"
BLACK  = "#000000"
WHITE  = "#FFFFFF"
RED    = "#E63946"
GREEN  = "#2DC653"
GRAY   = "#1C1C1C"
LGRAY  = "#2A2A2A"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;700&family=IBM+Plex+Sans:wght@200;400;700;900&display=swap');

  :root {{
    --gold:  {GOLD};
    --black: {BLACK};
    --red:   {RED};
    --green: {GREEN};
    --gray:  {GRAY};
  }}

  html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    background: #0D0D0D;
    color: #E8E8E8;
  }}

  .page-header {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.05rem;
    font-weight: 300;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold);
    border-bottom: 1px solid var(--gold);
    padding-bottom: 0.4rem;
    margin-bottom: 1.4rem;
  }}

  .kpi-gold {{
    background: linear-gradient(135deg, #1A1700 0%, #2A2100 60%, #1A1700 100%);
    border: 1px solid var(--gold);
    border-radius: 6px;
    padding: 1.1rem 1.4rem;
    text-align: center;
  }}
  .kpi-gold .kpi-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.35rem;
  }}
  .kpi-gold .kpi-value {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 1.9rem;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1;
  }}
  .kpi-gold .kpi-delta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    margin-top: 0.3rem;
    color: #AAAAAA;
  }}

  .alert-red {{
    background: linear-gradient(135deg, #1A0007 0%, #250010 100%);
    border-left: 3px solid var(--red);
    border-radius: 4px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.5rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
  }}
  .alert-red .alert-title {{ color: var(--red); font-weight: 700; }}
  .alert-red .alert-body  {{ color: #D0D0D0; margin-top: 0.2rem; }}

  .alert-green {{
    background: linear-gradient(135deg, #001A06 0%, #002510 100%);
    border-left: 3px solid var(--green);
    border-radius: 4px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.5rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
  }}
  .alert-green .alert-title {{ color: var(--green); font-weight: 700; }}
  .alert-green .alert-body  {{ color: #D0D0D0; margin-top: 0.2rem; }}

  .versus-box {{
    background: linear-gradient(180deg, #121212 0%, #0D0D0D 100%);
    border: 1px solid #333;
    border-radius: 6px;
    padding: 1rem 1.2rem;
  }}
  .versus-box h5 {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 0.6rem;
  }}

  .crm-pill {{
    display: inline-block;
    background: var(--gold);
    color: #000;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 0.18rem 0.55rem;
    border-radius: 3px;
    text-transform: uppercase;
    margin-right: 0.4rem;
  }}

  /* Streamlit overrides */
  .stSidebar {{ background: #0A0A0A !important; }}
  .stMetric {{ background: #141414 !important; border-radius: 6px; padding: 0.7rem !important; }}
  div[data-testid="metric-container"] {{ background: #141414; border-radius: 6px; padding: 0.7rem; }}
</style>
""", unsafe_allow_html=True)

# ── CRM Actions dict ──────────────────────────────────────────────────────────
CRM_ACTIONS = {
    "downgrade": {
        "label": "Alerte Churn — Intervention Urgente",
        "action": "Email personnalisé + offre 15% + appel conseillère (VIP uniquement)",
        "canal":  "Email + SMS + App Push",
        "retention_48h": 0.18,
        "retention_30d": 0.32,
        "cost_per_client": 3.5,
    },
    "upgrade": {
        "label": "Signal d'Ascension — Nurturing Premium",
        "action": "Programme Beauty Insider Next Level + invitation événement privé",
        "canal":  "Email + App Push",
        "retention_48h": 0.08,
        "retention_30d": 0.22,
        "cost_per_client": 2.0,
    },
    "lateral": {
        "label": "Migration Latérale — Réengagement Axe",
        "action": "Recommandations personnalisées sur l'axe de destination",
        "canal":  "App Push + Email",
        "retention_48h": 0.05,
        "retention_30d": 0.14,
        "cost_per_client": 1.2,
    },
}

MARGIN = 0.35  # marge Sephora estimée

# ── Helpers ───────────────────────────────────────────────────────────────────

@st.cache_resource
def load_model_cached():
    try:
        from src.clustering import load_model
        return load_model()
    except Exception:
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
            df = pd.read_csv(path, parse_dates=["date"])
            assert df["date"].max() <= pd.Timestamp("2025-09-30"), \
                f"Données hors période attendue : {df['date'].max()}"
            return df
    except AssertionError as e:
        st.error(f"⚠️ {e}")
        return None
    except Exception:
        pass
    return None

@st.cache_data
def load_active_client_ids():
    try:
        path = os.path.join(DATA_PATH, "transactions_test.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, dtype={"anonymized_card_code": str},
                             usecols=["anonymized_card_code"])
            def _norm(x):
                try:
                    return "{:.0f}".format(float(str(x).strip()))
                except Exception:
                    return str(x).strip()
            return set(df["anonymized_card_code"].apply(_norm).unique())
    except Exception:
        pass
    return set()

def _norm_id(x):
    try:
        return "{:.0f}".format(float(str(x).strip()))
    except Exception:
        return str(x).strip()

def compute_business_kpis(feat_train, migrations=None, active_ids=None):
    """Calcule les KPIs financiers globaux."""
    kpis = {}
    kpis["n_clients"]   = len(feat_train)
    kpis["ca_total"]    = feat_train["monetary"].sum() if "monetary" in feat_train.columns else 0
    kpis["ca_moyen"]    = feat_train["monetary"].mean() if "monetary" in feat_train.columns else 0
    kpis["panier_moyen"]= feat_train["avg_basket"].mean() if "avg_basket" in feat_train.columns else 0

    # Dormants
    if active_ids:
        train_ids_norm = feat_train.index.map(_norm_id)
        dormant_mask   = ~train_ids_norm.isin(active_ids)
        kpis["n_dormants"]  = dormant_mask.sum()
        kpis["ca_at_risk"]  = feat_train.loc[dormant_mask, "monetary"].sum() if "monetary" in feat_train.columns else 0
    else:
        kpis["n_dormants"] = None
        kpis["ca_at_risk"] = None

    # Migrations
    if migrations is not None and len(migrations) > 0:
        kpis["n_migrations"]  = len(migrations)
        kpis["n_downgrades"]  = (migrations["direction"] == "downgrade").sum()
        kpis["n_upgrades"]    = (migrations["direction"] == "upgrade").sum()
        kpis["migration_rate"]= migrations["client_id"].nunique() / len(feat_train)
    else:
        kpis["n_migrations"]  = 0
        kpis["n_downgrades"]  = 0
        kpis["n_upgrades"]    = 0
        kpis["migration_rate"]= 0.0

    return kpis

def compute_crm_saving(migrations, feat_train, direction="downgrade"):
    """Estime le CA récupérable via intervention CRM pour une direction de migration."""
    if migrations is None or len(migrations) == 0:
        return 0.0, pd.DataFrame()
    crm = CRM_ACTIONS[direction]
    cluster_ca = feat_train.groupby("cluster")["monetary"].mean().to_dict() if "cluster" in feat_train.columns else {}
    mig = migrations[migrations["direction"] == direction].copy()
    if len(mig) == 0:
        return 0.0, mig
    mig["ca_origine"]  = mig["from_cluster"].map(cluster_ca).fillna(feat_train["monetary"].mean() if "monetary" in feat_train.columns else 0)
    mig["saving_30d"]  = mig["ca_origine"] * crm["retention_30d"] * MARGIN
    mig["saving_48h"]  = mig["ca_origine"] * crm["retention_48h"] * MARGIN
    mig["crm_cost"]    = crm["cost_per_client"]
    mig["roi"]         = mig["saving_30d"] / mig["crm_cost"]
    total = mig["saving_30d"].sum()
    return total, mig

def kpi_card_html(label, value, delta=""):
    return f"""
    <div class="kpi-gold">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {'<div class="kpi-delta">' + delta + '</div>' if delta else ''}
    </div>
    """

def alert_html(title, body, kind="red"):
    return f"""
    <div class="alert-{kind}">
        <div class="alert-title">{title}</div>
        <div class="alert-body">{body}</div>
    </div>
    """

def fmt_eur(v):
    if v >= 1_000_000:
        return f"{v/1_000_000:.2f}M €"
    if v >= 1_000:
        return f"{v/1_000:.1f}K €"
    return f"{v:.0f} €"

# ── Données ───────────────────────────────────────────────────────────────────
from src.utils import DATA_PATH, OUTPUTS_PATH, MODELS_PATH

# Auto-détection features corrigées (Chantier 1)
FEAT_CORRECTED_PATH = os.path.join(DATA_PATH, "customer_features_train_corrected.csv")
FEAT_TRAIN_PATH     = os.path.join(DATA_PATH, "customer_features_train.csv")

if os.path.exists(FEAT_CORRECTED_PATH):
    feat_train   = load_features(FEAT_CORRECTED_PATH)
    _feat_source = "corrigées (biais saisonnalité Q3 neutralisé)"
elif os.path.exists(FEAT_TRAIN_PATH):
    feat_train   = load_features(FEAT_TRAIN_PATH)
    _feat_source = "standard (sans correction saisonnalité)"
else:
    feat_train   = None
    _feat_source = "non chargées"

data_loaded  = feat_train is not None
model, scaler = load_model_cached()
persona_cards = load_personas()
migrations    = load_migrations()
active_ids    = load_active_client_ids() if data_loaded else set()
kpis = compute_business_kpis(feat_train, migrations, active_ids) if data_loaded else {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
     letter-spacing:0.14em;color:{GOLD};text-transform:uppercase;
     border-bottom:1px solid #333;padding-bottom:0.5rem;margin-bottom:0.8rem;">
  Sephora × Albert School<br/>Groupe 5 · BDD #7
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "",
    options=[
        "💰 Command Center",
        "📡 Migrations Live",
        "📈 Valeur Business",
        "🧩 Personas",
        "👤 Vue Client",
    ],
    index=0,
)

st.sidebar.divider()

# Indicateur source features
src_color = GREEN if "corrigées" in _feat_source else "#AAAAAA"
st.sidebar.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:{src_color};">
  ● Features : {_feat_source}
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
if st.sidebar.button("🔄 Rafraîchir", use_container_width=True):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

st.sidebar.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.6rem;
     color:#555;margin-top:1rem;line-height:1.7;">
  Jury : Youri ZAKHVATOV<br/>
  Dir. Data Analytics — Sephora<br/>
  Avril 2026
</div>
""", unsafe_allow_html=True)

if not data_loaded:
    st.markdown('<div class="page-header">DONNÉES NON GÉNÉRÉES</div>', unsafe_allow_html=True)
    st.info("Exécuter les notebooks 0 → 4 pour produire les fichiers dans `data/` et `outputs/`.")
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — COMMAND CENTER
# ═════════════════════════════════════════════════════════════════════════════
if page == "💰 Command Center":
    st.markdown('<div class="page-header">💰 Command Center — Vue Financière Globale</div>',
                unsafe_allow_html=True)

    if migrations is not None and migrations["date"].max() > pd.Timestamp("2025-09-30"):
        st.warning(
            f"⚠️ Données disponibles jusqu'au {migrations['date'].max().strftime('%d/%m/%Y')} uniquement — "
            "les périodes au-delà de septembre 2025 sont hors périmètre."
        )

    # ── 4 KPI cards ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card_html(
            "CA Total Base Train",
            fmt_eur(kpis["ca_total"]),
            f"{kpis['n_clients']:,} clients analysés"
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card_html(
            "CA Moyen / Client",
            fmt_eur(kpis["ca_moyen"]),
            f"Panier moy. : {kpis['panier_moyen']:.0f} €"
        ), unsafe_allow_html=True)
    with c3:
        dorm_label = f"{kpis['n_dormants']:,} clients inactifs" if kpis["n_dormants"] is not None else "—"
        st.markdown(kpi_card_html(
            "CA à Risque (Dormants)",
            fmt_eur(kpis["ca_at_risk"]) if kpis["ca_at_risk"] is not None else "—",
            dorm_label
        ), unsafe_allow_html=True)
    with c4:
        mig_pct = f"{kpis['migration_rate']*100:.1f}% de la base"
        st.markdown(kpi_card_html(
            "Migrations Détectées",
            f"{kpis['n_migrations']:,}",
            f"↓ {kpis['n_downgrades']} churn · ↑ {kpis['n_upgrades']} upgrade"
        ), unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    left, right = st.columns([3, 2])

    # ── Gauche : Alertes churn top-3 ─────────────────────────────────────────
    with left:
        st.markdown("#### Top Alertes Churn — Segments Prioritaires")

        if migrations is not None and len(migrations) > 0 and "cluster" in feat_train.columns:
            cluster_ca = feat_train.groupby("cluster")["monetary"].mean()
            mig_down   = migrations[migrations["direction"] == "downgrade"].copy()
            mig_down["ca_origine"] = mig_down["from_cluster"].map(cluster_ca).fillna(0)
            mig_down["saving"]     = mig_down["ca_origine"] * CRM_ACTIONS["downgrade"]["retention_30d"] * MARGIN

            top_clusters = (
                mig_down.groupby("from_cluster")
                .agg(n_clients=("client_id", "nunique"), ca_sauve=("saving", "sum"))
                .sort_values("ca_sauve", ascending=False)
                .head(3)
            )

            from src.personas import PERSONA_NAMES  # type: ignore
            for cl_id, row in top_clusters.iterrows():
                pname = PERSONA_NAMES.get(int(cl_id), f"Cluster {cl_id}")
                st.markdown(alert_html(
                    f"⚠ Cluster {cl_id} — {pname}",
                    f"{int(row['n_clients'])} clients en downgrade · "
                    f"CA récupérable : <strong>{fmt_eur(row['ca_sauve'])}</strong> / mois "
                    f"(rétention 30j @ {CRM_ACTIONS['downgrade']['retention_30d']*100:.0f}%)"
                ), unsafe_allow_html=True)
        else:
            st.markdown(alert_html(
                "⚠ Aucune donnée migration",
                "Exécuter notebook 3 pour détecter les migrations et activer les alertes.",
                "red"
            ), unsafe_allow_html=True)

        # Répartition CA par segment
        if "cluster" in feat_train.columns and "monetary" in feat_train.columns:
            st.markdown("#### Répartition CA par Segment")
            ca_seg = feat_train.groupby("cluster")["monetary"].sum().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(8, 3.2), facecolor="#0D0D0D")
            ax.set_facecolor("#0D0D0D")
            colors_bar = [GOLD if i == 0 else "#444" for i in range(len(ca_seg))]
            bars = ax.barh(range(len(ca_seg)), ca_seg.values / 1000,
                           color=colors_bar, edgecolor="none", height=0.6)
            ax.set_yticks(range(len(ca_seg)))
            ax.set_yticklabels([f"C{c}" for c in ca_seg.index],
                                fontfamily="monospace", color="#AAA", fontsize=9)
            ax.set_xlabel("CA (K€)", color="#AAA", fontsize=9)
            ax.tick_params(colors="#555", labelcolor="#AAA")
            ax.spines[:].set_color("#333")
            for bar, val in zip(bars, ca_seg.values):
                ax.text(val / 1000 + ca_seg.values.max() * 0.001 / 1000,
                        bar.get_y() + bar.get_height() / 2,
                        f"{val/1000:.0f}K", va="center", color="#DDD",
                        fontsize=8, fontfamily="monospace")
            ax.set_title("CA par cluster (K€)", color=GOLD, fontsize=10,
                         fontfamily="monospace", pad=10)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    # ── Droite : Système vs RFM statique Sephora ─────────────────────────────
    with right:
        st.markdown("#### Notre Système vs RFM Statique Sephora")
        st.markdown('<div class="versus-box"><h5>Comparaison méthodologique</h5>', unsafe_allow_html=True)

        comp_data = {
            "Critère":            ["Méthode",         "Nb segments",   "Données",         "Mise à jour",    "Action CRM",    "Saisonnalité"],
            "RFM Sephora":        ["Score statique",  "9 segments",    "3 vars",          "Mensuelle",      "Générique",     "❌ Ignorée"],
            "Notre Système":      ["MiniBatch KMeans","5-8 personas",  "25 features",     "Temps réel",     "Personnalisée", "✅ Corrigée"],
        }
        df_comp = pd.DataFrame(comp_data).set_index("Critère")

        def _style_row(row):
            styles = []
            for col in row.index:
                if col == "Notre Système":
                    styles.append(f"color: {GOLD}; font-weight: bold;")
                else:
                    styles.append("color: #888;")
            return styles

        st.dataframe(
            df_comp,
            use_container_width=True,
            height=260,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Delta KPIs vs RFM
        st.markdown("<br/>", unsafe_allow_html=True)
        if kpis.get("n_migrations", 0) > 0:
            st.markdown(alert_html(
                "✅ Avantage détection précoce",
                f"<strong>{kpis['n_downgrades']}</strong> churn détectés avant perte effective. "
                f"RFM statique : 0 alertes en temps réel.",
                "green"
            ), unsafe_allow_html=True)

        # SI visualization si features corrigées
        si_path = os.path.join(DATA_PATH, "seasonality_index.csv")
        if os.path.exists(si_path):
            st.markdown("#### Indice de Saisonnalité (Correction Q3)")
            si_df = pd.read_csv(si_path)
            if "month" in si_df.columns and "si" in si_df.columns:
                fig_si, ax_si = plt.subplots(figsize=(5, 2.8), facecolor="#0D0D0D")
                ax_si.set_facecolor("#0D0D0D")
                month_labels = ["Jan","Fév","Mar","Avr","Mai","Jun","Jul","Aoû","Sep","Oct","Nov","Déc"]
                bar_colors = [RED if si_df.loc[i,"si"] > 1.15 else ("#555" if si_df.loc[i,"si"] < 0.9 else GOLD)
                              for i in range(len(si_df))]
                ax_si.bar(si_df["month"], si_df["si"], color=bar_colors, edgecolor="none", width=0.7)
                ax_si.axhline(1.0, color=WHITE, lw=0.8, ls="--", alpha=0.4)
                ax_si.set_xticks(si_df["month"])
                ax_si.set_xticklabels(month_labels[:len(si_df)], fontsize=7, color="#AAA")
                ax_si.set_ylabel("SI", color="#AAA", fontsize=8)
                ax_si.tick_params(colors="#555", labelcolor="#AAA")
                ax_si.spines[:].set_color("#333")
                ax_si.set_title("SI(m) — Jul–Sep gonflés artificiellement", color=GOLD,
                                fontsize=8, fontfamily="monospace")
                plt.tight_layout()
                st.pyplot(fig_si)
                plt.close(fig_si)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MIGRATIONS LIVE
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📡 Migrations Live":
    st.markdown('<div class="page-header">📡 Migrations Live — Détection & Actions CRM</div>',
                unsafe_allow_html=True)

    if migrations is None or len(migrations) == 0:
        st.warning("Exécuter notebook 3 pour générer `outputs/data/migrations.csv`.")
        st.stop()

    # ── Slider temporel ───────────────────────────────────────────────────────
    min_d = migrations["date"].min().date()
    max_d = migrations["date"].max().date()

    selected_date = st.slider(
        "Avancer dans le temps",
        min_value=min_d, max_value=max_d, value=min_d,
        format="DD/MM/YYYY"
    )

    mig_slice = migrations[migrations["date"].dt.date <= selected_date].copy()

    # ── KPIs slice ────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    n_down_s = (mig_slice["direction"] == "downgrade").sum()
    n_up_s   = (mig_slice["direction"] == "upgrade").sum()
    n_lat_s  = (mig_slice["direction"] == "lateral").sum()

    total_saving, mig_down_detail = compute_crm_saving(mig_slice, feat_train, "downgrade")

    with c1:
        st.markdown(kpi_card_html("Migrations cumulées", f"{len(mig_slice):,}",
                                   f"jusqu'au {selected_date}"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card_html("↓ Downgrades", f"{n_down_s:,}",
                                   f"CA récupérable : {fmt_eur(total_saving)}"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card_html("↑ Upgrades", f"{n_up_s:,}",
                                   "Clients en ascension"), unsafe_allow_html=True)
    with c4:
        roi_moy = mig_down_detail["roi"].mean() if len(mig_down_detail) > 0 else 0
        st.markdown(kpi_card_html("ROI CRM Moyen", f"{roi_moy:.0f}x",
                                   f"sur interventions downgrade"), unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    left, right = st.columns([2, 3])

    # ── Gauche : Action CRM recommandée selon direction ───────────────────────
    with left:
        direction_select = st.selectbox(
            "Direction de migration",
            options=["downgrade", "upgrade", "lateral"],
            format_func=lambda x: {"downgrade": "↓ Downgrade (Churn Risk)",
                                    "upgrade":   "↑ Upgrade (Ascension)",
                                    "lateral":   "→ Lateral (Réengagement)"}[x]
        )
        crm = CRM_ACTIONS[direction_select]
        n_dir = (mig_slice["direction"] == direction_select).sum()
        total_s, detail_s = compute_crm_saving(mig_slice, feat_train, direction_select)
        cost_total = n_dir * crm["cost_per_client"]

        st.markdown(f"""
        <div class="versus-box" style="margin-top:0.5rem;">
        <h5>Action CRM — {crm['label']}</h5>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.78rem;line-height:1.9;">
          <span class="crm-pill">{crm['canal']}</span><br/><br/>
          <span style="color:#AAA;">Action :</span> {crm['action']}<br/><br/>
          <span style="color:#AAA;">Clients ciblés :</span>
          <strong style="color:{GOLD};">{n_dir:,}</strong><br/>
          <span style="color:#AAA;">Rétention 48h :</span>
          <strong style="color:{GREEN};">{crm['retention_48h']*100:.0f}%</strong><br/>
          <span style="color:#AAA;">Rétention 30j :</span>
          <strong style="color:{GREEN};">{crm['retention_30d']*100:.0f}%</strong><br/><br/>
          <span style="color:#AAA;">Coût campagne :</span>
          <strong style="color:{RED};">{fmt_eur(cost_total)}</strong><br/>
          <span style="color:#AAA;">CA récupéré 30j :</span>
          <strong style="color:{GOLD};">{fmt_eur(total_s)}</strong><br/>
          <span style="color:#AAA;">ROI net :</span>
          <strong style="color:{GOLD};">
            {(total_s - cost_total) / cost_total * 100:.0f}% ({fmt_eur(total_s - cost_total)})
          </strong>
        </div>
        </div>
        """, unsafe_allow_html=True)

        # Saving 48h vs 30j comparison
        if len(detail_s) > 0:
            st.markdown("<br/>", unsafe_allow_html=True)
            s48 = detail_s["saving_48h"].sum()
            s30 = detail_s["saving_30d"].sum()
            fig_sv, ax_sv = plt.subplots(figsize=(4.5, 2.5), facecolor="#0D0D0D")
            ax_sv.set_facecolor("#0D0D0D")
            bars_sv = ax_sv.bar(["48h", "30 jours"], [s48, s30],
                                 color=[GOLD + "99", GOLD], edgecolor="none", width=0.5)
            for bar, val in zip(bars_sv, [s48, s30]):
                ax_sv.text(bar.get_x() + bar.get_width()/2, val + s30 * 0.02,
                           fmt_eur(val), ha="center", color=WHITE,
                           fontsize=8, fontfamily="monospace")
            ax_sv.set_ylabel("CA récupéré (€)", color="#AAA", fontsize=8)
            ax_sv.tick_params(colors="#555", labelcolor="#AAA")
            ax_sv.spines[:].set_color("#333")
            ax_sv.set_title("Impact intervention CRM", color=GOLD,
                            fontsize=9, fontfamily="monospace")
            plt.tight_layout()
            st.pyplot(fig_sv)
            plt.close(fig_sv)

    # ── Droite : Timeline + distribution ─────────────────────────────────────
    with right:
        # Timeline cumulative par direction
        fig_t, ax_t = plt.subplots(figsize=(8, 3.8), facecolor="#0D0D0D")
        ax_t.set_facecolor("#0D0D0D")
        dir_colors = {"downgrade": RED, "upgrade": GREEN, "lateral": GOLD}
        for direction, color in dir_colors.items():
            sub = mig_slice[mig_slice["direction"] == direction]
            if len(sub) > 0:
                cumul = sub.set_index("date").resample("D").size().cumsum()
                ax_t.plot(cumul.index, cumul.values, color=color, lw=2,
                          label=f"{direction.capitalize()} ({len(sub):,})")
                ax_t.fill_between(cumul.index, cumul.values, alpha=0.08, color=color)
        ax_t.set_title("Migrations cumulées par direction", color=GOLD,
                        fontsize=10, fontfamily="monospace")
        ax_t.set_xlabel("Date", color="#AAA", fontsize=8)
        ax_t.set_ylabel("Nb cumulé", color="#AAA", fontsize=8)
        ax_t.tick_params(colors="#555", labelcolor="#AAA")
        ax_t.spines[:].set_color("#333")
        ax_t.legend(facecolor="#1A1A1A", labelcolor="white", fontsize=8,
                    edgecolor="#333")
        plt.xticks(rotation=25, fontsize=7)
        plt.tight_layout()
        st.pyplot(fig_t)
        plt.close(fig_t)

        # Top 10 clients à risque (downgrade, CA le plus élevé)
        if len(mig_down_detail) > 0 and "monetary" in feat_train.columns:
            st.markdown("**Top 10 clients downgrade — CA origine**")
            top10 = mig_down_detail.nlargest(10, "ca_origine")[
                ["client_id", "from_cluster", "to_cluster", "ca_origine", "saving_30d", "roi"]
            ].copy()
            top10["ca_origine"] = top10["ca_origine"].round(0).astype(int)
            top10["saving_30d"] = top10["saving_30d"].round(0).astype(int)
            top10["roi"]        = top10["roi"].round(1)
            top10.columns = ["Client", "De", "Vers", "CA (€)", "Récupérable (€)", "ROI"]
            st.dataframe(top10, use_container_width=True, hide_index=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3 — VALEUR BUSINESS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "📈 Valeur Business":
    st.markdown('<div class="page-header">📈 Valeur Business — CLV & Opportunités ROI</div>',
                unsafe_allow_html=True)

    if feat_train is None or "cluster" not in feat_train.columns:
        st.warning("Exécuter notebooks 0 → 2.")
        st.stop()

    try:
        from src.utils import compute_clv  # type: ignore
    except ImportError:
        def compute_clv(avg_basket, frequency, tenure_days):
            return avg_basket * frequency * MARGIN * min(tenure_days / 365, 3)

    try:
        from src.personas import PERSONA_NAMES  # type: ignore
    except ImportError:
        PERSONA_NAMES = {}

    # CLV computation
    feat_train["clv"] = feat_train.apply(
        lambda r: compute_clv(
            r.get("avg_basket", 0), r.get("frequency", 0), r.get("tenure_days", 365)
        ), axis=1
    )

    clv_df = feat_train.groupby("cluster").agg(
        clv_mean      = ("clv",      "mean"),
        clv_total     = ("clv",      "sum"),
        n_clients     = ("clv",      "count"),
        ca_mean       = ("monetary", "mean"),
        ca_total      = ("monetary", "sum"),
        freq_mean     = ("frequency","mean"),
    ).round(0)
    clv_df["nom"] = [PERSONA_NAMES.get(int(c), f"Cluster {c}") for c in clv_df.index]

    # ── KPIs CLV ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card_html("CLV Totale Estimée",
                                   fmt_eur(clv_df["clv_total"].sum()),
                                   "sur horizon 3 ans, marge 35%"), unsafe_allow_html=True)
    with c2:
        best_seg = clv_df["clv_mean"].idxmax()
        st.markdown(kpi_card_html("Meilleur Segment CLV",
                                   f"C{best_seg}",
                                   f"{fmt_eur(clv_df.loc[best_seg,'clv_mean'])} / client"), unsafe_allow_html=True)
    with c3:
        active_ids = load_active_client_ids()
        if active_ids:
            train_ids_norm = feat_train.index.map(_norm_id)
            dormant_mask = ~train_ids_norm.isin(active_ids)
            ca_risk = feat_train.loc[dormant_mask, "monetary"].sum()
            st.markdown(kpi_card_html("Revenue at Risk",
                                       fmt_eur(ca_risk),
                                       f"{dormant_mask.sum():,} clients dormants"), unsafe_allow_html=True)
        else:
            st.markdown(kpi_card_html("Revenue at Risk", "—", "Données test absentes"),
                        unsafe_allow_html=True)
    with c4:
        clv_vs_ca_ratio = clv_df["clv_total"].sum() / clv_df["ca_total"].sum()
        st.markdown(kpi_card_html("Multiplicateur CLV/CA",
                                   f"{clv_vs_ca_ratio:.2f}x",
                                   "potentiel valeur projetée"), unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    left, right = st.columns([3, 2])

    # ── Scatter : Revenue récupérable × CLV potentiel ─────────────────────────
    with left:
        st.markdown("#### Scatter — CLV Potentiel × CA Moyen par Segment")
        fig_sc, ax_sc = plt.subplots(figsize=(8, 5), facecolor="#0D0D0D")
        ax_sc.set_facecolor("#0D0D0D")
        sizes = (clv_df["n_clients"] / clv_df["n_clients"].max() * 1200).clip(80)
        scatter = ax_sc.scatter(
            clv_df["ca_mean"], clv_df["clv_mean"],
            s=sizes, c=clv_df.index,
            cmap="YlOrBr", alpha=0.85, edgecolors=GOLD, linewidths=0.8,
            zorder=3
        )
        for idx, row in clv_df.iterrows():
            ax_sc.annotate(
                f"C{idx}\n{row['nom'][:12]}",
                (row["ca_mean"], row["clv_mean"]),
                xytext=(8, 4), textcoords="offset points",
                fontsize=7, color=WHITE, fontfamily="monospace",
                zorder=4
            )
        ax_sc.axhline(clv_df["clv_mean"].mean(), color=GOLD, lw=0.8, ls="--", alpha=0.5)
        ax_sc.axvline(clv_df["ca_mean"].mean(),  color=GOLD, lw=0.8, ls="--", alpha=0.5)
        ax_sc.text(clv_df["ca_mean"].min(), clv_df["clv_mean"].mean() * 1.02,
                   "moy. CLV", color=GOLD, fontsize=7, fontfamily="monospace")
        ax_sc.set_xlabel("CA Moyen / Client (€)", color="#AAA", fontsize=9)
        ax_sc.set_ylabel("CLV Moyenne Estimée (€)", color="#AAA", fontsize=9)
        ax_sc.tick_params(colors="#555", labelcolor="#AAA")
        ax_sc.spines[:].set_color("#333")
        ax_sc.set_title("Taille bulles ∝ nombre de clients", color="#888",
                         fontsize=8, fontfamily="monospace")
        ax_sc.grid(True, color="#222", lw=0.5, alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig_sc)
        plt.close(fig_sc)

    # ── Droite : Top-10 ROI table + vs RFM ───────────────────────────────────
    with right:
        st.markdown("#### Opportunités ROI — Classement Segments")
        roi_table = clv_df[["nom","n_clients","ca_mean","clv_mean","clv_total"]].copy()
        roi_table["roi_clv"] = (roi_table["clv_mean"] / roi_table["ca_mean"]).round(2)
        roi_table = roi_table.sort_values("clv_total", ascending=False)
        roi_table.columns = ["Persona","N Clients","CA Moy €","CLV Moy €","CLV Tot €","ROI CLV"]
        roi_table["CA Moy €"]  = roi_table["CA Moy €"].astype(int)
        roi_table["CLV Moy €"] = roi_table["CLV Moy €"].astype(int)
        roi_table["CLV Tot €"] = roi_table["CLV Tot €"].astype(int)
        roi_table["N Clients"] = roi_table["N Clients"].astype(int)
        st.dataframe(roi_table, use_container_width=True, hide_index=False)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Vs RFM comparison
        st.markdown('<div class="versus-box"><h5>Notre CLV vs Approche RFM Sephora</h5>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.76rem;line-height:2;">
          <span style="color:#888;">RFM Sephora :</span> score statique 1-9<br/>
          &nbsp;&nbsp;→ 0 projection CLV<br/>
          &nbsp;&nbsp;→ 0 modélisation valeur future<br/><br/>
          <span style="color:{GOLD};">Notre modèle :</span> CLV 3 ans estimée<br/>
          &nbsp;&nbsp;→ <strong style="color:{GOLD};">{fmt_eur(clv_df['clv_total'].sum())}</strong> de valeur identifiée<br/>
          &nbsp;&nbsp;→ Priorisation capital client<br/>
          &nbsp;&nbsp;→ Budget CRM alloué par ROI
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PERSONAS
# ═════════════════════════════════════════════════════════════════════════════
elif page == "🧩 Personas":
    st.markdown('<div class="page-header">🧩 Personas — Profils des Clusters</div>',
                unsafe_allow_html=True)

    if feat_train is None or "cluster" not in feat_train.columns:
        st.warning("Exécuter notebooks 0 → 2 pour générer les clusters.")
        st.stop()

    try:
        from src.personas import profile_cluster, PERSONA_NAMES  # type: ignore
        profile = profile_cluster(feat_train)
    except ImportError:
        PERSONA_NAMES = {}
        profile = feat_train.groupby("cluster").agg(
            n_clients    = ("monetary", "count"),
            monetary     = ("monetary", "mean"),
            avg_basket   = ("avg_basket", "mean"),
            frequency    = ("frequency", "mean"),
            recency_days = ("recency_days", "mean"),
            discount_ratio = ("discount_ratio", "mean"),
        ) if all(c in feat_train.columns for c in ["monetary","avg_basket","frequency"]) else pd.DataFrame()
        if len(profile) > 0:
            profile["pct_clients"] = profile["n_clients"] / profile["n_clients"].sum() * 100

    cluster_options = sorted(feat_train["cluster"].unique())
    selected_cl = st.selectbox(
        "Sélectionner un cluster :",
        options=cluster_options,
        format_func=lambda c: f"Cluster {c} — {PERSONA_NAMES.get(int(c), '?')}"
    )

    row  = profile.loc[selected_cl] if selected_cl in profile.index else None
    name = PERSONA_NAMES.get(int(selected_cl), f"Cluster {selected_cl}")

    if row is not None:
        global_mean = profile.select_dtypes(include=[np.number]).mean()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"### {name}")
            n_cl  = int(row.get("n_clients", 0))
            pct   = float(row.get("pct_clients", 0))
            st.metric("Taille", f"{n_cl:,} clients", f"{pct:.1f}% de la base")
        with c2:
            def _delta(key):
                if key in row and key in global_mean:
                    d = (row[key] - global_mean[key]) / (abs(global_mean[key]) + 1e-9) * 100
                    return f"{d:+.1f}% vs moy."
                return ""
            st.metric("CA moyen",    f"{row.get('monetary',0):.0f} €",    _delta("monetary"))
            st.metric("Panier moyen",f"{row.get('avg_basket',0):.0f} €",  _delta("avg_basket"))
            st.metric("Fréquence",   f"{row.get('frequency',0):.1f} tickets", _delta("frequency"))
        with c3:
            st.metric("Recency",       f"{row.get('recency_days',0):.0f} jours")
            if "discount_ratio" in row:
                d_ratio = row["discount_ratio"]
                d_global = global_mean.get("discount_ratio", 0)
                st.metric("Discount rate", f"{d_ratio*100:.1f}%",
                          f"{(d_ratio-d_global)*100:+.1f} pp vs moy.")
            if "icb_score" in row:
                st.metric("ICB Score", f"{row['icb_score']:.0f}/100")

    # Radar chart
    radar_path = os.path.join(OUTPUTS_PATH, "figures", f"3_radar_persona_{selected_cl}.png")
    if os.path.exists(radar_path):
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            st.image(radar_path, caption=f"Radar — {name}", use_container_width=True)
        with col_r2:
            st.subheader("Recommandations Marketing")
            if persona_cards:
                card = next((c for c in persona_cards if c["cluster_id"] == int(selected_cl)), None)
                if card:
                    for rec in card["recommendations"]:
                        st.markdown(f"→ {rec}")
    else:
        st.info("Radar charts non générés — exécuter notebook 3.")

    # Tableau comparatif
    st.markdown("#### Comparaison tous clusters vs moyenne globale")
    kpi_cols_disp = [c for c in ["n_clients","pct_clients","monetary","avg_basket",
                                  "frequency","recency_days","discount_ratio"] if c in profile.columns]
    st.dataframe(profile[kpi_cols_disp].round(2), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 5 — VUE CLIENT
# ═════════════════════════════════════════════════════════════════════════════
elif page == "👤 Vue Client":
    st.markdown('<div class="page-header">👤 Vue Client Individuel</div>',
                unsafe_allow_html=True)

    if feat_train is None:
        st.warning("Exécuter notebooks 0 → 2.")
        st.stop()

    try:
        from src.personas import PERSONA_NAMES  # type: ignore
    except ImportError:
        PERSONA_NAMES = {}

    col_in, col_btn = st.columns([4, 1])
    with col_in:
        client_id_input = st.text_input(
            "Identifiant client (anonymized_card_code) :",
            placeholder="Ex: 1234567890",
            key="client_search"
        )
    with col_btn:
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("🎲 Aléatoire", use_container_width=True):
            st.session_state["client_id"] = str(np.random.choice(feat_train.index))
            st.rerun()

    if "client_id" in st.session_state and not client_id_input:
        client_id_input = st.session_state["client_id"]

    if client_id_input:
        client_id = str(client_id_input).strip()
        feat_idx_str = feat_train.index.astype(str)

        if client_id not in feat_idx_str:
            st.error(f"Client '{client_id}' non trouvé dans le feature store.")
        else:
            client_row  = feat_train.loc[feat_train.index.astype(str) == client_id].iloc[0]
            cluster_id  = int(client_row.get("cluster", -1))
            persona_name = PERSONA_NAMES.get(cluster_id, f"Cluster {cluster_id}")

            # Determine churn risk
            recency = client_row.get("recency_days", 0)
            disc    = client_row.get("discount_ratio", 0)
            churn_risk = recency > 90 or disc > 0.25

            st.markdown(f"""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;
                 color:{RED if churn_risk else GREEN};letter-spacing:0.12em;
                 margin-bottom:0.8rem;">
              {'⚠ CHURN RISK DÉTECTÉ' if churn_risk else '✅ CLIENT ACTIF — PROFIL STABLE'}
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Segment",   f"Cluster {cluster_id}")
                st.metric("Persona",   persona_name)
            with c2:
                st.metric("CA total",       f"{client_row.get('monetary', 0):.0f} €")
                st.metric("Panier moyen",   f"{client_row.get('avg_basket', 0):.0f} €")
            with c3:
                st.metric("Fréquence",  f"{client_row.get('frequency', 0):.0f} tickets")
                st.metric("Recency",    f"{recency:.0f} jours")

            # Profil détaillé
            with st.expander("Profil Détaillé", expanded=False):
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

            # Historique migrations
            if migrations is not None and len(migrations) > 0:
                client_mig = migrations[migrations["client_id"] == client_id]
                if len(client_mig) > 0:
                    st.markdown(f"**Historique migrations — {len(client_mig)} événement(s)**")
                    st.dataframe(
                        client_mig[["date","from_cluster","to_cluster","direction"]],
                        use_container_width=True, hide_index=True
                    )
                    # Alerte si dernier mouvement est downgrade
                    last_dir = client_mig.sort_values("date").iloc[-1]["direction"]
                    if last_dir == "downgrade":
                        st.markdown(alert_html(
                            "⚠ Dernier mouvement : Downgrade",
                            f"Action recommandée : {CRM_ACTIONS['downgrade']['action']}"
                        ), unsafe_allow_html=True)
                    elif last_dir == "upgrade":
                        st.markdown(alert_html(
                            "✅ Dernier mouvement : Upgrade",
                            f"Action recommandée : {CRM_ACTIONS['upgrade']['action']}",
                            "green"
                        ), unsafe_allow_html=True)
                else:
                    st.info("Ce client n'a pas migré de segment pendant la période Juil–Sep.")

            # Recommandation marketing
            st.markdown("**Action Marketing Recommandée**")
            if churn_risk:
                st.markdown(alert_html(
                    f"⚠ Intervention CRM — {CRM_ACTIONS['downgrade']['label']}",
                    f"{CRM_ACTIONS['downgrade']['action']}<br/>"
                    f"Canal : {CRM_ACTIONS['downgrade']['canal']} · "
                    f"Rétention 30j : {CRM_ACTIONS['downgrade']['retention_30d']*100:.0f}%"
                ), unsafe_allow_html=True)
            elif persona_cards:
                card = next((c for c in persona_cards if c["cluster_id"] == cluster_id), None)
                if card:
                    for rec in card["recommendations"]:
                        st.markdown(f"→ {rec}")
                else:
                    st.markdown(f"→ Activer le segment {cluster_id} selon les recommandations cluster.")
            else:
                st.markdown(f"→ Segment {cluster_id} — {persona_name} : appliquer la stratégie CRM du cluster.")
