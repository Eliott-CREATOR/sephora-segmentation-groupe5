"""
feature_engineering.py
─────────────────────────────────────────────────────────────────────────────
Rôle : transformer les 400K lignes de transactions brutes en un dataframe
de 64K clients, chacun décrit par ~25 features comportementales et
démographiques agrégées.

Fonctions prévues :
    - load_raw_data()         : chargement et nettoyage du CSV brut
    - fix_data_quality()      : correction des anomalies (typo MAEK UP,
                                 types, valeurs manquantes...)
    - compute_rfm()           : calcul recency, frequency, monetary
    - compute_behavioral()    : entropie marques, diversité axes, régularité
    - compute_channel()       : part estore, flag omnicanal
    - compute_market()        : parts EXCLUSIVE / SELECTIVE / SEPHORA
    - compute_temporal()      : tenure, trend de dépense mensuel
    - build_feature_store()   : dictionnaire {client_id: profil} pour la
                                 phase de simulation dynamique
    - save_features()         : export CSV en data/customer_features.csv

Appelé par : notebooks/0_cleaning_features.ipynb
Produit    : data/customer_features.csv
             data/customer_features_train.csv  (Jan–Juin)
             data/customer_features_test.csv   (Juil–Sep)
─────────────────────────────────────────────────────────────────────────────
"""

# TODO : implémenter
