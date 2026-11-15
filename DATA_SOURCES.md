# CLEO External Resources & Data Provenance (`DATA_SOURCES.md`)

Every dataset, API endpoint, scientific publication, mapping service, and software library integrated into CLEO is documented below with its canonical URL.

## 1. Official NASA Datasets & APIs Used
1. **NASA Fire Information for Resource Management System (FIRMS)**
   - **Portal**: [https://firms.modaps.eosdis.nasa.gov/](https://firms.modaps.eosdis.nasa.gov/)
   - **NASA Earthdata Tool Page**: [https://www.earthdata.nasa.gov/data/tools/firms](https://www.earthdata.nasa.gov/data/tools/firms)
   - **FAQ & Sensor Documentation**: [https://www.earthdata.nasa.gov/data/tools/firms/faq](https://www.earthdata.nasa.gov/data/tools/firms/faq)
2. **MODIS Collection 6.1 Active Fire Products (`MCD14ML` Standard Processing & `MCD14DL` Near Real-Time)**
   - **Instruments**: Terra MODIS (EOS AM-1, `2000-11-01` – present) and Aqua MODIS (EOS PM-1, `2002-07-03` – present)
   - **Attribute Specification**: [https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_MODIS_Firehotspots.html](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_MODIS_Firehotspots.html)
   - **User's Guide**: [MODIS Collection 6 Active Fire Product User's Guide, Revision B](https://www.earthdata.nasa.gov/sites/default/files/imported/MODIS_C6_Fire_User_Guide_B.pdf)
   - **DOIs**: `10.5067/FIRMS/MODIS/MCD14DL.NRT.0061` (NRT) and `10.5067/FIRMS/MODIS/MCD14ML` (SP)
3. **VIIRS 375 m Collection 2 Active Fire Products (`VNP14IMG`, `VJ114IMG`, `VJ214IMG`)**
   - **Instruments**: Suomi-NPP VIIRS (`2012-01-20` – `2026-11-02 15:40 UTC`), NOAA-20 / JPSS-1 VIIRS (`2018-04-01` – present), and NOAA-21 / JPSS-2 VIIRS (`2024-01-17` – present)
   - **Instrument Data Page**: [https://www.earthdata.nasa.gov/data/instruments/viirs/viirs-i-band-375-m-active-fire-data](https://www.earthdata.nasa.gov/data/instruments/viirs/viirs-i-band-375-m-active-fire-data)
   - **Attribute Specification**: [https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html)
   - **User's Guide**: [Collection 2 VIIRS 375 m Active Fire User's Guide v1.2](https://www.earthdata.nasa.gov/s3fs-public/2025-06/VIIRS_C2_AF-375m_User_Guide_1.2.pdf)
   - **Suomi-NPP LANCE Operational Transition Bulletins**:
     - [Transitioning From Suomi NPP to NOAA-20 and NOAA-21: What LANCE Users Need to Know](https://www.earthdata.nasa.gov/news/blog/transitioning-from-suomi-npp-noaa-20-noaa-21-what-lance-users-need-know)
     - [Transitioning from Suomi NPP VIIRS & OMPS: What FIRMS Users Need to Know](https://www.earthdata.nasa.gov/news/blog/transitioning-from-suomi-npp-viirs-omps-what-firms-users-need-know)
   - **DOIs**: `10.5067/FIRMS/VIIRS/VNP14IMGT_NRT.002` and `10.5067/FIRMS/VIIRS/VJ114IMGT_NRT.002`
4. **NASA FIRMS Web Services & Archive Endpoints**
   - **API Overview**: [https://firms.modaps.eosdis.nasa.gov/api/](https://firms.modaps.eosdis.nasa.gov/api/)
   - **Area Hotspot CSV API**: [https://firms.modaps.eosdis.nasa.gov/api/area/](https://firms.modaps.eosdis.nasa.gov/api/area/)
   - **Data Availability API**: [https://firms.modaps.eosdis.nasa.gov/api/data_availability/](https://firms.modaps.eosdis.nasa.gov/api/data_availability/)
   - **MAP_KEY Registration**: [https://firms.modaps.eosdis.nasa.gov/api/map_key/](https://firms.modaps.eosdis.nasa.gov/api/map_key/)
   - **Standard Archive Download**: [https://firms.modaps.eosdis.nasa.gov/download/](https://firms.modaps.eosdis.nasa.gov/download/)
   - **Python API Academy Tutorial (Source of 30 Verbatim Reference Detections)**: [https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html](https://firms.modaps.eosdis.nasa.gov/content/academy/data_api/firms_api_use.html)

## 2. Verbatim Regional NASA FIRMS Mirrors & Peer-Reviewed Benchmark Studies
1. **UN OCHA Humanitarian Data Exchange (HDX) — NASA FIRMS Regional Feeds (Source of 40 Verbatim November 2026 Reference Detections)**:
   - [South Asia VIIRS NOAA-20 C2 24h CSV](https://data.humdata.org/en/dataset/nasa-firms-active-fire-south-asia-viirs/resource/b8a89bec-56e5-4a69-9622-b01133374654)
   - [Europe VIIRS NOAA-21 C2 48h CSV](https://data.humdata.org/dataset/nasa-firms-active-fire-europe-viirs/resource/4b4707d3-c2ba-4d5c-ba1e-9451d40e674d)
   - [Northern & Central Africa VIIRS Suomi-NPP C2 7d CSV](https://data.humdata.org/en/dataset/nasa-firms-active-fire-northern-and-central-africa-viirs/resource/ae90f850-8f11-4f74-8554-bc4f01abe4bf)
   - [Southeast Asia MODIS C6.1 Terra/Aqua 24h CSV](https://data.humdata.org/en/dataset/nasa-firms-active-fire-southeast-asia-modis/resource/a1e8cff6-b0b8-4ff0-a161-6c67726b3074)
2. **Decadal (2012–2023) VIIRS vs. MODIS Inter-Comparison Benchmark**:
   - Majumdar, D. (2025). *Decadal (2012–2023) account of spatio-temporal variability in satellite-detected biomass fires on Indian landmass and their fire radiative power*. **Scientific Reports**, 15, 27233. [https://pmc.ncbi.nlm.nih.gov/articles/PMC12297426/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12297426/)
3. **Mediterranean Multi-Year Seasonal & Temporal Purity Benchmark (2016–2025)**:
   - *Automated Event-Based Burned-Area Delineation and dNBR Recovery Assessment on Zakynthos, Greece (2016–2025 Suomi-NPP VIIRS Cohort)*. **Forests** (MDPI), 17(10), 1144 (2026). [https://www.mdpi.com/1999-4907/17/10/1144](https://www.mdpi.com/1999-4907/17/10/1144)
4. **Global 2000–2026 NASA FIRMS Daily File Inventory Benchmark**:
   - *2000–2026 Global Active Fire Dataset Inventory (18,174 Daily CSV Files Across MODIS_SP, VIIRS_SNPP_SP, VIIRS_NOAA20_SP, and NRT Streams)*. [https://blog.csdn.net/m0_63269495/article/details/160409628](https://blog.csdn.net/m0_63269495/article/details/160409628)

## 3. Mapping Resources & Open-Source Libraries
- **Esri ArcGIS Online MapServer Basemap Tiles**:
  - [World Dark Gray Base (`World_Dark_Gray_Base`)](https://www.arcgis.com/home/item.html?id=648fc3a72e40477a98935c2bd128d5c9) (`https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}`)
  - [World Imagery (`World_Imagery`)](https://community.esri.com/en/discussion/1567734/inquiry-about-world-imagery-service-integration-and-response-differentiation) (`https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`)
- **Frontend & Visualization Libraries (Loaded via Public CDN)**:
  - **Leaflet `1.9.4`**: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js` & `leaflet.css` (BSD-2-Clause License)
  - **Chart.js `4.4.1`**: `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js` (MIT License)
  - **Tailwind CSS `3.4.17`**: `https://cdn.tailwindcss.com/3.4.17` (MIT License)
  - **Lucide Icons `0.460.0`**: `https://unpkg.com/lucide@0.460.0/dist/umd/lucide.min.js` (ISC License)
