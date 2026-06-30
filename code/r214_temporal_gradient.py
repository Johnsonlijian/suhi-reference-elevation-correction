# -*- coding: utf-8 -*-
"""
R214  Temporal robustness of the rural skin-LST elevation gradient (the mechanism),
      and an honest bound on reference-elevation TREND contamination.

Data: data/lst/YYYYMM.tif = MODIS MOD11 monthly LST, native Sinusoidal 926 m, uint16
      (DN*0.02 - 273.15 = degC), nodata 65535. 3 years x 4 months: 2008/2015/2018 x 01,04,07,10.
      (Single daytime band; matches r169 'mmlst_*_mean4', SUHI Gamma ~ -5.0.)

Method: sample each raster at the SAME 421,936 r173 rural-reference pixels (lon/lat ->
      sinusoidal once; the 12 rasters share one grid so col/row compute ONCE), 4-month-mean
      per year, then the within-block fixed-effect LST-elevation gradient pooled across blocks
      (identical estimator to r211). GPU block-bootstrap (50 km block = resampling unit, B=1e5)
      gives each year's CI and the PAIRED 2018-2008 change (same resampled blocks -> covariance
      preserved). If the gradient is stable across the decade, the bias is a stable LEVEL offset
      that does not materially contaminate decadal SUHI trends (honest, bounded claim).
"""
import os, time
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import numpy as np, pandas as pd, rasterio
from pyproj import Transformer

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_CAUSAL = os.environ.get('SUHI_RAW_CAUSAL_DIR')
LST  = os.environ.get('SUHI_MODIS_LST_DIR')
if not RAW_CAUSAL:
    raise SystemExit('Set SUHI_RAW_CAUSAL_DIR to the local directory containing r173_reference_pixel_lapse_poc/.')
if not LST:
    raise SystemExit('Set SUHI_MODIS_LST_DIR to the local directory containing monthly MODIS LST rasters such as 200801.tif.')
PTS  = os.path.join(RAW_CAUSAL,'r173_reference_pixel_lapse_poc','r173_reference_pixel_lapse_points.csv')
OUT  = os.path.join(REPO,'derived','r214_temporal_gradient'); os.makedirs(OUT, exist_ok=True)

YEARS=[2008,2015,2018]; MONTHS=['01','04','07','10']
MIN_PIX=8; B=100_000; SEED=20260628

t0=time.time()
df=pd.read_csv(PTS)
print(f'loaded {len(df):,} pixels  ({time.time()-t0:.1f}s)')
lon=df['lon'].values; lat=df['lat'].values

# lon/lat -> MODIS sinusoidal, col/row via shared inverse affine (compute ONCE)
with rasterio.open(os.path.join(LST,'200801.tif')) as ds0:
    tr=Transformer.from_crs('EPSG:4326', ds0.crs, always_xy=True)
    xs,ys=tr.transform(lon,lat)
    inv=~ds0.transform
    cols,rows=inv*(np.array(xs),np.array(ys))
    cols=np.floor(cols).astype(np.int64); rows=np.floor(rows).astype(np.int64)
    H,W=ds0.height,ds0.width
ok0=(rows>=0)&(rows<H)&(cols>=0)&(cols<W)
print(f'  projected; {ok0.mean()*100:.1f}% of pixels in-grid  ({time.time()-t0:.1f}s)')

def sample(path):
    with rasterio.open(path) as ds:
        band=ds.read(1)                       # uint16 full band (~1.9 GB)
    raw=np.full(len(lon),65535,dtype=np.uint16)
    raw[ok0]=band[rows[ok0],cols[ok0]]
    val=raw.astype(np.float64)*0.02-273.15
    val[(raw==65535)|(raw<7500)|(raw>17000)]=np.nan   # nodata + implausible LST
    return val

