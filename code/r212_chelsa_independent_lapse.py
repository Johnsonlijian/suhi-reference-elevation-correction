# -*- coding: utf-8 -*-
"""
R212  Independent cross-validation of the SEB attenuation factor f with CHELSA v2.1.

Idea
----
MODIS gives the OBSERVED rural skin-LST lapse (~ -5 K/km).  The SEB model (Eq.1) says
this is the free-air environmental lapse Gamma_a ATTENUATED by a factor f<1:
    skin_lapse = f * Gamma_a.
CHELSA v2.1 (1 km, ERA5 statistically downscaled with orography) provides an independent,
data-driven estimate of the local free-air 2 m AIR-temperature lapse Gamma_a over the SAME
rural reference blocks -- replacing the textbook -6.5 K/km constant.  Then
    f_observed = skin_lapse / air_lapse        (block-by-block, same pixels)
is a falsifiable, instrument-independent estimate of the attenuation. SEB predicts f~0.77.

Honesty: CHELSA's air-elevation slope is partly imposed by its downscaling lapse model, so
this is NOT an independent measurement of the skin lapse; it is an independent estimate of
Gamma_a (the SEB input) against which the *observed* skin lapse is shown to be attenuated.
MODIS day <-> CHELSA tasmax (warm phase); MODIS night <-> CHELSA tasmin (cool phase).
"""
import os, time
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'
import numpy as np, pandas as pd, rasterio

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_CAUSAL = os.environ.get('SUHI_RAW_CAUSAL_DIR')
CHE = os.environ.get('SUHI_CHELSA_DIR')
if not RAW_CAUSAL:
    raise SystemExit('Set SUHI_RAW_CAUSAL_DIR to the local directory containing r173_reference_pixel_lapse_poc/.')
if not CHE:
    raise SystemExit('Set SUHI_CHELSA_DIR to the local directory containing CHELSA_tasmax_*.tif and CHELSA_tasmin_*.tif.')
PTS  = os.path.join(RAW_CAUSAL,'r173_reference_pixel_lapse_poc','r173_reference_pixel_lapse_points.csv')
OUT  = os.path.join(REPO,'derived','r212_chelsa_independent_lapse'); os.makedirs(OUT, exist_ok=True)

PAIRS = [('jan_day','tasmax_01'),('apr_day','tasmax_04'),('jul_day','tasmax_07'),('oct_day','tasmax_10'),
         ('jan_night','tasmin_01'),('apr_night','tasmin_04'),('jul_night','tasmin_07'),('oct_night','tasmin_10')]
MIN_PIX=8; B=100_000; SEED=20260628

t0=time.time()
df=pd.read_csv(PTS)
print(f'loaded {len(df):,} pixels  ({time.time()-t0:.1f}s)')
lon=df['lon'].values; lat=df['lat'].values

# sample each CHELSA raster at the reference-pixel coordinates (full-band read + fancy index)
def sample(che_key):
    p=os.path.join(CHE, f'CHELSA_{che_key}.tif')
    with rasterio.open(p) as ds:
        inv=~ds.transform
        cols,rows=inv*(lon,lat)
        cols=np.floor(cols).astype(np.int64); rows=np.floor(rows).astype(np.int64)
        ok=(rows>=0)&(rows<ds.height)&(cols>=0)&(cols<ds.width)
        band=ds.read(1)                          # uint16 full band (~1.8 GB)
        raw=np.full(len(lon), 0, dtype=np.uint16)
        raw[ok]=band[rows[ok],cols[ok]]
    val=raw.astype(np.float64)*0.1-273.15
    val[(raw<1500)|(raw>3700)]=np.nan            # ocean/fill + implausible
    return val

for w,che in PAIRS:
    df['air_'+w]=sample(che)
    print(f'  sampled CHELSA {che:9s} -> air_{w:9s} valid {np.isfinite(df["air_"+w]).mean()*100:5.1f}%  ({time.time()-t0:.1f}s)')

# per-block within-FE cross products on COMMON-valid pixels, per window
def block_terms(sub, ycol):
    x=sub['elev_m']-sub.groupby('block_id')['elev_m'].transform('mean')
    y=sub[ycol]-sub.groupby('block_id')[ycol].transform('mean')
    g=sub['block_id']
    Sxx=(x*x).groupby(g).sum(); Sxy=(x*y).groupby(g).sum(); n=g.groupby(g).size()
    return pd.concat([n.rename('n'),Sxx.rename('Sxx'),Sxy.rename('Sxy')],axis=1)

