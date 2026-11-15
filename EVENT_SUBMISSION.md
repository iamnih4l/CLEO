# 2026 NASA Space Apps Challenge — Official Submission Package (`EVENT_SUBMISSION.md`)

## 1. Project Title
**CLEO — Unified Earth Fire Intelligence & Historical Burning Activity Platform**

## 2. Project Summary (164 Words — Within Mandatory 50–200 Word Limit)
**CLEO** transforms more than two decades of fragmented satellite active-fire observations from [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) into a unified, sensor-aware **Burning Activity Calendar** and geospatial intelligence platform. While **NASA MODIS** (`1 km` resolution aboard Terra since November 2000 and Aqua since July 2002) provides a 26-year baseline, **NASA/NOAA VIIRS** (`375 m` resolution aboard Suomi-NPP from January 2012 until its November 2, 2026 LANCE decommissioning, NOAA-20 since 2018, and NOAA-21 since 2024) detects `6.3x` to `7.7x` more raw hotspots due to its smaller pixel footprint and higher sensitivity to low-intensity fires. Simply merging raw CSV files creates severe artificial trend distortions. CLEO solves this through an **8-stage harmonization pipeline**: reconciling numeric (`0–100%`) and categorical (`low`/`nominal`/`high`) confidence scales, projecting observations onto an equal-area spherical spatial grid (`0.10°–0.50°`) to compute **Unique Active Cell-Days** and normalized density (`detections / 1,000 km²`), and applying non-parametric Median Absolute Deviation (`MAD`) robust z-scores to isolate genuine burning anomalies within any custom Area of Interest.

