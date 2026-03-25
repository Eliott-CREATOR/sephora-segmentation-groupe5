"""
clustering.py
─────────────────────────────────────────────────────────────────────────────
Rôle : entraîner, valider et sauvegarder le modèle de clustering
MiniBatchKMeans sur les profils clients agrégés.

Fonctions prévues :
    - preprocess()            : StandardScaler + gestion des NaN
    - find_optimal_k()        : itération K=4→11, calcul Silhouette Score,
                                 Calinski-Harabasz Index et Inertia (elbow)
    - train_model()           : entraînement MiniBatchKMeans avec le K optimal
                                 (random_state=42, n_init=10)
    - validate_model()        : rapport complet de validation (métriques +
                                 visualisation UMAP 2D des clusters)
    - save_model()            : sauvegarde models/kmeans_model.pkl +
                                 models/scaler.pkl via joblib
    - load_model()            : chargement du modèle et du scaler sauvegardés
    - assign_cluster()        : prédiction du cluster pour un vecteur de
                                 features normalisé (utilisé par migration_detector)

Appelé par : notebooks/2_clustering.ipynb
Produit    : models/kmeans_model.pkl
             models/scaler.pkl
             outputs/figures/2_elbow_curve.png
             outputs/figures/2_silhouette_scores.png
             outputs/figures/2_umap_clusters.png
─────────────────────────────────────────────────────────────────────────────
"""

# TODO : implémenter
