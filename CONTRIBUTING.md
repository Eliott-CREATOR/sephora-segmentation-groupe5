# Guide de contribution — Groupe 5

Ce document explique comment rejoindre le projet, configurer son environnement et contribuer proprement.

---

## 1. Cloner le repo

```bash
git clone https://github.com/<votre-org>/sephora-segmentation-groupe5.git
cd sephora-segmentation-groupe5
```

---

## 2. Placer le dataset

Le fichier CSV Sephora **n'est pas dans le repo** (données sensibles + 90 Mo).

1. Récupérer le fichier `BDD#7_Database_Albert_School_Sephora.csv` auprès de l'équipe
2. Le placer dans le dossier `data/` :

```
data/
└── BDD#7_Database_Albert_School_Sephora.csv   ← ici
```

> ⚠️ Ne jamais faire `git add data/*.csv`. Le `.gitignore` le protège, mais restez vigilants.

---

## 3. Installer les dépendances

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

# Installer
pip install -r requirements.txt
```

---

## 4. Lancer les notebooks dans l'ordre

Les notebooks sont **séquentiels** — chacun produit des fichiers utilisés par le suivant.

```bash
jupyter notebook
```

| Ordre | Fichier | Produit |
|-------|---------|---------|
| 0 | `0_cleaning_features.ipynb` | `data/customer_features.csv` |
| 1 | `1_eda.ipynb` | figures dans `outputs/figures/` |
| 2 | `2_clustering.ipynb` | `models/kmeans_model.pkl` + `models/scaler.pkl` |
| 3 | `3_personas_migration.ipynb` | `outputs/data/migrations.csv` |
| 4 | `4_business_value.ipynb` | tableaux et figures de valeur business |

> Si un notebook plante, vérifier que le notebook précédent a bien été exécuté en entier.

---

## 5. Convention de commits

Utiliser le préfixe approprié pour chaque commit :

| Préfixe | Usage | Exemple |
|---------|-------|---------|
| `feat:` | Nouvelle fonctionnalité ou notebook | `feat: ajout feature brand_entropy` |
| `fix:` | Correction d'un bug ou d'une erreur | `fix: correction typo MAEK UP` |
| `data:` | Modification liée aux données (pas le CSV) | `data: ajout README data/` |
| `notebook:` | Avancement dans un notebook | `notebook: EDA sections 1 et 2 complètes` |
| `refactor:` | Nettoyage de code sans changer le comportement | `refactor: extraction fonction dans utils.py` |
| `docs:` | Documentation uniquement | `docs: mise à jour README` |

### Exemple de workflow

```bash
git checkout -b feat/feature-engineering
# ... travailler ...
git add src/feature_engineering.py notebooks/0_cleaning_features.ipynb
git commit -m "feat: feature engineering complet — 25 features par client"
git push origin feat/feature-engineering
# Ouvrir une Pull Request sur GitHub
```

---

## 6. Règles importantes

- **Ne jamais committer le CSV** — le `.gitignore` est là pour ça, mais restez vigilants
- **Ne jamais committer les `.pkl`** — les modèles se régénèrent via le notebook 2
- **Seed = 42** partout pour la reproductibilité
- **Un notebook = une phase** — ne pas mélanger le feature engineering et le clustering dans le même notebook
