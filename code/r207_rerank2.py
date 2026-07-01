import os
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
a=pd.read_csv(RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv',
  usecols=['label','original_SUHI_warm','elev100_rural50_SUHI_warm','elev100_rural50_n','rural50_n','rural_ref_minus_urban_elev_m'])
for c in a.columns:
    if c!='label': a[c]=pd.to_numeric(a[c],errors='coerce')
a=a.dropna(subset=['original_SUHI_warm','elev100_rural50_SUHI_warm']).copy()
conv,corr='original_SUHI_warm','elev100_rural50_SUHI_warm'
def report(d,tag):
    d=d.copy(); d['dz']=d['rural_ref_minus_urban_elev_m']; d['terr']=d['dz'].abs()>200
    rho=spearmanr(d[conv],d[corr]).correlation
    out=[f"[{tag}] n={len(d)}  Spearman(conv,corrected)={rho:.3f}"]
    for N in (50,100,500):
        tc=set(d.nlargest(N,conv)['label']); tm=set(d.nlargest(N,corr)['label']); disp=tc-tm
        sub=d[d.label.isin(d.nlargest(N,conv)['label'])]
        out.append(f"   top-{N}: {len(disp)}/{N} displaced ({len(disp)/N*100:.0f}%); terrain share {sub['terr'].mean()*100:.0f}% (base {d['terr'].mean()*100:.0f}%); mean conv {sub[conv].mean():.2f}->corr {sub[corr].mean():.2f}C")
    d['dm']=(pd.qcut(d[corr],10,labels=False)-pd.qcut(d[conv],10,labels=False)).abs()
    out.append(f"   move >=1 decile {(d['dm']>=1).mean()*100:.1f}% ; >=2 {(d['dm']>=2).mean()*100:.1f}%")
    return "\n".join(out)
print(report(a,"unfiltered (has retained retrieval outliers)"))
# Manuscript ranking-analysis filter: five extreme retrieval outliers are retained
# in the released table but excluded from ranking statistics.
ranking=a[(a[conv].between(-15,15))&(a[corr].between(-15,15))]
print(report(ranking,"ranking-analysis population (|SUHI|<=15C)"))
print(f"\nRanking filter removed {len(a)-len(ranking)} cities ({(len(a)-len(ranking))/len(a)*100:.2f}%).")
# Stricter diagnostic only; not the manuscript ranking population.
q=ranking[ranking['elev100_rural50_n']>=30]
print(report(q,"strict matched-pixel diagnostic (ranking filter plus matched n>=30)"))
