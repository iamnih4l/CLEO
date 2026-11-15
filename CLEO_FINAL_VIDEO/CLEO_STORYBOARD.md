# CLEO Demonstration Film Storyboard (`CLEO_STORYBOARD.md`)

**Title:** CLEO — Unified Earth Fire Intelligence & Historical Burning Activity Platform  
**Target Duration:** 28.00 Seconds (840 frames @ 30 fps)  
**Format:** 16:9 Landscape (1920 × 1080)  
**Narration Engine:** Kokoro-82M (`bm_george` British Documentary Narrator)  
**Soundtrack:** Ende.app Atmospheric Documentary Score (`happy-beats-business-moves-vol-12`)

---

## Storyboard Overview & Scene Architecture

```mermaid
timeline
    title CLEO 28-Second Cinematic Documentary Timeline
    00:00 - 04:00 : Scene 1 - Earth's Fire Record : Planetary Orbit & Active Fire Hotspots
    04:00 - 10:00 : Scene 2 - The Numbers Behind the Science : Animated 26-Year Historical Sensor Timeline
    10:00 - 15:00 : Scene 3 - Why Harmonization Matters : 1km vs 375m Spatial Resolution Comparison
    15:00 - 20:00 : Scene 4 - Introducing CLEO : Real Interactive Map, AOI Polygon & Sensor Splitting
    20:00 - 26:00 : Scene 5 - The Burning-Activity Calendar : Heatmap Matrix, Active Cell-Days & MAD z-score
    26:00 - 28:00 : Scene 6 - Closing & Attribution : High Orbital Resolution, Wordmark & NASA FIRMS Credit
```

---

## Detailed Scene Breakdown

### Scene 1: Earth's Fire Record (0.00s – 4.00s)
* **Goal**: Establish the vast global scale of Earth's burning activity and the orbital perspective of Earth observation.
* **Visual Composition**:
  - Deep aerospace midnight black background (`#03050a`).
  - Slowly rotating 3D Earth globe with high-resolution continents, atmospheric glow, and illuminated orbital tracks.
  - Glowing ember active-fire hotspots (`#FF6A00` / `#FF3B30`) pulsing organically across equatorial savannas, boreal forests, and the Amazon basin.
  - Large cinematic typography:
    - `0.5s`: `"EARTH HAS BEEN BURNING."` (Smooth blur-to-focus reveal)
    - `2.2s`: `"SATELLITES HAVE BEEN WATCHING."` (Subtle upward drift)
* **On-Screen Telemetry**:
  - Top Badge: `AI-GENERATED VISUALS` (Space Apps Super Intelligence compliance).
  - Bottom Telemetry: `GLOBAL THERMAL ANOMALY INVENTORY // 2000–2026`.
* **Audio & Music**:
  - `0.00s`: Deep cinematic bell impact (`impactBell_heavy_000.ogg`).
  - Warm ambient synth pad swelling up.
* **Narration**:
  - `0.80s – 3.80s`: *"Earth's fire activity has been observed from space for decades."*

---

### Scene 2: The Numbers Behind the Science (4.00s – 10.00s)
* **Goal**: Present the chronological growth of satellite observations through numerical motion graphics.
* **Visual Composition**:
  - Horizontal animated chronological timeline spanning 2000 to 2026 with illuminated milestone nodes:
    - `4.8s`: **MODIS TERRA** — `NOV 2000` (Morning Orbit, 10:30 LT)
    - `6.0s`: **MODIS AQUA** — `JUL 2002` (Afternoon Orbit, 13:30 LT)
    - `7.2s`: **VIIRS SUOMI-NPP** — `JAN 2012` (Afternoon Orbit, 13:30 LT)
    - `8.4s`: **VIIRS NOAA-20** — `APR 2018` (JPSS-1 Constellation)
    - `9.2s`: **VIIRS NOAA-21** — `JAN 2024` (JPSS-2 Constellation)
  - Animated Numerical Counter (Upper Right):
    - Counts up smoothly from `0` to `26` with label: `"YEARS OF CONTINUOUS OBSERVATIONS"`.
    - Sensor Mission Counter: Counts up to `5 SATELLITE MISSIONS`.
  - Supporting Typography:
    - `"MORE THAN 25 YEARS OF MODIS OBSERVATIONS."`
    - `"VIIRS ADDS FINER-SPATIAL-DETAIL OBSERVATIONS."`
* **Audio & Music**:
  - Rhythm percussion kicks in on strong beat `4.39s` and `8.74s`.
  - Subtle interface tick on each milestone appearance (`switch_001.ogg`).
* **Narration**:
  - `4.20s – 9.80s`: *"MODIS began its record in 2000. VIIRS later added finer spatial detail."*

---

