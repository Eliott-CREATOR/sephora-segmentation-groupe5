# Sephora × Albert School — BDD #7 | Groupe 5 | Case 2 ML Segmentation

> **Segmentation Dynamique des Clients & Détection de Migrations**
> Business Deep Dive #7 — Albert School × Sephora
> Jury : Youri ZAKHVATOV, Directeur Data Analytics & Reports, Sephora

---

## Contexte

Ce projet répond au **Case 2** du BDD #7 organisé par Albert School en partenariat avec Sephora.

L'objectif est de construire une **segmentation dynamique des clients Sephora** par Machine Learning, capable de détecter en quasi-temps réel les migrations de comportement — et de déclencher automatiquement les actions marketing adaptées.

Contrairement à une segmentation RFM statique recalculée mensuellement, notre système met à jour le segment d'un client dès qu'il effectue un nouvel achat, en comparant son profil mis à jour aux centroïdes existants du clustering.

---

## Dataset

| Indicateur | Valeur |
|---|---|
| Lignes totales | 399 997 transactions |
| Clients uniques | 64 469 |
| Tickets uniques | 184 282 |
| Période | Janvier – Septembre 2025 |
| CA total | ~12,7M EUR |
| Taux de remise moyen | ~13% |
| Pays principal | France (98,6%) |

> ⚠️ **Le fichier CSV n'est pas commité dans ce repo** (données sensibles Sephora + taille 90 Mo).
> Voir `data/README.md` pour les instructions de placement.

---

## Pipeline

Le projet est structuré en **6 étapes séquentielles**, chacune correspondant à un notebook :

```
0. Nettoyage & Feature Engineering
   └── 400K lignes → 64K profils clients × 25 features

1. Analyse Exploratoire (EDA)
   └── Distributions, corrélations, top marques, comparaisons store/estore

2. Clustering & Validation
   └── MiniBatchKMeans, Silhouette Score, Elbow Method, profiling des clusters

3. Personas & Simulation des Migrations
   └── Fiches personas, split temporel Jan-Juin/Juil-Sep, matrice de migration, Sankey

4. Valeur Business
   └── CLV par segment, revenue at risk, recommandations actionnables avec ROI estimé
```

---

## Installation

```bash
# Cloner le repo
git clone https://github.com/<votre-org>/sephora-segmentation-groupe5.git
cd sephora-segmentation-groupe5

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# Installer les dépendances
pip install -r requirements.txt
```

---

## Lancement

### Notebooks (dans l'ordre)

```bash
jupyter notebook
# Ouvrir et exécuter dans l'ordre :
# notebooks/0_cleaning_features.ipynb
# notebooks/1_eda.ipynb
# notebooks/2_clustering.ipynb
# notebooks/3_personas_migration.ipynb
# notebooks/4_business_value.ipynb
```

### Dashboard Streamlit

```bash
streamlit run app/dashboard.py
```

---

## Structure du repo

```
sephora-segmentation-groupe5/
├── README.md
├── requirements.txt
├── .gitignore
├── CONTRIBUTING.md
├── data/               ← placer le CSV ici (non commité)
├── notebooks/          ← pipeline analytique en 5 notebooks
├── src/                ← modules Python réutilisables
│   ├── feature_engineering.py
│   ├── clustering.py
│   ├── migration_detector.py
│   ├── personas.py
│   └── utils.py
├── models/             ← modèles .pkl générés (non commités)
├── outputs/            ← figures et exports CSV (régénérables)
└── app/
    └── dashboard.py    ← interface Streamlit
```

---

## Équipe

**Groupe 5 — Case 2 | BDD #7 Sephora × Albert School**
