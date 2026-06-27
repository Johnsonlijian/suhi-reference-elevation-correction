# Data Dictionary

File: `data/per_city_reference_elevation_bias.csv`

| Column | Type | Description |
|---|---:|---|
| `label` | string | GHS-SMOD urban-centre identifier. |
| `lon` | numeric | Urban-centre centroid longitude in decimal degrees. |
| `lat` | numeric | Urban-centre centroid latitude in decimal degrees. |
| `urban_elev_m` | numeric | Mean urban-core elevation from GMTED2010, metres. |
| `rural_ref_elev_m` | numeric | Mean elevation of the conventional rural reference, metres. |
| `reference_elevation_surplus_m` | numeric | Rural-reference elevation minus urban-core elevation, metres. |
| `conventional_SUHI_C` | numeric | Satellite SUHI using the conventional 50 km rural reference, degrees Celsius. |
| `elevation_matched_SUHI_C` | numeric | Satellite SUHI using the elevation-matched rural reference, degrees Celsius. |
| `reference_elevation_bias_C` | numeric | Conventional minus elevation-matched SUHI; subtract this from the conventional estimate to apply the correction, degrees Celsius. |
| `correction_uncertainty_C` | numeric | Per-city uncertainty proxy across matching definitions, degrees Celsius. |
| `matched_ref_pixels` | integer | Number of rural-reference pixels retained after elevation matching. |
| `trust_flag` | string | Practical quality flag derived from matched-reference support and correction stability. |

Raw input products are public datasets and are not redistributed here. See `README.md` for source attribution.
