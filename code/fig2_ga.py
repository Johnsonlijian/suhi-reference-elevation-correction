# -*- coding: utf-8 -*-
"""Rebuild Figure 2 and the graphical abstract from released data."""

from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "mathtext.default": "regular",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

URBAN = "#C0392B"
RURAL = "#2563EB"
MATCH = "#16A085"


def save(fig, name, dpi=400):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def region_color(lon, lat):
    if 70 <= lon <= 105 and 26 <= lat <= 42:
        return "#D55E00"  # Himalaya-Tibet
    if -82 <= lon <= -62 and -56 <= lat <= 14:
        return "#E69F00"  # Andes
    if 36 <= lon <= 62 and 30 <= lat <= 45:
        return "#CC79A7"  # Anatolian/Iranian
    if -125 <= lon <= -98 and 15 <= lat <= 52:
        return "#0072B2"  # North America
    return "#999999"


def build_figure2():
    fig = plt.figure(figsize=(10.4, 4.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.05], wspace=0.24)

    ax = fig.add_subplot(gs[0, 0])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    grad = np.linspace(0, 1, 200).reshape(-1, 1)
    ax.imshow(grad, extent=[0, 10, 0, 6.2], origin="lower", cmap="RdYlBu", alpha=0.20, aspect="auto", zorder=0)
    tx = np.linspace(0, 10, 200)
    ty = 1.2 + 1.7 * (1 - np.exp(-((tx - 5) ** 2) / 3.2))
    ax.add_patch(Polygon(np.c_[np.r_[tx, [10, 0]], np.r_[ty, [0, 0]]], closed=True, fc="#e9ddc9", ec="#cbb89a", lw=1, zorder=1))
    ax.add_patch(Rectangle((4.5, ty[90]), 1.0, 0.95, fc=URBAN, ec="k", lw=0.6, zorder=3))
    ax.text(5.0, ty[90] + 1.2, "urban core\nzU (low, warm)", ha="center", va="bottom", color=URBAN, fontsize=8.5)
    for xp in (1.4, 8.6):
        idx = int(xp / 10 * 199)
        ax.add_patch(Rectangle((xp - 0.18, ty[idx]), 0.36, 0.36, fc=RURAL, ec="k", lw=0.5, zorder=3))
        ax.text(xp, ty[idx] + 0.5, "rural ref\nzR (high, cool)", ha="center", va="bottom", color=RURAL, fontsize=8.5)
    ax.annotate("", xy=(8.6, ty[int(8.6 / 10 * 199)]), xytext=(8.6, ty[90]), arrowprops=dict(arrowstyle="<->", color="#444", lw=1.2))
    ax.text(8.95, (ty[int(8.6 / 10 * 199)] + ty[90]) / 2, "Delta z", fontsize=9, color="#444")
    ax.text(0.15, 5.8, "cooler", fontsize=7, color="#3B5BA5")
    ax.text(0.15, 0.25, "warmer", fontsize=7, color="#C0392B")
    ax.set_title("a  Terrain mismatch", loc="left", fontsize=9.5)

    ax = fig.add_subplot(gs[0, 1])
    z = np.array([0, 1.5])
    grad_c = -5.0
    lst0 = 31
    ax.plot(z, lst0 + grad_c * z, color="#333", lw=2.3, zorder=2)
    ax.text(1.52, lst0 + grad_c * 1.5, "  surface LST\n  approx -5 deg C/km", va="center", fontsize=8.5, color="#333")
    zU, zR = 0.25, 1.05
    LU, LR, LRm = lst0 + grad_c * zU, lst0 + grad_c * zR, lst0 + grad_c * zU
    ax.scatter([zU], [LU], color=URBAN, s=70, zorder=5, ec="k", lw=0.5)
    ax.text(zU, LU + 0.5, "urban U", color=URBAN, ha="center", fontsize=8.4)
    ax.scatter([zR], [LR], color=RURAL, s=70, zorder=5, ec="k", lw=0.5)
    ax.text(
        zR + 0.20,
        LR - 0.35,
        "rural ref R\n(conventional)",
        color=RURAL,
        ha="left",
        fontsize=7.4,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.72, pad=0.2),
    )
    ax.scatter([zU], [LRm], color=MATCH, s=80, marker="s", zorder=5, ec="k", lw=0.5)
    ax.add_patch(FancyArrowPatch((zR, LR), (zU + 0.02, LRm), connectionstyle="arc3,rad=0.25", arrowstyle="->", color=MATCH, lw=1.8, zorder=4))
    ax.text(0.5, 28.0, "match reference\nto urban elevation", color=MATCH, fontsize=9.5, ha="center")
    ax.annotate("", xy=(zR + 0.08, LR), xytext=(zR + 0.08, LU), arrowprops=dict(arrowstyle="<->", color=URBAN, lw=1.4))
    ax.text(zR + 0.20, (LR + LU) / 2, "S = U - R\n(inflated)", color=URBAN, va="center", fontsize=7.6)
    ax.annotate("", xy=(zU - 0.07, LRm), xytext=(zU - 0.07, LU), arrowprops=dict(arrowstyle="<->", color=MATCH, lw=1.4))
    ax.text(zU - 0.12, (LRm + LU) / 2, "S' near 0", color=MATCH, va="center", ha="right", fontsize=7.8)
    for zz, LL in ((zU, LU), (zR, LR)):
        ax.plot([zz, zz], [20, LL], color="#e2e2e2", lw=0.8, zorder=0)
    ax.set_xlim(-0.18, 1.85)
    ax.set_ylim(22.5, 32)
    ax.set_xlabel("elevation (km)")
    ax.set_ylabel("land-surface temperature (deg C)")
    ax.set_title("b  Reference matching", loc="left", fontsize=9.5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    save(fig, "Figure2_mechanism_schematic")
    print("Figure 2 rebuilt")


def build_graphical_abstract():
    d = pd.read_csv(DATA / "per_city_reference_elevation_bias.csv").dropna(
        subset=["conventional_SUHI_C", "elevation_matched_SUHI_C", "reference_elevation_surplus_m", "lon", "lat"]
    )
    if "ranking_analysis_included" in d.columns:
        d = d[d["ranking_analysis_included"].astype(bool)]
    else:
        d = d[d["conventional_SUHI_C"].between(-15, 15) & d["elevation_matched_SUHI_C"].between(-15, 15)]

    top = d.nlargest(100, "conventional_SUHI_C").copy()
    top["color"] = [region_color(lon, lat) for lon, lat in zip(top["lon"], top["lat"])]
    mean_conv = top["conventional_SUHI_C"].mean()
    mean_matched = top["elevation_matched_SUHI_C"].mean()

    fig = plt.figure(figsize=(13.3, 5.32))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.15], wspace=0.05)
    fig.suptitle(
        "Conventional rural references inflate upper-tail satellite surface urban heat-island rankings",
        x=0.5,
        y=0.99,
        fontsize=14,
        fontweight="bold",
    )

    ax = fig.add_subplot(gs[0, 0])
    for _, row in top.iterrows():
        ax.plot([0, 1], [row["conventional_SUHI_C"], row["elevation_matched_SUHI_C"]], color=row["color"], lw=0.9, alpha=0.6, zorder=2)
    ax.plot([0, 1], [mean_conv, mean_matched], color="#111", lw=4, zorder=6, solid_capstyle="round")
    ax.scatter([0, 1], [mean_conv, mean_matched], color="#111", s=70, zorder=7)
    ax.text(0.5, (mean_conv + mean_matched) / 2 + 1.6, f"mean {mean_conv:.1f} -> {mean_matched:.1f} deg C", ha="center", fontsize=13, fontweight="bold")
    ax.set_xlim(-0.22, 1.22)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Conventional\nreference", "Elevation-\nmatched"], fontsize=11)
    ax.set_ylim(-1, 13.5)
    ax.set_ylabel("SUHI of the 100 most-intense conventional-reference cities (deg C)", fontsize=10.5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    handles = [
        Line2D([], [], color=color, lw=3, label=label)
        for color, label in [
            ("#D55E00", "Himalaya-Tibet"),
            ("#E69F00", "Andes"),
            ("#CC79A7", "Anatolian/Iranian"),
            ("#0072B2", "N. America"),
            ("#999999", "other"),
        ]
    ]
    legend = ax.legend(handles=handles, loc="upper right", frameon=True, framealpha=0.92, fontsize=8.2, title="mountain region", title_fontsize=8.5)
    legend.get_frame().set_edgecolor("#dddddd")
    legend.get_frame().set_linewidth(0.6)

    ax = fig.add_subplot(gs[0, 1])
    ax.axis("off")
    ax.text(0.0, 0.90, "Of the conventional-reference top 100:", fontsize=13, fontweight="bold", transform=ax.transAxes)
    for i, (big, small, big_size, small_x) in enumerate(
        [
            ("97 / 100", "drop out of the top 100 after correction", 24, 0.34),
            ("98 %", "are high-terrain cities (vs 20.4% baseline)", 24, 0.34),
            ("rho = 0.68", "conventional vs elevation-matched ranking", 21, 0.52),
        ]
    ):
        yy = 0.74 - i * 0.20
        ax.text(0.02, yy, big, fontsize=big_size, fontweight="bold", color="#C0392B", transform=ax.transAxes)
        ax.text(small_x, yy + 0.03, small, fontsize=11.5, va="center", transform=ax.transAxes)
    ax.text(
        0.0,
        0.07,
        "Dominated by the Himalaya-Tibet, Andes, Iranian and N. American cordillera.\nA within-city correction and a global per-city dataset are released.",
        fontsize=10.5,
        color="#333",
        transform=ax.transAxes,
    )
    save(fig, "Graphical_Abstract", dpi=300)
    print("Graphical abstract rebuilt at ~3990 x 1596 px")


if __name__ == "__main__":
    build_figure2()
    build_graphical_abstract()
