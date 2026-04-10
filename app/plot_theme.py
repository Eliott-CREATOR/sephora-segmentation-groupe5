"""
plot_theme.py — Matplotlib Dark Theme Sephora
Thème cohérent avec le design system pour tous les graphiques.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False

SEPHORA_DARK = {
    "bg":      "#0A0A0A",
    "surface": "#0D0D0D",
    "grid":    "#1A1A1A",
    "text":    "#F5F0EB",
    "muted":   "#444444",
    "gold":    "#C9A84C",
    "red":     "#CC0033",
    "green":   "#2EC4B6",
}

CLUSTER_COLORS = [
    "#C9A84C", "#FF6B9D", "#444444", "#E8B4A0",
    "#2EC4B6", "#7CB99A", "#9B7FD4", "#B0A090", "#E8D5A3"
]


def apply_dark_theme(fig, ax_or_axes):
    """Applique le thème Sephora dark sur une figure matplotlib."""
    fig.patch.set_facecolor(SEPHORA_DARK["bg"])
    axes = ax_or_axes if isinstance(ax_or_axes, (list, np.ndarray)) else [ax_or_axes]
    for ax in axes:
        ax.set_facecolor(SEPHORA_DARK["surface"])
        ax.tick_params(colors=SEPHORA_DARK["muted"], labelsize=8)
        ax.xaxis.label.set_color(SEPHORA_DARK["muted"])
        ax.yaxis.label.set_color(SEPHORA_DARK["muted"])
        ax.title.set_color(SEPHORA_DARK["text"])
        ax.title.set_fontfamily("serif")
        ax.title.set_fontsize(10)
        for spine in ax.spines.values():
            spine.set_color(SEPHORA_DARK["grid"])
        ax.grid(True, color=SEPHORA_DARK["grid"], linewidth=0.5, alpha=0.5)
        ax.set_axisbelow(True)
    fig.tight_layout()
    return fig, axes[0] if len(axes) == 1 else axes


def plot_migration_timeline_dark(migrations, selected_date=None):
    """Timeline cumulative des migrations — thème dark."""
    fig, ax = plt.subplots(figsize=(10, 3.5))
    apply_dark_theme(fig, ax)

    colors = {
        "downgrade": SEPHORA_DARK["red"],
        "upgrade":   SEPHORA_DARK["green"],
        "lateral":   SEPHORA_DARK["gold"],
    }
    for direction, color in colors.items():
        sub = migrations[migrations["direction"] == direction]
        if len(sub) > 0:
            cumul = sub.set_index("date").resample("D").size().cumsum()
            ax.fill_between(cumul.index, cumul.values, alpha=0.15, color=color)
            ax.plot(cumul.index, cumul.values, color=color, lw=1.5,
                    label=f"{direction.capitalize()} ({len(sub):,})")

    if selected_date and _HAS_PANDAS:
        ax.axvline(pd.Timestamp(selected_date), color=SEPHORA_DARK["gold"],
                   lw=1, ls="--", alpha=0.7)

    ax.legend(frameon=False, labelcolor=SEPHORA_DARK["muted"],
              fontsize=7, loc="upper left")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=25, labelsize=7)
    return fig


def plot_radar_dark(values, labels, cluster_id: int = 0, persona_name: str = ""):
    """Radar chart en thème dark pour un cluster."""
    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = list(values) + [values[0]]
    angles_plot  = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(SEPHORA_DARK["bg"])
    ax.set_facecolor(SEPHORA_DARK["surface"])

    color = CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)]
    ax.fill(angles_plot, values_plot, alpha=0.2, color=color)
    ax.plot(angles_plot, values_plot, color=color, lw=2)
    ax.scatter(angles, values, s=40, color=color, zorder=5)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, size=7, color=SEPHORA_DARK["muted"])
    ax.set_yticklabels([])
    ax.spines["polar"].set_color(SEPHORA_DARK["grid"])
    ax.grid(color=SEPHORA_DARK["grid"], linewidth=0.5)
    ax.tick_params(colors=SEPHORA_DARK["muted"])

    if persona_name:
        ax.set_title(persona_name, color=SEPHORA_DARK["text"],
                     fontsize=10, pad=15, fontfamily="serif")
    return fig


def plot_clv_scatter_dark(clv_df):
    """Scatter CLV vs CA moyen — thème dark."""
    fig, ax = plt.subplots(figsize=(9, 5))
    apply_dark_theme(fig, ax)

    for i, (idx, row) in enumerate(clv_df.iterrows()):
        color = CLUSTER_COLORS[int(idx) % len(CLUSTER_COLORS)]
        size  = (row["n_clients"] / clv_df["n_clients"].max()) * 1500 + 100
        ax.scatter(row["ca_mean"], row["clv_mean"], s=size,
                   color=color, alpha=0.7, edgecolors=color, lw=1.5)
        ax.annotate(row.get("nom", f"C{idx}"),
                    (row["ca_mean"], row["clv_mean"]),
                    textcoords="offset points", xytext=(8, 4),
                    fontsize=7, color=SEPHORA_DARK["muted"])

    ax.set_xlabel("CA Moyen (€)", color=SEPHORA_DARK["muted"], fontsize=8)
    ax.set_ylabel("CLV Estimée (€)", color=SEPHORA_DARK["muted"], fontsize=8)
    ax.set_title("CLV vs CA Moyen par Segment", color=SEPHORA_DARK["text"],
                 fontsize=10, pad=12)
    return fig


def plot_ca_barplot_dark(profile_df):
    """Barplot horizontal CA par cluster — thème dark."""
    fig, ax = plt.subplots(figsize=(9, 4))
    apply_dark_theme(fig, ax)

    df_sorted = profile_df.sort_values("monetary", ascending=True)
    colors = [CLUSTER_COLORS[int(i) % len(CLUSTER_COLORS)] for i in df_sorted.index]
    bars = ax.barh(range(len(df_sorted)), df_sorted["monetary"],
                   color=colors, alpha=0.8, height=0.6)

    ax.set_yticks(range(len(df_sorted)))
    ax.set_yticklabels([f"C{i}" for i in df_sorted.index],
                        fontsize=8, color=SEPHORA_DARK["muted"])

    mean_val = profile_df["monetary"].mean()
    ax.axvline(mean_val, color=SEPHORA_DARK["gold"], lw=1, ls="--",
               label=f"Moy. {mean_val:.0f}€", alpha=0.7)
    ax.legend(frameon=False, labelcolor=SEPHORA_DARK["muted"], fontsize=7)
    ax.set_xlabel("CA Moyen (€)", color=SEPHORA_DARK["muted"], fontsize=8)

    for i, (val, bar) in enumerate(zip(df_sorted["monetary"], bars)):
        ax.text(val + mean_val * 0.01, i, f"{val:.0f}€",
                va="center", fontsize=7, color=SEPHORA_DARK["muted"])
    return fig
