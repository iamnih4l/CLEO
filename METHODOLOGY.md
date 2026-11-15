# CLEO Scientific Methodology (`METHODOLOGY.md`)
## Harmonization of MODIS and VIIRS Active-Fire Observations (2000–2026)

### 1. Physical & Orbital Characteristics of Satellite Instruments
Active-fire hotspots represent the center of a satellite pixel flagged by a contextual thermal-anomaly algorithm at the moment of satellite overpass. Harmonizing observations across instruments requires accounting for their distinct spatial footprints, spectral channels, orbital overpass times, and operational lifespans documented by [NASA Earthdata FIRMS](https://www.earthdata.nasa.gov/data/tools/firms).

| Instrument / Platform | Product Codes | Nominal Spatial Resolution | Spectral Detection Channels | Equator Crossing (Local Time) | Operational Archive Window | Confidence Scale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MODIS Terra** ([EOS AM-1](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_MODIS_Firehotspots.html)) | `MOD14` / `MCD14ML` (SP) / `MCD14DL` (NRT) Collection 6.1 | `1,000 m` (`1.0 km²` at nadir) | Channels 21/22 (`~3.96 µm`) & Channel 31 (`~11 µm`) | `10:30` (Descending) / `22:30` (Ascending) | `2000-11-01` – Present | Numeric `0–100%` (`<30%` Low, `30–79%` Nominal, `>=80%` High) |
| **MODIS Aqua** ([EOS PM-1](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_MODIS_Firehotspots.html)) | `MYD14` / `MCD14ML` (SP) / `MCD14DL` (NRT) Collection 6.1 | `1,000 m` (`1.0 km²` at nadir) | Channels 21/22 (`~3.96 µm`) & Channel 31 (`~11 µm`) | `13:30` (Ascending) / `01:30` (Descending) | `2002-07-03` – Present | Numeric `0–100%` (`<30%` Low, `30–79%` Nominal, `>=80%` High) |
| **VIIRS Suomi-NPP** ([S-NPP](https://www.earthdata.nasa.gov/data/instruments/viirs/viirs-i-band-375-m-active-fire-data)) | `VNP14IMG` (SP) / `VNP14IMGT_NRT` Collection 2 | `375 m` (`0.1406 km²` at nadir) | I4 (`3.55–3.93 µm`), I5 (`10.5–12.4 µm`) & M13 (`3.97–4.13 µm` for FRP) | `13:30` (Ascending) / `01:30` (Descending) | `2012-01-20` – `2026-11-02 15:40 UTC` ([LANCE Transition](https://www.earthdata.nasa.gov/news/blog/transitioning-from-suomi-npp-noaa-20-noaa-21-what-lance-users-need-know)) | Categorical `l` (Low), `n` (Nominal), `h` (High) |
| **VIIRS NOAA-20** ([JPSS-1](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html)) | `VJ114IMG` (SP) / `VJ114IMGT_NRT` Collection 2 | `375 m` (`0.1406 km²` at nadir) | I4 (`3.55–3.93 µm`), I5 (`10.5–12.4 µm`) & M13 (`3.97–4.13 µm`) | `13:30` (Ascending, ~50 min behind N21) | `2018-04-01` – Present | Categorical `l` (Low), `n` (Nominal), `h` (High) |
| **VIIRS NOAA-21** ([JPSS-2](https://www.earthdata.nasa.gov/data/instruments/viirs/viirs-i-band-375-m-active-fire-data)) | `VJ214IMG` / `VIIRS_NOAA21_NRT` Collection 2 | `375 m` (`0.1406 km²` at nadir) | I4 (`3.55–3.93 µm`), I5 (`10.5–12.4 µm`) & M13 (`3.97–4.13 µm`) | `13:30` (Ascending, ~50 min ahead of N20) | `2024-01-17` – Present | Categorical `l` (Low), `n` (Nominal), `h` (High) |

### 2. Eight-Stage Harmonization Pipeline
#### Stage 1: Data Ingestion
Ingests CSV hotspot records from the [NASA FIRMS Area API](https://firms.modaps.eosdis.nasa.gov/api/area/) (`/api/area/csv/[MAP_KEY]/[SOURCE]/[BBOX]/[DAY_RANGE]`) or historical archive files from [NASA FIRMS Archive Download](https://firms.modaps.eosdis.nasa.gov/download/). Standard Processing (`SP`) records are prioritized for historical baselines, while Near Real-Time (`NRT`/`RT`/`URT`) records are flagged separately due to multi-month SP lag.

#### Stage 2: Source Identification
Parses `instrument`, `satellite` (`Terra`/`T`, `Aqua`/`A`, `N`/`S-NPP`, `N20`/`NOAA-20`, `N21`/`NOAA-21`), and `version` (`6.1`, `6.1NRT`, `2.0`, `2.0NRT`, `2.0RT`, `2.0URT`) to assign canonical `source_sensor` (`MODIS` vs. `VIIRS`), `collection`, and `source_type` (`SP` vs. `NRT`).

#### Stage 3: Schema Normalization
Maps heterogeneous sensor columns into CLEO's common internal structure while retaining `original_attributes` verbatim:
- `observation_id`: Deterministic hash of `(source_sensor, satellite, acq_date, acq_time_utc, latitude, longitude)`
- `source_sensor`: `'MODIS' | 'VIIRS'`
- `satellite`: `'Terra' | 'Aqua' | 'Suomi-NPP' | 'NOAA-20' | 'NOAA-21'`
- `instrument`: `'MODIS' | 'VIIRS'`
- `acquisition_date`: ISO-8601 `YYYY-MM-DD` (UTC)
- `acquisition_time_utc`: Zero-padded 4-digit UTC string `HHMM` (e.g., `1` -> `'0001'`, `631` -> `'0631'`)
- `latitude`, `longitude`: Decimal degrees (`WGS84`)
- `confidence_raw`: Native string or numeric value (`83`, `'nominal'`, `'n'`, `'h'`, `'l'`)
- `confidence_category`: Harmonized tier (`'LOW' | 'NOMINAL' | 'HIGH' | 'UNKNOWN'`)
- `fire_radiative_power`: Pixel-integrated FRP in megawatts (`MW`, `null` when missing)
- `brightness_primary_k`: `brightness` (MODIS Channel 21/22) or `bright_ti4` (VIIRS I4) in Kelvin
- `brightness_secondary_k`: `bright_t31` (MODIS Channel 31) or `bright_ti5` (VIIRS I5) in Kelvin
- `pixel_area_km2`: Instantaneous scan-track footprint $\text{scan} \times \text{track}$ ($\text{km}^2$)
- `daynight`: `'D' | 'N'`
- `product_version`: e.g., `'6.1NRT'`, `'2.0NRT'`, `'6.1'`, `'2.0'`
- `source_type`: `'SP' | 'NRT' | 'VERIFIED_ARCHIVE' | 'SYNTHETIC_DEMO_FIXTURE'`

#### Stage 4: Quality Control & Confidence Interpretation
1. **Coordinate Validation**: Rejects records with non-numeric coordinates or outside $\text{lat} \in [-90, 90]$, $\text{lon} \in [-180, 180]$.
2. **Duplicate Record Check**: Deduplicates exact matches on `(source_sensor, satellite, acquisition_date, acquisition_time_utc, latitude, longitude)`.
3. **Missing-Value Handling**: Missing FRP or confidence values are stored as `null` (`UNKNOWN`), never coerced to `0.0 MW` or `0%`.
4. **Sensor-Specific Confidence Mapping**:
   - **MODIS (`0–100%`)**: Per the [MODIS Collection 6 User's Guide](https://www.earthdata.nasa.gov/sites/default/files/imported/MODIS_C6_Fire_User_Guide_B.pdf), $0 \le c < 30 \rightarrow \text{LOW}$, $30 \le c < 80 \rightarrow \text{NOMINAL}$, $80 \le c \le 100 \rightarrow \text{HIGH}$. (For specific land-use studies such as [Majumdar 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12297426/), a $>50\%$ MODIS threshold is also supported).
   - **VIIRS (`l`/`n`/`h`)**: Per the [VIIRS 375m Active Fire User Guide](https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf), `'l'`/`'low'` $\rightarrow \text{LOW}$ (often associated with daytime sun glint or South Atlantic Magnetic Anomaly prior to filtering), `'n'`/`'nominal'` $\rightarrow \text{NOMINAL}$, `'h'`/`'high'` $\rightarrow \text{HIGH}$ (saturated I4 pixels corroborated by thermal tests).
5. **Static Non-Fire Filtering**: Where Standard Processing (`SP`) `type` is present (`MCD14ML`/`VNP14IMG`), CLEO allows filtering to `type = 0` (presumed vegetation fire) to exclude `type = 1` (active volcano), `type = 2` (other static land source/industrial flare), and `type = 3` (offshore gas flare).

#### Stage 5: Spatial Harmonization (Common Grid & Active Cell-Days)
Because a single burning fire perimeter of $1\text{ km}^2$ can trigger 1 MODIS pixel (`1 km`) but 5 to 10 VIIRS pixels (`375 m`), raw detection counts cannot be directly summed or compared across sensors. CLEO aggregates detections onto a common latitude-longitude grid of configurable step $\Delta\theta \in \{0.10^\circ, 0.25^\circ, 0.50^\circ\}$ (default $0.25^\circ \approx 27.8\text{ km}$ at the equator, matching the GFED4 spatial grid convention):
- **Grid Cell Assignment**:
  $$\text{cell\_lat} = \lfloor \text{lat} / \Delta\theta \rfloor \cdot \Delta\theta, \quad \text{cell\_lon} = \lfloor \text{lon} / \Delta\theta \rfloor \cdot \Delta\theta$$
- **Exact Spherical Cell Area ($\text{km}^2$)**:
  $$A(\phi_1, \phi_2, \Delta\lambda) = R_\oplus^2 \cdot \left(\Delta\lambda \cdot \frac{\pi}{180}\right) \cdot \left|\sin\left(\phi_2 \frac{\pi}{180}\right) - \sin\left(\phi_1 \frac{\pi}{180}\right)\right|, \quad R_\oplus = 6371.0088\text{ km}$$
- **Harmonized Metrics Computed per Grid Cell**:
  1. **Unique Active Cell-Days**: Count of distinct `(cell_id, acquisition_date)` pairs with $\ge 1$ nominal/high detection. This metric substantially reduces the resolution-induced inflation between `375 m` VIIRS clusters and `1 km` MODIS pixels.
  2. **Normalized Spatial Fire Activity Density**: Detections per $1,000\text{ km}^2$ ($1000 \times N_{\text{cell}} / A_{\text{cell}}$) and Active Cell-Days per $1,000\text{ km}^2$.
  3. **Sensor-Specific & Combined FRP Density**: Sum and median FRP ($\text{MW}$) per cell, keeping MODIS and VIIRS series separate alongside combined presence.

#### Stage 6: Temporal Harmonization
All timestamps are normalized to UTC (`acquisition_date` + `acquisition_time_utc`). Aggregations support:
- **Daily** (`YYYY-MM-DD`)
- **Weekly** (ISO week)
- **Monthly** (`YYYY-MM`)
- **Seasonal**: Boreal/Astronomical (`DJF`, `MAM`, `JJA`, `SON`) plus regional fire-year regimes (e.g., the `March–February` Indian Fire-Year defined by [Boschetti & Roy 2008 / Majumdar 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12297426/)).
- **Annual** (`YYYY`)

#### Stage 7: Cross-Sensor Overlap & Co-location Analysis
For the overlapping MODIS–VIIRS era (`2012-01-20` to present):
- **Empirical VIIRS/MODIS Detection Ratio**: Computes the ratio $R_{\text{VM}} = N_{\text{VIIRS}} / N_{\text{MODIS}}$ and excess VIIRS detections ($N_{\text{VIIRS}} - N_{\text{MODIS}}$).
- **Proximity Co-location Matching**: Identifies VIIRS detections occurring on the same UTC date within a configurable great-circle haversine radius $d_{\max} \in \{1.0, 2.0, 5.0\}\text{ km}$ of a MODIS pixel center. Co-located detections are flagged as **Corroborated Thermal Anomalies** while preserving all individual satellite records (never deleting nearby detections as assumed duplicates, since consecutive orbits ~50–60 minutes apart observe active fire progression).

#### Stage 8: Statistical Anomaly & Baseline Methodology
When historical baseline observations exist ($N \ge 5$ historical periods), CLEO computes non-parametric statistics that are resilient to extreme wildfire spikes:
- **Baseline Median ($M$)**: $\text{median}(X)$ across historical reference periods.
- **Median Absolute Deviation ($\text{MAD}$)**:
  $$\text{MAD} = \text{median}(|X_i - M|)$$
- **Robust Z-Score ($z_{\text{rob}}$)**:
  $$z_{\text{rob}} = \frac{0.6745 \cdot (x - M)}{\text{MAD}}$$
  (where $0.6745 \approx 1 / \Phi^{-1}(0.75)$ makes $\text{MAD} / 0.6745$ a consistent estimator of standard deviation under normality).
- **Anomaly Classification Thresholds**:
  - `Below Historical Activity`: $z_{\text{rob}} < -1.0$ or $x < P_{25}$
  - `Typical Activity`: $-1.0 \le z_{\text{rob}} < 1.0$ ($P_{25} \le x < P_{75}$)
  - `Elevated Activity`: $1.0 \le z_{\text{rob}} < 2.0$ ($P_{75} \le x < P_{90}$)
  - `Unusually Elevated Activity`: $z_{\text{rob}} \ge 2.0$ or $x \ge P_{90}$

### 3. Explicit Methodological & Scientific Limitations
1. **Harmonized Aggregation vs. Physical Sensor Calibration**: CLEO performs common space-time aggregation (`Active Cell-Days` and equal-area grid density) and sensor-stratified comparison. It does **not** apply a synthetic multiplier to scale MODIS counts up to VIIRS counts or vice versa, because the VIIRS/MODIS detection ratio varies non-linearly by biome, fire size distribution, time of day, and scan angle ([Majumdar 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12297426/)).
2. **Hotspots Are Not Burned Area**: Active-fire pixels represent thermal anomalies at the instant of satellite overpass—not total burned area perimeters (`MCD64A1`). Cloud cover, heavy smoke plumes, dense forest canopy, or fires igniting and extinguishing between satellite overpasses cause omission errors ([NASA FIRMS FAQ](https://www.earthdata.nasa.gov/data/tools/firms/faq)).
3. **VIIRS I4 Saturation & Hybrid FRP**: The VIIRS `375 m` I4 channel (`3.55–3.93 µm`) frequently saturates at `367 K` over intense fires; consequently, VIIRS FRP retrievals since 2015 use a hybrid algorithm combining `375 m` I-band and `750 m` M13 (`3.973–4.128 µm`) radiances ([FIRMS VIIRS Description](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html)).
4. **Suomi-NPP Decommissioning (November 2, 2026)**: Delivery of new Suomi-NPP VIIRS science data ceased on **November 2, 2026 at 15:40 UTC** ([NASA Earthdata LANCE Notice](https://www.earthdata.nasa.gov/news/blog/transitioning-from-suomi-npp-noaa-20-noaa-21-what-lance-users-need-know)). Post-November 2026 VIIRS monitoring relies on NOAA-20 (`JPSS-1`) and NOAA-21 (`JPSS-2`), which must be accounted for when comparing multi-satellite VIIRS sums across late 2026.
5. **Not an Emergency Dispatch System**: Statistical anomalies identify historical and near-real-time thermal deviations for scientific and land-management intelligence; they are not confirmed ground wildfire emergencies or predictive fire-weather forecasts.
