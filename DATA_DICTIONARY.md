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
| reference_elevation_bias_C | numeric | Conventional minus elevation-matched SUHI for the released conventional-reference implementation. |
| correction_uncertainty_C | numeric | Matching-definition sensitivity: standard deviation of the per-city bias across five matching-band definitions (+/-100 m/50 km, +/-100 m/100 km, +/-200 m/100 km, +/-500 m/100 km, and closest-quartile/100 km). This is not a full remote-sensing retrieval or pixel-sampling uncertainty. |
| matched_ref_pixels | integer | Number of rural-reference pixels retained after elevation matching under the primary +/-100 m/50 km definition. |
| trust_flag | string | "ok" if matched_ref_pixels >= 30; "low_pixel" otherwise. |
| ranking_analysis_included | boolean | True for cities included in the ranking analysis and Figure 1 statistics. False only for the five retained extreme retrieval outliers with \|conventional_SUHI_C\| > 15 C or \|elevation_matched_SUHI_C\| > 15 C. |
| exclusion_reason | string | Reason for exclusion from ranking analysis; blank for included cities. The excluded rows remain in the released table for transparency. |

## data/source_data.xlsx

| Sheet | Figures | Description |
|---|---|---|
| Figs1_3_per_city_bias | Figures 1 and 3 | Full released per-city table used for Figures 1 and 3, including correction sensitivity and trust/exclusion flags. |
| Table1_surplus_class_summary | Table 1 | Surplus-class summary computed from the released per-city table. |
| Fig4_slope_sensitivity | Figure 4 | SUHI-elevation slope and 95% CI for each reference design, with covariance/source metadata columns. |
| Fig5_pixel_gradient | Figure 5 | Per-window spatial-block bootstrap gradient estimates. |
| Fig5_gradient_summary | Figure 5 | Pooled/day/night gradient summary and free-air lapse reference line used for Figure 5 annotation. |
| Fig6_CHELSA_MODIS_lapse | Figure 6 | CHELSA air-temperature and MODIS skin-temperature lapse estimates used for the attenuation benchmark. |
| Outlier_audit | Figures 1 and 3 | Retained extreme-retrieval rows excluded from ranking-display/top-100 statistics, with threshold flag and contamination note. |

## Additional derived data

| File | Use |
|---|---|
| data/r173_reference_pixel_lapse_models.csv | Figure 5 input. |
| data/fig4_slope_sensitivity.csv | Figure 4 source table. |
| data/fig5_gradient_summary.csv | Figure 5 pooled-gradient source table. |
| data/outlier_audit.csv | Audit table for the five retained extreme retrieval outliers. |
| data/r212_chelsa_vs_modis_lapse.csv | Figure 6 input. |
| data/coast.zip | Natural Earth 110 m coastline geometry used to draw Figure 3; redistributed here under Natural Earth's public-domain terms. |

Large raw third-party input products are not redistributed. The small Natural Earth coastline shapefile used for Figure 3 is redistributed with its bundled README and version file. See `DATASETS_AND_LINKS.csv`.