import torch
dev='cuda' if torch.cuda.is_available() else 'cpu'
g=torch.Generator(device=dev).manual_seed(SEED)

rows_out=[]; fboot_store={}
print('\n=== per-window: skin (MODIS) vs air (CHELSA) lapse, and f=skin/air ===')
for w,che in PAIRS:
    sub=df[['block_id','elev_m',f'lst_{w}_C','air_'+w]].dropna()
    bm=block_terms(sub, f'lst_{w}_C').rename(columns={'Sxy':'Sxy_m'})
    ba=block_terms(sub, 'air_'+w)[['Sxy']].rename(columns={'Sxy':'Sxy_a'})
    blk=bm.join(ba); blk=blk[(blk['n']>=MIN_PIX)&(blk['Sxx']>0)]
    K=len(blk)
    skin=blk['Sxy_m'].sum()/blk['Sxx'].sum()*1000
    air =blk['Sxy_a'].sum()/blk['Sxx'].sum()*1000
    f=skin/air
    # joint block bootstrap (same resampled blocks for skin, air, f)
    Sxx=torch.tensor(blk['Sxx'].values,dtype=torch.float64,device=dev)
    Sm =torch.tensor(blk['Sxy_m'].values,dtype=torch.float64,device=dev)
    Sa =torch.tensor(blk['Sxy_a'].values,dtype=torch.float64,device=dev)
    fb=[]; sk=[]; ai=[]; done=0; CH=4000
    while done<B:
        b=min(CH,B-done); idx=torch.randint(0,K,(b,K),generator=g,device=dev)
        dxx=Sxx[idx].sum(1); nm=Sm[idx].sum(1); na=Sa[idx].sum(1)
        sk.append((nm/dxx*1000).cpu().numpy()); ai.append((na/dxx*1000).cpu().numpy()); fb.append((nm/na).cpu().numpy())
        done+=b
    skb=np.concatenate(sk); aib=np.concatenate(ai); fbb=np.concatenate(fb)
    fboot_store[w]=fbb
    rows_out.append((w,che,K,skin,np.percentile(skb,2.5),np.percentile(skb,97.5),
                     air,np.percentile(aib,2.5),np.percentile(aib,97.5),
                     f,np.percentile(fbb,2.5),np.percentile(fbb,97.5)))
    print(f'  {w:10s} skin {skin:+.2f} [{np.percentile(skb,2.5):+.2f},{np.percentile(skb,97.5):+.2f}]  '
          f'air {air:+.2f} [{np.percentile(aib,2.5):+.2f},{np.percentile(aib,97.5):+.2f}]  '
          f'f={f:.3f} [{np.percentile(fbb,2.5):.3f},{np.percentile(fbb,97.5):.3f}]')

res=pd.DataFrame(rows_out,columns=['window','chelsa','n_blocks','skin_lapse','skin_lo','skin_hi',
                                   'air_lapse','air_lo','air_hi','f','f_lo','f_hi'])
res.to_csv(os.path.join(OUT,'r212_chelsa_vs_modis_lapse.csv'),index=False)

# annual / day / night aggregate f (mean over windows, same draws preserved per-window then averaged)
day_f=np.mean([fboot_store[w] for w in ['jan_day','apr_day','jul_day','oct_day']],axis=0)
night_f=np.mean([fboot_store[w] for w in ['jan_night','apr_night','jul_night','oct_night']],axis=0)
ann_f=np.mean([fboot_store[w] for w in fboot_store],axis=0)
print('\n=== aggregate attenuation factor f (independent CHELSA Gamma_a) ===')
for nm,a in [('ANNUAL',ann_f),('DAY',day_f),('NIGHT',night_f)]:
    print(f'  f_{nm:7s} = {a.mean():.3f}  95% CI [{np.percentile(a,2.5):.3f}, {np.percentile(a,97.5):.3f}]')
print(f'\n  SEB-model predicted f = 0.77  (Eq.1, two-conductance)')
pd.DataFrame({'f_annual':ann_f,'f_day':day_f,'f_night':night_f}).to_csv(
    os.path.join(OUT,'r212_f_bootstrap_samples.csv'),index=False)
print('\nsaved ->',OUT); print('DONE',f'{time.time()-t0:.1f}s')
