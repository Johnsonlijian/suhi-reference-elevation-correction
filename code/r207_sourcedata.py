"""Build the source-data workbook from released derived tables.

If the raw/intermediate causal-panel files are available under SUHI_RAW_CAUSAL_DIR,
the per-city release table can be rebuilt first. Otherwise the script uses the
archived derived CSVs shipped with this release.
"""

import os
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get("SUHI_RAW_CAUSAL_DIR", ROOT / "raw_inputs"))
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


def _outlier_reasons():
    audit = DATA / "outlier_audit.csv"
    if not audit.exists():
        return {}
    a = pd.read_csv(audit, dtype={"label": str})
    return {
        str(row.label): f"extreme retrieval outlier; {row.contamination_type}"
        for row in a.itertuples(index=False)
    }


def load_or_rebuild_per_city():
    raw_panel = RAW / "r159_alternative_reference_bias" / "r159_alternative_reference_panel.csv"
    raw_geo = RAW / "r59_aridity_pet_background_gate" / "r59_city_panel_aridity_pet.csv"
    released = DATA / "per_city_reference_elevation_bias.csv"

    if raw_panel.exists() and raw_geo.exists():
        usecols = [
            "label",
            "original_SUHI_warm",
            "elev100_rural50_SUHI_warm",
            "urban_elev_calc",
            "rural_ref_elev_50km_block",
            "rural_ref_minus_urban_elev_m",
        ]
        a = pd.read_csv(raw_panel, usecols=usecols)
        b = pd.read_csv(raw_geo, usecols=["label", "lon", "lat"])
        d = a.merge(b, on="label")
        for col in d.columns:
            if col != "label":
                d[col] = pd.to_numeric(d[col], errors="coerce")
        d["reference_elevation_bias_C"] = d["original_SUHI_warm"] - d["elev100_rural50_SUHI_warm"]
        deliv = d.rename(
            columns={
                "urban_elev_calc": "urban_elev_m",
                "rural_ref_elev_50km_block": "rural_ref_elev_m",
                "rural_ref_minus_urban_elev_m": "reference_elevation_surplus_m",
                "original_SUHI_warm": "conventional_SUHI_C",
                "elev100_rural50_SUHI_warm": "elevation_matched_SUHI_C",
            }
        )[
            [
                "label",
                "lon",
                "lat",
                "urban_elev_m",
                "rural_ref_elev_m",
                "reference_elevation_surplus_m",
                "conventional_SUHI_C",
                "elevation_matched_SUHI_C",
                "reference_elevation_bias_C",
            ]
        ].dropna(subset=["lon", "lat", "reference_elevation_bias_C"])
    elif released.exists():
        deliv = pd.read_csv(released)
    else:
        raise FileNotFoundError(
            "Neither raw/intermediate files nor data/per_city_reference_elevation_bias.csv are available."
        )

    if "ranking_analysis_included" not in deliv.columns:
        deliv["ranking_analysis_included"] = deliv["conventional_SUHI_C"].between(-15, 15) & deliv[
            "elevation_matched_SUHI_C"
        ].between(-15, 15)
    reasons = _outlier_reasons()
    if "exclusion_reason" not in deliv.columns:
        deliv["exclusion_reason"] = ""
    deliv["exclusion_reason"] = deliv["label"].astype(str).map(reasons).fillna(deliv["exclusion_reason"])
    return deliv


def read_required_csv(name):
    path = DATA / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def table1_summary(deliv):
    d = deliv.copy()
    d["abs_surplus_m"] = pd.to_numeric(d["reference_elevation_surplus_m"], errors="coerce").abs()
    d["abs_bias_C"] = pd.to_numeric(d["reference_elevation_bias_C"], errors="coerce").abs()
    bins = [
        ("|s| < 100 m", d["abs_surplus_m"] < 100),
        ("100 <= |s| < 200 m", (d["abs_surplus_m"] >= 100) & (d["abs_surplus_m"] < 200)),
        ("200 <= |s| < 500 m", (d["abs_surplus_m"] >= 200) & (d["abs_surplus_m"] < 500)),
        ("|s| >= 500 m", d["abs_surplus_m"] >= 500),
    ]
    rows = []
    total = len(d)
    for name, mask in bins:
        sub = d[mask]
        rows.append(
            {
                "surplus_class": name,
                "n": len(sub),
                "share_percent": round(len(sub) / total * 100, 1),
                "median_abs_bias_C": round(sub["abs_bias_C"].median(), 2),
                "abs_bias_gt_1C_percent": round((sub["abs_bias_C"] > 1).mean() * 100, 1),
                "abs_bias_gt_2C_percent": round((sub["abs_bias_C"] > 2).mean() * 100, 1),
            }
        )
    rows.append(
        {
            "surplus_class": f"All {total:,} cities",
            "n": total,
            "share_percent": 100.0,
            "median_abs_bias_C": round(d["abs_bias_C"].median(), 2),
            "abs_bias_gt_1C_percent": round((d["abs_bias_C"] > 1).mean() * 100, 1),
            "abs_bias_gt_2C_percent": round((d["abs_bias_C"] > 2).mean() * 100, 1),
        }
    )
    return pd.DataFrame(rows)


def main():
    deliv = load_or_rebuild_per_city()
    table1 = table1_summary(deliv)
    fig4 = read_required_csv("fig4_slope_sensitivity.csv")
    fig5 = read_required_csv("r173_reference_pixel_lapse_models.csv")
    fig5_summary = read_required_csv("fig5_gradient_summary.csv")
    fig6_path = DATA / "r212_chelsa_vs_modis_lapse.csv"
    fig6 = pd.read_csv(fig6_path) if fig6_path.exists() else pd.DataFrame()
    outliers = read_required_csv("outlier_audit.csv")

    with pd.ExcelWriter(DATA / "source_data.xlsx") as xl:
        deliv.to_excel(xl, sheet_name="Figs1_3_per_city_bias", index=False)
        table1.to_excel(xl, sheet_name="Table1_surplus_class_summary", index=False)
        fig4.to_excel(xl, sheet_name="Fig4_slope_sensitivity", index=False)
        fig5.to_excel(xl, sheet_name="Fig5_pixel_gradient", index=False)
        fig5_summary.to_excel(xl, sheet_name="Fig5_gradient_summary", index=False)
        if len(fig6):
            fig6.to_excel(xl, sheet_name="Fig6_CHELSA_MODIS_lapse", index=False)
        outliers.to_excel(xl, sheet_name="Outlier_audit", index=False)

    print("source_data.xlsx written:", DATA / "source_data.xlsx")
    print(
        "rows:",
        "Figs1_3", len(deliv),
        "| Table1", len(table1),
        "| Fig4", len(fig4),
        "| Fig5", len(fig5),
        "| Fig5 summary", len(fig5_summary),
        "| Fig6", len(fig6),
        "| outliers", len(outliers),
    )


if __name__ == "__main__":
    main()
