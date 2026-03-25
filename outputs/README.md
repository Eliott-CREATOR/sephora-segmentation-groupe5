# outputs/

Ce dossier contient les exports du projet. **Les fichiers générés ne sont pas commités dans le repo** — ils sont régénérables en ré-exécutant les notebooks.

## Structure

```
outputs/
├── figures/    ← graphiques exportés en PNG (EDA, clusters, radar charts, Sankey...)
└── data/       ← tableaux exportés en CSV (migrations, KPIs par persona, CLV...)
```

## Fichiers générés par notebook

| Notebook | Fichiers produits |
|----------|-------------------|
| `1_eda.ipynb` | `figures/distribution_rfm.png`, `figures/top_brands.png`, `figures/channel_comparison.png`... |
| `2_clustering.ipynb` | `figures/elbow_curve.png`, `figures/silhouette_scores.png`, `figures/umap_clusters.png` |
| `3_personas_migration.ipynb` | `figures/radar_persona_*.png`, `figures/sankey_migration.png`, `data/migrations.csv` |
| `4_business_value.ipynb` | `figures/clv_by_segment.png`, `data/business_kpis.csv`, `data/revenue_at_risk.csv` |

## Convention de nommage des figures

```
figures/<notebook>_<description>.<ext>
# Exemples :
figures/2_umap_clusters_k6.png
figures/3_radar_beauty_addict.png
figures/3_sankey_migrations_juil_sep.png
```

## Régénérer tous les outputs

```bash
jupyter nbconvert --to notebook --execute notebooks/1_eda.ipynb
jupyter nbconvert --to notebook --execute notebooks/2_clustering.ipynb
jupyter nbconvert --to notebook --execute notebooks/3_personas_migration.ipynb
jupyter nbconvert --to notebook --execute notebooks/4_business_value.ipynb
```
