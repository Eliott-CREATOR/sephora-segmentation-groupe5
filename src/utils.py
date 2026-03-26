"""
utils.py
─────────────────────────────────────────────────────────────────────────────
Rôle : fonctions utilitaires partagées entre tous les modules du projet.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle

# ── Chemins ──────────────────────────────────────────────────────────────────

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DATA_PATH    = os.path.join(_ROOT, "data")
MODELS_PATH  = os.path.join(_ROOT, "models")
OUTPUTS_PATH = os.path.join(_ROOT, "outputs")

RANDOM_SEED = 42


# ── Style matplotlib ──────────────────────────────────────────────────────────

SEPHORA_COLORS = {
    "black":   "#1A1A1A",
    "pink":    "#FF0066",
    "lgray":   "#F5F5F5",
    "mgray":   "#CCCCCC",
    "white":   "#FFFFFF",
    "cluster": ["#FF0066", "#1A1A1A", "#FF6699", "#990033",
                "#FF99BB", "#660022", "#FF3377", "#CC0055"],
}


def set_global_style():
    """Configure le thème matplotlib/seaborn cohérent sur toutes les visu."""
    plt.rcParams.update({
        "figure.facecolor":  SEPHORA_COLORS["white"],
        "axes.facecolor":    SEPHORA_COLORS["lgray"],
        "axes.edgecolor":    SEPHORA_COLORS["mgray"],
        "axes.labelcolor":   SEPHORA_COLORS["black"],
        "text.color":        SEPHORA_COLORS["black"],
        "xtick.color":       SEPHORA_COLORS["black"],
        "ytick.color":       SEPHORA_COLORS["black"],
        "grid.color":        SEPHORA_COLORS["mgray"],
        "grid.alpha":        0.5,
        "grid.linestyle":    "--",
        "font.family":       "sans-serif",
        "font.size":         11,
        "axes.titlesize":    13,
        "axes.titleweight":  "bold",
        "axes.labelsize":    11,
        "figure.dpi":        150,
        "savefig.dpi":       200,
        "savefig.bbox":      "tight",
        "savefig.facecolor": SEPHORA_COLORS["white"],
    })


# ── Sauvegarde figures ────────────────────────────────────────────────────────

def save_figure(fig: plt.Figure, filename: str, subdir: str = "figures") -> str:
    """
    Sauvegarde une figure matplotlib dans outputs/<subdir>/<filename>.

    Returns
    -------
    str : chemin absolu du fichier sauvegardé
    """
    dest = os.path.join(OUTPUTS_PATH, subdir)
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, filename)
    fig.savefig(path)
    plt.close(fig)
    return path


# ── Shannon entropy ───────────────────────────────────────────────────────────

def shannon_entropy(series: pd.Series) -> float:
    """
    Calcule l'entropie de Shannon d'une distribution discrète (valeurs brutes).

    Parameters
    ----------
    series : pd.Series
        Valeurs brutes (ex: liste de marques, de CA par marque).

    Returns
    -------
    float : entropie H = -Σ p_i * log2(p_i)  (0 si distribution uniforme à 1 val.)
    """
    if series.empty or series.sum() == 0:
        return 0.0
    probs = series / series.sum()
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


# ── CLV ───────────────────────────────────────────────────────────────────────

def compute_clv(avg_basket: float, frequency: float, tenure_days: float,
                margin: float = 0.35, horizon_years: float = 3.0) -> float:
    """
    Estime la Customer Lifetime Value (CLV) simple.

    CLV = avg_basket × avg_purchases_per_year × margin × horizon_years

    Parameters
    ----------
    avg_basket     : CA moyen par ticket (EUR)
    frequency      : nombre de tickets sur la période observée
    tenure_days    : durée d'observation en jours
    margin         : taux de marge estimé (défaut 35%)
    horizon_years  : projection en années (défaut 3 ans)

    Returns
    -------
    float : CLV estimée en EUR
    """
    if tenure_days <= 0 or frequency <= 0:
        return 0.0
    purchases_per_year = frequency / max(tenure_days / 365.25, 0.1)
    return avg_basket * purchases_per_year * margin * horizon_years


# ── Format delta ──────────────────────────────────────────────────────────────

def format_delta(value: float, reference: float, unit: str = "%",
                 decimals: int = 1) -> str:
    """
    Formate un delta vs référence pour affichage.

    Examples
    --------
    >>> format_delta(85.0, 69.31)         # "+22.6%"
    >>> format_delta(0.18, 0.131, "pp")   # "+4.9 pp"
    """
    if reference == 0:
        return "N/A"
    if unit == "%":
        delta = (value - reference) / reference * 100
        sign = "+" if delta >= 0 else ""
        return f"{sign}{delta:.{decimals}f}%"
    else:
        delta = value - reference
        sign = "+" if delta >= 0 else ""
        return f"{sign}{delta:.{decimals}f} {unit}"


# ── Validation dataframe ──────────────────────────────────────────────────────

def validate_dataframe(df: pd.DataFrame,
                       required_cols: list = None,
                       no_nan_cols: list = None,
                       min_rows: int = 1) -> bool:
    """
    Assertions basiques sur un dataframe.

    Parameters
    ----------
    df            : dataframe à valider
    required_cols : colonnes qui doivent exister
    no_nan_cols   : colonnes qui ne doivent pas avoir de NaN
    min_rows      : nombre minimum de lignes

    Returns
    -------
    bool : True si tout est valide

    Raises
    ------
    AssertionError si une vérification échoue
    """
    assert len(df) >= min_rows, f"DataFrame trop petit : {len(df)} < {min_rows} lignes"

    if required_cols:
        missing = [c for c in required_cols if c not in df.columns]
        assert not missing, f"Colonnes manquantes : {missing}"

    if no_nan_cols:
        for col in no_nan_cols:
            n_nan = df[col].isna().sum()
            assert n_nan == 0, f"NaN dans '{col}' : {n_nan} lignes"

    return True
