# Reproducible Runbook

## Environment

Recommended: Python 3.11.

```bash
pip install -r requirements.txt
```

Optional raw-raster and GPU bootstrap checks additionally require:

```bash
pip install -r requirements-optional.txt
```

## Rebuild Submission Figures From Released Derived Data

The repository includes:

- `data/per_city_reference_elevation_bias.csv`: released per-city correction table.
- `data/source_data.xlsx`: figure/source-data workbook.
- `data/fig4_slope_sensitivity.csv`: Figure 4 source table.
- `data/fig5_gradient_summary.csv`: Figure 5 pooled-gradient source table.
- `data/outlier_audit.csv`: audit table for the five retained extreme retrieval outliers.
- `data/r212_chelsa_vs_modis_lapse.csv`: independent CHELSA attenuation source data for Figure 6.
- `data/coast.zip`: Natural Earth 110 m coastline geometry redistributed under public-domain terms for Figure 3.

Large raw third-party datasets are not redistributed. See `DATASETS_AND_LINKS.csv`.

## Quick Check From Released Data

Run from the repository root:

```bash
python code/rebuild_figs_v2.py
python code/fig2_ga.py
python code/fig3_polish.py
python code/fig45.py
python code/r213_fig_chelsa.py
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

## Expected Core Checks

- `rebuild_figs_v2.py` reports top-100 conventional mean approximately 8.3 C, elevation-matched mean approximately 2.2 C, Spearman rho approximately 0.68, and terrain share approximately 98%.
- The active figure scripts rebuild Figures 1--6 and the graphical abstract from released data without local machine paths or deprecated panels.
- `r207_sensitivity.py` reports the conventional slope near +0.499 C per 100 m and elevation-matched slopes near zero.
- `fig45.py` reads `data/fig4_slope_sensitivity.csv`, `data/r173_reference_pixel_lapse_models.csv`, and `data/fig5_gradient_summary.csv`; Figure 4 and the pooled Figure 5 annotations are therefore archived as source data rather than embedded only in plotting code.
- `r207_uq.py` regenerates `correction_uncertainty_C` (matching-definition SD, not a full retrieval uncertainty) and trust flags in `data/per_city_reference_elevation_bias.csv`; rerun it only when rebuilding the released table from the raw/intermediate inputs.
- `r207_sourcedata.py` rebuilds `data/source_data.xlsx` from the released CSV/source tables and adds the outlier audit sheet.

Most optional raw-data diagnostics write under `derived/`. Scripts that regenerate released artifacts (`r207_sourcedata.py` and `r207_uq.py`) intentionally update files under `data/`; compare the resulting row count, ranking-analysis inclusion flag, source-data sheet list, and checksums before replacing an archived release.

## Public/Private Boundary

This repository includes code, derived data, figures, runbooks, source links, licenses, citation metadata, and the small Natural Earth coastline shapefile needed to render Figure 3. It excludes large raw third-party archives, active submission manuscripts, cover letters, reviewer-response drafts, private project-round outputs, logs, credentials, and private author files.
