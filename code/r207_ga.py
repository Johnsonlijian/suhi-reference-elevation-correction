# -*- coding: utf-8 -*-
import numpy as np, pandas as pd, matplotlib as mpl
from pathlib import Path
mpl.use('Agg'); import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
if (HERE / 'per_city_reference_elevation_bias.csv').exists():
    ROOT = HERE
    OUT = ROOT / 'figs'
    DATA = ROOT / 'per_city_reference_elevation_bias.csv'
else:
    ROOT = HERE.parent
    OUT = ROOT / 'figures'
    DATA = ROOT / 'data' / 'per_city_reference_elevation_bias.csv'
OUT.mkdir(exist_ok=True)
a=pd.read_csv(DATA, usecols=['conventional_SUHI_C','elevation_matched_SUHI_C','reference_elevation_surplus_m'])
for c in a.columns:
    a[c]=pd.to_numeric(a[c],errors='coerce')
a=a.dropna(subset=['conventional_SUHI_C','elevation_matched_SUHI_C','reference_elevation_surplus_m'])
a=a[a['conventional_SUHI_C'].between(-8,15)&a['elevation_matched_SUHI_C'].between(-8,15)].copy()
a['adz']=(a['reference_elevation_surplus_m'].abs()/1000).clip(0,2); a=a.sort_values('adz')
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'ps.fonttype':42})
fig=plt.figure(figsize=(7.5,4.0), facecolor='white'); 
fig.text(0.5,0.95,"The world's most intense surface heat islands are largely a reference-elevation artifact",
         ha='center',fontsize=11.5)
ax=fig.add_axes([0.10,0.13,0.55,0.70])
sc=ax.scatter(a['conventional_SUHI_C'],a['elevation_matched_SUHI_C'],c=a['adz'],cmap='plasma',s=4,lw=0,alpha=0.7)
ax.plot([-6,14],[-6,14],'--',color='#333',lw=1)
top=a.nlargest(100,'conventional_SUHI_C')
ax.scatter(top['conventional_SUHI_C'],top['elevation_matched_SUHI_C'],facecolors='none',edgecolors='#16A085',s=22,lw=0.9)
ax.set_xlim(-6,14); ax.set_ylim(-6,14); ax.set_aspect('equal')
ax.set_xlabel('Conventional SUHI (°C)',fontsize=9); ax.set_ylabel('Elevation-matched SUHI (°C)',fontsize=9)
cb=fig.colorbar(sc,ax=ax,fraction=0.046,pad=0.02,extend='max'); cb.set_label('|elevation mismatch| (km)',fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)
# right callout panel
axr=fig.add_axes([0.72,0.13,0.26,0.70]); axr.axis('off')
axr.text(0.0,0.92,'11,453 cities · MODIS LST',fontsize=8.5,color='#555',transform=axr.transAxes)
axr.text(0.0,0.78,'Top-100 conventional ranking',fontsize=8.5,color='#333',transform=axr.transAxes)
stats=[('97 / 100','displaced after correction'),
       ('8.3 → 2.2 °C','mean apparent SUHI'),
       ('98 %','terrain-structured cities')]
ys=[0.60,0.39,0.18]
for (big,small),yy in zip(stats,ys):
    axr.text(0.0,yy,big,fontsize=16,color='#C0392B',transform=axr.transAxes)
    axr.text(0.0,yy-0.09,small,fontsize=8,color='#333',transform=axr.transAxes)
for ext in ('png','pdf','svg'):
    fig.savefig(
        OUT / f'Graphical_Abstract.{ext}',
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
        edgecolor='white',
        transparent=False,
    )
plt.close(fig); print('graphical abstract written')
