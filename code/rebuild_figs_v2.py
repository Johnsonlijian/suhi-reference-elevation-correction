# -*- coding: utf-8 -*-
"""
Comprehensive figure rebuild v2
- Fig 1: hexbin density background for panel (a) instead of gray scatter cloud
- Fig 3: 2-panel redesign — (a) per-city scatter map + (b) CDF by terrain category
- Prints regional statistics for Table 1
"""
import os, numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
import geopandas as gpd

BASE = os.path.join(os.path.dirname(__file__), '..')
REPO_DATA = os.path.join(BASE, 'data')
OUT = os.path.join(BASE, 'figures')

mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.linewidth':0.9,
                     'pdf.fonttype':42,'ps.fonttype':42})

coast = gpd.read_file(os.path.join(REPO_DATA, 'coast.zip'))

d = pd.read_csv(os.path.join(REPO_DATA, 'per_city_reference_elevation_bias.csv')).dropna(
    subset=['lon','lat','reference_elevation_bias_C','conventional_SUHI_C','elevation_matched_SUHI_C'])
d['abs_bias'] = d['reference_elevation_bias_C'].abs()
d['abs_surplus'] = d['reference_elevation_surplus_m'].abs()
d['is_terrain'] = d['abs_surplus'] > 200

def region_clean(lon, lat):
    if 70 <= lon <= 105 and 26 <= lat <= 42: return 'Himalaya–Tibet & Hindu Kush'
    if 60 <= lon < 70 and 36 <= lat <= 45: return 'Pamir–Tianshan'
    if -82 <= lon <= -62 and -56 <= lat <= 14: return 'Andes'
    if -125 <= lon <= -98 and 15 <= lat <= 52: return 'Rockies & Mexican Plateau'
    if 36 <= lon <= 62 and 30 <= lat <= 45: return 'Anatolian & Iranian'
    if 28 <= lon <= 46 and -15 <= lat <= 18: return 'E. African Rift'
    return 'Flatland & other'

d['region'] = [region_clean(a, b) for a, b in zip(d['lon'], d['lat'])]

# ===== REGIONAL STATISTICS (for Table 1) =====
print("=== REGIONAL STATISTICS FOR TABLE 1 ===")
region_order = ['Himalaya–Tibet & Hindu Kush','Andes','Anatolian & Iranian',
                'E. African Rift','Rockies & Mexican Plateau','Pamir–Tianshan']
for reg in region_order:
    sub = d[d['region'] == reg]
    n = len(sub)
    n_t = sub['is_terrain'].sum()
    med = sub['abs_bias'].median()
    p1 = (sub['abs_bias'] > 1).mean() * 100
    msurp = sub['reference_elevation_surplus_m'].mean()
    print(f"  {reg}: n={n}, terrain={n_t} ({n_t/n*100:.0f}%), "
          f"mean_surplus={msurp:.0f}m, median|bias|={med:.2f}C, >1C={p1:.1f}%")

flat = d[~d['is_terrain']]
terr = d[d['is_terrain']]
print(f"  ALL TERRAIN (|surplus|>200m): n={len(terr)}, "
      f"median|bias|={terr['abs_bias'].median():.2f}C, >1C={(terr['abs_bias']>1).mean()*100:.1f}%")
print(f"  FLATLAND (|surplus|<200m): n={len(flat)}, "
      f"median|bias|={flat['abs_bias'].median():.2f}C, >1C={(flat['abs_bias']>1).mean()*100:.1f}%")

# ===== TOP NAMED CITIES =====
print("\n=== TOP TERRAIN CITIES (trust=ok, |bias|>5C) ===")
top_c = d[(d['trust_flag']=='ok') & (d['abs_bias']>5)].sort_values('abs_bias', ascending=False).head(20)
for _, r in top_c.iterrows():
    print(f"  ({r['lon']:.1f}, {r['lat']:.1f}) surplus={r['reference_elevation_surplus_m']:.0f}m "
          f"conv={r['conventional_SUHI_C']:.1f} matched={r['elevation_matched_SUHI_C']:.1f} "
          f"bias={r['reference_elevation_bias_C']:.1f} trust={r['trust_flag']}")

# ===== FIG 1: HEXBIN VERSION =====
d_f = d[(d['conventional_SUHI_C'].between(-8, 15)) & (d['elevation_matched_SUHI_C'].between(-8, 15))].copy()
d_f['region'] = [region_clean(a, b) for a, b in zip(d_f['lon'], d_f['lat'])]
top = d_f.nlargest(100, 'conventional_SUHI_C').copy()
mc, mm = top['conventional_SUHI_C'].mean(), top['elevation_matched_SUHI_C'].mean()
rho = d_f['conventional_SUHI_C'].corr(d_f['elevation_matched_SUHI_C'], method='spearman')
terr_frac = (top['abs_surplus'] > 200).mean() * 100
baseline_frac = (d_f['abs_surplus'] > 200).mean() * 100  # full-sample baseline (≈20.4%)

