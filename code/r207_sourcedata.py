import os, numpy as np, pandas as pd
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('SUHI_RAW_CAUSAL_DIR', ROOT / 'raw_inputs'))
OUT = ROOT / 'outputs'
SD = ROOT / 'data'
OUT.mkdir(exist_ok=True)
SD.mkdir(exist_ok=True)
# deliverable: per-city reference-elevation bias + correction inputs
a=pd.read_csv(RAW/'r159_alternative_reference_bias'/'r159_alternative_reference_panel.csv',
  usecols=['label','original_SUHI_warm','elev100_rural50_SUHI_warm','urban_elev_calc','rural_ref_elev_50km_block','rural_ref_minus_urban_elev_m'])
b=pd.read_csv(RAW/'r59_aridity_pet_background_gate'/'r59_city_panel_aridity_pet.csv',usecols=['label','lon','lat'])
d=a.merge(b,on='label')
for c in d.columns:
    if c!='label': d[c]=pd.to_numeric(d[c],errors='coerce')
d['reference_elevation_bias_C']=d['original_SUHI_warm']-d['elev100_rural50_SUHI_warm']
deliv=d.rename(columns={'urban_elev_calc':'urban_elev_m','rural_ref_elev_50km_block':'rural_ref_elev_m',
  'rural_ref_minus_urban_elev_m':'reference_elevation_surplus_m','original_SUHI_warm':'conventional_SUHI_C',
  'elev100_rural50_SUHI_warm':'elevation_matched_SUHI_C'})[['label','lon','lat','urban_elev_m','rural_ref_elev_m',
  'reference_elevation_surplus_m','conventional_SUHI_C','elevation_matched_SUHI_C','reference_elevation_bias_C']].dropna(subset=['lon','lat','reference_elevation_bias_C'])
deliv.to_csv(SD/'per_city_reference_elevation_bias.csv',index=False)
print('deliverable rows:',len(deliv))
# Fig2 slope table (verified numbers)
fig2=pd.DataFrame([['conventional (original)',0.499,0.484,0.514],['distance-only 50km',0.361,0.341,0.382],
 ['distance-only 100km',0.403,0.379,0.428],['constant -6.5 K/km lapse',-0.151,-0.166,-0.136],
 ['elev-matched +/-100m',-0.066,-0.080,-0.052],['elev-matched +/-200m',-0.049,-0.065,-0.033],
 ['elev-matched +/-500m',0.025,0.007,0.042],['elev-matched closest-quartile',-0.018,-0.037,0.001]],
 columns=['reference_design','slope_C_per_100m','ci_low','ci_high'])
# Fig3 gradient table
fig3=pd.read_csv(RAW/'r173_reference_pixel_lapse_poc'/'r173_reference_pixel_lapse_models.csv',
  usecols=['label','n_points','n_blocks','coef_degC_per_km','ci_low_degC_per_km','ci_high_degC_per_km','share_blocks_negative'])
with pd.ExcelWriter(SD/'source_data.xlsx') as xl:
    deliv.to_excel(xl,'Fig1_per_city_bias',index=False)
    fig2.to_excel(xl,'Fig2_slope_by_reference',index=False)
    fig3.to_excel(xl,'Fig3_pixel_gradient',index=False)
print('source_data.xlsx written (3 sheets):', SD/'source_data.xlsx')
print('Fig1 sheet rows', len(deliv), '| Fig2 rows', len(fig2), '| Fig3 rows', len(fig3))
