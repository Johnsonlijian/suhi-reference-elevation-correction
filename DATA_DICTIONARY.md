# Data Dictionary

## data/per_city_reference_elevation_bias.csv

| Column | Type | Description |
|---|---:|---|
| label | string | GHS-SMOD urban-centre identifier. |
| lon | numeric | Urban-centre centroid longitude in decimal degrees. |
| lat | numeric | Urban-centre centroid latitude in decimal degrees. |
| urban_elev_m | numeric | Mean urban-core elevation from GMTED2010, metres. |
| rural_ref_elev_m | numeric | Mean elevation of the conventional rural reference, metres. |
| reference_elevation_surplus_m | numeric | Rural-reference elevation minus urban-core elevation, metres. |
| conventional_SUHI_C | numeric | Satellite SUHI using the conventional 50 km rural reference, degrees Celsius. |
| elevation_matched_SUHI_C | numeric | Satellite SUHI using the elevation-matched rural reference, degrees Celsius. |
| reference_elevation_bias_C | numeric | Conventional minus elevation-matched SUHI. Subtract this value from the conventional estimate to apply the correction. |
| correction_uncertainty_C | numeric | Standard deviation of the per-city bias across five matching-band definitions: +/-100 m/50 km, +/-100 m/100 km, +/-200 m/100 km, +/-500 m/100 km, and closest-quartile/100 km. |
| matched_ref_pixels | integer | Number of rural-reference pixels retained after elevation matching under the primary +/-100 m/50 km definition. |
| trust_flag | string | "ok" if matched_ref_pixels >= 30; "low_pixel" otherwise. |

## data/source_data.xlsx

| Sheet | Figures | Description |
|---|---|---|
| Figs1_3_per_city_bias | Figures 1 and 3 | Per-city subset with identifiers, location, elevations, conventional SUHI, elevation-matched SUHI, and bias. |
| Fig4_slope_sensitivity | Figure 4 | SUHI-elevation slope and 95% CI for each matching definition. |
| Fig5_pixel_gradient | Figure 5 | Per-window spatial-block bootstrap gradient estimates. |

## Additional derived data

| File | Use |
|---|---|
| data/r173_reference_pixel_lapse_models.csv | Figure 5 input. |
| data/r212_chelsa_vs_modis_lapse.csv | Figure 6 input. |
| data/coast.zip | Natural Earth coastline geometry used to draw Figure 3. |

Raw third-party input products are not redistributed. See `DATASETS_AND_LINKS.csv`.
