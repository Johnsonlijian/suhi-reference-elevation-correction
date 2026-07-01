# -*- coding: utf-8 -*-
"""Rebuild Figures 4 and 5 from archived source-data tables."""

from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.linewidth": 0.9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=400, bbox_inches="tight")
    plt.close(fig)


def figure4():
    src = pd.read_csv(DATA / "fig4_slope_sensitivity.csv")
    col = {
        "conventional": "#111827",
        "distance-only": "#D97706",
        "constant lapse": "#7C3AED",
        "elevation-matched": "#2563EB",
    }

    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    y = np.arange(len(src))[::-1]
    matched = src[src["family"].eq("elevation-matched")]
    ax.axvspan(
        matched["slope_C_per_100m"].min(),
        matched["slope_C_per_100m"].max(),
        color="#e7f0e7",
        zorder=0,
    )
    ax.text(
        0.0,
        5.5,
        "corrected\n(slope near 0)",
        ha="center",
        va="center",
        fontsize=7.8,
        color="#3a7d3a",
    )
    for yi, row in zip(y, src.itertuples(index=False)):
        color = col[row.family]
        ax.plot(
            [row.ci_low_C_per_100m, row.ci_high_C_per_100m],
            [yi, yi],
            color=color,
            lw=1.7,
            zorder=2,
        )
        ax.scatter([row.slope_C_per_100m], [yi], color=color, s=36, zorder=3)
    ax.axvline(0, color="#9CA3AF", lw=1, ls="--", zorder=1)
    ax.set_yticks(y)
    ax.set_yticklabels(src["reference_design"])
    ax.set_xlabel("Slope of SUHI on reference-elevation surplus (deg C per 100 m)")
    ax.set_title("Reference-design sensitivity", loc="left", fontsize=10.5)
    ax.set_xlim(-0.22, 0.56)
    ax.legend(
        handles=[
            Patch(color=col["conventional"], label="conventional"),
            Patch(color=col["distance-only"], label="distance-only"),
            Patch(color=col["constant lapse"], label="constant lapse"),
            Patch(color=col["elevation-matched"], label="elevation-matched"),
        ],
        loc="lower right",
        frameon=False,
        fontsize=8,
    )
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    save(fig, "Figure4_slope_sensitivity_forest")


def figure5():
    windows = pd.read_csv(DATA / "r173_reference_pixel_lapse_models.csv")
    summary = pd.read_csv(DATA / "fig5_gradient_summary.csv")
    pooled = summary[summary["summary"].eq("pooled_all")].iloc[0]
    free_air = summary[summary["summary"].eq("free_air_lapse_reference")].iloc[0]

    seasons = ["jan", "apr", "jul", "oct"]
    fig, ax = plt.subplots(figsize=(7.8, 4.4))
    ax.axhline(free_air.coef_degC_per_km, color="#b0b0b0", ls=":", lw=1.4, zorder=1)
    ax.text(
        7.1,
        free_air.coef_degC_per_km,
        "constant lapse\n(-6.5)",
        va="center",
        ha="left",
        fontsize=7,
        color="#777",
    )

    xpos = {}
    for i, season in enumerate(seasons):
        day = windows[windows["key"].eq(f"{season}_day")].iloc[0]
        night = windows[windows["key"].eq(f"{season}_night")].iloc[0]
        xd, xn = 2 * i, 2 * i + 1
        xpos[f"{season}_day"] = xd
        xpos[f"{season}_night"] = xn
        ax.plot(
            [xd, xn],
            [day["coef_degC_per_km"], night["coef_degC_per_km"]],
            color="#cbd2da",
            lw=1.4,
            zorder=1,
        )

    for _, row in windows.iterrows():
        x = xpos[row["key"]]
        color = "#E07A1F" if "day" in row["key"] else "#3B5BA5"
        ax.errorbar(
            x,
            row["coef_degC_per_km"],
            yerr=[
                [row["coef_degC_per_km"] - row["ci_low_degC_per_km"]],
                [row["ci_high_degC_per_km"] - row["coef_degC_per_km"]],
            ],
            fmt="o",
            ms=7,
            color=color,
            ecolor=color,
            elinewidth=1.2,
            capsize=2,
            zorder=3,
        )

    ax.axhline(pooled.coef_degC_per_km, color="#2563EB", ls="--", lw=1.2, zorder=1)
    ax.text(
        7.45,
        pooled.coef_degC_per_km + 0.05,
        f"pooled mean {pooled.coef_degC_per_km:.2f}\n"
        f"[{pooled.ci_low_degC_per_km:.2f}, {pooled.ci_high_degC_per_km:.2f}]",
        va="bottom",
        ha="left",
        fontsize=7.5,
        color="#1D4ED8",
    )
    ax.set_xticks(range(8))
    ax.set_xticklabels(
        [key.split("_")[0].upper() + "\n" + key.split("_")[1] for key in windows["key"]],
        rotation=0,
        ha="center",
        fontsize=8.5,
    )
    ax.set_ylabel("Surface LST-elevation gradient (deg C/km)", labelpad=8)
    ax.set_title("Rural LST-elevation gradients", loc="left", fontsize=9.2)
    ax.set_ylim(-7.0, -3.4)
    ax.set_xlim(-0.6, 9.0)
    fig.subplots_adjust(left=0.16, right=0.98, bottom=0.18, top=0.88)
    ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#E07A1F", label="daytime", markersize=7),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#3B5BA5", label="night-time", markersize=7),
            Line2D([0], [0], color="#cbd2da", lw=1.4, label="day-night pair"),
        ],
        frameon=False,
        fontsize=8.5,
        loc="lower left",
    )
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    save(fig, "Figure5_rural_pixel_gradient")


if __name__ == "__main__":
    figure4()
    print("Figure 4 rebuilt from data/fig4_slope_sensitivity.csv")
    figure5()
    print("Figure 5 rebuilt from data/r173_reference_pixel_lapse_models.csv and data/fig5_gradient_summary.csv")
