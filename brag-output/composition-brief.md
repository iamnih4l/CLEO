# Hyperframes Composition Brief: CLEO

## Objective
Create a short, cinematic, scientifically authoritative demonstration film for CLEO (NASA Space Apps Challenge 2026), communicating the scientific problem of satellite sensor comparability across MODIS and VIIRS, demonstrating the actual application's burning activity calendar and anomaly intelligence, and delivering an Apple/BBC Earth-grade product launch experience within 25.0 seconds.

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Final submission video: `brag-output/CLEO_NASA_SPACE_APPS_DEMO.mp4`
- Format: landscape — 1920x1080 (16:9)
- Duration: 25.0 seconds

## Source Material
- Project root: `c:\Users\nihal\OneDrive\Desktop\CLEO`
- Primary files: `public/cleo_platform.html`, `python/cleo_engine.py`, `README.md`, `METHODOLOGY.md`
- Product name: CLEO
- Tagline / strongest claim: "From fragmented observations to a unified view of Earth's fire activity." / "VIIRS detects 6.31x–7.67x more raw pixels than MODIS over identical fire grounds — CLEO harmonizes both across 26 years without false trends."
- Key UI moments to recreate:
  1. 3D Orbital Thermal Globe with live orbit lines (Terra, Aqua, Suomi-NPP, NOAA-20) and thermal plume spikes.
  2. The 1 km MODIS vs 375 m VIIRS pixel footprint geometry disparity.
  3. Interactive CLEO Explore Map with 0.25° GFED4 equal-area grid cells, FRP intensity rings, and tactical HUD reticles.
  4. The Burning Activity Calendar heatmap matrix showing monthly and daily Active Cell-Days.
  5. The Non-Parametric Anomaly Engine showing Median Absolute Deviation (MAD) robust z-scores (+2.15 peak).
- Copy that must appear verbatim:
  - "EARTH IS ALWAYS CHANGING."
  - "AND FIRE LEAVES A RECORD."
  - "DECADES OF DATA. DIFFERENT SATELLITE SENSORS. ONE CHALLENGE: COMPARABILITY."
  - "MEET CLEO."
  - "EARTH'S FIRE ACTIVITY. ONE VIEW."
  - "EXPLORE HISTORICAL PATTERNS."
  - "COMPARE SATELLITE OBSERVATIONS."
  - "IDENTIFY UNUSUAL ACTIVITY."
  - "CLEO"
  - "UNDERSTANDING EARTH'S BURNING PATTERNS."
  - "POWERED BY SATELLITE FIRE OBSERVATIONS."
  - "DATA: NASA FIRMS | MODIS | VIIRS"

## Creative Direction
- Tone preset: `cinematic`
- Creative direction: BBC Earth documentary cinematography meets Apple product launch filmmaking and NASA Earth-observation visual storytelling.
- Visual characteristics: Deep obsidian blacks (`#06080d`), slow orbital camera pan, glowing ember markers (`#f97316`), amber diamonds (`#f59e0b`), aurora emerald (`#10b981`), cosmic purple gradients, clean HUD telemetry brackets, high readability.
- Avoid:
  - Generic SaaS language ("Streamline your workflow")
  - Random video game glitch effects or explosions
  - Fabricated predictions or fake NASA mission logos
  - Abstract filler graphics unrelated to satellite data

## Visual Identity
- Background: `#06080d` (Deep space cosmic black)
- Card Surface: `#0b0f19` / `#161d2a` with border `rgba(41, 53, 72, 0.6)`
- Accent Ember: `#f97316` (VIIRS 375m & Hotspots)
- Accent Amber: `#f59e0b` (MODIS 1km)
- Accent Emerald: `#10b981` (Harmonized Cell-Days)
- Accent Cyan: `#38bdf8` (Orbital telemetry & live UTC clock)
- Typography: High-contrast sans-serif with monospace technical telemetry labels.

## Storyboard
Scene 1: The Planet (0.0s – 4.0s) — Rotating cinematic Earth globe in space with glowing fire clusters.
Scene 2: The Problem (4.0s – 8.74s) — Split-screen satellite disparity: MODIS 1 km vs VIIRS 375 m footprint.
Scene 3: Introducing CLEO (8.74s – 13.5s) — Aerospace HUD sweep into the working CLEO global active-fire map.
Scene 4: The Intelligence (13.5s – 21.5s) — Burning Activity Calendar heatmap, AOI selection, and robust MAD anomaly engine.
Scene 5: Closing (21.5s – 25.0s) — Global fire network return, CLEO wordmark, NASA FIRMS attribution.

## Audio
- Audio role: Cinematic scientific documentary bed with atmospheric presence and subtle telemetry accents.
- Music: `happy-beats-business-moves-vol-12-by-ende-dot-app.mp3` (copied to `brag-output/composition/assets/music/`).
- Cue guidance: Strong beat locks at 8.74s (Scene 3 reveal), 13.11s (Scene 4 reveal), 17.47s (MAD Anomaly reveal), and 22.93s (Scene 5 logo lock).
- Voiceover: Kokoro TTS narration track `assets/voiceover.wav` on track 3 with music ducked to 0.15 during narration.
- SFX:
  - `impactBell_heavy_000.ogg` (0.0s opening impact)
  - `switch_001.ogg` (4.2s sensor mode switch)
  - `impactSoft_medium_000.ogg` (8.74s HUD reveal)
  - `mouseclick1.ogg` (13.7s AOI select)
  - `drop_001.ogg` (14.2s Calendar drop)
  - `impactSoft_medium_000.ogg` (22.93s Logo lock)
