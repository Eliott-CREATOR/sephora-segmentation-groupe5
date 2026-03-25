# models/

Ce dossier accueille les modèles ML entraînés. **Les fichiers `.pkl` ne sont pas commités dans le repo.**

## Pourquoi les modèles ne sont pas dans le repo ?

Les fichiers `.pkl` sont **régénérables** en ré-exécutant le notebook `2_clustering.ipynb` sur le dataset. Les committer n'apporterait aucune valeur et alourdirait le repo.

## Fichiers générés par le notebook 2

| Fichier | Contenu | Utilisé par |
|---------|---------|-------------|
| `kmeans_model.pkl` | Modèle MiniBatchKMeans entraîné sur Jan–Juin | Notebook 3, Dashboard |
| `scaler.pkl` | StandardScaler ajusté sur Jan–Juin | Notebook 3, Dashboard |

## ⚠️ Important : toujours sauvegarder le scaler avec le modèle

Le `scaler.pkl` doit impérativement être entraîné sur les **mêmes données** que le modèle (période Jan–Juin). Il sera utilisé pour normaliser les nouvelles transactions lors de la simulation Juil–Sep. Ne jamais ré-ajuster le scaler sur des données différentes.

## Régénérer les modèles

```bash
jupyter notebook notebooks/2_clustering.ipynb
# Exécuter toutes les cellules — les .pkl seront sauvegardés automatiquement dans models/
```
