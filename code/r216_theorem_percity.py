# -*- coding: utf-8 -*-
"""
R216  Per-city validation of the central theorem  bias ~= -gamma * dz.

The released per-city correction (reference_elevation_bias_C) is computed by RURAL-REFERENCE
SUBSTITUTION (matched-rural LST minus conventional-rural LST) -- it never uses a lapse rate.
The theorem predicts it should equal -gamma*dz, where gamma is the rural skin-LST elevation
gradient and dz = reference_elevation_surplus_m. If we regress the released (substitution-based)
bias on the surplus, the recovered slope should INDEPENDENTLY reproduce the bootstrapped
gradient gamma = -5.00 K/km (r211/r214). That triangulates gamma a 3rd way AND shows the simple
linear-lapse theorem reproduces the full substitution correction city-by-city.

HC3-robust SE; also report the scatter (where nonlinearity / block heterogeneity enters) honestly.
"""
import os, numpy as np, pandas as pd
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV=os.path.join(REPO,'data','per_city_reference_elevation_bias.csv')
d=pd.read_csv(CSV)

dz=d['reference_elevation_surplus_m'].values          # metres, rural_ref - urban
bias=d['reference_elevation_bias_C'].values           # degC, from substitution (NO lapse used)
m=np.isfinite(dz)&np.isfinite(bias)
dz,bias=dz[m],bias[m]; n=len(dz)
print(f'n cities = {n:,}')

# regress bias on dz THROUGH THE ORIGIN (theorem: bias = -gamma * dz, no intercept)
# slope_origin = sum(dz*bias)/sum(dz^2);  effective gamma = -slope*1000 (per km)
b0=(dz*bias).sum()/(dz*dz).sum()
# HC3 for through-origin slope: var = sum(dz^2 * e^2/(1-h)^2)/ (sum dz^2)^2 , h_i = dz_i^2/sum(dz^2)
e=bias-b0*dz; Sdd=(dz*dz).sum(); h=dz*dz/Sdd
varb=((dz*dz)*(e*e)/(1-h)**2).sum()/Sdd**2; se=np.sqrt(varb)
gamma_eff=-b0*1000; gse=se*1000
print('\n=== THROUGH-ORIGIN (theorem form bias = -gamma*dz) ===')
print(f'  slope = {b0:+.6f} degC/m   effective gamma = {gamma_eff:+.3f} K/km  HC3 95% CI [{gamma_eff-1.96*gse:+.3f},{gamma_eff+1.96*gse:+.3f}]')
print(f'  bootstrapped within-block gamma (r211/r214) = -5.00 / -4.79..-4.84  -> agreement check')

# with intercept (does an offset sneak in?)
xb=dz.mean(); xc=dz-xb; Sxx=(xc*xc).sum()
b1=(xc*(bias-bias.mean())).sum()/Sxx; a1=bias.mean()-b1*xb
e1=bias-(a1+b1*dz); hh=1.0/n+xc*xc/Sxx
vb1=((xc*xc)*(e1*e1)/(1-hh)**2).sum()/Sxx**2; sb1=np.sqrt(vb1)
print('\n=== WITH INTERCEPT ===')
print(f'  slope = {b1:+.6f} degC/m  (gamma_eff = {-b1*1000:+.3f} K/km)  intercept = {a1:+.4f} degC  HC3 SE slope {sb1:.6f}')
ss_tot=((bias-bias.mean())**2).sum(); r2=1-(e1*e1).sum()/ss_tot
print(f'  R^2 = {r2:.4f}   corr(predicted -5.00*dz/1000 , released bias) = {np.corrcoef(-5.00*dz/1000,bias)[0,1]:.4f}')

# how well does the SIMPLE theorem with the bootstrapped gamma=-5.00 reproduce the substitution bias?
pred=-(-5.00)*dz/1000.0    # = +5.00*dz/1000  (predicted bias from theorem + bootstrap gamma)
resid=bias-pred
print('\n=== THEOREM (gamma=-5.00, no fit) vs SUBSTITUTION bias ===')
print(f'  median |released - predicted| = {np.median(np.abs(resid)):.3f} degC ;  mean = {resid.mean():+.3f} ;  std = {resid.std():.3f}')
print(f'  fraction within 0.25 degC = {(np.abs(resid)<0.25).mean()*100:.1f}% ;  within 0.5 = {(np.abs(resid)<0.5).mean()*100:.1f}%')
print('DONE')
