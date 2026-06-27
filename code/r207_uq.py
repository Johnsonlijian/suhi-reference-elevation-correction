import os
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
cols=['label','original_SUHI_warm','elev100_rural50_SUHI_warm','elev100_rural100_SUHI_warm','elev200_rural100_SUHI_warm','elev500_rural100_SUHI_warm','elev_q25_rural100_SUHI_warm','elev100_rural50_n']
a=pd.read_csv(RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv',usecols=lambda c:c in cols)
for c in a.columns:
    if c!='label': a[c]=pd.to_numeric(a[c],errors='coerce')
conv='original_SUHI_warm'
bands=['elev100_rural50_SUHI_warm','elev100_rural100_SUHI_warm','elev200_rural100_SUHI_warm','elev500_rural100_SUHI_warm','elev_q25_rural100_SUHI_warm']
B=a.dropna(subset=[conv,'elev100_rural50_SUHI_warm']).copy()
for b in bands: B['bias_'+b]=B[conv]-B[b]
bc=['bias_'+b for b in bands]
B['bias_mean']=B[bc].mean(axis=1); B['bias_sd']=B[bc].std(axis=1)   # across-band-definition uncertainty
B['trust_n']=B['elev100_rural50_n']
print(f"n cities with multi-band correction: {len(B)}")
print(f"per-city correction band-definition uncertainty (SD across 5 matched-ref definitions):")
print(f"  median {B['bias_sd'].median():.3f} °C ; p90 {B['bias_sd'].quantile(.9):.3f} °C")
print(f"  as fraction of |bias|: median {(B['bias_sd']/B['bias_mean'].abs().clip(lower=0.05)).median()*100:.0f}%")
print(f"trust flag (matched-ref pixel count elev100_rural50_n): median {B['trust_n'].median():.0f}; "
      f"share <30 px (low-trust) {(B['trust_n']<30).mean()*100:.1f}% ; <10 px {(B['trust_n']<10).mean()*100:.1f}%")
# terrain cities specifically
t=B[B['bias_100' if False else 'bias_elev100_rural50_SUHI_warm'].abs()>0.5]
# attach to released per-city table
out = ROOT/'data'/'per_city_reference_elevation_bias.csv'
pc=pd.read_csv(out)
pc=pc.merge(B[['label','bias_sd','trust_n']].rename(columns={'bias_sd':'correction_uncertainty_C','trust_n':'matched_ref_pixels'}),on='label',how='left')
pc['trust_flag']=np.where(pc['matched_ref_pixels']>=30,'ok','low_pixel')
pc.to_csv(out,index=False)
print(f"\nupdated released table with: correction_uncertainty_C, matched_ref_pixels, trust_flag  ({len(pc)} cities)")
print("=> RSE methods #2 (per-city UQ + QA/trust flag) addressed.")