order = ['Himalaya–Tibet & Hindu Kush','Andes','Anatolian & Iranian',
         'Rockies & Mexican Plateau','Pamir–Tianshan','E. African Rift','Flatland & other']
pal = {'Himalaya–Tibet & Hindu Kush':'#C0392B','Andes':'#E67E22',
       'Anatolian & Iranian':'#8E44AD','Rockies & Mexican Plateau':'#2E86C1',
       'Pamir–Tianshan':'#16A085','E. African Rift':'#D4AC0D','Flatland & other':'#95A5A6'}
top_counts = top['region'].value_counts()
print(f"\nTop-100 region counts: {top_counts.to_dict()}")

fig = plt.figure(figsize=(11.6, 5.3))
gs = fig.add_gridspec(1, 2, width_ratios=[1.18, 1.18], wspace=0.24)

# Panel (a): hexbin density background
ax = fig.add_subplot(gs[0, 0])
lim = [-6, 14]
ax.axhline(0, color='#ececec', lw=0.8, zorder=0)
ax.axvline(0, color='#ececec', lw=0.8, zorder=0)
ax.plot(lim, lim, '--', color='#9aa0a6', lw=1.1, zorder=2, label='1:1 line')

# Hexbin density for all cities
hb = ax.hexbin(d_f['conventional_SUHI_C'], d_f['elevation_matched_SUHI_C'],
               gridsize=60, cmap='Blues', bins='log', extent=lim+lim,
               alpha=0.65, mincnt=1, zorder=1, linewidths=0.2)
cb_hb = fig.colorbar(hb, ax=ax, fraction=0.04, pad=0.01, shrink=0.55)
cb_hb.set_label('log₁₀ city count', fontsize=7)
cb_hb.ax.tick_params(labelsize=6.5)

for rg in order:
    s = top[top['region'] == rg]
    if len(s):
        ax.scatter(s['conventional_SUHI_C'], s['elevation_matched_SUHI_C'],
                   s=34, c=pal[rg], edgecolor='k', lw=0.35, zorder=5,
                   label=f'{rg} ({len(s)})')

ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect('equal')
ax.set_xlabel('Conventional SUHI (°C)')
ax.set_ylabel('Elevation-matched SUHI (°C)')
ax.set_title('a   Conventional versus matched SUHI',
             loc='left', fontsize=10)
ax.text(0.03, 0.97,
        f'97/100 displaced after correction\n'
        f'{terr_frac:.0f}% terrain-structured (vs {baseline_frac:.1f}% baseline)\n'
        f'Spearman ρ = {rho:.2f}',
        transform=ax.transAxes, va='top', fontsize=8,
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec='#d0d0d0', lw=0.8))
ax.text(0.03, 0.03, 'Density of all 11,452 cities (log₁₀ scale)',
        transform=ax.transAxes, fontsize=7.2, color='#4a6fa5',
        bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='none', alpha=0.80))
for s in ('top', 'right'): ax.spines[s].set_visible(False)

# Panel (b): collapse by region (unchanged logic, keep the same)
ax = fig.add_subplot(gs[0, 1])
for rg in order:
    s = top[top['region'] == rg]
    for _, r in s.iterrows():
        ax.plot([0, 1], [r['conventional_SUHI_C'], r['elevation_matched_SUHI_C']],
                color=pal[rg], lw=0.85, alpha=0.58, zorder=2)
ax.plot([0, 1], [mc, mm], color='#111', lw=3.4, zorder=6, solid_capstyle='round')
ax.scatter([0, 1], [mc, mm], color='#111', s=48, zorder=7)
ax.annotate(f'mean {mc:.1f} → {mm:.1f} °C',
            xy=(0.5, (mc+mm)/2), xytext=(0.5, (mc+mm)/2+1.7),
            ha='center', fontsize=9.5,
            arrowprops=dict(arrowstyle='-', color='#111', lw=0.8))
ax.set_xlim(-0.25, 1.25); ax.set_xticks([0, 1])
ax.set_xticklabels(['Conventional\nreference', 'Elevation-\nmatched'])
ax.set_ylim(-1, 13.5)
ax.set_ylabel('SUHI of the 100 most-intense cities (°C)')
ax.set_title('b   Top-100 cities after correction',
             loc='left', fontsize=10)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
present = [rg for rg in order if (top['region'] == rg).any() and rg != 'Flatland & other']
leg = [Line2D([], [], color=pal[rg], lw=2.4, label=f"{rg} ({top_counts.get(rg, 0)})")
       for rg in present]
if (top['region'] == 'Flatland & other').any():
    leg.append(Line2D([], [], color=pal['Flatland & other'], lw=2.4,
                      label=f"Other ({top_counts.get('Flatland & other', 0)})"))
lg = ax.legend(handles=leg, loc='upper right', frameon=True, framealpha=0.92,
               fontsize=7.6, title='mountain region (count)', title_fontsize=8)
lg.get_frame().set_edgecolor('#dddddd'); lg.get_frame().set_linewidth(0.6)

