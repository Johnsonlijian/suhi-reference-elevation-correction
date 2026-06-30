# -*- coding: utf-8 -*-
"""
Surface Energy Balance (SEB) derivation of the rural-reference surface LST-elevation gradient.

Question the paper currently hand-waves: WHY is the surface LST lapse rate ~-5 K/km
(not the -6.5 K/km free-air environmental lapse), and WHY is it steeper by day than by night?

Physics (linearised surface energy balance, R_n = H + LE + G):
  The skin temperature T_s is coupled to the free-air temperature T_a (which falls at the
  environmental lapse rate Gamma_a) through the surface energy balance. Implicit-function
  differentiation of the SEB w.r.t. elevation gives:

      dT_s/dz = f * Gamma_a ,   with attenuation factor   f = g_a / (g_a + g_r + g_LE + g_G)

  where
      g_r = 4 eps sigma T_s^3 / (rho c_p)   radiative (longwave) conductance  [NO free parameter]
      g_a                                   aerodynamic (turbulent) conductance [literature]
      g_LE, g_G                             latent + ground-heat feedback conductances (2nd order)

  Predictions (no tuning to the 8 windows):
    (1) f < 1  => |surface gradient| < |air lapse rate|  (the -5 vs -6.5 gap)
    (2) g_a(day) >> g_a(night) (unstable vs stable boundary layer)
        => f larger by day => surface gradient STEEPER by day      <-- the observed asymmetry
    (3) g_r grows with T_s^3 => warm windows damp slightly more (second-order seasonal structure)

  g_r is computed from the REAL per-window MODIS LST. g_a takes ONE daytime and ONE night-time
  literature value (held fixed across all 4 seasons). 2 physical inputs predict 8 observed numbers.

  Inverse check: solve g_a implied by each observed gradient; confirm it lands in the literature
  range and is ordered day > night.
"""
import os, numpy as np, pandas as pd, matplotlib as mpl
mpl.use('Agg'); import matplotlib.pyplot as plt

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW_CAUSAL = os.environ.get('SUHI_RAW_CAUSAL_DIR')
if not RAW_CAUSAL:
    raise SystemExit('Set SUHI_RAW_CAUSAL_DIR to the local directory containing r173_reference_pixel_lapse_poc/.')
PTS  = os.path.join(RAW_CAUSAL, 'r173_reference_pixel_lapse_poc','r173_reference_pixel_lapse_points.csv')
MOD  = os.path.join(REPO, 'data','r173_reference_pixel_lapse_models.csv')
OUTD = os.path.join(REPO, 'derived','seb_lapse_model')
FIGD = OUTD
os.makedirs(OUTD, exist_ok=True)

# ---------- physical constants ----------
SIGMA = 5.670374419e-8     # Stefan-Boltzmann  W m-2 K-4
EPS   = 0.96               # broadband emissivity, rural land (semi-arid~0.96, veg~0.98)
RHO   = 1.15               # air density kg m-3 (terrain ~1000-1500 m -> ~1.10-1.20)
CP    = 1005.0             # specific heat of air  J kg-1 K-1
GAMMA_A = -6.5             # environmental (free-air) lapse rate  K/km  (ICAO standard / paper's reference)

# Aerodynamic conductance (m/s) -- standard literature values for rural short-veg / sparse terrain.
# Monteith & Unsworth; Garratt (1992). r_a ~ 20-50 s/m day (unstable), ~100-300 s/m night (stable).
GA_DAY   = 0.025          # central daytime value (r_a = 40 s/m)
GA_NIGHT = 0.0070         # central night value  (r_a = 143 s/m)
# sensitivity envelope
GA_DAY_LO, GA_DAY_HI     = 0.018, 0.035   # r_a 29-56 s/m
GA_NIGHT_LO, GA_NIGHT_HI = 0.0045, 0.011  # r_a 91-222 s/m

def g_r(T_s_C):
    """radiative conductance (m/s) from skin temperature in Celsius (no free parameter)."""
    T = T_s_C + 273.15
    return 4.0 * EPS * SIGMA * T**3 / (RHO * CP)

