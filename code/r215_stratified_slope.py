# -*- coding: utf-8 -*-
"""
R215  Is the reference-elevation bias driven by one region/climate, or universal?
Stratified slope of conventional SUHI on reference-elevation surplus (per 100 m),
within each Koppen broad zone and across elevation/latitude bands, with HC3
heteroskedasticity-robust 95% CIs. Tests the obvious referee concern that the
headline is a high-Asia / cold-climate artifact. Honest: report whatever it shows.
"""
import os, numpy as np, pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_CAUSAL = os.environ.get('SUHI_RAW_CAUSAL_DIR')
if not RAW_CAUSAL:
    raise SystemExit('Set SUHI_RAW_CAUSAL_DIR to the local directory containing r169_endpoint_law_anchor/.')
d=pd.read_csv(os.path.join(RAW_CAUSAL,'r169_endpoint_law_anchor','r169_warm_analysis_panel.csv'))
OUTDIR=os.path.join(REPO,'derived')
os.makedirs(OUTDIR, exist_ok=True)

def hc3_slope(x, y):
    """simple OLS y~1+x, HC3-robust SE of the slope; returns slope, se, lo, hi, n."""
    m=np.isfinite(x)&np.isfinite(y); x=x[m]; y=y[m]; n=len(x)
    if n<30: return (np.nan,)*4+(n,)
    xb=x.mean(); xc=x-xb; Sxx=(xc**2).sum()
    b=(xc*(y-y.mean())).sum()/Sxx; a=y.mean()-b*xb
    e=y-(a+b*x); h=1.0/n + xc**2/Sxx           # leverage (simple regression)
    varb=((xc**2)*(e**2)/(1-h)**2).sum()/Sxx**2 # HC3
    se=np.sqrt(varb)
    return b, se, b-1.96*se, b+1.96*se, n

x=d['rural_ref_minus_urban_elev_m'].values/100.0   # per 100 m
y=d['SUHI_warm'].values

print('=== OVERALL ===')
b,se,lo,hi,n=hc3_slope(x,y)
print(f'  all matched cities: slope {b:+.3f} degC/100m  HC3 95% CI [{lo:+.3f},{hi:+.3f}]  n={n}')

print('\n=== BY KOPPEN BROAD ZONE ===')
rows=[]
name_col='koppen_broad_name' if 'koppen_broad_name' in d else 'koppen_broad'
for z,sub in d.groupby(name_col):
    b,se,lo,hi,n=hc3_slope(sub['rural_ref_minus_urban_elev_m'].values/100, sub['SUHI_warm'].values)
    rows.append((z,n,b,lo,hi));
    if n>=30: print(f'  {str(z)[:26]:26s} n={n:5d}  slope {b:+.3f}  CI [{lo:+.3f},{hi:+.3f}]')
pd.DataFrame(rows,columns=['zone','n','slope','ci_lo','ci_hi']).to_csv(
    os.path.join(OUTDIR,'r215_zone_slope.csv'),index=False)

print('\n=== BY ELEVATION BAND (urban_elev_calc) ===')
ev=d['urban_elev_calc'].values
for lab,m in [('low  <500 m', ev<500),('mid  500-1500 m',(ev>=500)&(ev<1500)),
              ('high 1500-3000 m',(ev>=1500)&(ev<3000)),('v.high >=3000 m',ev>=3000)]:
    b,se,lo,hi,n=hc3_slope(x[m],y[m])
    print(f'  {lab:18s} n={n:5d}  slope {b:+.3f}  CI [{lo:+.3f},{hi:+.3f}]')

print('\n=== EXCLUDING ALL HIGH-ALTITUDE CITIES (drops Tibet+Andes+Anatolia jointly) ===')
for thr in (1500,1000,800):
    m=ev<thr
    b,se,lo,hi,n=hc3_slope(x[m],y[m])
    print(f'  urban elev < {thr} m only: slope {b:+.3f}  CI [{lo:+.3f},{hi:+.3f}]  n={n}  (drops {int((~m).sum())} cities)')

print('\n=== BY ABS LATITUDE BAND ===')
al=d['abslat'].values
for lab,m in [('tropical <23.5',al<23.5),('subtrop 23.5-35',(al>=23.5)&(al<35)),
              ('mid 35-50',(al>=35)&(al<50)),('high >=50',al>=50)]:
    b,se,lo,hi,n=hc3_slope(x[m],y[m])
    print(f'  {lab:16s} n={n:5d}  slope {b:+.3f}  CI [{lo:+.3f},{hi:+.3f}]')

# fraction of the variance / robustness summary
print('\n=== SIGN-CONSISTENCY SUMMARY ===')
zr=pd.DataFrame(rows,columns=['zone','n','slope','ci_lo','ci_hi'])
zr=zr[zr.n>=100]
print(f'  zones with n>=100: {len(zr)};  all positive slope: {(zr.slope>0).all()};  all CI excludes 0: {(zr.ci_lo>0).all()}')
print(f'  slope range across zones: [{zr.slope.min():+.3f}, {zr.slope.max():+.3f}]')
print('DONE')
