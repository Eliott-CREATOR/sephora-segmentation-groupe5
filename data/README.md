# data/

Ce dossier accueille le dataset Sephora. **Le fichier CSV n'est pas commité dans le repo.**

## Pourquoi le CSV n'est pas dans le repo ?

1. **Données sensibles** : le dataset contient des transactions réelles de clients Sephora, anonymisées mais confidentielles dans le cadre du BDD #7.
2. **Taille** : le fichier fait ~90 Mo, ce qui dépasse les recommandations GitHub (50 Mo) et alourdirait inutilement le repo.

## Comment obtenir le dataset ?

Demander le fichier `BDD#7_Database_Albert_School_Sephora.csv` à un membre du groupe qui l'a reçu via Albert School.

## Où le placer ?

```
data/
└── BDD#7_Database_Albert_School_Sephora.csv   ← ici, exactement ce nom
```

## Fichiers générés (aussi ignorés par git)

Le notebook `0_cleaning_features.ipynb` génère dans ce dossier :

| Fichier | Produit par | Contenu |
|---------|-------------|---------|
| `customer_features.csv` | Notebook 0 | 64 469 clients × 25 features |
| `customer_features_train.csv` | Notebook 0 | Période Jan–Juin (entraînement) |
| `customer_features_test.csv` | Notebook 0 | Période Juil–Sep (simulation) |

Ces fichiers sont régénérables à tout moment en ré-exécutant le notebook 0.