def f_atten(g_a, g_rad):
    return g_a / (g_a + g_rad)

# ---------- observed gradients ----------
mod = pd.read_csv(MOD)
windows = ['jan_day','jan_night','apr_day','apr_night','jul_day','jul_night','oct_day','oct_night']

# ---------- per-window mean rural-reference LST (for g_r) ----------
print("Loading 422k-pixel reference panel to get per-window mean LST ...")
pts = pd.read_csv(PTS)
print(f"  loaded {len(pts):,} pixels")
lst_cols = {
    'jan_day':'lst_jan_day_C','jan_night':'lst_jan_night_C',
    'apr_day':'lst_apr_day_C','apr_night':'lst_apr_night_C',
    'jul_day':'lst_jul_day_C','jul_night':'lst_jul_night_C',
    'oct_day':'lst_oct_day_C','oct_night':'lst_oct_night_C'}
meanLST = {w: float(pts[lst_cols[w]].mean()) for w in windows}

# ---------- build the comparison table ----------
rows = []
for w in windows:
    obs   = float(mod.loc[mod['key']==w,'coef_degC_per_km'].iloc[0])
    obs_lo= float(mod.loc[mod['key']==w,'ci_low_degC_per_km'].iloc[0])
    obs_hi= float(mod.loc[mod['key']==w,'ci_high_degC_per_km'].iloc[0])
    T_s   = meanLST[w]
    grad_r= g_r(T_s)
    is_day = w.endswith('day')
    g_a    = GA_DAY if is_day else GA_NIGHT
    g_a_lo = GA_DAY_LO if is_day else GA_NIGHT_LO
    g_a_hi = GA_DAY_HI if is_day else GA_NIGHT_HI
    f       = f_atten(g_a, grad_r)
    pred    = f * GAMMA_A
    pred_lo = f_atten(g_a_lo, grad_r) * GAMMA_A   # NB more g_a -> steeper (more negative)
    pred_hi = f_atten(g_a_hi, grad_r) * GAMMA_A
    # inverse: solve g_a from observed f_obs = obs/GAMMA_A = g_a/(g_a+g_r) -> g_a = g_r f/(1-f)
    f_obs   = obs / GAMMA_A
    g_a_impl= grad_r * f_obs / (1.0 - f_obs)
    rows.append(dict(window=w, day_night=('day' if is_day else 'night'),
                     mean_LST_C=round(T_s,2),
                     g_r_mm_s=round(grad_r*1000,3),
                     g_a_used_mm_s=round(g_a*1000,2),
                     f_pred=round(f,3),
                     pred_grad=round(pred,3), pred_lo=round(min(pred_lo,pred_hi),3),
                     pred_hi=round(max(pred_lo,pred_hi),3),
                     obs_grad=round(obs,3), obs_lo=round(obs_lo,3), obs_hi=round(obs_hi,3),
                     resid=round(pred-obs,3),
                     f_obs=round(f_obs,3), g_a_implied_mm_s=round(g_a_impl*1000,2)))
tab = pd.DataFrame(rows)
pd.set_option('display.width',200); pd.set_option('display.max_columns',30)
print("\n================ SEB FORWARD PREDICTION vs OBSERVED ================")
print(tab[['window','mean_LST_C','g_r_mm_s','g_a_used_mm_s','f_pred','pred_grad','obs_grad','resid','g_a_implied_mm_s']].to_string(index=False))

