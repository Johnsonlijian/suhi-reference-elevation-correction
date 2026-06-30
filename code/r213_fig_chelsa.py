# -*- coding: utf-8 -*-
"""R213  Figure 6: independent CHELSA cross-validation of surface-attenuation f."""
import os, numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg'); import matplotlib.pyplot as plt
_REPO=os.path.join(os.path.dirname(__file__),'..')
OUT=os.path.join(_REPO,'figures')
d=pd.read_csv(os.path.join(_REPO,'data','r212_chelsa_vs_modis_lapse.csv'))
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.linewidth':0.9,'pdf.fonttype':42,'ps.fonttype':42})

order=['jan_day','apr_day','jul_day','oct_day','jan_night','apr_night','jul_night','oct_night']
d=d.set_index('window').loc[order].reset_index()
lab=[w.split('_')[0].upper()+'\n'+w.split('_')[1] for w in order]
x=np.arange(len(order)); isday=np.array([w.endswith('day') for w in order])

fig,(axL,axR)=plt.subplots(1,2,figsize=(11.4,4.3),gridspec_kw=dict(wspace=0.24,left=0.07,right=0.985,top=0.9,bottom=0.16))

# ---- Panel a: skin vs air lapse ----
# air (CHELSA free-air) -- grey squares, ~flat
axL.errorbar(x, d['air_lapse'], yerr=[d['air_lapse']-d['air_lo'], d['air_hi']-d['air_lapse']],
             fmt='s', ms=6, color='#555', mfc='white', mec='#555', capsize=3, lw=1.1, label='Free-air lapse  (CHELSA air T)', zorder=3)
# skin (MODIS) -- colored circles
for m,c,l in [(isday,'#E07B00','Skin lapse, day  (MODIS)'),(~isday,'#2563EB','Skin lapse, night  (MODIS)')]:
    axL.errorbar(x[m], d['skin_lapse'][m], yerr=[(d['skin_lapse']-d['skin_lo'])[m], (d['skin_hi']-d['skin_lapse'])[m]],
                 fmt='o', ms=7, color=c, capsize=3, lw=1.2, label=l, zorder=4)
axL.axhline(-6.5, color='#999', ls=':', lw=1.0, zorder=1)
axL.text(7.35,-6.46,'textbook $-6.5$',fontsize=7,color='#777',ha='right',va='bottom')
axL.axvline(3.5,color='#ccc',lw=0.8)
axL.set_xticks(x); axL.set_xticklabels(lab,fontsize=7.5)
axL.set_ylabel('LST / air-T elevation lapse  (°C km$^{-1}$)',fontsize=9)
axL.set_ylim(-6.8,-3.6); axL.invert_yaxis()
axL.set_title('a   Lapse rates',loc='left',fontsize=9.5)
axL.legend(fontsize=8.0,loc='lower center',ncol=1,frameon=True,framealpha=0.93,edgecolor='#ddd')
for s in('top','right'):axL.spines[s].set_visible(False)
axL.text(1.5,-3.75,'DAY',ha='center',fontsize=8.5,color='#E07B00')
axL.text(5.5,-3.75,'NIGHT',ha='center',fontsize=8.5,color='#2563EB')

# ---- Panel b: attenuation factor f = skin/air ----
for m,c in [(isday,'#E07B00'),(~isday,'#2563EB')]:
    axR.errorbar(x[m], d['f'][m], yerr=[(d['f']-d['f_lo'])[m], (d['f_hi']-d['f'])[m]],
                 fmt='o', ms=7, color=c, capsize=3, lw=1.2, zorder=4)
# Annotate April daytime f > 1 (x=1, apr_day)
apr_f = d.iloc[1]['f']
axR.annotate(f'Apr day\nf = {apr_f:.2f}',
             xy=(1, apr_f), xytext=(1.9, apr_f + 0.06),
             fontsize=7.5, color='#B35F00',
             arrowprops=dict(arrowstyle='->', color='#B35F00', lw=0.9),
             ha='left', va='bottom', zorder=5)
axR.axhline(1.0, color='#999', ls='--', lw=1.0); axR.text(7.4,1.005,'f = 1  (no attenuation)',fontsize=7.5,color='#777',ha='right',va='bottom')
fday=d['f'][isday].mean(); fnight=d['f'][~isday].mean()
axR.axhspan(fday-0.005,fday+0.005,xmin=0.02,xmax=0.48,color='#E07B00',alpha=0.18)
axR.axhspan(fnight-0.005,fnight+0.005,xmin=0.52,xmax=0.98,color='#2563EB',alpha=0.18)
axR.text(1.5,fday+0.018,f'day mean f = {fday:.2f}',ha='center',fontsize=7.5,color='#B35F00')
axR.text(5.5,fnight-0.028,f'night mean f = {fnight:.2f}',ha='center',fontsize=7.5,color='#1D4ED8')
axR.axvline(3.5,color='#ccc',lw=0.8)
axR.set_xticks(x); axR.set_xticklabels(lab,fontsize=7.5)
axR.set_ylabel('Attenuation factor  f = skin lapse / air lapse',fontsize=9)
axR.set_ylim(0.60,1.10)
axR.set_title('b   Attenuation factor',loc='left',fontsize=9.5)
for s in('top','right'):axR.spines[s].set_visible(False)

for ext in('png','pdf','svg'):
    fig.savefig(os.path.join(OUT,f'Figure6_chelsa_independent_attenuation.{ext}'),
                dpi=(450 if ext=='png' else None),bbox_inches='tight')
print('saved Figure6 ->',OUT)
print(f'day f={fday:.3f}  night f={fnight:.3f}  annual f={d["f"].mean():.3f}')
print('DONE')
