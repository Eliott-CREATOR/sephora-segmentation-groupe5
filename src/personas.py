"""
personas.py
─────────────────────────────────────────────────────────────────────────────
Rôle : profiler chaque cluster issu du clustering et générer les fiches
personas utilisables par les équipes marketing Sephora.

Fonctions prévues :
    - profile_cluster()          : calcule les KPIs moyens de chaque cluster
                                    (CA moyen, panier, fréquence, recency,
                                     discount rate, top marques, top axes...)
    - compute_delta_vs_global()  : calcule le delta de chaque KPI par rapport
                                    à la moyenne globale du dataset (obligatoire
                                    selon le brief Sephora)
    - generate_persona_card()    : retourne un dict structuré par persona avec
                                    nom, taille, KPIs, top marques, profil démo
    - plot_radar_chart()         : génère un radar chart à 8 axes par persona
                                    (Budget, Fidélité, Diversité, Premium,
                                     Digital, Promo, Skincare, Fragrance)
    - compute_beauty_curiosity_index()  : calcule le score ICB (Indice de
                                          Curiosité Beauté) 0–100 par client
    - compare_with_sephora_rfm() : compare nos segments avec les RFM_Segment_ID
                                    fournis par Sephora (colonne du dataset)

Appelé par : notebooks/3_personas_migration.ipynb
Produit    : outputs/figures/3_radar_persona_*.png
             outputs/data/personas_profiles.csv
─────────────────────────────────────────────────────────────────────────────
"""

# TODO : implémenter
