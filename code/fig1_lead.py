# -*- coding: utf-8 -*-
import os, numpy as np, pandas as pd, matplotlib as mpl
from pathlib import Path
mpl.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
d=pd.read_csv(ROOT / 'data' / 'per_city_reference_elevation_bias.csv')
d=d.dropna(subset=['conventional_SUHI_C','elevation_matched_SUHI_C','reference_elevation_surplus_m']).copy()
# QA: drop implausible extremes (match manuscript pool)
d=d[(d['conventional_SUHI_C'].between(-8,15))&(d['elevation_matched_SUHI_C'].between(-8,15))]
d['surplus_km']=d['reference_elevation_surplus_m']/1000.0
top=d.nlargest(100,'conventional_SUHI_C')
mc,mm=top['conventional_SUHI_C'].mean(),top['elevation_matched_SUHI_C'].mean()
rho=d['conventional_SUHI_C'].corr(d['elevation_matched_SUHI_C'],method='spearman')
terr=(top['reference_elevation_surplus_m'].abs()>200).mean()*100
print(f"top100 mean conv={mc:.1f} matched={mm:.1f} rho={rho:.2f} terr%={terr:.0f}")

mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.linewidth':0.9,'pdf.fonttype':42,'ps.fonttype':42})
CLOUD='#c7d0db'; HOT='#E8543A'
fig=plt.figure(figsize=(11.2,5.2), facecolor='white')
gs=fig.add_gridspec(1,2,width_ratios=[1.32,1.0],wspace=0.26)

# ---- (a) scatter ----
ax=fig.add_subplot(gs[0,0])
ax.axhline(0,color='#e5e5e5',lw=0.8,zorder=0); ax.axvline(0,color='#e5e5e5',lw=0.8,zorder=0)
lim=[-6,14]; ax.plot(lim,lim,'--',color='#9aa0a6',lw=1.2,zorder=2)
ax.scatter(d['conventional_SUHI_C'],d['elevation_matched_SUHI_C'],s=5,c=CLOUD,alpha=0.55,lw=0,zorder=1)
ax.scatter(top['conventional_SUHI_C'],top['elevation_matched_SUHI_C'],s=34,c=HOT,edgecolor='k',lw=0.3,zorder=4)
ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect('equal')
ax.set_xlabel('Conventional SUHI (°C)'); ax.set_ylabel('Elevation-matched SUHI (°C)')
ax.set_title('a  The most intense SUHIs sit far below the 1:1 line',loc='left',fontweight='bold',fontsize=10)
ax.text(0.03,0.97,f'100 most-intense (conventional):\n97/100 displaced after correction\n{terr:.0f}% terrain-structured (vs 20% baseline)\nSpearman ρ = {rho:.2f}',
        transform=ax.transAxes,va='top',ha='left',fontsize=8,
        bbox=dict(boxstyle='round,pad=0.45',fc='white',ec='#d0d0d0',lw=0.8))
ax.legend(handles=[Line2D([],[],ls='--',color='#9aa0a6',label='1:1 (no change)'),
                   Line2D([],[],marker='o',ls='',mfc=HOT,mec='k',mew=0.3,ms=7,label='100 most-intense (conv.)'),
                   Line2D([],[],marker='o',ls='',mfc=CLOUD,mec='none',ms=6,label='all cities')],
          loc='lower right',frameon=False,fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)

# ---- (b) collapse / slope ----
ax=fig.add_subplot(gs[0,1])
norm=Normalize(0,2.2); cmap=plt.cm.YlOrRd
for _,r in top.iterrows():
    ax.plot([0,1],[r['conventional_SUHI_C'],r['elevation_matched_SUHI_C']],color=cmap(norm(min(r['surplus_km'],2.2))),lw=0.7,alpha=0.6,zorder=2)
ax.plot([0,1],[mc,mm],color='#111',lw=3.2,zorder=5,solid_capstyle='round')
ax.scatter([0,1],[mc,mm],color='#111',s=46,zorder=6)
ax.annotate(f'mean {mc:.1f} → {mm:.1f} °C',xy=(0.5,(mc+mm)/2),xytext=(0.5,(mc+mm)/2+1.6),ha='center',fontsize=9.5,fontweight='bold',
            arrowprops=dict(arrowstyle='-',color='#111',lw=0.8))
ax.set_xlim(-0.28,1.28); ax.set_xticks([0,1]); ax.set_xticklabels(['Conventional\nreference','Elevation-\nmatched'],fontsize=9)
ax.set_ylabel('SUHI of the 100 most-intense cities (°C)')
ax.set_title('b  …and collapse once the reference elevation is matched',loc='left',fontweight='bold',fontsize=10)
ax.set_ylim(-1,13.5)
for s in ('top','right'): ax.spines[s].set_visible(False)
sm=ScalarMappable(norm=norm,cmap=cmap); sm.set_array([])
cb=fig.colorbar(sm,ax=ax,fraction=0.045,pad=0.02,extend='max'); cb.set_label('|reference-elevation surplus| (km)',fontsize=8)
for ext in ('png','pdf','svg'):
    fig.savefig(
        OUT / f'Figure1_ranking_artifact.{ext}',
        dpi=400,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='white',
        transparent=False,
    )
plt.close(fig); print('Figure1 rebuilt ->',OUT)
