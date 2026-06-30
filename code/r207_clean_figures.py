# -*- coding: utf-8 -*-
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt


HERE = Path(__file__).resolve().parent
if (HERE / "source_data" / "source_data.xlsx").exists():
    ROOT = HERE
    OUT = ROOT / "figs"
    SOURCE = ROOT / "source_data" / "source_data.xlsx"
else:
    ROOT = HERE.parent
    OUT = ROOT / "figures"
    SOURCE = ROOT / "data" / "source_data.xlsx"

OUT.mkdir(exist_ok=True)

mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


def save(fig, name, dpi=360):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(
            OUT / f"{name}.{ext}",
            dpi=dpi,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="white",
            transparent=False,
        )
    plt.close(fig)


def figure3_map():
    city = pd.read_excel(SOURCE, sheet_name="Fig1_per_city_bias")
    city = city.dropna(subset=["lon", "lat", "reference_elevation_bias_C"]).copy()
    city = city[city["lat"].between(-60, 85)]
    step = 2.5
    city["lon_cell"] = np.floor((city["lon"] + 180) / step) * step - 180 + step / 2
    city["lat_cell"] = np.floor((city["lat"] + 90) / step) * step - 90 + step / 2
    grid = (
        city.groupby(["lon_cell", "lat_cell"])["reference_elevation_bias_C"]
        .agg(mean_abs_bias_C=lambda s: s.abs().mean(), n_cities="size")
        .reset_index()
    )
    grid = grid[grid["n_cities"] >= 2]

    fig = plt.figure(figsize=(9.1, 4.25), facecolor="white")
    try:
        import cartopy.crs as ccrs
        import cartopy.feature as cfeature

        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_extent([-180, 180, -60, 84], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.OCEAN.with_scale("110m"), facecolor="#f7f9fb", zorder=0)
        ax.add_feature(cfeature.LAND.with_scale("110m"), facecolor="#f2f4f6", edgecolor="none", zorder=0)
        ax.coastlines(resolution="110m", linewidth=0.35, color="#a8b0ba", zorder=1)
        transform = ccrs.PlateCarree()
    except Exception:
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlim(-180, 180)
        ax.set_ylim(-60, 84)
        ax.set_facecolor("#f7f9fb")
        transform = None

    sc = ax.scatter(
        grid["lon_cell"],
        grid["lat_cell"],
        c=grid["mean_abs_bias_C"].clip(0, 1.6),
        s=11,
        marker="s",
        cmap="Reds",
        vmin=0,
        vmax=1.6,
        linewidths=0,
        alpha=0.9,
        transform=transform,
        zorder=2,
    )
    ax.set_title("Reference-elevation bias concentrates in terrain", loc="left", fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in getattr(ax, "spines", {}).values():
        spine.set_visible(False)
    cb = fig.colorbar(sc, ax=ax, fraction=0.025, pad=0.015, extend="max")
    cb.set_label("mean |SUHI bias| per 2.5° cell (°C)", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    save(fig, "Figure3_global_bias_map")


def figure4_forest():
    df = pd.read_excel(SOURCE, sheet_name="Fig2_slope_by_reference")
    label_map = {
        "conventional (original)": "conventional",
        "distance-only 50km": "distance-only\n50 km",
        "distance-only 100km": "distance-only\n100 km",
        "constant -6.5 K/km lapse": "constant lapse",
        "elev-matched +/-100m": "matched\n±100 m",
        "elev-matched +/-200m": "matched\n±200 m",
        "elev-matched +/-500m": "matched\n±500 m",
        "elev-matched closest-quartile": "matched\nclosest quartile",
    }
    colors = []
    for ref in df["reference_design"]:
        if ref.startswith("conventional"):
            colors.append("#111827")
        elif ref.startswith("distance"):
            colors.append("#d97706")
        elif ref.startswith("constant"):
            colors.append("#7c3aed")
        else:
            colors.append("#2563eb")

    fig, ax = plt.subplots(figsize=(7.0, 4.2), facecolor="white")
    y = np.arange(len(df))[::-1]
    ax.axvline(0, color="#8b98a8", lw=0.9, ls="--", zorder=0)
    ax.axhspan(-0.5, 3.5, color="#e8f2e8", zorder=0)
    for yi, row, color in zip(y, df.itertuples(index=False), colors):
        x = row.slope_C_per_100m
        ax.errorbar(
            x,
            yi,
            xerr=[[x - row.ci_low], [row.ci_high - x]],
            fmt="o",
            ms=5,
            lw=1.2,
            capsize=0,
            color=color,
            zorder=2,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([label_map.get(v, v) for v in df["reference_design"]], fontsize=8)
    ax.set_xlabel("Slope of SUHI on reference-elevation surplus (°C per 100 m)")
    ax.set_title("Terrain dependence by reference design", loc="left", fontsize=10)
    ax.set_xlim(-0.22, 0.55)
    ax.set_ylim(-0.6, len(df) - 0.4)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    save(fig, "Figure4_slope_sensitivity_forest")


def figure5_gradient():
    df = pd.read_excel(SOURCE, sheet_name="Fig3_pixel_gradient")
    x = np.arange(len(df))
    is_day = df["label"].str.contains("day", case=False)
    colors = np.where(is_day, "#d97706", "#2f56a6")

    fig, ax = plt.subplots(figsize=(7.2, 4.2), facecolor="white")
    ax.plot(x, df["coef_degC_per_km"], color="#c7d0db", lw=1.4, zorder=1)
    for xi, row, color in zip(x, df.itertuples(index=False), colors):
        y = row.coef_degC_per_km
        ax.errorbar(
            xi,
            y,
            yerr=[[y - row.ci_low_degC_per_km], [row.ci_high_degC_per_km - y]],
            fmt="o",
            ms=5,
            lw=1.1,
            capsize=2.5,
            color=color,
            zorder=2,
        )
    ax.axhline(-6.5, color="#9aa0a6", lw=1.0, ls=":", zorder=0)
    ax.axhline(0, color="#e5e7eb", lw=0.8, zorder=0)
    ax.set_xticks(x)
    ax.set_xticklabels([v.upper() for v in df["label"]], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Rural-pixel surface LST-elevation gradient (°C km$^{-1}$)")
    ax.set_title("Pixel-scale LST-elevation gradients are negative in every window", loc="left", fontsize=10)
    ax.set_ylim(-7.0, -3.3)
    day_proxy = plt.Line2D([], [], marker="o", ls="", color="#d97706", label="day")
    night_proxy = plt.Line2D([], [], marker="o", ls="", color="#2f56a6", label="night")
    lapse_proxy = plt.Line2D([], [], ls=":", color="#9aa0a6", label="−6.5 K km$^{-1}$")
    ax.legend(handles=[day_proxy, night_proxy, lapse_proxy], loc="lower left", frameon=False, fontsize=8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    save(fig, "Figure5_rural_pixel_gradient")


if __name__ == "__main__":
    figure3_map()
    figure4_forest()
    figure5_gradient()
    print("Clean display figures written ->", OUT)