# ---------- fit quality ----------
pred = tab['pred_grad'].values; obs = tab['obs_grad'].values
rmse = float(np.sqrt(np.mean((pred-obs)**2)))
mae  = float(np.mean(np.abs(pred-obs)))
r    = float(np.corrcoef(pred,obs)[0,1])
day_obs = tab.loc[tab.day_night=='day','obs_grad'].mean()
nig_obs = tab.loc[tab.day_night=='night','obs_grad'].mean()
day_pred= tab.loc[tab.day_night=='day','pred_grad'].mean()
nig_pred= tab.loc[tab.day_night=='night','pred_grad'].mean()
print(f"\nFIT: RMSE={rmse:.3f} K/km  MAE={mae:.3f}  Pearson r={r:.3f}  (2 inputs -> 8 outputs)")
print(f"Day/night asymmetry  observed: {day_obs:.2f} vs {nig_obs:.2f} (Delta {day_obs-nig_obs:+.2f})")
print(f"Day/night asymmetry  predicted:{day_pred:.2f} vs {nig_pred:.2f} (Delta {day_pred-nig_pred:+.2f})")
print(f"Annual-mean attenuation factor f_obs = {(obs.mean()/GAMMA_A):.3f}  (=> surface gradient is {(obs.mean()/GAMMA_A)*100:.0f}% of the air lapse rate)")
print(f"Implied g_a day mean  = {tab.loc[tab.day_night=='day','g_a_implied_mm_s'].mean():.1f} mm/s (lit. day 18-35)")
print(f"Implied g_a night mean= {tab.loc[tab.day_night=='night','g_a_implied_mm_s'].mean():.1f} mm/s (lit. night 4.5-11)")

tab.to_csv(os.path.join(OUTD,'r210_seb_lapse_prediction.csv'), index=False)

# ---------- emissivity / rho / g_a sensitivity on the annual-mean f ----------
print("\n================ SENSITIVITY (annual-mean predicted gradient, K/km) ================")
sens=[]
for eps in (0.92,0.96,0.99):
    for rho in (1.10,1.15,1.20):
        gpred=[]
        for w in windows:
            T=meanLST[w]+273.15
            gr=4*eps*SIGMA*T**3/(rho*CP)
            ga=GA_DAY if w.endswith('day') else GA_NIGHT
            gpred.append(ga/(ga+gr)*GAMMA_A)
        sens.append(dict(eps=eps,rho=rho,mean_pred=round(np.mean(gpred),3)))
sdf=pd.DataFrame(sens)
print(sdf.to_string(index=False))
print(f"observed annual-mean = {obs.mean():.3f} K/km")
sdf.to_csv(os.path.join(OUTD,'r210_seb_sensitivity.csv'), index=False)

# =================== FIGURE 6: SEB derivation ===================
mpl.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.linewidth':0.9,
                     'pdf.fonttype':42,'ps.fonttype':42})
fig = plt.figure(figsize=(11.4,4.6))
gs  = fig.add_gridspec(1,2,width_ratios=[1.12,1.0],wspace=0.28)

# panel a: predicted vs observed, 8 windows
ax = fig.add_subplot(gs[0,0])
x = np.arange(8)
order = windows
oda = tab.set_index('window').loc[order]
# observed with CI
ax.errorbar(x-0.12, oda['obs_grad'], yerr=[oda['obs_grad']-oda['obs_lo'], oda['obs_hi']-oda['obs_grad']],
            fmt='o', ms=6, color='#333', ecolor='#333', elinewidth=1.1, capsize=2, label='observed (MODIS, 417k pixels)', zorder=4)
# predicted with sensitivity band
ax.errorbar(x+0.12, oda['pred_grad'], yerr=[oda['pred_grad']-oda['pred_lo'], oda['pred_hi']-oda['pred_grad']],
            fmt='s', ms=6, color='#C0392B', ecolor='#C0392B', elinewidth=1.1, capsize=2, label='SEB prediction (2 inputs)', zorder=4, alpha=0.9)
