# Reproducible Runbook

## Environment

Recommended: Python 3.11.

Install the lightweight analysis environment:

```bash
pip install -r requirements.txt
```

## Included Derived Data

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
```

Outputs are written to `figures/`.

## Full Reproduction With Raw Intermediate Inputs

Some scripts require local intermediate tables derived from public raw products. Place those tables under a directory with the following structure, then set `SUHI_RAW_CAUSAL_DIR`:

```text
raw_inputs/
  r159_alternative_reference_bias/r159_alternative_reference_panel.csv
  r59_aridity_pet_background_gate/r59_city_panel_aridity_pet.csv
  r173_reference_pixel_lapse_poc/r173_reference_pixel_lapse_models.csv
```

On Windows PowerShell:

```powershell
$env:SUHI_RAW_CAUSAL_DIR="C:\path\to\raw_inputs"
python code/r207_sensitivity.py
python code/r207_rerank.py
python code/r207_spatial.py
python code/r207_uq.py
```

## Expected Core Checks

- `fig1_lead.py` reports top-100 conventional mean approximately 8.3 C, elevation-matched mean approximately 2.2 C, Spearman rho approximately 0.68, and terrain share approximately 98%.
- `r207_clean_figures.py` rebuilds Figures 3--5 without in-map region labels or in-plot explanatory text; Cartopy coastlines are optional.
- `r207_sensitivity.py` reports the conventional slope near +0.499 C per 100 m and elevation-matched slopes near zero.
- `r207_uq.py` updates the derived table with correction uncertainty and trust flags.

## Public/Private Boundary

This repository includes code and derived data only. It excludes raw third-party archives, active submission manuscripts, cover letters, reviewer-response drafts, private logs, credentials, and local project-round folders.
