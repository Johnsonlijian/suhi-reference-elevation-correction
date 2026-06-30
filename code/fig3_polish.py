# -*- coding: utf-8 -*-
"""
Fig 3 polish + terrain stats for Table 1
"""
import os, numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd

BASE = os.path.join(os.path.dirname(__file__), '..')
REPO_DATA = os.path.join(BASE, 'data')
OUT = os.path.join(BASE, 'figures')
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.linewidth':0.9,
                     'pdf.fonttype':42,'ps.fonttype':42})

coast = gpd.read_file(os.path.join(REPO_DATA, 'coast.zip'))
d = pd.read_csv(os.path.join(REPO_DATA, 'per_city_reference_elevation_bias.csv')).dropna(
    subset=['lon','lat','reference_elevation_bias_C'])
d['abs_bias'] = d['reference_elevation_bias_C'].abs()
d['abs_surplus'] = d['reference_elevation_surplus_m'].abs()

# ===== TERRAIN STATS FOR TABLE 1 =====
print("=== TERRAIN-STRATIFIED STATS (for Table 1) ===")
bins = [(0, 100), (100, 200), (200, 500), (500, 5000)]
labels = ['|surplus| < 100 m', '100–200 m', '200–500 m', '> 500 m']
for (lo, hi), lbl in zip(bins, labels):
    sub = d[(d['abs_surplus'] >= lo) & (d['abs_surplus'] < hi)]
    n = len(sub)
    med = sub['abs_bias'].median()
    p1 = (sub['abs_bias'] > 1).mean() * 100
    p2 = (sub['abs_bias'] > 2).mean() * 100
    print(f"  {lbl}: n={n}, median|bias|={med:.2f}C, >1C={p1:.1f}%, >2C={p2:.1f}%")

# Headline stats for caption
print("\n=== HEADLINE NUMBERS ===")
terrain = d[d['abs_surplus'] > 200]
flatland = d[d['abs_surplus'] <= 200]
print(f"  Terrain n={len(terrain)}, median={terrain['abs_bias'].median():.2f}C")
print(f"  Flatland n={len(flatland)}, median={flatland['abs_bias'].median():.2f}C")
print(f"  Terrain/Total = {len(terrain)/len(d)*100:.1f}%")

# CDF values at key thresholds for text
for thresh in [0.5, 1.0, 2.0, 3.0]:
    all_frac = (d['abs_bias'] > thresh).mean() * 100
    t_frac = (terrain['abs_bias'] > thresh).mean() * 100
    f_frac = (flatland['abs_bias'] > thresh).mean() * 100
    print(f"  |bias|>{thresh}C: all={all_frac:.1f}%, terrain={t_frac:.1f}%, flatland={f_frac:.1f}%")

# Top named cities
print("\n=== NAMED CITIES FOR PAPER TEXT ===")
named = {
    # (lon_approx, lat_approx): name
    (74.3, 35.9): 'Gilgit, Pakistan',
    (71.8, 35.8): 'Chitral, Pakistan',
    (-73.1, 7.0): 'Bucaramanga, Colombia',
    (-76.3, 3.5): 'Popayan, Colombia',
    (51.3, 35.7): 'Tehran, Iran',
    (11.3, 46.5): 'Bolzano, Italy',
    (-70.7, -33.5): 'Santiago, Chile',
    (29.0, -2.9): 'S. Kivu highlands, DRC',  # GHS centre at this coord is NOT Bukavu proper
}
top_ok = d[(d['trust_flag']=='ok') & (d['abs_bias'] > 5)].sort_values('abs_bias', ascending=False)
for _, r in top_ok.head(20).iterrows():
    # match to named dict
    city = None
    for (ln, lt), nm in named.items():
        if abs(r['lon']-ln)<0.5 and abs(r['lat']-lt)<0.5:
            city = nm; break
    if city:
        print(f"  {city}: surplus={r['reference_elevation_surplus_m']:.0f}m, "
              f"conv={r['conventional_SUHI_C']:.1f}->matched={r['elevation_matched_SUHI_C']:.1f}C, "
              f"bias={r['reference_elevation_bias_C']:.1f}C")

# ===== REVISED FIG 3: better layout =====
fig = plt.figure(figsize=(12.8, 4.8))
# Use gridspec with proper spacing
gs = fig.add_gridspec(1, 2, width_ratios=[2.5, 1.0], wspace=0.10,
                      left=0.01, right=0.98, top=0.92, bottom=0.06)

# ---- Panel (a): per-city scatter map ----
ax_map = fig.add_subplot(gs[0, 0])
ax_map.set_facecolor('#f0f2f5')
coast.plot(ax=ax_map, linewidth=0.4, color='#888e96', zorder=1)

