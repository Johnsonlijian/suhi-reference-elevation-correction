# -*- coding: utf-8 -*-
import os, numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
_REPO=os.path.join(os.path.dirname(__file__),'..'); B=_REPO
OUT=os.path.join(_REPO,'figures')
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.linewidth':0.9,'pdf.fonttype':42,'ps.fonttype':42})
def save(fig,n):
    for e in ('png','pdf','svg'): fig.savefig(os.path.join(OUT,f'{n}.{e}'),dpi=400,bbox_inches='tight')
    plt.close(fig)

# ===== Figure 4: forest (no 'b' label; corrected zone) =====
rows=[('conventional (original)',0.499,0.484,0.514,'conv'),('distance-only 50 km',0.361,0.341,0.382,'dist'),
('distance-only 100 km',0.403,0.379,0.428,'dist'),('constant −6.5 K/km lapse',-0.151,-0.166,-0.136,'lapse'),
('elevation-matched ±100 m',-0.066,-0.080,-0.052,'match'),('elevation-matched ±200 m',-0.049,-0.065,-0.033,'match'),
('elevation-matched ±500 m',0.025,0.007,0.042,'match'),('elevation-matched closest-quartile',-0.018,-0.037,0.001,'match')]
col={'conv':'#111827','dist':'#D97706','lapse':'#7C3AED','match':'#2563EB'}
fig,ax=plt.subplots(figsize=(7.6,4.3)); y=np.arange(len(rows))[::-1]
ax.axvspan(-0.066,0.025,color='#e7f0e7',zorder=0)  # corrected zone (residual range from elevation-matched refs)
ax.text(0.0,5.5,'corrected\n(slope ≈ 0)',ha='center',va='center',fontsize=7.8,color='#3a7d3a')
for yi,(lab,b,lo,hi,fam) in zip(y,rows):
    ax.plot([lo,hi],[yi,yi],color=col[fam],lw=1.7,zorder=2); ax.scatter([b],[yi],color=col[fam],s=36,zorder=3)
ax.axvline(0,color='#9CA3AF',lw=1,ls='--',zorder=1)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows]); ax.set_xlabel('Slope of SUHI on reference-elevation surplus (°C per 100 m)')
ax.set_title('Reference-design sensitivity',loc='left',fontsize=9.5)
ax.set_xlim(-0.22,0.56)
ax.legend(handles=[Patch(color=col['conv'],label='conventional'),Patch(color=col['dist'],label='distance-only'),
                   Patch(color=col['lapse'],label='constant lapse'),Patch(color=col['match'],label='elevation-matched')],
          loc='lower right',frameon=False,fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)
save(fig,'Figure4_slope_sensitivity_forest'); print('Fig4 done')

# ===== Figure 5: gradient (no 'c'; day/night links; −6.5 ref line) =====
g=pd.read_csv(os.path.join(_REPO,'data','r173_reference_pixel_lapse_models.csv'))
seasons=['jan','apr','jul','oct']
fig,ax=plt.subplots(figsize=(7.6,4.2))
ax.axhline(-6.5,color='#b0b0b0',ls=':',lw=1.4,zorder=1)
ax.text(7.1,-6.5,'assumed constant\nlapse (−6.5)',va='center',ha='left',fontsize=7,color='#777')
xpos={}
for i,se in enumerate(seasons):
    dd=g[g['key']==f'{se}_day'].iloc[0]; nn=g[g['key']==f'{se}_night'].iloc[0]
    xd,xn=2*i,2*i+1; xpos[f'{se}_day']=xd; xpos[f'{se}_night']=xn
    ax.plot([xd,xn],[dd['coef_degC_per_km'],nn['coef_degC_per_km']],color='#cbd2da',lw=1.4,zorder=1)
for _,r in g.iterrows():
    x=xpos[r['key']]; c='#E07A1F' if 'day' in r['key'] else '#3B5BA5'
    ax.errorbar(x,r['coef_degC_per_km'],yerr=[[r['coef_degC_per_km']-r['ci_low_degC_per_km']],[r['ci_high_degC_per_km']-r['coef_degC_per_km']]],
                fmt='o',ms=7,color=c,ecolor=c,elinewidth=1.2,capsize=2,zorder=3)
mean=-5.00; ax.axhline(mean,color='#2563EB',ls='--',lw=1.2,zorder=1)
ax.text(7.45,mean+0.05,'pooled mean −5.00\n[−5.09, −4.91]',va='bottom',ha='left',fontsize=7.5,color='#1D4ED8')
ax.set_xticks(range(8)); ax.set_xticklabels([k.split('_')[0].upper()+'\n'+k.split('_')[1] for k in g['key']],rotation=0,ha='center',fontsize=8.5)
ax.set_ylabel('Rural-pixel surface LST–elevation gradient (°C km⁻¹)')
ax.set_title('Rural LST-elevation gradients',loc='left',fontsize=9.2)
ax.set_ylim(-7.0,-3.4); ax.set_xlim(-0.6,9.0)
from matplotlib.lines import Line2D
ax.scatter([],[],color='#E07A1F',label='daytime'); ax.scatter([],[],color='#3B5BA5',label='night-time')
ax.legend(handles=[plt.scatter([],[],color='#E07A1F',label='daytime'),plt.scatter([],[],color='#3B5BA5',label='night-time'),
                   Line2D([0],[0],color='#cbd2da',lw=1.4,label='day–night pair')],
          frameon=False,fontsize=8.5,loc='lower left')
for s in ('top','right'): ax.spines[s].set_visible(False)
save(fig,'Figure5_rural_pixel_gradient'); print('Fig5 done')
