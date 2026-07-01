"""Attach matching-definition sensitivity and QA flags to the released table."""

import os
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get("SUHI_RAW_CAUSAL_DIR", ROOT / "raw_inputs"))
DATA = ROOT / "data"

cols = [
    "label",
    "original_SUHI_warm",
    "elev100_rural50_SUHI_warm",
    "elev100_rural100_SUHI_warm",
    "elev200_rural100_SUHI_warm",
    "elev500_rural100_SUHI_warm",
    "elev_q25_rural100_SUHI_warm",
    "elev100_rural50_n",
]

raw_panel = RAW / "r159_alternative_reference_bias" / "r159_alternative_reference_panel.csv"
if not raw_panel.exists():
    raise FileNotFoundError(
        f"{raw_panel} not found. Set SUHI_RAW_CAUSAL_DIR to rebuild correction sensitivity from raw/intermediate inputs."
    )

a = pd.read_csv(raw_panel, usecols=lambda c: c in cols)
for col in a.columns:
    if col != "label":
        a[col] = pd.to_numeric(a[col], errors="coerce")

conv = "original_SUHI_warm"
bands = [
    "elev100_rural50_SUHI_warm",
    "elev100_rural100_SUHI_warm",
    "elev200_rural100_SUHI_warm",
    "elev500_rural100_SUHI_warm",
    "elev_q25_rural100_SUHI_warm",
]
B = a.dropna(subset=[conv, "elev100_rural50_SUHI_warm"]).copy()
for band in bands:
    B["bias_" + band] = B[conv] - B[band]
bias_cols = ["bias_" + band for band in bands]
B["bias_mean"] = B[bias_cols].mean(axis=1)
B["bias_sd"] = B[bias_cols].std(axis=1)
B["trust_n"] = B["elev100_rural50_n"]

print(f"n cities with multi-band correction: {len(B)}")
print("per-city correction matching-definition sensitivity (SD across 5 matched-reference definitions):")
print(f"  median {B['bias_sd'].median():.3f} deg C ; p90 {B['bias_sd'].quantile(.9):.3f} deg C")
print(
    f"  as fraction of |bias|: median "
    f"{(B['bias_sd'] / B['bias_mean'].abs().clip(lower=0.05)).median() * 100:.0f}%"
)
print(
    f"trust flag (matched-ref pixel count elev100_rural50_n): median {B['trust_n'].median():.0f}; "
    f"share <30 px (low-trust) {(B['trust_n'] < 30).mean() * 100:.1f}% ; "
    f"<10 px {(B['trust_n'] < 10).mean() * 100:.1f}%"
)

out = DATA / "per_city_reference_elevation_bias.csv"
pc = pd.read_csv(out)
pc = pc.drop(columns=["correction_uncertainty_C", "matched_ref_pixels"], errors="ignore")
pc = pc.merge(
    B[["label", "bias_sd", "trust_n"]].rename(
        columns={"bias_sd": "correction_uncertainty_C", "trust_n": "matched_ref_pixels"}
    ),
    on="label",
    how="left",
)
pc["trust_flag"] = np.where(pc["matched_ref_pixels"] >= 30, "ok", "low_pixel")

conv_col = "conventional_SUHI_C"
corr_col = "elevation_matched_SUHI_C"
if conv_col in pc.columns and corr_col in pc.columns:
    pc["ranking_analysis_included"] = pc[conv_col].between(-15, 15) & pc[corr_col].between(-15, 15)
    audit = DATA / "outlier_audit.csv"
    if audit.exists():
        a = pd.read_csv(audit, dtype={"label": str})
        reasons = {
            str(row.label): f"extreme retrieval outlier; {row.contamination_type}"
            for row in a.itertuples(index=False)
        }
    else:
        reasons = {}
    pc["exclusion_reason"] = pc["label"].astype(str).map(reasons).fillna("")

pc.to_csv(out, index=False)
print(
    "updated released table with: correction_uncertainty_C (matching-definition SD), "
    f"matched_ref_pixels, trust_flag, ranking_analysis_included, exclusion_reason ({len(pc)} cities)"
)
