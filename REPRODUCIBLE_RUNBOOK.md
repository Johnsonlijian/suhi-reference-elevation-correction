# Reproducible Runbook

## Environment

Recommended: Python 3.11.

```bash
pip install -r requirements.txt
```

## Rebuild Submission Figures From Released Derived Data

<<<<<<< HEAD
The repository includes:

- `data/per_city_reference_elevation_bias.csv`: released per-city correction table.
- `data/source_data.xlsx`: figure/source-data workbook.

Raw third-party datasets are not redistributed. See `DATASETS_AND_LINKS.csv`.

## Quick Check From Released Data

Regenerate the final submission figures from the released per-city table and source-data workbook:

```bash
python code/fig1_lead.py
python code/r207_mechanism.py
python code/r207_clean_figures.py
python code/r207_ga.py
=======
Run from the repository root:

```bash
python code/rebuild_figs_v2.py
python code/fig2_ga.py
python code/fig3_polish.py
python code/fig45.py
python code/r213_fig_chelsa.py
>>>>>>> a484a54 (Prepare v1.0.3 Urban Climate release package)
```

Expected outputs:

```text
figures/Figure1_ranking_artifact.{pdf,png,svg}
figures/Figure2_mechanism_schematic.{pdf,png,svg}
figures/Figure3_global_bias_map.{pdf,png,svg}
figures/Figure4_slope_sensitivity_forest.{pdf,png,svg}
figures/Figure5_rural_pixel_gradient.{pdf,png,svg}
figures/Figure6_chelsa_independent_attenuation.{pdf,png,svg}
figures/Graphical_Abstract.{pdf,png,svg}
```

## Optional Raw-Data Reproduction

Raw third-party archives are not included. Scripts that require local raw or intermediate products use environment variables and stop with a clear message if inputs are absent.

Set these only if you have rebuilt or downloaded the corresponding public inputs:

```bash
export SUHI_RAW_CAUSAL_DIR=/path/to/raw_inputs_or_intermediate_causal_outputs
export SUHI_CHELSA_DIR=/path/to/chelsa_rasters
export SUHI_MODIS_LST_DIR=/path/to/monthly_modis_lst_rasters
```

Expected raw/intermediate structure under `SUHI_RAW_CAUSAL_DIR`:

```text
r159_alternative_reference_bias/r159_alternative_reference_panel.csv
r59_aridity_pet_background_gate/r59_city_panel_aridity_pet.csv
r169_endpoint_law_anchor/r169_warm_analysis_panel.csv
r173_reference_pixel_lapse_poc/r173_reference_pixel_lapse_points.csv
```

Optional checks:

```bash
python code/r207_sensitivity.py
python code/r207_rerank.py
python code/r207_spatial.py
python code/r207_uq.py
python code/r211_gpu_block_bootstrap.py
python code/r212_chelsa_independent_lapse.py
python code/r214_temporal_gradient.py
python code/r215_stratified_slope.py
python code/r216_theorem_percity.py
python code/seb_lapse_model.py
```

<<<<<<< HEAD
## Expected Core Checks

- `fig1_lead.py` reports top-100 conventional mean approximately 8.3 C, elevation-matched mean approximately 2.2 C, Spearman rho approximately 0.68, and terrain share approximately 98%.
- `r207_clean_figures.py` rebuilds Figures 3--5 without in-map region labels or in-plot explanatory text; Cartopy coastlines are optional.
- `r207_sensitivity.py` reports the conventional slope near +0.499 C per 100 m and elevation-matched slopes near zero.
- `r207_uq.py` updates the derived table with correction uncertainty and trust flags.
=======
Outputs from optional raw-data scripts are written under `derived/`.
>>>>>>> a484a54 (Prepare v1.0.3 Urban Climate release package)

## Public/Private Boundary

This repository includes code, derived data, figures, runbooks, source links, licenses, and citation metadata. It excludes raw third-party archives, active submission manuscripts, cover letters, reviewer-response drafts, private project-round outputs, logs, credentials, and private author files.
