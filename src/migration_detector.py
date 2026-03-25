"""
migration_detector.py
─────────────────────────────────────────────────────────────────────────────
Rôle : simuler la mise à jour dynamique des clusters clients.
Pour chaque transaction de la période Juil–Sep 2025, mettre à jour le
profil du client dans le feature store, réassigner son cluster via le
modèle existant, et détecter si une migration de segment a eu lieu.

Fonctions prévues :
    - build_feature_store()      : initialise le dict {client_id: profil}
                                    à partir de customer_features_train.csv
    - update_client_features()   : recalcule incrémentalement les features
                                    d'un client après un nouvel achat
    - reassign_cluster()         : normalise le profil mis à jour avec le
                                    scaler existant et prédit le nouveau cluster
    - detect_migration()         : compare ancien et nouveau cluster,
                                    retourne un dict Migration si changement
    - replay_transactions()      : rejoue toutes les transactions Juil–Sep
                                    dans l'ordre chronologique, accumule les
                                    migrations détectées
    - build_migration_matrix()   : construit la matrice de transition
                                    NxN (ancien_cluster → nouveau_cluster)
    - save_migrations()          : export outputs/data/migrations.csv

Appelé par : notebooks/3_personas_migration.ipynb
Produit    : outputs/data/migrations.csv
             outputs/figures/3_sankey_migrations.png
─────────────────────────────────────────────────────────────────────────────
"""

# TODO : implémenter