### Scene 3: Why Harmonization Matters (10.00s – 15.00s)
* **Goal**: Deliver the core scientific insight—spatial resolution disparity and why naive data concatenation creates artificial spikes.
* **Visual Composition**:
  - Side-by-side animated spatial resolution grid comparison:
    - **Left Panel (MODIS)**:
      - Coarse $1\text{ km} \times 1\text{ km}$ footprint schematic with amber perimeter.
      - Animated metric counter: `1,000 m` nominal nadir resolution ($1.0\text{ km}^2$ area).
      - Label: `"MODIS TERRA / AQUA (2000–PRESENT)"`.
    - **Right Panel (VIIRS)**:
      - High-density $375\text{ m} \times 375\text{ m}$ sub-divided grid nested into the same geographical area.
      - Animated metric counter: `375 m` nominal nadir resolution ($0.14\text{ km}^2$ area).
      - Callout badge: `7.1× FINER NADIR FOOTPRINT`.
      - Label: `"VIIRS S-NPP / NOAA-20 / NOAA-21 (2012–PRESENT)"`.
  - Scientific Alert Callout:
    - `"NAIVE MERGING CAUSES 6.3× – 7.7× ARTIFICIAL FIRE COUNT JUMPS."`
    - Seamless transition into: `"ONE COMMON ANALYTICAL FRAMEWORK."`
* **Audio & Music**:
  - Data-scan pulse tone (`switch_001.ogg`) + harmonic drop tone at `13.11s` (`drop_001.ogg`).
* **Narration**:
  - `10.20s – 14.80s`: *"But different sensors produce observations that cannot simply be compared."*

---

### Scene 4: Introducing CLEO (15.00s – 20.00s)
* **Goal**: Demonstrate the actual working application, interactive map, and custom Area of Interest (AOI) polygon engine.
* **Visual Composition**:
  - Authentic screen capture of the CLEO Geospatial Workbench:
    - Tactical dark Esri basemap with coordinate axes and live telemetry headers.
    - Sensor-aware hotspot rendering: Amber squares ($1\text{ km}$ MODIS) vs. Ember circles ($375\text{ m}$ VIIRS).
    - Client-side AOI Polygon actively drawn around the Amazon Basin fire front (`-8.84° S, -53.64° W`).
    - Ray-casting point-in-polygon filtering instantly updating detection counts.
  - Animated UI Telemetry:
    - Active Cell-Days counter recalculating in real time.
    - Sensor split badge: `MODIS: 28` | `VIIRS: 42` | `TOTAL: 70 NASA REFERENCE DETECTIONS`.
  - Typography Header:
    - `"MEET CLEO."`
    - `"EARTH'S FIRE ACTIVITY. ONE SENSOR-AWARE VIEW."`
* **Audio & Music**:
  - Crisp UI mouseclick sound effect (`mouseclick1.ogg`).
  - Dynamic drum groove continues building momentum.
* **Narration**:
  - `15.00s – 19.50s`: *"CLEO brings them into a sensor-aware analytical framework."*

---

### Scene 5: The Burning-Activity Calendar (20.00s – 26.00s)
* **Goal**: Highlight the central product feature—the Burning-Activity Calendar and non-parametric MAD anomaly detection.
* **Visual Composition**:
  - High-resolution interactive view of the **Burning Activity Calendar**:
    - Multi-decade Annual Heatmap Matrix (Year × Month) showing seasonal burning peaks across August, September, and October.
    - Monthly daily breakdown grid showing sensor-attributed daily distribution.
    - Metric toggle animation from *Raw Hotspot Counts* to **Harmonized Active Cell-Days**.
  - Robust Anomaly Intelligence Callout Card:
    - Metric: `MAD ROBUST Z-SCORE: +2.15` (Highlighted in vivid amber).
    - Classification: `UNUSUALLY ELEVATED BURNING ACTIVITY`.
    - Baseline: Non-parametric Median Absolute Deviation across historical distribution.
  - Typography:
    - `"DISCOVER SEASONAL PATTERNS."`
    - `"COMPARE HISTORICAL ACTIVITY."`
    - `"IDENTIFY UNUSUALLY ACTIVE PERIODS."`
* **Audio & Music**:
  - Interface transition click + bass swell at `22.93s` (strong musical drop).
* **Narration**:
  - `19.80s – 25.20s`: *"Explore locations, compare observations, and discover historical burning patterns."*

---

### Scene 6: Closing & Attribution (26.00s – 28.00s)
* **Goal**: Deliver a confident, professional brand and scientific attribution resolution.
* **Visual Composition**:
  - Camera pulls back to high orbital space.
  - Global Equal-Area observation mesh pulses softly across continents.
  - Bold **CLEO** aerospace typography locks into the optical center with glowing ember gradient (`#FF8A00` to `#FF3B30`).
  - Subtitle: `"UNDERSTANDING EARTH'S BURNING PATTERNS."`
  - Canonical Data Attribution:
    - `DATA: NASA FIRMS | MODIS C6.1 | VIIRS C2 | NOAA JPSS`
  - Top Badge: `AI-GENERATED VISUALS` (Space Apps Super Intelligence compliant).
* **Audio & Music**:
  - Warm low-frequency bass impact (`impactSoft_medium_000.ogg`).
  - Natural musical tail fades out smoothly at `28.00s`.
* **Narration**:
  - `25.60s – 27.20s`: *"This is CLEO."*

---

*Authored for the 2026 NASA Space Apps Challenge • CLEO Documentation Suite*
