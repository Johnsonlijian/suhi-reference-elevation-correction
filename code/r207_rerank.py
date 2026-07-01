import os
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
a=pd.read_csv(RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv',
  usecols=['label','original_SUHI_warm','elev100_rural50_SUHI_warm','rural_ref_minus_urban_elev_m'])
b=pd.read_csv(RAW/'r59_aridity_pet_background_gate'/'r59_city_panel_aridity_pet.csv',usecols=['label','lon','lat'])
d=a.merge(b,on='label')
for c in d.columns:
    if c!='label': d[c]=pd.to_numeric(d[c],errors='coerce')
d=d.dropna(subset=['original_SUHI_warm','elev100_rural50_SUHI_warm']).copy()
d['dz']=d['rural_ref_minus_urban_elev_m']; d['terr']=d['dz'].abs()>200
conv,corr='original_SUHI_warm','elev100_rural50_SUHI_warm'
d=d[(d[conv].between(-15,15)) & (d[corr].between(-15,15))].copy()
d['ranking_analysis_included']=True
n=len(d); print(f"n={n}")
rho_all=spearmanr(d[conv],d[corr]).correlation
rho_terr=spearmanr(d[d.terr][conv],d[d.terr][corr]).correlation
print(f"Spearman rank corr conv vs corrected: all {rho_all:.3f} | terrain(|dz|>200m,n={d.terr.sum()}) {rho_terr:.3f}")
# top-N displacement
for N in (50,100,500):
    tc=set(d.nlargest(N,conv)['label']); tm=set(d.nlargest(N,corr)['label'])
    disp=tc-tm; print(f"top-{N} most-intense SUHI: {len(disp)} of {N} ({len(disp)/N*100:.0f}%) displaced after correction; "
          f"median |dz| of displaced = {d[d.label.isin(disp)]['dz'].abs().median():.0f} m")
# decile moves
d['dconv']=pd.qcut(d[conv],10,labels=False); d['dcorr']=pd.qcut(d[corr],10,labels=False)
d['dmove']=(d['dcorr']-d['dconv']).abs()
print(f"\ncities moving >=1 SUHI decile after correction: {(d['dmove']>=1).mean()*100:.1f}%  ; >=2 deciles: {(d['dmove']>=2).mean()*100:.1f}%")
print(f"  among terrain cities: >=1 decile {(d[d.terr]['dmove']>=1).mean()*100:.1f}% ; >=2 {(d[d.terr]['dmove']>=2).mean()*100:.1f}%")
# most-overestimated cities (largest positive bias = conventional too hot)
d['bias']=d[conv]-d[corr]
print("\nThe 8 most reference-inflated SUHI cities (conventional − corrected, °C):")
print(d.nlargest(8,'bias')[['lon','lat','dz','original_SUHI_warm','elev100_rural50_SUHI_warm','bias']].round(2).to_string(index=False))
# how many top-100-conventional are terrain
tc=d.nlargest(100,conv); print(f"\nof top-100 conventional-SUHI cities, terrain share = {tc['terr'].mean()*100:.0f}% (vs {d['terr'].mean()*100:.0f}% baseline) => conventional ranking over-represents terrain cities")
