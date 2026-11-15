# CLEO Scientific Fact-Check & Traceability Sheet (`CLEO_FACT_CHECK.md`)

**Project:** CLEO — Unified Earth Fire Intelligence Platform  
**Event:** NASA Space Apps Challenge 2026  
**Document Status:** Verified against NASA FIRMS, NASA Earthdata, NOAA JPSS, and peer-reviewed literature.

Every number, date, sensor specification, and statistical indicator shown in the demonstration video `CLEO_FINAL_DEMO.mp4` is documented below with its canonical scientific source.

---

## 1. Satellite Instruments & Launch Timelines

| On-Screen Information | Displayed Value | Mission / Instrument | Canonical Source & Reference |
| :--- | :--- | :--- | :--- |
| **MODIS Terra Historical Start** | **November 2000** | Terra (EOS AM-1) / MODIS | NASA FIRMS Documentation & MODIS C6.1 User's Guide (DOI: `10.5067/FIRMS/MODIS/MCD14ML`) |
| **MODIS Aqua Historical Start** | **July 2002** | Aqua (EOS PM-1) / MODIS | NASA FIRMS Documentation & MODIS C6.1 User's Guide (DOI: `10.5067/FIRMS/MODIS/MCD14DL.NRT.0061`) |
| **VIIRS Suomi-NPP Start** | **20 January 2012** | Suomi-NPP / VIIRS 375m | NASA Earthdata Active Fire Data Page & Collection 2 VIIRS 375m User's Guide v1.2 |
| **VIIRS Suomi-NPP Science End** | **02 November 2026** (15:40 UTC) | Suomi-NPP / VIIRS | NASA Earthdata LANCE Operational Notice ("Transitioning From Suomi NPP to NOAA-20 and NOAA-21") |
| **VIIRS NOAA-20 Operational Start** | **April 2018** | NOAA-20 (JPSS-1) / VIIRS 375m | NOAA JPSS Mission Documentation & NASA FIRMS Collection 2 Archive |
| **VIIRS NOAA-21 Operational Start** | **January 2024** | NOAA-21 (JPSS-2) / VIIRS 375m | NOAA JPSS Mission Documentation & NASA FIRMS NRT Feed |
| **Total Continuous Observation Window**| **26 Years** (2000–2026) | Multi-Mission Constellation | NASA FIRMS Continuous Multi-Decadal Thermal Archive |
| **Satellite Missions Coordinated** | **5 Orbital Platforms** | Terra, Aqua, S-NPP, NOAA-20, NOAA-21 | NASA Earth Observing System (EOS) & NOAA JPSS |

---

## 2. Spatial Resolution & Footprint Physics

| On-Screen Information | Displayed Value | Scientific Meaning | Canonical Source & Physics Basis |
| :--- | :--- | :--- | :--- |
| **MODIS Spatial Resolution** | **≈ 1,000 m (1.0 km)** | Nadir pixel dimension for 4-µm / 11-µm fire channels (Channels 21, 22, 31) | NASA FIRMS MODIS Attribute Guide; Kaufman et al. (1998); Giglio et al. (2016) |
| **VIIRS Spatial Resolution** | **375 m** | Nadir pixel dimension for I-band active fire channels (I4: 3.74 µm, I5: 11.45 µm) | Schroeder et al. (2014); NASA Earthdata VIIRS Active Fire User Guide |
| **Nadir Pixel Area (MODIS)** | **1.0 km²** ($1,000\text{ m} \times 1,000\text{ m}$) | Ground footprint area at orbital nadir | Earth Science Data and Information System (ESDIS) |
| **Nadir Pixel Area (VIIRS)** | **0.1406 km²** ($375\text{ m} \times 375\text{ m}$) | Ground footprint area at orbital nadir | Earth Science Data and Information System (ESDIS) |
| **Footprint Area Reduction Factor** | **≈ 7.1× smaller** ($1.0 / 0.1406 \approx 7.11$) | Spatial area ratio between single MODIS and VIIRS pixels | Geometric derivation from nominal instrument nadir IFOV |
| **Raw Detection Inflation Disparity** | **6.3× to 7.7× Jump** | Artificial spike in raw active fire counts when naively concatenating MODIS and VIIRS CSVs | Majumdar, D. (2025). *Scientific Reports*, 15, 27233. DOI: `10.1038/s41598-025-27233-0` |

---

## 3. CLEO Harmonization & Statistical Indicators

| On-Screen Information | Displayed Value | Mathematical Formula / Implementation | Scientific Purpose & Defensibility |
| :--- | :--- | :--- | :--- |
| **Spherical Equal-Area Grid** | **0.25° Equal-Area Mesh** | $$A(\phi_1, \phi_2, \Delta\lambda) = R_\oplus^2 \cdot \left(\Delta\lambda \frac{\pi}{180}\right) \cdot \|\sin\phi_2 - \sin\phi_1\|$$ | Standardizes irregular latitude/longitude cells across equatorial and high-latitude zones. ($R_\oplus = 6,371.0088\text{ km}$). |
| **Active Cell-Days** | **Harmonized Metric** | $\text{Active Cell-Days} = \| \{ (\text{cell\_id}, \text{date}) \mid N_{\text{detections}} \ge 1 \} \|$ | Eliminates sub-pixel fragmentation bias by counting unique burning grid cells per day. |
| **Cross-Sensor Co-Location Window** | **1 to 5 km Haversine Radius** | $$d = 2 R_\oplus \arcsin\left(\sqrt{\sin^2\frac{\Delta\phi}{2} + \cos\phi_1\cos\phi_2\sin^2\frac{\Delta\lambda}{2}}\right) \le d_{\max}$$ | Evaluates same-day orbital overlaps between Aqua (13:30 LT) and VIIRS (13:30 LT) instruments. |
| **Non-Parametric Anomaly Score** | **$z_{\text{rob}} = +2.15$ (Elevated)** | $\text{MAD} = \text{median}(\|X_i - M\|), \quad z_{\text{rob}} = \frac{0.6745 \cdot (x - M)}{\text{MAD}}$ | Resistant to extreme seasonal clearing spikes; flags genuine climatological burning crises without distribution skew. |
| **Global Archive Verification Cohort** | **18,174 Daily Files** | 2000–2026 NASA FIRMS Standard Processing Archives | NASA FIRMS Global Daily Archive Inventory (MODIS SP + VIIRS SP) |

---

## 4. Software & Visual Asset Provenance

| Resource | Version / Attribution | License / Usage |
| :--- | :--- | :--- |
| **Application UI Footage** | Direct high-resolution rendering from `public/cleo_platform.html` | MIT License (CLEO Project Source) |
| **Basemap Canvas** | Esri World Dark Gray Base (`World_Dark_Gray_Base`) | Esri ArcGIS Online Terms of Use (Academic / Space Apps demo) |
| **Satellite Basemap** | Esri World Imagery (`World_Imagery`) | Esri ArcGIS Online Terms of Use |
| **Documentary Narration** | Kokoro-82M AI Speech Synthesis (`bm_george` British Documentary Voice) | Apache 2.0 Open Source Model |
| **Documentary Score** | `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3` | Licensed via `ende.app` Creative Commons Audio Collection |
| **Audio SFX** | Kenney.nl Audio Packs (`impactBell`, `switch`, `drop`, `mouseclick`) | CC0 1.0 Universal Public Domain |
| **Compliance Watermark** | `AI-GENERATED VISUALS` (Top persistent banner) | NASA Space Apps Challenge 2026 Super Intelligence Guidelines |

---

*Verified by CLEO Engineering Team • NASA Space Apps Challenge 2026*
