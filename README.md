# Global Per-City Reference-Elevation Correction For Satellite Urban Heat-Island Estimates

Data and code accompanying:

REN, L. Reference-elevation mismatch biases satellite urban heat-island rankings: a within-city correction across 11,452 cities.

Version: 1.0.3

## Purpose

In terrain-structured cities, the rural reference used to compute satellite surface urban heat-island intensity (SUHI = urban minus rural land-surface temperature) can sit at a different elevation from the urban core. Because land-surface temperature declines with elevation, this mismatch can bias conventional SUHI values. This release provides a global per-city quantification of that bias and a ready-to-use correction.

## Contents

```text
data/
  per_city_reference_elevation_bias.csv
  source_data.xlsx
  coast.zip
  r173_reference_pixel_lapse_models.csv
  r212_chelsa_vs_modis_lapse.csv
figures/
  Figure1_ranking_artifact.{pdf,png,svg}
  Figure2_mechanism_schematic.{pdf,png,svg}
  Figure3_global_bias_map.{pdf,png,svg}
  Figure4_slope_sensitivity_forest.{pdf,png,svg}
  Figure5_rural_pixel_gradient.{pdf,png,svg}
  Figure6_chelsa_independent_attenuation.{pdf,png,svg}
  Graphical_Abstract.{pdf,png,svg}
code/
<<<<<<< HEAD
  fig1_lead.py              # final two-panel lead ranking-artifact figure
  r207_clean_figures.py     # final Figures 3--5 from source_data.xlsx
  r207_ga.py                # graphical abstract
  r207_mechanism.py         # mechanism schematic
  r207_rerank.py            # ranking-artifact analysis
  r207_rerank2.py           # ranking-artifact robustness
  r207_sensitivity.py       # reference-definition sensitivity and lapse comparison
  r207_sourcedata.py        # source-data workbook
  r207_spatial.py           # spatial clustering checks
  r207_uq.py                # per-city uncertainty and trust flag
=======
  rebuild_figs_v2.py
  fig2_ga.py
  fig3_polish.py
  fig45.py
  r213_fig_chelsa.py
  r207_*.py and r211-r216 analysis scripts
>>>>>>> a484a54 (Prepare v1.0.3 Urban Climate release package)
DATA_DICTIONARY.md
DATASETS_AND_LINKS.csv
REPRODUCIBLE_RUNBOOK.md
CITATION.cff
LICENSE.txt
```

## Core Data File

`data/per_city_reference_elevation_bias.csv` contains one row per usable city and the columns documented in `DATA_DICTIONARY.md`.

To correct a conventional SUHI estimate, subtract `reference_elevation_bias_C`, equivalent to using `elevation_matched_SUHI_C`.

## Public Data Sources

Raw input products are public and are not redistributed here. They include GHSL GHS-SMOD/GHS-POP, MODIS MOD11A2 land-surface temperature via OpenLandMap, GMTED2010, Copernicus GLO-30 DSM, CHELSA v2.1, and Yang et al. (2024) global UHII data for external validation.

## Reproducibility

<<<<<<< HEAD
Python 3.11 with numpy, pandas, statsmodels, scipy, matplotlib, and openpyxl is expected. Scripts in `code/` reproduce the analyses and figures from the public inputs and derived tables. `r207_clean_figures.py` uses Cartopy when available for coastlines and otherwise falls back to a plain lon/lat map.
=======
Recommended environment: Python 3.11 with numpy, pandas, statsmodels, scipy, matplotlib, geopandas, rasterio, pyproj, openpyxl, and torch for optional GPU bootstraps.

The five active figure generators are self-contained against the released `data/` directory and write to `figures/`:

```bash
python code/rebuild_figs_v2.py
python code/fig2_ga.py
python code/fig3_polish.py
python code/fig45.py
python code/r213_fig_chelsa.py
```

Raw-data analysis scripts that cannot be run from the released derived tables use explicit environment variables rather than local machine paths. See `REPRODUCIBLE_RUNBOOK.md`.
>>>>>>> a484a54 (Prepare v1.0.3 Urban Climate release package)

## License

Derived data: CC BY 4.0.
Code: MIT.
See `LICENSE.txt`.

## Citation

See `CITATION.cff`. After Zenodo DOI minting, cite both the accompanying paper and the dataset DOI.
