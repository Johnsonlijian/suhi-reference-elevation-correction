import os
from pathlib import Path
import pandas as pd, numpy as np, statsmodels.api as sm
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
P = RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv'
DELTA="rural_ref_minus_urban_elev_m"; CTRL=["H2020","rugged","abslat","aridity_index","et0_mm_year","logpop"]
variants={"original (conventional)":"original_SUHI_warm","distance-only 50km":"rural50_SUHI_warm",
 "distance-only 100km":"rural100_SUHI_warm","elev-matched +/-100m,50km":"elev100_rural50_SUHI_warm",
 "elev-matched +/-100m,100km":"elev100_rural100_SUHI_warm","elev-matched +/-200m":"elev200_rural100_SUHI_warm",
 "elev-matched +/-500m":"elev500_rural100_SUHI_warm","elev-matched closest-quartile":"elev_q25_rural100_SUHI_warm"}
use=["label",DELTA,"original_SUHI_warm"]+list(variants.values())+CTRL
df=pd.read_csv(P,usecols=lambda c:c in set(use))
for c in df.columns:
    if c!="label": df[c]=pd.to_numeric(df[c],errors="coerce")
df["dz_km"]=df[DELTA]/1000.0
def slope(y):
    d=df[[y,DELTA]+CTRL].replace([np.inf,-np.inf],np.nan).dropna()
    m=sm.OLS(d[y],sm.add_constant(d[[DELTA]+CTRL])).fit(cov_type="HC3")
    return m.params[DELTA]*100, m.conf_int().loc[DELTA,0]*100, m.conf_int().loc[DELTA,1]*100, int(m.nobs)
print("=== (B1/C2) Reference-definition sensitivity: slope of SUHI on reference-elevation surplus (degC/100m) ===")
print(f"{'reference design':32s} {'slope':>7s} {'95% CI':>18s}  {'median|Δ vs orig|':>16s}  n")
for lab,col in variants.items():
    b,lo,hi,n=slope(col)
    if col=="original_SUHI_warm": md="-"
    else:
        d=(df["original_SUHI_warm"]-df[col]).abs(); md=f"{d.median():.3f}"
    print(f"{lab:32s} {b:+7.3f} [{lo:+6.3f},{hi:+6.3f}]  {md:>16s}  {n}")
print("\n=== (B5/C2) Elevation-matching vs constant -6.5 K/km lapse correction ===")
# lapse-corrected original: SUHI_lapse = original_SUHI - 6.5*dz_km  (bring rural ref to urban elevation)
df["suhi_lapse65"]=df["original_SUHI_warm"]-6.5*df["dz_km"]
for lab,col in [("original (no correction)","original_SUHI_warm"),("constant -6.5 lapse corrected","suhi_lapse65"),
                ("elevation-matched (+/-100m,50km)","elev100_rural50_SUHI_warm")]:
    b,lo,hi,n=slope(col); print(f"  {lab:34s}: residual slope on surplus = {b:+.3f} [{lo:+.3f},{hi:+.3f}] degC/100m  n={n}")
print("  -> interpretation: a residual slope near 0 = terrain dependence removed; large |slope| = under/over-corrected.")
# also report the implied constant lapse the matching/identity removes
b_o=slope("original_SUHI_warm")[0]; b_m=slope("elev100_rural50_SUHI_warm")[0]
print(f"\n  reference-side component removed by matching = {b_o-b_m:+.3f} degC/100m (= effective reference response).")
