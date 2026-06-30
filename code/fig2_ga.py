# -*- coding: utf-8 -*-
import os, numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
_REPO=os.path.join(os.path.dirname(__file__),'..'); B=_REPO
OUT=os.path.join(_REPO,'figures')
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'mathtext.default':'regular','pdf.fonttype':42,'ps.fonttype':42})
URB='#C0392B'; RUR='#2563EB'; MATCH='#16A085'
def save(fig,n,dpi=400):
    for e in ('png','pdf','svg'): fig.savefig(os.path.join(OUT,f'{n}.{e}'),dpi=dpi,bbox_inches='tight')
    plt.close(fig)

# ===== Figure 2: mechanism (polished) =====
fig=plt.figure(figsize=(10.4,4.4)); gs=fig.add_gridspec(1,2,width_ratios=[1.1,1.05],wspace=0.24)
ax=fig.add_subplot(gs[0,0]); ax.set_xlim(0,10); ax.set_ylim(0,6.2); ax.axis('off')
# LST-with-elevation colour band (cool up high) behind terrain
grad=np.linspace(0,1,200).reshape(-1,1)
ax.imshow(grad,extent=[0,10,0,6.2],origin='lower',cmap='RdYlBu',alpha=0.20,aspect='auto',zorder=0)
tx=np.linspace(0,10,200); ty=1.2+1.7*(1-np.exp(-((tx-5)**2)/3.2))
ax.add_patch(Polygon(np.c_[np.r_[tx,[10,0]],np.r_[ty,[0,0]]],closed=True,fc='#e9ddc9',ec='#cbb89a',lw=1,zorder=1))
ax.add_patch(Rectangle((4.5,ty[90]),1.0,0.95,fc=URB,ec='k',lw=0.6,zorder=3))
ax.text(5.0,ty[90]+1.2,'urban core\n$z_U$ (low, warm)',ha='center',va='bottom',color=URB,fontsize=8.5)
for xp in (1.4,8.6):
    i=int(xp/10*199); ax.add_patch(Rectangle((xp-0.18,ty[i]),0.36,0.36,fc=RUR,ec='k',lw=0.5,zorder=3))
    ax.text(xp,ty[i]+0.5,'rural ref\n$z_R$ (high, cool)',ha='center',va='bottom',color=RUR,fontsize=8.5)
ax.annotate('',xy=(8.6,ty[int(8.6/10*199)]),xytext=(8.6,ty[90]),arrowprops=dict(arrowstyle='<->',color='#444',lw=1.2))
ax.text(8.95,(ty[int(8.6/10*199)]+ty[90])/2,'Δz',fontsize=11,color='#444')
ax.text(0.15,5.8,'cooler',fontsize=7,color='#3B5BA5'); ax.text(0.15,0.25,'warmer',fontsize=7,color='#C0392B')
ax.set_title('a  Terrain mismatch',loc='left',fontsize=9.5)
# panel b
ax=fig.add_subplot(gs[0,1]); z=np.array([0,1.5]); g=-5.0; L0=31
ax.plot(z,L0+g*z,color='#333',lw=2.3,zorder=2)
ax.text(1.52,L0+g*1.5,'  surface LST\n  ≈ −5 °C/km',va='center',fontsize=8.5,color='#333')
zU,zR=0.25,1.05; LU=L0+g*zU; LR=L0+g*zR; LRm=LU
ax.scatter([zU],[LU],color=URB,s=70,zorder=5,ec='k',lw=0.5); ax.text(zU,LU+0.5,'urban U',color=URB,ha='center',fontsize=8.4)
ax.scatter([zR],[LR],color=RUR,s=70,zorder=5,ec='k',lw=0.5); ax.text(zR+0.04,LR-0.2,'rural ref R\n(conventional)',color=RUR,ha='left',fontsize=7.8)
ax.scatter([zU],[LRm],color=MATCH,s=80,marker='s',zorder=5,ec='k',lw=0.5)
ax.add_patch(FancyArrowPatch((zR,LR),(zU+0.02,LRm),connectionstyle='arc3,rad=0.25',arrowstyle='->',color=MATCH,lw=1.8,zorder=4))
ax.text(0.5,28.0,"match reference\nto urban elevation",color=MATCH,fontsize=9.5,ha='center')
# S and S' brackets
ax.annotate('',xy=(zR+0.06,LR),xytext=(zR+0.06,LU),arrowprops=dict(arrowstyle='<->',color=URB,lw=1.4))
ax.text(zR+0.10,(LR+LU)/2,'S = U−R\n(inflated)',color=URB,va='center',fontsize=7.8)
ax.annotate('',xy=(zU-0.07,LRm),xytext=(zU-0.07,LU),arrowprops=dict(arrowstyle='<->',color=MATCH,lw=1.4))
ax.text(zU-0.12,(LRm+LU)/2,"S' ≈ 0",color=MATCH,va='center',ha='right',fontsize=7.8)
for zz,LL in ((zU,LU),(zR,LR)): ax.plot([zz,zz],[20,LL],color='#e2e2e2',lw=0.8,zorder=0)
ax.set_xlim(-0.18,1.85); ax.set_ylim(22.5,32); ax.set_xlabel('elevation (km)'); ax.set_ylabel('land-surface temperature (°C)')
ax.set_title('b  Reference matching',loc='left',fontsize=9.5)
for s in ('top','right'): ax.spines[s].set_visible(False)
save(fig,'Figure2_mechanism_schematic')
print('Fig2 done')

