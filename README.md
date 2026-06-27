# Global Per-City Reference-Elevation Correction For Satellite Urban Heat-Island Estimates

Data and code accompanying: REN, L. *Reference-elevation mismatch biases satellite urban heat-island rankings: a within-city correction across 11,453 cities* (prepared for Urban Climate).

In terrain-structured cities, the rural reference used to compute satellite surface urban heat-island intensity (SUHI = urban minus rural land-surface temperature) can sit at a different elevation than the urban core. Because land-surface temperature declines with elevation, this mismatch biases conventional SUHI values. This release provides a global per-city quantification of the bias and a ready-to-use correction.

## Contents

```text
data/
  per_city_reference_elevation_bias.csv   # 11,452 cities: conventional and elevation-matched SUHI, bias, uncertainty, trust flag
  source_data.xlsx                        # source data for manuscript figures
code/
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
DATA_DICTIONARY.md
CITATION.cff
LICENSE.txt
```

## Core Data File

`data/per_city_reference_elevation_bias.csv` contains one row per usable city and the columns documented in `DATA_DICTIONARY.md`.

To correct a conventional SUHI estimate, subtract `reference_elevation_bias_C`, equivalent to using `elevation_matched_SUHI_C`.

## Public Data Sources

Raw input products are public and are not redistributed here: GHSL GHS-SMOD/GHS-POP, MODIS MOD11A2 land-surface temperature via OpenLandMap, GMTED2010, Copernicus GLO-30 DSM, and Yang et al. (2024) global UHII data for external validation.

## Reproducibility

Python 3.11 with numpy, pandas, statsmodels, scipy, matplotlib, and openpyxl is expected. Scripts in `code/` reproduce the analyses and figures from the public inputs and derived tables. `r207_clean_figures.py` uses Cartopy when available for coastlines and otherwise falls back to a plain lon/lat map.

## License

Derived data: CC BY 4.0. Code: MIT. See `LICENSE.txt`.

## Citation

See `CITATION.cff`. After DOI deposit, cite both the paper and the dataset DOI.