## 3. Detailed Technical Description
CLEO is architected around eight integrated modules:
1. **8-Stage MODIS–VIIRS Harmonization Engine (`python/cleo_engine.py` & `cleo_platform.html`)**:
   - **Ingestion & Source Identification**: Supports live server-proxied queries to the [NASA FIRMS Area API](https://firms.modaps.eosdis.nasa.gov/api/area/), availability checks via the [Data Availability API](https://firms.modaps.eosdis.nasa.gov/api/data_availability/), and client/server CSV archive ingestion (`MCD14ML`, `MCD14DL`, `VNP14IMG`, `VJ114IMG`, `VJ214IMG`).
   - **Schema & Confidence Normalization**: Normalizes heterogeneous MODIS (`brightness`, `bright_t31`, numeric confidence `0–100%`) and VIIRS (`bright_ti4`, `bright_ti5`, categorical confidence `l`/`n`/`h`) schemas while retaining all original attributes and missing-value nulls (`never coercing nulls to zero`).
   - **Spherical Equal-Area Spatial Aggregation**: Computes exact spherical grid cell areas ($A = R_\oplus^2 \Delta\lambda |\sin\phi_2 - \sin\phi_1|$) at configurable resolutions (`0.10°`, `0.25°`, `0.50°`), calculating **Unique Active Cell-Days**, **Normalized Spatial Density** ($\text{detections}/1,000\text{ km}^2$), and sensor-separated FRP metrics.
   - **Cross-Sensor Overlap & Co-location Matching**: Computes empirical VIIRS/MODIS detection ratios and haversine proximity co-location (`1.0–5.0 km` same-UTC-day corroboration) without destructively merging distinct satellite overpasses.
2. **Interactive Global Fire Map & AOI Engine**:
   - Built with Leaflet `1.9.4` and keyless Esri ArcGIS MapServer layers (`World_Dark_Gray_Base` and `World_Imagery`).
   - Distinguishes MODIS (`1 km` amber squares) from VIIRS (`375 m` ember circles), renders scan × track footprint geometry, and supports Bounding-Box and Polygon AOI selection with local ray-casting point-in-polygon filtering.
3. **Multi-Perspective Burning Activity Calendar & MAD Anomaly Intelligence**:
   - **Annual Heatmap** (Year × Month matrix), **Monthly Daily Grid** (with daily MODIS/VIIRS bars and FRP readouts), and **Historical Regime Comparison** (`Pre-VIIRS` vs. `Overlap Era`).
   - **Robust Anomaly Detection**: Uses historical median ($M$), Median Absolute Deviation ($\text{MAD}$), and robust z-scores ($z_{\text{rob}} = 0.6745(x - M)/\text{MAD}$) alongside percentiles ($P_{25}, P_{50}, P_{75}, P_{90}$).

## 4. Actual NASA Datasets & Resources Used
- [NASA FIRMS (Fire Information for Resource Management System)](https://firms.modaps.eosdis.nasa.gov/) & [NASA Earthdata FIRMS Portal](https://www.earthdata.nasa.gov/data/tools/firms)
- [MODIS Collection 6.1 Active Fire (`MCD14ML` SP / `MCD14DL` NRT)](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_MODIS_Firehotspots.html) (`doi:10.5067/FIRMS/MODIS/MCD14DL.NRT.0061`, `doi:10.5067/FIRMS/MODIS/MCD14ML`)
- [VIIRS 375 m Collection 2 Active Fire (`VNP14IMG` S-NPP, `VJ114IMG` NOAA-20, `VJ214IMG` NOAA-21)](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html) (`doi:10.5067/FIRMS/VIIRS/VNP14IMGT_NRT.002`, `doi:10.5067/FIRMS/VIIRS/VJ114IMGT_NRT.002`)
- [NASA FIRMS Area API](https://firms.modaps.eosdis.nasa.gov/api/area/), [Data Availability API](https://firms.modaps.eosdis.nasa.gov/api/data_availability/), and [Python API Academy Tutorial](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html)
- [NASA LANCE Suomi-NPP Transition Notice (Nov 2, 2026)](https://www.earthdata.nasa.gov/news/blog/transitioning-from-suomi-npp-noaa-20-noaa-21-what-lance-users-need-know)

## 5. Other Data & Resources
- [UN OCHA Humanitarian Data Exchange (HDX) NASA FIRMS Regional Feeds](https://data.humdata.org/en/dataset/nasa-firms-active-fire-south-asia-viirs/resource/b8a89bec-56e5-4a69-9622-b01133374654)
- [Majumdar (2025), *Scientific Reports* 15:27233 — Decadal (2012–2023) VIIRS vs. MODIS Biomass Fire Inter-Comparison](https://pmc.ncbi.nlm.nih.gov/articles/PMC12297426/)
- [MDPI *Forests* (2026) 17(10):1144 — Zakynthos 2016–2025 VIIRS S-NPP Temporal Diagnostic Cohort](https://www.mdpi.com/1999-4907/17/10/1144)
- [Esri ArcGIS Online Dark Gray Canvas & World Imagery MapServer Tiles](https://www.arcgis.com/home/item.html?id=648fc3a72e40477a98935c2bd128d5c9)

## 6. Super Intelligence (SI) Use Disclosure
AI assistance was used for software architecture scaffolding, implementing the Python and JavaScript 8-stage MODIS–VIIRS harmonization and MAD statistical algorithms, verified against 15 automated QA unit tests (`tests/test_cleo_engine.py`), and formatting documentation. Zero AI-generated raster images, audio, or video were used, and no NASA logos or insignia were generated. Full details are provided in `SI_DISCLOSURE.md`.

## 7. 30-Second Demonstration Video Script
- **0:00–0:05 | Hook & Problem**: *(View: CLEO Overview & Sensor Comparison)* "For 26 years, NASA's MODIS and VIIRS satellites have tracked Earth's fires—but because 375-meter VIIRS detects over 7 times more raw hotspots than 1-kilometer MODIS, simply merging CSVs distorts historical climate trends."
- **0:05–0:13 | Map & Polygon AOI Selection**: *(Action: Click 'Explore Map', select 'South & Southeast Asia' AOI or draw a custom Polygon)* "Meet CLEO. On our interactive map, 1-kilometer MODIS squares and 375-meter VIIRS circles are visually distinct and locally filtered by exact polygon geometry."
- **0:13–0:22 | Harmonized Burning Activity Calendar**: *(Action: Switch to 'Fire Calendar', toggle metric to 'Harmonized Active Cell-Days' & inspect 2012–2025 matrix)* "CLEO's 8-stage harmonization pipeline normalizes detections onto an equal-area spherical grid, powering a multi-decade Burning Activity Calendar across Annual, Monthly, and Daily views."
- **0:22–0:30 | Anomaly Detection & Provenance Export**: *(Action: Click 'Anomaly Intelligence' -> highlight 2021 peak z-score +2.68 -> click 'Export GeoJSON')* "Using non-parametric Median Absolute Deviation z-scores, CLEO pinpoints unusually elevated burning periods and exports provenance-stamped GeoJSON and CSV intelligence."

## 8. Seven-Slide Presentation Outline
1. **Slide 1 — Title & Mission**: *CLEO: Harmonizing 26 Years of NASA MODIS & VIIRS Fire Intelligence* — Positioning, team roles, and challenge objective.
2. **Slide 2 — The Scientific Problem**: Why raw concatenation fails — `1 km` MODIS (`1.0 km²`) vs. `375 m` VIIRS (`0.14 km²`), the `6.3x–7.7x` detection jump after 2012 ([Majumdar 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12297426/)), incompatible confidence scales (`0–100%` vs. `l/n/h`), and the November 2, 2026 Suomi-NPP decommissioning.
3. **Slide 3 — CLEO's 8-Stage Harmonization Architecture**: Ingestion -> Source ID -> Schema Normalization -> Quality Control -> Spherical Equal-Area Grid (`Active Cell-Days` & density per `1,000 km²`) -> UTC Temporal Alignment -> Cross-Sensor Co-location -> Historical Aggregation.
4. **Slide 4 — Interactive Geospatial Map & Local Polygon AOI Engine**: Visual differentiation of MODIS and VIIRS footprints, scan × track pixel geometry, and API bounding-box retrieval vs. exact local polygon ray-casting.
5. **Slide 5 — The Burning Activity Calendar**: Annual Year × Month heatmap, Monthly daily sensor-split cells, and Pre-VIIRS (`2000–2011`) vs. Overlap (`2012–2026`) regime comparisons.
6. **Slide 6 — Non-Parametric Anomaly Intelligence**: Median and Median Absolute Deviation ($\text{MAD}$) robust z-scores ($z_{\text{rob}}$) and percentile classification (`Below Historical`, `Typical`, `Elevated`, `Unusually Elevated`) with confidence/coverage caveats.
7. **Slide 7 — Live Demonstration, Provenance Exports & Open Science Impact**: Live NASA FIRMS API proxy, drag-and-drop CSV archive validator, provenance-stamped GeoJSON/CSV exports, and methodological transparency.

## 9. Deployment & Repository Links
- **Public Live Deployment URL**: `[DEPLOYMENT_URL_PLACEHOLDER]`
- **Public GitHub Repository URL**: `[REPOSITORY_URL_PLACEHOLDER]`
- **30-Second Demo Video / 7-Slide Deck URL**: `[DEMO_URL_PLACEHOLDER]`
