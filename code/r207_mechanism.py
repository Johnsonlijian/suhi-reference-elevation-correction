# -*- coding: utf-8 -*-
import os, numpy as np, matplotlib as mpl
from pathlib import Path
mpl.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'mathtext.default':'regular','pdf.fonttype':42,'ps.fonttype':42})
URB='#C0392B'; RUR='#2563EB'; MATCH='#16A085'
fig=plt.figure(figsize=(10.2,4.3)); gs=fig.add_gridspec(1,2,width_ratios=[1.15,1.0],wspace=0.26)
# (a) terrain cross-section
ax=fig.add_subplot(gs[0,0]); ax.set_xlim(0,10); ax.set_ylim(0,6); ax.axis('off')
tx=np.linspace(0,10,200); ty=1.2+1.6*(1-np.exp(-((tx-5)**2)/3.0))
ax.add_patch(Polygon(np.c_[np.r_[tx,[10,0]],np.r_[ty,[0,0]]],closed=True,fc='#efe6d8',ec='#cbb89a',lw=1,zorder=1))
ax.add_patch(Rectangle((4.5,ty[90]),1.0,0.9,fc=URB,ec='k',lw=0.6,zorder=3))
ax.text(5.0,ty[90]+1.15,'urban core\nz_U (low, warm)',ha='center',va='bottom',color=URB,fontsize=8.5,fontweight='bold')
for xp in (1.4,8.6):
    i=int(xp/10*199); ax.add_patch(Rectangle((xp-0.18,ty[i]),0.36,0.36,fc=RUR,ec='k',lw=0.5,zorder=3))
    ax.text(xp,ty[i]+0.55,'rural ref\nz_R (high, cool)',ha='center',va='bottom',color=RUR,fontsize=8)
ax.annotate('',xy=(8.6,ty[int(8.6/10*199)]),xytext=(8.6,ty[90]),arrowprops=dict(arrowstyle='<->',color='#555',lw=1.2))
ax.text(8.95,(ty[int(8.6/10*199)]+ty[90])/2,'Δz',fontsize=11,color='#555')
ax.set_title('a  In terrain, the rural reference sits above the urban core',loc='left',fontweight='bold',fontsize=9.5)
# (b) LST vs elevation
ax=fig.add_subplot(gs[0,1]); z=np.array([0,1.5]); g=-5.0; L0=31
ax.plot(z,L0+g*z,color='#333',lw=2.2,zorder=2)
ax.text(1.52,L0+g*1.5,'  surface LST\n  ≈ −5 °C/km',va='center',fontsize=8,color='#333')
zU,zR=0.25,1.05; LU=L0+g*zU; LR=L0+g*zR; LRm=LU
ax.scatter([zU],[LU],color=URB,s=70,zorder=5,ec='k',lw=0.5); ax.text(zU,LU+0.6,'urban U',color=URB,ha='center',fontsize=8.5,fontweight='bold')
ax.scatter([zR],[LR],color=RUR,s=70,zorder=5,ec='k',lw=0.5); ax.text(zR,LR-1.05,'rural ref R\n(conventional)',color=RUR,ha='center',fontsize=8)
ax.scatter([zU],[LRm],color=MATCH,s=70,marker='s',zorder=5,ec='k',lw=0.5); ax.text(zU-0.02,LRm-1.45,"elevation-\nmatched R'",color=MATCH,ha='center',fontsize=8)
ax.annotate('',xy=(zR+0.05,LR),xytext=(zR+0.05,LU),arrowprops=dict(arrowstyle='<->',color=URB,lw=1.4))
ax.text(zR+0.10,(LR+LU)/2,'bias\n= −γ·Δz',color=URB,va='center',fontsize=8.5)
for zz,LL in ((zU,LU),(zR,LR)): ax.plot([zz,zz],[20,LL],color='#ddd',lw=0.8,zorder=0)
ax.set_xlim(0,1.85); ax.set_ylim(22,32); ax.set_xlabel('elevation (km)'); ax.set_ylabel('land-surface temperature (°C)')
ax.set_title('b  Elevation-mismatched reference biases SUHI = U − R',loc='left',fontweight='bold',fontsize=9.5)
for s in ('top','right'): ax.spines[s].set_visible(False)
ax.text(0.02,0.04,'Conventional S = U − R is inflated by −γ·Δz;\nmatching the reference to z_U removes it.',transform=ax.transAxes,fontsize=7.5,color='#444')
for ext in ('png','pdf','svg'): fig.savefig(os.path.join(OUT,f'Figure0_mechanism_schematic.{ext}'),dpi=300,bbox_inches='tight')
plt.close(fig); print('mechanism schematic OK ->',OUT)
