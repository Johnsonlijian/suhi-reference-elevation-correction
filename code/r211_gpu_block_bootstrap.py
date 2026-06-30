# -*- coding: utf-8 -*-
"""
R211  GPU spatial-block bootstrap of the rural reference skin-LST elevation gradient.

Method
------
Headline gradient = within-block (block fixed-effect) regression of LST on elevation,
pooled across blocks:   slope_w = sum_b Sxy_b(w) / sum_b Sxx_b
where for block b, x=elev demeaned within block, y=LST_w demeaned within block,
Sxy_b = sum_i x_i y_i,  Sxx_b = sum_i x_i^2  (Sxx independent of window).

Spatial autocorrelation lives at/below the 50 km block scale, so the resampling unit
is the BLOCK (cluster bootstrap). Because the pooled slope is a ratio of block-additive
sums, a block bootstrap = resample blocks with replacement -> re-sum precomputed
(Sxy_b, Sxx_b). That is a pure gather+sum, done massively in parallel on the GPU.

Reproducibility: deterministic per-window CPU reduction (float64, exact) verified against
the published r173 per-window coefficients; GPU only does the resampling arithmetic.
"""
import os, time
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import numpy as np, pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_CAUSAL = os.environ.get('SUHI_RAW_CAUSAL_DIR')
if not RAW_CAUSAL:
    raise SystemExit('Set SUHI_RAW_CAUSAL_DIR to the local directory containing r173_reference_pixel_lapse_poc/.')
PTS  = os.path.join(RAW_CAUSAL, 'r173_reference_pixel_lapse_poc', 'r173_reference_pixel_lapse_points.csv')
MODELS = os.path.join(REPO, 'data', 'r173_reference_pixel_lapse_models.csv')
OUTDIR = os.path.join(REPO, 'derived', 'r211_gpu_block_bootstrap')
os.makedirs(OUTDIR, exist_ok=True)

WINDOWS = ['jan_day','jan_night','apr_day','apr_night','jul_day','jul_night','oct_day','oct_night']
LSTCOL  = {w: f'lst_{w}_C' for w in WINDOWS}
MIN_PIX_PER_BLOCK = 8
B = 100_000
SEED = 20260628

t0 = time.time()
print('loading', PTS)
df = pd.read_csv(PTS)
print(f'  {len(df):,} pixels, {df.block_id.nunique():,} blocks  ({time.time()-t0:.1f}s)')

# within-block demean of elevation (shared across windows)
df['x'] = df['elev_m'] - df.groupby('block_id')['elev_m'].transform('mean')
nblk = df.groupby('block_id').size().rename('n')
Sxx_b = (df['x']*df['x']).groupby(df['block_id']).sum().rename('Sxx')

# per-window Sxy_b
sxy = {}
for w in WINDOWS:
    y = df[LSTCOL[w]] - df.groupby('block_id')[LSTCOL[w]].transform('mean')
    sxy[w] = (df['x']*y).groupby(df['block_id']).sum().rename(w)

blk = pd.concat([nblk, Sxx_b] + [sxy[w] for w in WINDOWS], axis=1)
blk = blk[(blk['n'] >= MIN_PIX_PER_BLOCK) & (blk['Sxx'] > 0)].copy()
K = len(blk)
print(f'  usable blocks (n>={MIN_PIX_PER_BLOCK}, Sxx>0): {K:,}')

# point estimate per window (km units: elev in m -> *1000)
print('\n=== point estimates vs published r173 ===')
pub = pd.read_csv(MODELS).set_index('key')['coef_degC_per_km'].to_dict()
point = {}
for w in WINDOWS:
    slope_m = blk[w].sum() / blk['Sxx'].sum()      # degC per m
    slope_km = slope_m * 1000.0
    point[w] = slope_km
    p = pub.get(w, np.nan)
    print(f'  {w:10s}: this {slope_km:+.3f}   published {p:+.3f}   d={slope_km-p:+.3f}')

# ---------------- GPU block bootstrap ----------------
import torch
dev = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'\nGPU bootstrap on {dev}: B={B:,}, K={K:,}')
Sxx = torch.tensor(blk['Sxx'].values, dtype=torch.float64, device=dev)            # (K,)
Sxy = torch.tensor(np.stack([blk[w].values for w in WINDOWS]), dtype=torch.float64, device=dev)  # (W,K)
W = len(WINDOWS)
g = torch.Generator(device=dev).manual_seed(SEED)
chunks = []
done = 0; CH = 2000
while done < B:
    b = min(CH, B-done)
    idx = torch.randint(0, K, (b, K), generator=g, device=dev)         # (b,K) resampled blocks
    num = Sxy[:, idx].sum(dim=2)                                        # (W,b)
    den = Sxx[idx].sum(dim=1)                                          # (b,)
    slope_km = (num/den) * 1000.0                                       # (W,b)
    chunks.append(slope_km.to('cpu'))
    done += b
boot = torch.cat(chunks, dim=1).numpy()        # (W, B)  degC/km per window
print(f'  bootstrap done ({time.time()-t0:.1f}s total)')

# aggregate distributions (same resampled blocks across windows -> covariance preserved)
annual = boot.mean(axis=0)                       # (B,)
day    = boot[[0,2,4,6],:].mean(axis=0)
night  = boot[[1,3,5,7],:].mean(axis=0)

def ci(a): return np.percentile(a, [2.5,50,97.5])

rows = []
for i,w in enumerate(WINDOWS):
    lo,md,hi = ci(boot[i]); rows.append((w, point[w], boot[i].mean(), boot[i].std(), lo, hi))
for nm,arr,pe in [('ANNUAL_mean', annual, np.mean([point[w] for w in WINDOWS])),
                  ('DAY_mean', day, np.mean([point[w] for w in WINDOWS if w.endswith('day')])),
                  ('NIGHT_mean', night, np.mean([point[w] for w in WINDOWS if w.endswith('night')]))]:
    lo,md,hi = ci(arr); rows.append((nm, pe, arr.mean(), arr.std(), lo, hi))

res = pd.DataFrame(rows, columns=['window','point_degC_per_km','boot_mean','boot_se','ci2.5','ci97.5'])
res.to_csv(os.path.join(OUTDIR,'r211_gradient_block_bootstrap_ci.csv'), index=False)
print('\n=== block-bootstrap 95% CIs (degC/km) ===')
for _,r in res.iterrows():
    print(f"  {r['window']:12s}  {r['point_degC_per_km']:+.3f}   95% CI [{r['ci2.5']:+.3f}, {r['ci97.5']:+.3f}]   SE {r['boot_se']:.3f}")

# day-minus-night asymmetry distribution (paired)
dmn = day - night
lo,md,hi = ci(dmn)
print(f'\n  DAY - NIGHT steeper-by: {md:+.3f} K/km  95% CI [{lo:+.3f},{hi:+.3f}]  '
      f'(P(day steeper)={(dmn<0).mean()*100:.1f}%)')
pd.DataFrame({'day_minus_night_degC_per_km':dmn}).describe().to_csv(
    os.path.join(OUTDIR,'r211_day_night_asymmetry.csv'))
print('\nsaved ->', OUTDIR)
print('DONE', f'{time.time()-t0:.1f}s')