# 4-month mean per year (mean of available months, require >=3 valid)
for yr in YEARS:
    acc=np.zeros(len(lon)); cnt=np.zeros(len(lon))
    for m in MONTHS:
        v=sample(os.path.join(LST,f'{yr}{m}.tif'))
        ok=np.isfinite(v); acc[ok]+=v[ok]; cnt[ok]+=1
        print(f'  {yr}{m} valid {ok.mean()*100:5.1f}%  ({time.time()-t0:.1f}s)')
    ly=np.where(cnt>=3, acc/np.maximum(cnt,1), np.nan)
    df[f'lst_{yr}']=ly
    print(f'  -> lst_{yr} mean4 valid {np.isfinite(ly).mean()*100:5.1f}%')

# within-block FE cross-products per year, on common-valid pixels
def block_terms(sub, ycol):
    x=sub['elev_m']-sub.groupby('block_id')['elev_m'].transform('mean')
    y=sub[ycol]-sub.groupby('block_id')[ycol].transform('mean')
    g=sub['block_id']
    Sxx=(x*x).groupby(g).sum(); Sxy=(x*y).groupby(g).sum(); n=g.groupby(g).size()
    return pd.concat([n.rename('n'),Sxx.rename('Sxx'),Sxy.rename('Sxy')],axis=1)

import torch
dev='cuda' if torch.cuda.is_available() else 'cpu'
gen=torch.Generator(device=dev).manual_seed(SEED)
print(f'\nGPU block bootstrap on {dev}: B={B:,}')

# common block set across the 3 years (paired bootstrap needs identical blocks)
sub=df[['block_id','elev_m','lst_2008','lst_2015','lst_2018']].dropna()
terms={yr:block_terms(sub,f'lst_{yr}') for yr in YEARS}
common=set.intersection(*[set(terms[yr].index[(terms[yr]['n']>=MIN_PIX)&(terms[yr]['Sxx']>0)]) for yr in YEARS])
common=sorted(common); K=len(common)
print(f'  common usable blocks across 3 years: {K:,}')

Sxx=torch.tensor(terms[2008].loc[common,'Sxx'].values,dtype=torch.float64,device=dev)
Sxy={yr:torch.tensor(terms[yr].loc[common,'Sxy'].values,dtype=torch.float64,device=dev) for yr in YEARS}
point={yr: float(terms[yr].loc[common,'Sxy'].sum()/terms[yr].loc[common,'Sxx'].sum()*1000) for yr in YEARS}

boot={yr:[] for yr in YEARS}; done=0; CH=3000
while done<B:
    b=min(CH,B-done); idx=torch.randint(0,K,(b,K),generator=gen,device=dev)
    den=Sxx[idx].sum(1)
    for yr in YEARS:
        boot[yr].append(((Sxy[yr][idx].sum(1))/den*1000).cpu().numpy())
    done+=b
boot={yr:np.concatenate(v) for yr,v in boot.items()}

def ci(a): return (a.mean(), np.percentile(a,2.5), np.percentile(a,97.5))
print('\n=== per-year within-block daytime gradient (mmlst 4-month mean) ===')
rows_out=[]
for yr in YEARS:
    m,lo,hi=ci(boot[yr]); rows_out.append((yr,point[yr],m,lo,hi))
    print(f'  {yr}: {point[yr]:+.3f}  boot {m:+.3f}  95% CI [{lo:+.3f},{hi:+.3f}]')
d=boot[2018]-boot[2008]; dm,dlo,dhi=ci(d)
frac_pos=(d>0).mean()
print(f'\n  2018 - 2008 change: {dm:+.3f} K/km  95% CI [{dlo:+.3f},{dhi:+.3f}]  P(|>0)={max(frac_pos,1-frac_pos)*100:.1f}%')
print(f'  => gradient {"STABLE" if dlo<0<dhi else "CHANGED"} across the decade (CI {"includes" if dlo<0<dhi else "excludes"} 0)')

pd.DataFrame(rows_out,columns=['year','point','boot_mean','ci2.5','ci97.5']).to_csv(
    os.path.join(OUT,'r214_temporal_gradient_ci.csv'),index=False)
pd.DataFrame({'delta_2018_2008':d}).describe().to_csv(os.path.join(OUT,'r214_delta_summary.csv'))
print('\nsaved ->',OUT); print('DONE',f'{time.time()-t0:.1f}s')