for ext in ('png', 'pdf', 'svg'):
    fig.savefig(os.path.join(OUT, f'Figure1_ranking_artifact.{ext}'), dpi=400, bbox_inches='tight')
plt.close()
print('\nFig1 rebuilt with hexbin background')

# ===== FIG 3: CITY SCATTER MAP + BIAS CDF =====
fig, (ax_map, ax_cdf) = plt.subplots(1, 2, figsize=(12.4, 4.6),
                                      gridspec_kw={'width_ratios': [2.3, 1.0], 'wspace': 0.06})

# Panel (a): per-city scatter on world map
ax_map.set_facecolor('#f2f4f7')
coast.plot(ax=ax_map, linewidth=0.4, color='#8a949e', zorder=1)

# Sort by abs_bias so high-bias cities are drawn on top
d_sorted = d.sort_values('abs_bias')

# Use a clipped colormap: white (0) -> pale yellow -> orange -> dark red
cmap_bias = plt.cm.YlOrRd
norm_bias = mcolors.Normalize(vmin=0, vmax=3.0)

# Low-bias cities: small, pale
lo = d_sorted[d_sorted['abs_bias'] < 0.5]
ax_map.scatter(lo['lon'], lo['lat'], s=1.2, c='#d4d8dc', alpha=0.35, lw=0, zorder=2, rasterized=True)

# High-bias cities: colored, slightly larger
hi = d_sorted[d_sorted['abs_bias'] >= 0.5]
sc = ax_map.scatter(hi['lon'], hi['lat'],
                    c=hi['abs_bias'], cmap=cmap_bias, norm=norm_bias,
                    s=np.clip(hi['abs_bias'] * 2.5, 2.5, 14),
                    alpha=0.78, lw=0, zorder=3, rasterized=True)

# Colorbar
cb = fig.colorbar(sc, ax=ax_map, fraction=0.022, pad=0.01, extend='max',
                  shrink=0.72, anchor=(0.0, 0.4))
cb.set_label('|reference-elevation\nbias| (°C)', fontsize=7.5)
cb.ax.tick_params(labelsize=7)

# Mountain region labels
annotations = [
    ('Andes', -67, -20), ('Mexican\nPlateau', -103, 23), ('Rockies', -113, 45),
    ('E. African\nRift', 37, 1), ('Anatolian /\nIranian', 55, 36),
    ('Himalaya–Tibet\n& Hindu Kush', 85, 32),
]
for name, x, y in annotations:
    ax_map.annotate(name, (x, y), fontsize=6.2, color='#111', ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.82),
                    zorder=6)

ax_map.set_xlim(-170, 180); ax_map.set_ylim(-57, 80)
ax_map.set_xticks([]); ax_map.set_yticks([])
for s in ax_map.spines.values(): s.set_visible(False)
ax_map.set_title('a   Global distribution of |reference-elevation bias|',
                 loc='left', fontsize=9.5)
ax_map.text(0.01, 0.06, f'|bias| > 1°C in 47.4% of cities',
            transform=ax_map.transAxes, fontsize=7.8, color='#222',
            bbox=dict(boxstyle='round,pad=0.22', fc='white', ec='none', alpha=0.8), zorder=7)

# Panel (b): CDF of |bias| by terrain category
cats = [
    ('Flatland (|surplus| < 200 m)', ~d['is_terrain'], '#2563EB'),
    ('Moderate terrain\n(200–500 m)', (d['abs_surplus'] >= 200) & (d['abs_surplus'] < 500), '#F59E0B'),
    ('High terrain (> 500 m)', d['abs_surplus'] >= 500, '#C0392B'),
]
for label, mask, col in cats:
    sub = d.loc[mask, 'abs_bias'].values
    xs = np.sort(sub)
    ys = np.arange(1, len(xs)+1) / len(xs)
    ax_cdf.plot(xs, ys, color=col, lw=2.0, label=f'{label}\n(n = {len(sub):,})')

ax_cdf.axvline(1.0, color='#666', lw=0.9, ls='--', zorder=0)
ax_cdf.text(1.04, 0.12, '1°C', fontsize=7.5, color='#555')
ax_cdf.set_xlim(0, 5.5); ax_cdf.set_ylim(0, 1.03)
ax_cdf.set_xlabel('|reference-elevation bias| (°C)', fontsize=8.5)
ax_cdf.set_ylabel('Cumulative fraction of cities', fontsize=8.5)
ax_cdf.set_title('b   Bias by terrain class', loc='left',
                 fontsize=9.5)
ax_cdf.legend(fontsize=6.8, loc='lower right', frameon=True, framealpha=0.92,
              edgecolor='#ddd', handlelength=1.4)
for s in ('top', 'right'): ax_cdf.spines[s].set_visible(False)

for ext in ('png', 'pdf', 'svg'):
    dpi = 500 if ext == 'png' else None
    fig.savefig(os.path.join(OUT, f'Figure3_global_bias_map.{ext}'),
                dpi=dpi, bbox_inches='tight')
plt.close()
print('Fig3 rebuilt: city scatter map + CDF')
print('DONE')
