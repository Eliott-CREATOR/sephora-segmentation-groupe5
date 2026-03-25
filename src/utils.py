"""
utils.py
─────────────────────────────────────────────────────────────────────────────
Rôle : fonctions utilitaires partagées entre tous les modules du projet.

Fonctions prévues :
    - set_global_style()     : configure le thème matplotlib/seaborn
                                cohérent sur toutes les visualisations
    - save_figure()          : sauvegarde une figure matplotlib dans
                                outputs/figures/ avec le bon nommage
    - shannon_entropy()      : calcule l'entropie de Shannon d'une
                                distribution (utilisée pour brand_entropy
                                et axe_entropy dans feature_engineering)
    - compute_clv()          : estime la Customer Lifetime Value d'un client
                                à partir de avg_basket, frequency, tenure
    - format_delta()         : formate un delta vs moyenne pour affichage
                                (ex: "+23%" ou "-5 pp")
    - validate_dataframe()   : assertions basiques sur un dataframe (pas de
                                NaN critiques, types corrects, plages valides)
    - DATA_PATH              : constante chemin vers data/
    - MODELS_PATH            : constante chemin vers models/
    - OUTPUTS_PATH           : constante chemin vers outputs/
    - RANDOM_SEED            : constante = 42 (reproductibilité)

Importé par : tous les autres modules et notebooks
─────────────────────────────────────────────────────────────────────────────
"""

# TODO : implémenter