d_lo = d[d['abs_bias'] < 0.5].sort_values('abs_bias')
d_hi = d[d['abs_bias'] >= 0.5].sort_values('abs_bias')

ax_map.scatter(d_lo['lon'], d_lo['lat'], s=1.0, c='#cdd0d5', alpha=0.3, lw=0, zorder=2, rasterized=True)

cmap_bias = plt.cm.YlOrRd
norm_bias = mcolors.Normalize(vmin=0.5, vmax=3.0)
sc = ax_map.scatter(d_hi['lon'], d_hi['lat'],
                    c=d_hi['abs_bias'], cmap=cmap_bias, norm=norm_bias,
                    s=np.clip(d_hi['abs_bias'] * 2.8, 2.0, 13.0),
                    alpha=0.80, lw=0, zorder=3, rasterized=True)

ax_map.set_xlim(-170, 180); ax_map.set_ylim(-57, 80)
ax_map.set_xticks([]); ax_map.set_yticks([])
for s in ax_map.spines.values(): s.set_visible(False)

# Colorbar placed BELOW the map
cax = ax_map.inset_axes([0.01, -0.045, 0.30, 0.035])
cb = fig.colorbar(sc, cax=cax, orientation='horizontal', extend='max')
cb.set_label('|reference-elevation bias| (°C)', fontsize=8.5, labelpad=2)
cb.ax.tick_params(labelsize=8.0)
cb.set_ticks([0.5, 1, 2, 3])
cb.ax.set_xticklabels(['0.5', '1', '2', '≥3'])

# Mountain region labels — repositioned to avoid crowding
annots = [
    ('Andes',       -66, -20, 'center'),
    ('Mexican\nPlateau', -103, 23, 'center'),
    ('Rockies',     -115, 47, 'center'),
    ('E. African\nRift', 38,  2,  'center'),
    ('Anatolian &\nIranian',  55,  38, 'center'),
    ('Himalaya–Tibet\n& Hindu Kush', 88, 31, 'center'),
]
for name, x, y, ha in annots:
    ax_map.annotate(name, (x, y), fontsize=8.5, color='#111', ha=ha, va='center',
                    bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='#bbb', alpha=0.93, lw=0.6),
                    zorder=6)

ax_map.set_title('a   Global distribution of |reference-elevation bias|',
                 loc='left', fontsize=9.5, pad=4)
ax_map.text(0.008, 0.06, '|bias| > 1°C in 47.4% of cities  |  median 0.92°C (all 11,452)',
            transform=ax_map.transAxes, fontsize=8.0, color='#222',
            bbox=dict(boxstyle='round,pad=0.22', fc='white', ec='none', alpha=0.82), zorder=7)

# ---- Panel (b): CDF ----
ax_cdf = fig.add_subplot(gs[0, 1])
cats = [
    ('Flatland\n(|surplus| ≤ 200 m)',   d['abs_surplus'] <= 200,  '#2563EB'),
    ('Moderate terrain\n(200–500 m)',  (d['abs_surplus'] > 200) & (d['abs_surplus'] <= 500), '#F59E0B'),
    ('High terrain\n(> 500 m)',         d['abs_surplus'] > 500,   '#C0392B'),
]
for label, mask, col in cats:
    sub = d.loc[mask, 'abs_bias'].dropna().values
    xs = np.sort(sub); ys = np.arange(1, len(xs)+1) / len(xs)
    n = len(sub)
    ax_cdf.plot(xs, ys, color=col, lw=2.0, label=f'{label} (n = {n:,})')

ax_cdf.axvline(1.0, color='#777', lw=0.9, ls='--', zorder=0)
ax_cdf.text(1.08, 0.10, '1°C', fontsize=7.5, color='#666')
ax_cdf.set_xlim(0, 5.5); ax_cdf.set_ylim(0, 1.03)
ax_cdf.set_xlabel('|reference-elevation bias| (°C)', fontsize=8.5)
ax_cdf.set_ylabel('Cumulative fraction of cities', fontsize=8.5)
ax_cdf.set_title('b   Bias by terrain class',
                 loc='left', fontsize=9.5)
ax_cdf.legend(fontsize=8.0, loc='lower right', frameon=True, framealpha=0.93,
              edgecolor='#ddd', handlelength=1.5, labelspacing=0.5)
for s in ('top', 'right'): ax_cdf.spines[s].set_visible(False)
ax_cdf.tick_params(labelsize=8)

for ext in ('png', 'pdf', 'svg'):
    fig.savefig(os.path.join(OUT, f'Figure3_global_bias_map.{ext}'),
                dpi=(500 if ext == 'png' else None), bbox_inches='tight')
plt.close()
print('\nFig3 polished and saved.')
print('DONE')
