# -*- coding: utf-8 -*-
import os, numpy as np, pandas as pd, matplotlib as mpl
from pathlib import Path
mpl.use('Agg'); import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
a=pd.read_csv(RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv',
  usecols=['label','original_SUHI_warm','elev100_rural50_SUHI_warm','rural_ref_minus_urban_elev_m'])
for c in a.columns:
    if c!='label': a[c]=pd.to_numeric(a[c],errors='coerce')
a=a.dropna(subset=['original_SUHI_warm','elev100_rural50_SUHI_warm'])
a=a[a['original_SUHI_warm'].between(-8,15)&a['elev100_rural50_SUHI_warm'].between(-8,15)].copy()
a['adz']=(a['rural_ref_minus_urban_elev_m'].abs()/1000).clip(0,2)
a=a.sort_values('adz')  # high-mismatch on top
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42,'ps.fonttype':42})
fig,ax=plt.subplots(figsize=(6.6,6.0))
sc=ax.scatter(a['original_SUHI_warm'],a['elev100_rural50_SUHI_warm'],c=a['adz'],cmap='plasma',s=5,lw=0,alpha=0.7)
lim=[-6,14]; ax.plot(lim,lim,color='#333',lw=1,ls='--',zorder=4,label='1:1 (no change)')
ax.axhline(0,color='#bbb',lw=0.6); ax.axvline(0,color='#bbb',lw=0.6)
# top-100 conventional
top=a.nlargest(100,'original_SUHI_warm')
ax.scatter(top['original_SUHI_warm'],top['elev100_rural50_SUHI_warm'],facecolors='none',edgecolors='#16A085',s=26,lw=0.9,zorder=5,label='100 most-intense (conventional)')
ax.set_xlim(lim); ax.set_ylim(lim); ax.set_aspect('equal')
ax.set_xlabel('Conventional SUHI (°C)'); ax.set_ylabel('Elevation-matched SUHI (°C)')
ax.set_title('The most intense SUHIs collapse after correction',loc='left',fontsize=10)
cb=fig.colorbar(sc,ax=ax,fraction=0.046,pad=0.02,extend='max'); cb.set_label('|reference-elevation surplus| (km)',fontsize=8)
ax.text(0.03,0.95,'Top-100 most-intense: 98% terrain (vs 20% baseline)\nmean 8.3 → 2.2 °C; 97/100 displaced; Spearman ρ = 0.68',
        transform=ax.transAxes,va='top',fontsize=8,bbox=dict(fc='white',ec='#ccc',alpha=0.85,pad=3))
ax.legend(loc='lower right',frameon=False,fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)
for ext in ('png','pdf','svg'): fig.savefig(OUT/f'Figure5_ranking_artifact.{ext}',dpi=300,bbox_inches='tight')
plt.close(fig); print('Fig5 written, n=',len(a))