# ===== Graphical Abstract (wide, Elsevier ~1328x531) =====
d=pd.read_csv(os.path.join(_REPO,'data','per_city_reference_elevation_bias.csv')).dropna(subset=['conventional_SUHI_C','elevation_matched_SUHI_C','reference_elevation_surplus_m','lon','lat'])
d=d[(d['conventional_SUHI_C'].between(-8,15))&(d['elevation_matched_SUHI_C'].between(-8,15))]
def region(lon,lat):
    if 70<=lon<=105 and 26<=lat<=42: return '#D55E00'   # Himalaya-Tibet (vermillion)
    if -82<=lon<=-62 and -56<=lat<=14: return '#E69F00' # Andes (orange)
    if 36<=lon<=62 and 30<=lat<=45: return '#CC79A7'    # Anatolian/Iranian (reddish purple)
    if -125<=lon<=-98 and 15<=lat<=52: return '#0072B2' # N. America (blue)
    return '#999999'
top=d.nlargest(100,'conventional_SUHI_C').copy(); top['c']=[region(a,b) for a,b in zip(top['lon'],top['lat'])]
mc,mm=top['conventional_SUHI_C'].mean(),top['elevation_matched_SUHI_C'].mean()
fig=plt.figure(figsize=(13.3,5.32)); gs=fig.add_gridspec(1,2,width_ratios=[1.0,1.15],wspace=0.05)
fig.suptitle("The world's most intense satellite urban heat islands are largely a reference-elevation artifact",
             x=0.5,y=0.99,fontsize=14,fontweight='bold')
# left: collapse
ax=fig.add_subplot(gs[0,0])
for _,r in top.iterrows(): ax.plot([0,1],[r['conventional_SUHI_C'],r['elevation_matched_SUHI_C']],color=r['c'],lw=0.9,alpha=0.6,zorder=2)
ax.plot([0,1],[mc,mm],color='#111',lw=4,zorder=6,solid_capstyle='round'); ax.scatter([0,1],[mc,mm],color='#111',s=70,zorder=7)
ax.text(0.5,(mc+mm)/2+1.6,f'mean {mc:.1f} → {mm:.1f} °C',ha='center',fontsize=13,fontweight='bold')
ax.set_xlim(-0.22,1.22); ax.set_xticks([0,1]); ax.set_xticklabels(['Conventional\nreference','Elevation-\nmatched'],fontsize=11); ax.set_ylim(-1,13.5)
ax.set_ylabel('SUHI of the 100 most-intense cities (°C)',fontsize=11)
for s in ('top','right'): ax.spines[s].set_visible(False)
hbL=[Line2D([],[],color=c,lw=3,label=l) for c,l in [('#D55E00','Himalaya–Tibet'),('#E69F00','Andes'),('#CC79A7','Anatolian/Iranian'),('#0072B2','N. America'),('#999999','other')]]
lgg=ax.legend(handles=hbL,loc='upper right',frameon=True,framealpha=0.92,fontsize=8.2,title='mountain region',title_fontsize=8.5)
lgg.get_frame().set_edgecolor('#dddddd'); lgg.get_frame().set_linewidth(0.6)
# right: message + numbers
ax=fig.add_subplot(gs[0,1]); ax.axis('off')
ax.text(0.0,0.90,'Of the 100 most-intense SUHIs worldwide:',fontsize=13,fontweight='bold',transform=ax.transAxes)
for i,(big,small) in enumerate([('97 / 100','displaced from the top 100 after correction'),
                                 ('98 %','are high-terrain cities (vs 20.4% baseline)'),
                                 ('ρ = 0.68','conventional vs corrected ranking')]):
    yy=0.74-i*0.20
    ax.text(0.02,yy,big,fontsize=24,fontweight='bold',color='#C0392B',transform=ax.transAxes)
    ax.text(0.34,yy+0.03,small,fontsize=11.5,va='center',transform=ax.transAxes)
ax.text(0.0,0.07,'Dominated by the Himalaya–Tibet, Andes, Iranian and N. American cordillera.\nA within-city correction and a global per-city dataset are released.',
        fontsize=10.5,color='#333',transform=ax.transAxes)
save(fig,'Graphical_Abstract',dpi=220)
print('GA done; px ~',int(13.3*220),'x',int(5.32*220))
