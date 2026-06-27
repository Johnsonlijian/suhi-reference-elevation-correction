# -*- coding: utf-8 -*-
import os, numpy as np, pandas as pd, matplotlib as mpl
from pathlib import Path
mpl.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
a=pd.read_csv(RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv',usecols=['label','original_SUHI_warm','elev100_rural50_SUHI_warm','rural_ref_minus_urban_elev_m'])
for c in a.columns:
    if c!='label': a[c]=pd.to_numeric(a[c],errors='coerce')
a=a.dropna(subset=['original_SUHI_warm','elev100_rural50_SUHI_warm'])
a=a[a['original_SUHI_warm'].between(-8,15)&a['elev100_rural50_SUHI_warm'].between(-8,15)].copy()
a['adz']=(a['rural_ref_minus_urban_elev_m'].abs()/1000).clip(0,2); a=a.sort_values('adz')
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'ps.fonttype':42})
fig=plt.figure(figsize=(7.5,4.0)); 
fig.text(0.5,0.95,"The world's most intense surface heat islands are largely a reference-elevation artifact",
         ha='center',fontsize=11.5,fontweight='bold')
ax=fig.add_axes([0.10,0.13,0.55,0.70])
sc=ax.scatter(a['original_SUHI_warm'],a['elev100_rural50_SUHI_warm'],c=a['adz'],cmap='plasma',s=4,lw=0,alpha=0.7)
ax.plot([-6,14],[-6,14],'--',color='#333',lw=1)
top=a.nlargest(100,'original_SUHI_warm')
ax.scatter(top['original_SUHI_warm'],top['elev100_rural50_SUHI_warm'],facecolors='none',edgecolors='#16A085',s=22,lw=0.9)
ax.set_xlim(-6,14); ax.set_ylim(-6,14); ax.set_aspect('equal')
ax.set_xlabel('Conventional SUHI (°C)',fontsize=9); ax.set_ylabel('Elevation-matched SUHI (°C)',fontsize=9)
cb=fig.colorbar(sc,ax=ax,fraction=0.046,pad=0.02,extend='max'); cb.set_label('|elevation mismatch| (km)',fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)
# right callout panel
axr=fig.add_axes([0.71,0.13,0.27,0.70]); axr.axis('off')
axr.text(0.0,0.92,'11,453 cities · MODIS LST',fontsize=8.5,color='#555',transform=axr.transAxes)
axr.barh([2,1],[8.3,2.2],color=['#C0392B','#16A085'],height=0.55)
axr.text(8.3,2,' 8.3 °C',va='center',fontsize=9,color='#C0392B',fontweight='bold')
axr.text(2.2,1,' 2.2 °C',va='center',fontsize=9,color='#16A085',fontweight='bold')
axr.set_xlim(0,11); axr.set_ylim(0.3,2.8)
axr.text(0.0,0.62,'Top-100 "worst SUHI" cities:',transform=axr.transAxes,fontsize=8.5,fontweight='bold')
axr.text(0.0,0.30,'conventional ref',transform=axr.transAxes,fontsize=8,color='#C0392B')
axr.text(0.0,0.18,'elevation-matched ref',transform=axr.transAxes,fontsize=8,color='#16A085')
axr.text(0.0,0.02,'97/100 displaced · 98% terrain\n(vs 20% baseline) · ρ = 0.68',transform=axr.transAxes,fontsize=8,color='#333')
for ext in ('png','pdf','svg'): fig.savefig(os.path.join(OUT,f'Graphical_Abstract.{ext}'),dpi=300,bbox_inches='tight')
plt.close(fig); print('graphical abstract written')
