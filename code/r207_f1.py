import os
from pathlib import Path
import numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg'); import matplotlib.pyplot as plt
try:
    from pyplot_cjk import set_style; set_style(lang='en')
except Exception: pass
import cmocean, geopandas as gpd
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
a=pd.read_csv(RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv',usecols=['label','original_SUHI_warm','elev100_rural50_SUHI_warm'])
bb=pd.read_csv(RAW/'r59_aridity_pet_background_gate'/'r59_city_panel_aridity_pet.csv',usecols=['label','lon','lat'])
m=a.merge(bb,on='label')
for c in ['original_SUHI_warm','elev100_rural50_SUHI_warm','lon','lat']: m[c]=pd.to_numeric(m[c],errors='coerce')
m['bias']=m['original_SUHI_warm']-m['elev100_rural50_SUHI_warm']; m=m.dropna(subset=['lon','lat','bias'])
coast_file = os.environ.get('SUHI_COASTLINE_FILE', str(ROOT / 'raw_inputs' / 'coast.zip'))
coast=gpd.read_file(coast_file)
fig,ax=plt.subplots(figsize=(7.2,3.7))
coast.plot(ax=ax,linewidth=0.3,color='#888888',zorder=1)
o=m.reindex(m['bias'].abs().sort_values().index)
sc=ax.scatter(o['lon'],o['lat'],c=o['bias'].clip(-2,2),s=4,cmap=cmocean.cm.balance,vmin=-2,vmax=2,linewidths=0,alpha=0.85,zorder=2)
ax.set_xlim(-180,180); ax.set_ylim(-60,84); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
cb=fig.colorbar(sc,ax=ax,fraction=0.022,pad=0.01,extend='both'); cb.set_label('Reference-elevation SUHI bias (°C)\n(original − elevation-matched)',fontsize=7); cb.ax.tick_params(labelsize=7)
ax.set_title('a   Reference-elevation bias in satellite SUHI across 11,452 cities  (|bias| > 1 °C in 47.4%)',loc='left',fontsize=8.5)
for name,x,y in [('Andes',-71,-24),('Himalaya–Tibet',84,34),('E. African Rift',38,0),('Anatolian/Iranian',53,38),('Mexican plateau',-105,24)]:
    ax.annotate(name,(x,y),fontsize=6,color='#222',ha='center',bbox=dict(boxstyle='round,pad=0.1',fc='white',ec='none',alpha=0.65))
for ext in ['png','pdf','svg']:
    fig.savefig(OUT/('Figure1_global_reference_elevation_bias_map.'+ext),dpi=(600 if ext=='png' else None),bbox_inches='tight')
print('F1 regenerated with coastlines')