ax.axhline(GAMMA_A, color='#888', ls=':', lw=1.3)
ax.text(7.95, GAMMA_A-0.04, 'free-air −6.5', va='top', ha='right', fontsize=6.8, color='#777')
ax.axhline(obs.mean(), color='#999', ls='--', lw=0.9)
ax.text(7.95, obs.mean()+0.05, f'obs. mean {obs.mean():.1f}', va='bottom', ha='right', fontsize=6.8, color='#777')
ax.set_xticks(x); ax.set_xticklabels([w.replace('_',' ').upper() for w in order], rotation=45, ha='right', fontsize=7.3)
ax.set_ylabel('surface LST–elevation gradient (°C km⁻¹)')
ax.set_ylim(-7.4,-2.9); ax.set_xlim(-0.6,8.2)
ax.set_title('a   Two-conductance SEB predicts all eight windows', loc='left', fontweight='bold', fontsize=9.6)
ax.legend(frameon=False, fontsize=7.6, loc='upper center', bbox_to_anchor=(0.5,0.995),
          ncol=2, borderaxespad=0, columnspacing=1.4, handletextpad=0.4)
ax.text(0.5,0.018,f'RMSE = {rmse:.2f} °C km⁻¹     r = {r:.2f}     2 inputs → 8 observations',
        transform=ax.transAxes, fontsize=7.3, color='#333', ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='#d8d8d8', lw=0.7))
for s in ('top','right'): ax.spines[s].set_visible(False)

# panel b: attenuation factor vs aerodynamic conductance, with day/night regimes
ax = fig.add_subplot(gs[0,1])
ga_axis = np.linspace(0.001,0.05,300)
for Tc,c in [(8,'#3B5BA5'),(28,'#E07A1F')]:
    gr = g_r(Tc)
    ax.plot(ga_axis*1000, ga_axis/(ga_axis+gr)*GAMMA_A, color=c, lw=2.0, label=f'$g_r$ at {Tc} °C')
# mark the regimes
gr_n=g_r(8); gr_d=g_r(28)
ax.scatter([GA_NIGHT*1000],[GA_NIGHT/(GA_NIGHT+gr_n)*GAMMA_A], color='#3B5BA5', s=58, ec='k', lw=0.5, zorder=5)
ax.scatter([GA_DAY*1000],  [GA_DAY/(GA_DAY+gr_d)*GAMMA_A],     color='#E07A1F', s=58, ec='k', lw=0.5, zorder=5)
ax.annotate('night\n(stable BL,\nlow turbulence)', (GA_NIGHT*1000, GA_NIGHT/(GA_NIGHT+gr_n)*GAMMA_A),
            xytext=(12,-3.55), fontsize=7, color='#3B5BA5', ha='left', va='center',
            arrowprops=dict(arrowstyle='->',color='#3B5BA5',lw=0.9))
ax.annotate('day\n(unstable BL,\nstrong turbulence)', (GA_DAY*1000, GA_DAY/(GA_DAY+gr_d)*GAMMA_A),
            xytext=(28,-6.05), fontsize=7, color='#E07A1F', ha='left', va='center',
            arrowprops=dict(arrowstyle='->',color='#E07A1F',lw=0.9))
ax.axhline(GAMMA_A, color='#888', ls=':', lw=1.3); ax.text(1.0,GAMMA_A-0.06,'free-air −6.5',ha='left',va='top',fontsize=6.8,color='#777')
ax.set_xlabel('aerodynamic conductance $g_a$ (mm s⁻¹)')
ax.set_ylabel('predicted surface gradient (°C km⁻¹)')
ax.set_title('b   The day/night asymmetry is a turbulence effect', loc='left', fontweight='bold', fontsize=9.6)
ax.set_ylim(-6.7,-2.6); ax.set_xlim(0,50)
ax.legend(frameon=False, fontsize=7.6, loc='upper right', title='radiative damping $g_r=4\\epsilon\\sigma T^3/\\rho c_p$', title_fontsize=7.4)
for s in ('top','right'): ax.spines[s].set_visible(False)

for ext in ('png','pdf','svg'):
    fig.savefig(os.path.join(FIGD,f'SEB_lapse_model_consistency.{ext}'),
                dpi=(420 if ext=='png' else None), bbox_inches='tight')
plt.close()
print('\nSEB_lapse_model_consistency written to', FIGD)
print('Outputs in', OUTD)
print('DONE')
