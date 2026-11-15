"""CLEO Scientific Harmonization & Geospatial Fire Intelligence Engine.

Implements the 8-stage MODIS Collection 6.1 and VIIRS 375 m Collection 2
harmonization pipeline, spherical equal-area spatial aggregation, local
point-in-polygon AOI filtering, cross-sensor proximity co-location, and
non-parametric Median Absolute Deviation (MAD) anomaly intelligence.
"""

from __future__ import annotations

import csv
import dataclasses
import datetime
import hashlib
import io
import json
import math
import os
import statistics
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Sequence

EARTH_RADIUS_KM = 6371.0088

VALID_FIRMS_SOURCES = frozenset((
    "MODIS_NRT",
    "MODIS_SP",
    "VIIRS_SNPP_NRT",
    "VIIRS_SNPP_SP",
    "VIIRS_NOAA20_NRT",
    "VIIRS_NOAA20_SP",
    "VIIRS_NOAA21_NRT",
    "VIIRS_NOAA21_SP",
))

SENSOR_AVAILABILITY = {
    "MODIS_SP": {"min_date": "2000-11-01", "max_date": "2025-12-31", "resolution_m": 1000},
    "MODIS_NRT": {"min_date": "2025-02-01", "max_date": "2026-11-15", "resolution_m": 1000},
    "VIIRS_SNPP_SP": {"min_date": "2012-01-20", "max_date": "2025-12-31", "resolution_m": 375},
    "VIIRS_SNPP_NRT": {"min_date": "2025-03-01", "max_date": "2026-11-02", "resolution_m": 375},
    "VIIRS_NOAA20_SP": {"min_date": "2018-04-01", "max_date": "2025-12-31", "resolution_m": 375},
    "VIIRS_NOAA20_NRT": {"min_date": "2025-03-01", "max_date": "2026-11-15", "resolution_m": 375},
    "VIIRS_NOAA21_NRT": {"min_date": "2024-01-17", "max_date": "2026-11-15", "resolution_m": 375},
}


@dataclasses.dataclass(frozen=True)
class HarmonizedObservation:
    """Stage 3: Common internal data structure for MODIS & VIIRS detections."""

    observation_id: str
    source_sensor: str  # 'MODIS' | 'VIIRS'
    satellite: str      # 'Terra' | 'Aqua' | 'Suomi-NPP' | 'NOAA-20' | 'NOAA-21'
    instrument: str     # 'MODIS' | 'VIIRS'
    acquisition_date: str       # 'YYYY-MM-DD'
    acquisition_time_utc: str   # 'HHMM'
    latitude: float
    longitude: float
    confidence_raw: str | int | None
    confidence_category: str    # 'LOW' | 'NOMINAL' | 'HIGH' | 'UNKNOWN'
    fire_radiative_power: float | None
    brightness_primary_k: float | None
    brightness_secondary_k: float | None
    scan_km: float | None
    track_km: float | None
    pixel_area_km2: float | None
    daynight: str               # 'D' | 'N' | 'U'
    product_version: str
    source_type: str            # 'SP' | 'NRT' | 'VERIFIED_ARCHIVE' | 'SYNTHETIC_DEMO_FIXTURE'
    inferred_type: int | None   # 0=vegetation fire, 1=volcano, 2=static land, 3=offshore
    original_attributes: dict[str, Any]


def validate_map_key(map_key: str | None) -> tuple[bool, str]:
    """Validates NASA FIRMS MAP_KEY format without exposing secrets."""
    if not map_key or not isinstance(map_key, str):
        return False, "Missing NASA FIRMS MAP_KEY. Operating in Verified NASA Reference Archive mode."
    cleaned = map_key.strip()
    if cleaned == "your_32_character_nasa_firms_map_key_here" or len(cleaned) != 32:
        return False, "Invalid MAP_KEY length (expected 32-character alphanumeric key)."
    if not cleaned.isalnum():
        return False, "Invalid MAP_KEY characters (expected alphanumeric characters only)."
    return True, "Valid MAP_KEY format."


def build_firms_area_url(
    map_key: str,
    source: str,
    bbox: tuple[float, float, float, float] | str,
    day_range: int = 1,
    date_str: str | None = None,
) -> str:
    """Builds a validated server-side NASA FIRMS Area API URL."""
    ok, msg = validate_map_key(map_key)
    if not ok:
        raise ValueError(msg)
    if source not in VALID_FIRMS_SOURCES:
        raise ValueError(f"Unsupported NASA FIRMS source: {source}")
    if not (1 <= int(day_range) <= 10):
        raise ValueError("day_range must be between 1 and 10 per NASA FIRMS API limits.")
    if isinstance(bbox, str):
        if bbox != "world":
            parts = [float(x.strip()) for x in bbox.split(",")]
            if len(parts) != 4:
                raise ValueError("Bounding box string must be 'west,south,east,north' or 'world'.")
            west, south, east, north = parts
            if not (-180 <= west <= 180 and -180 <= east <= 180 and -90 <= south <= 90 and -90 <= north <= 90 and west <= east and south <= north):
                raise ValueError("Invalid bounding box coordinates.")
            area_param = f"{west},{south},{east},{north}"
        else:
            area_param = "world"
    else:
        west, south, east, north = bbox
        if not (-180 <= west <= 180 and -180 <= east <= 180 and -90 <= south <= 90 and -90 <= north <= 90 and west <= east and south <= north):
            raise ValueError("Invalid bounding box coordinates.")
        area_param = f"{west},{south},{east},{north}"

    base = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{map_key.strip()}/{source}/{area_param}/{int(day_range)}"
    if date_str:
        datetime.date.fromisoformat(date_str)
        if source in SENSOR_AVAILABILITY:
            avail = SENSOR_AVAILABILITY[source]
            if date_str < avail["min_date"]:
                raise ValueError(f"Requested date {date_str} precedes {source} start date ({avail['min_date']}).")
        base = f"{base}/{date_str}"
    return base


def normalize_satellite_and_sensor(raw_row: dict[str, Any]) -> tuple[str, str, str]:
    """Stage 2: Identifies originating sensor, satellite, and instrument."""
    inst_raw = str(raw_row.get("instrument", "")).strip().upper()
    sat_raw = str(raw_row.get("satellite", "")).strip().upper()
    has_viirs_cols = "bright_ti4" in raw_row or "bright_ti5" in raw_row

    if inst_raw == "VIIRS" or has_viirs_cols or sat_raw in ("N", "S-NPP", "SNPP", "N20", "NOAA-20", "J1", "N21", "NOAA-21", "J2"):
        source_sensor = "VIIRS"
        instrument = "VIIRS"
        if sat_raw in ("N", "S-NPP", "SNPP", "SUOMI-NPP", "SUOMI NPP"):
            satellite = "Suomi-NPP"
        elif sat_raw in ("N20", "NOAA-20", "NOAA20", "J1", "JPSS-1"):
            satellite = "NOAA-20"
        elif sat_raw in ("N21", "NOAA-21", "NOAA21", "J2", "JPSS-2"):
            satellite = "NOAA-21"
        else:
            satellite = sat_raw or "VIIRS-Unknown"
    else:
        source_sensor = "MODIS"
        instrument = "MODIS"
        if sat_raw in ("T", "TERRA"):
            satellite = "Terra"
        elif sat_raw in ("A", "AQUA"):
            satellite = "Aqua"
        else:
            satellite = sat_raw or "MODIS-Combined"
    return source_sensor, satellite, instrument


def normalize_confidence(source_sensor: str, raw_conf: Any, modis_nominal_threshold: int = 30) -> tuple[str | int | None, str]:
    """Stage 4: Sensor-specific confidence interpretation without conflating scales."""
    if raw_conf is None:
        return None, "UNKNOWN"
    s = str(raw_conf).strip()
    if s == "" or s.lower() in ("null", "nan", "none", "na"):
        return None, "UNKNOWN"

    if source_sensor == "VIIRS":
        low_s = s.lower()
        if low_s in ("l", "low"):
            return s, "LOW"
        if low_s in ("n", "nominal", "m", "medium"):
            return s, "NOMINAL"
        if low_s in ("h", "high"):
            return s, "HIGH"
        try:
            val = float(s)
            if 0 <= val <= 100:
                if val < 30:
                    return int(round(val)), "LOW"
                if val < 80:
                    return int(round(val)), "NOMINAL"
                return int(round(val)), "HIGH"
        except ValueError:
            pass
        return s, "UNKNOWN"
    else:
        try:
            val = float(s)
            if not (0 <= val <= 100):
                return None, "UNKNOWN"
            ival = int(round(val))
            if ival < modis_nominal_threshold:
                return ival, "LOW"
            if ival < 80:
                return ival, "NOMINAL"
            return ival, "HIGH"
        except ValueError:
            low_s = s.lower()
            if low_s in ("l", "low"):
                return s, "LOW"
            if low_s in ("n", "nominal", "m", "medium"):
                return s, "NOMINAL"
            if low_s in ("h", "high"):
                return s, "HIGH"
            return None, "UNKNOWN"


def _parse_optional_float(val: Any) -> float | None:
    """Parses a float while preserving missing values as None (never 0.0)."""
    if val is None:
        return None
    s = str(val).strip()
    if s == "" or s.lower() in ("null", "nan", "none", "na", "-999", "-9999"):
        return None
    try:
        f = float(s)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except ValueError:
        return None


def normalize_time_utc(raw_time: Any) -> str:
    """Stage 6: Normalizes NASA FIRMS HHMM integer/string timestamps to 4-digit UTC."""
    if raw_time is None:
        return "0000"
    s = str(raw_time).strip().replace(":", "")
    if not s:
        return "0000"
    if len(s) > 4:
        s = s[:4]
    s = s.zfill(4)
    try:
        hh = int(s[:2])
        mm = int(s[2:4])
        if 0 <= hh <= 23 and 0 <= mm <= 59:
            return f"{hh:02d}{mm:02d}"
    except ValueError:
        pass
    return "0000"


def ingest_and_harmonize_records(
    raw_rows: Sequence[dict[str, Any]],
    default_source_type: str = "VERIFIED_ARCHIVE",
    modis_nominal_threshold: int = 30,
    exclude_non_vegetation_types: bool = True,
) -> dict[str, Any]:
    """Stages 1-4 & 6: Ingests, validates, deduplicates, and normalizes records."""
    harmonized: list[HarmonizedObservation] = []
    rejected_coordinates = 0
    rejected_dates = 0
    rejected_static_sources = 0
    duplicates_removed = 0
    missing_frp_count = 0
    missing_conf_count = 0
    seen_keys: set[tuple[str, str, str, str, float, float]] = set()

    for row in raw_rows:
        lat = _parse_optional_float(row.get("latitude"))
        lon = _parse_optional_float(row.get("longitude"))
        if lat is None or lon is None or not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            rejected_coordinates += 1
            continue

        acq_date = str(row.get("acq_date", row.get("acquisition_date", ""))).strip()
        try:
            datetime.date.fromisoformat(acq_date)
        except ValueError:
            rejected_dates += 1
            continue

        inferred_type: int | None = None
        if "type" in row and str(row["type"]).strip() != "":
            try:
                inferred_type = int(float(str(row["type"]).strip()))
                if exclude_non_vegetation_types and inferred_type != 0:
                    rejected_static_sources += 1
                    continue
            except ValueError:
                inferred_type = None

        source_sensor, satellite, instrument = normalize_satellite_and_sensor(row)
        acq_time_utc = normalize_time_utc(row.get("acq_time", row.get("acquisition_time_utc", "0000")))

        dedup_key = (source_sensor, satellite, acq_date, acq_time_utc, round(lat, 5), round(lon, 5))
        if dedup_key in seen_keys:
            duplicates_removed += 1
            continue
        seen_keys.add(dedup_key)

        conf_raw, conf_cat = normalize_confidence(
            source_sensor, row.get("confidence", row.get("confidence_raw")), modis_nominal_threshold
        )
        if conf_cat == "UNKNOWN":
            missing_conf_count += 1

        frp = _parse_optional_float(row.get("frp", row.get("fire_radiative_power")))
        if frp is not None and frp < 0:
            frp = None
        if frp is None:
            missing_frp_count += 1

        if source_sensor == "VIIRS":
            b1 = _parse_optional_float(row.get("bright_ti4", row.get("brightness")))
            b2 = _parse_optional_float(row.get("bright_ti5", row.get("bright_t31")))
        else:
            b1 = _parse_optional_float(row.get("brightness", row.get("bright_ti4")))
            b2 = _parse_optional_float(row.get("bright_t31", row.get("bright_ti5")))

        scan_km = _parse_optional_float(row.get("scan"))
        track_km = _parse_optional_float(row.get("track"))
        if scan_km is not None and track_km is not None and scan_km > 0 and track_km > 0:
            pixel_area = round(scan_km * track_km, 4)
        else:
            pixel_area = 0.1406 if source_sensor == "VIIRS" else 1.0000

        dn = str(row.get("daynight", "U")).strip().upper()
        if dn not in ("D", "N"):
            dn = "U"

        version = str(row.get("version", row.get("product_version", "Unknown"))).strip()
        if "source_type" in row and str(row["source_type"]).strip():
            src_type = str(row["source_type"]).strip()
        elif "NRT" in version.upper() or "RT" in version.upper() or "URT" in version.upper():
            src_type = "NRT"
        elif version in ("6.1", "6.0", "2.0", "1.0"):
            src_type = "SP"
        else:
            src_type = default_source_type

        obs_hash = hashlib.sha256(
            f"{source_sensor}:{satellite}:{acq_date}:{acq_time_utc}:{lat:.5f}:{lon:.5f}".encode("utf-8")
        ).hexdigest()[:12]

        harmonized.append(
            HarmonizedObservation(
                observation_id=f"CLEO-{source_sensor[:3]}-{obs_hash}",
                source_sensor=source_sensor,
                satellite=satellite,
                instrument=instrument,
                acquisition_date=acq_date,
                acquisition_time_utc=acq_time_utc,
                latitude=lat,
                longitude=lon,
                confidence_raw=conf_raw,
                confidence_category=conf_cat,
                fire_radiative_power=frp,
                brightness_primary_k=b1,
                brightness_secondary_k=b2,
                scan_km=scan_km,
                track_km=track_km,
                pixel_area_km2=pixel_area,
                daynight=dn,
                product_version=version,
                source_type=src_type,
                inferred_type=inferred_type,
                original_attributes=dict(row),
            )
        )

    return {
        "records": harmonized,
        "qc_summary": {
            "input_rows": len(raw_rows),
            "retained_rows": len(harmonized),
            "rejected_coordinates": rejected_coordinates,
            "rejected_dates": rejected_dates,
            "rejected_static_sources": rejected_static_sources,
            "duplicates_removed": duplicates_removed,
            "missing_frp_count": missing_frp_count,
            "missing_confidence_count": missing_conf_count,
        },
    }


def parse_csv_archive(csv_text: str, default_source_type: str = "IMPORTED_ARCHIVE") -> dict[str, Any]:
    """Parses NASA FIRMS CSV archive text and runs the harmonization pipeline."""
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    rows = [dict(r) for r in reader]
    return ingest_and_harmonize_records(rows, default_source_type=default_source_type)


def spherical_cell_area_km2(lat_south: float, lat_north: float, lon_span_deg: float) -> float:
    """Stage 5: Computes exact spherical surface area of a lat-lon grid cell in km^2."""
    phi1 = math.radians(max(-90.0, min(90.0, lat_south)))
    phi2 = math.radians(max(-90.0, min(90.0, lat_north)))
    d_lambda = math.radians(abs(lon_span_deg))
    return (EARTH_RADIUS_KM ** 2) * d_lambda * abs(math.sin(phi2) - math.sin(phi1))


def aggregate_spatial_grid(
    observations: Sequence[HarmonizedObservation],
    resolution_deg: float = 0.25,
) -> dict[str, Any]:
    """Stage 5: Aggregates MODIS and VIIRS observations onto a common equal-area grid."""
    if resolution_deg <= 0 or resolution_deg > 10:
        raise ValueError("Grid resolution_deg must be in (0, 10].")

    cells: dict[str, dict[str, Any]] = {}
    unique_cell_days: set[tuple[str, str]] = set()
    modis_cell_days: set[tuple[str, str]] = set()
    viirs_cell_days: set[tuple[str, str]] = set()

    for obs in observations:
        if obs.source_type == "SYNTHETIC_DEMO_FIXTURE":
            continue
        lat_idx = math.floor(obs.latitude / resolution_deg)
        lon_idx = math.floor(obs.longitude / resolution_deg)
        lat_s = round(lat_idx * resolution_deg, 6)
        lat_n = round((lat_idx + 1) * resolution_deg, 6)
        lon_w = round(lon_idx * resolution_deg, 6)
        lon_e = round((lon_idx + 1) * resolution_deg, 6)
        cell_id = f"G_{lat_s:.2f}_{lon_w:.2f}"

        if cell_id not in cells:
            area_km2 = spherical_cell_area_km2(lat_s, lat_n, resolution_deg)
            cells[cell_id] = {
                "cell_id": cell_id,
                "lat_south": lat_s,
                "lat_north": lat_n,
                "lon_west": lon_w,
                "lon_east": lon_e,
                "center_lat": round((lat_s + lat_n) / 2.0, 5),
                "center_lon": round((lon_w + lon_e) / 2.0, 5),
                "area_km2": round(area_km2, 3),
                "total_detections": 0,
                "modis_detections": 0,
                "viirs_detections": 0,
                "active_dates": set(),
                "modis_dates": set(),
                "viirs_dates": set(),
                "frp_values": [],
            }

        c = cells[cell_id]
        c["total_detections"] += 1
        c["active_dates"].add(obs.acquisition_date)
        unique_cell_days.add((cell_id, obs.acquisition_date))
        if obs.source_sensor == "MODIS":
            c["modis_detections"] += 1
            c["modis_dates"].add(obs.acquisition_date)
            modis_cell_days.add((cell_id, obs.acquisition_date))
        else:
            c["viirs_detections"] += 1
            c["viirs_dates"].add(obs.acquisition_date)
            viirs_cell_days.add((cell_id, obs.acquisition_date))

        if obs.fire_radiative_power is not None:
            c["frp_values"].append(obs.fire_radiative_power)

    formatted_cells = []
    for c in cells.values():
        area = c["area_km2"] or 1.0
        frp_vals = c["frp_values"]
        formatted_cells.append({
            "cell_id": c["cell_id"],
            "lat_south": c["lat_south"],
            "lat_north": c["lat_north"],
            "lon_west": c["lon_west"],
            "lon_east": c["lon_east"],
            "center_lat": c["center_lat"],
            "center_lon": c["center_lon"],
            "area_km2": c["area_km2"],
            "total_detections": c["total_detections"],
            "modis_detections": c["modis_detections"],
            "viirs_detections": c["viirs_detections"],
            "active_cell_days": len(c["active_dates"]),
            "modis_cell_days": len(c["modis_dates"]),
            "viirs_cell_days": len(c["viirs_dates"]),
            "density_per_1000km2": round((c["total_detections"] * 1000.0) / area, 3),
            "cell_days_per_1000km2": round((len(c["active_dates"]) * 1000.0) / area, 3),
            "total_frp_mw": round(sum(frp_vals), 2) if frp_vals else None,
            "median_frp_mw": round(statistics.median(frp_vals), 2) if frp_vals else None,
        })

    formatted_cells.sort(key=lambda x: x["total_detections"], reverse=True)
    return {
        "resolution_deg": resolution_deg,
        "unique_cells_count": len(formatted_cells),
        "unique_active_cell_days": len(unique_cell_days),
        "modis_active_cell_days": len(modis_cell_days),
        "viirs_active_cell_days": len(viirs_cell_days),
        "cells": formatted_cells,
    }


def point_in_polygon(lat: float, lon: float, polygon: Sequence[tuple[float, float]]) -> bool:
    """Ray-casting point-in-polygon check for local AOI filtering."""
    if len(polygon) < 3:
        return False
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]
        yj, xj = polygon[j]
        intersect = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


def filter_by_aoi(
    observations: Sequence[HarmonizedObservation],
    bbox: tuple[float, float, float, float] | None = None,
    polygon: Sequence[tuple[float, float]] | None = None,
) -> dict[str, Any]:
    """Section 7: Filters by API retrieval bounding box and exact local polygon."""
    if polygon and len(polygon) >= 3:
        lats = [p[0] for p in polygon]
        lons = [p[1] for p in polygon]
        derived_bbox = (min(lons), min(lats), max(lons), max(lats))
    else:
        derived_bbox = bbox

    bbox_matches: list[HarmonizedObservation] = []
    polygon_matches: list[HarmonizedObservation] = []

    for obs in observations:
        if derived_bbox is not None:
            west, south, east, north = derived_bbox
            if not (west <= obs.longitude <= east and south <= obs.latitude <= north):
                continue
        bbox_matches.append(obs)
        if polygon and len(polygon) >= 3:
            if point_in_polygon(obs.latitude, obs.longitude, polygon):
                polygon_matches.append(obs)
        else:
            polygon_matches.append(obs)

    return {
        "api_retrieval_bbox": derived_bbox,
        "bbox_matched_count": len(bbox_matches),
        "aoi_matched_count": len(polygon_matches),
        "bbox_vs_polygon_excluded_count": len(bbox_matches) - len(polygon_matches),
        "records": polygon_matches,
    }


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance in kilometers between two WGS84 points."""
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2.0) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def cross_sensor_colocation(
    observations: Sequence[HarmonizedObservation],
    proximity_km: float = 2.0,
) -> dict[str, Any]:
    """Stage 7: Proximity-based matching between MODIS and VIIRS on the same UTC date."""
    modis_obs = [o for o in observations if o.source_sensor == "MODIS" and o.source_type != "SYNTHETIC_DEMO_FIXTURE"]
    viirs_obs = [o for o in observations if o.source_sensor == "VIIRS" and o.source_type != "SYNTHETIC_DEMO_FIXTURE"]

    matched_pairs = []
    corroborated_modis_ids = set()
    corroborated_viirs_ids = set()

    viirs_by_date: dict[str, list[HarmonizedObservation]] = {}
    for v in viirs_obs:
        viirs_by_date.setdefault(v.acquisition_date, []).append(v)

    for m in modis_obs:
        candidates = viirs_by_date.get(m.acquisition_date, [])
        for v in candidates:
            dist = haversine_km(m.latitude, m.longitude, v.latitude, v.longitude)
            if dist <= proximity_km:
                corroborated_modis_ids.add(m.observation_id)
                corroborated_viirs_ids.add(v.observation_id)
                matched_pairs.append({
                    "modis_id": m.observation_id,
                    "viirs_id": v.observation_id,
                    "date": m.acquisition_date,
                    "distance_km": round(dist, 3),
                    "modis_frp": m.fire_radiative_power,
                    "viirs_frp": v.fire_radiative_power,
                })

    return {
        "proximity_threshold_km": proximity_km,
        "modis_count": len(modis_obs),
        "viirs_count": len(viirs_obs),
        "viirs_to_modis_ratio": round(len(viirs_obs) / len(modis_obs), 2) if modis_obs else None,
        "corroborated_modis_count": len(corroborated_modis_ids),
        "corroborated_viirs_count": len(corroborated_viirs_ids),
        "matched_pairs": matched_pairs,
    }


def build_burning_calendar(
    observations: Sequence[HarmonizedObservation],
    resolution_deg: float = 0.25,
) -> dict[str, Any]:
    """Section 4C & Stage 6/8: Builds daily and monthly burning activity calendars."""
    daily: dict[str, dict[str, Any]] = {}
    monthly: dict[str, dict[str, Any]] = {}

    for obs in observations:
        if obs.source_type == "SYNTHETIC_DEMO_FIXTURE":
            continue
        d_key = obs.acquisition_date
        m_key = d_key[:7]
        lat_idx = math.floor(obs.latitude / resolution_deg)
        lon_idx = math.floor(obs.longitude / resolution_deg)
        cell_id = f"G_{lat_idx}_{lon_idx}"

        for bucket_map, key in ((daily, d_key), (monthly, m_key)):
            if key not in bucket_map:
                bucket_map[key] = {
                    "period": key,
                    "modis_count": 0,
                    "viirs_count": 0,
                    "combined_count": 0,
                    "cells": set(),
                    "cell_days": set(),
                    "frp_values": [],
                }
            b = bucket_map[key]
            b["combined_count"] += 1
            if obs.source_sensor == "MODIS":
                b["modis_count"] += 1
            else:
                b["viirs_count"] += 1
            b["cells"].add(cell_id)
            b["cell_days"].add((cell_id, d_key))
            if obs.fire_radiative_power is not None:
                b["frp_values"].append(obs.fire_radiative_power)

    def _serialize(bucket_map: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        out = []
        for key in sorted(bucket_map.keys()):
            b = bucket_map[key]
            frps = b["frp_values"]
            out.append({
                "period": key,
                "modis_count": b["modis_count"],
                "viirs_count": b["viirs_count"],
                "combined_count": b["combined_count"],
                "unique_spatial_cells": len(b["cells"]),
                "active_cell_days": len(b["cell_days"]),
                "total_frp_mw": round(sum(frps), 2) if frps else None,
                "median_frp_mw": round(statistics.median(frps), 2) if frps else None,
            })
        return out

    return {
        "daily": _serialize(daily),
        "monthly": _serialize(monthly),
    }


def compute_robust_anomalies(
    series: Sequence[dict[str, Any]],
    value_key: str = "value",
    label_key: str = "period",
    aoi_name: str = "Selected AOI",
    sensor_contribution: str = "Harmonized VIIRS + MODIS",
    min_baseline_size: int = 5,
) -> dict[str, Any]:
    """Section 6: Computes non-parametric median, MAD, robust z-scores, and percentiles."""
    valid_items = [item for item in series if item.get(value_key) is not None]
    if len(valid_items) < min_baseline_size:
        return {
            "sufficient_data": False,
            "reason": f"Requires at least {min_baseline_size} historical observations; found {len(valid_items)}.",
            "anomalies": [],
        }

    values = [float(item[value_key]) for item in valid_items]
    sorted_vals = sorted(values)
    n = len(sorted_vals)

    def _percentile(p: float) -> float:
        idx = (n - 1) * p
        lo = math.floor(idx)
        hi = math.ceil(idx)
        if lo == hi:
            return sorted_vals[lo]
        return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)

    med = statistics.median(values)
    abs_devs = [abs(v - med) for v in values]
    mad = statistics.median(abs_devs)
    p25 = _percentile(0.25)
    p75 = _percentile(0.75)
    p90 = _percentile(0.90)

    results = []
    for item in valid_items:
        val = float(item[value_key])
        dev = val - med
        dev_pct = round((dev / med) * 100.0, 2) if med != 0 else 0.0
        if mad > 0:
            z_rob = round(0.6745 * dev / mad, 3)
        else:
            z_rob = 0.0 if dev == 0 else (3.0 if dev > 0 else -3.0)

        if z_rob >= 2.0 or val >= p90:
            category = "Unusually elevated activity"
        elif z_rob >= 1.0 or val >= p75:
            category = "Elevated activity"
        elif z_rob < -1.0 or val < p25:
            category = "Below historical activity"
        else:
            category = "Typical activity"

        results.append({
            "period": item[label_key],
            "aoi": aoi_name,
            "observed_activity": val,
            "historical_baseline_median": round(med, 2),
            "mad": round(mad, 2),
            "deviation_from_baseline": round(dev, 2),
            "deviation_percent": dev_pct,
            "robust_z_score": z_rob,
            "category": category,
            "sensor_contribution": item.get("sensor_contribution", sensor_contribution),
            "coverage_limitations": item.get(
                "coverage_limitations",
                "Standard Processing (SP) archive record; cloud cover and orbital revisit gaps may cause omission errors.",
            ),
        })

    return {
        "sufficient_data": True,
        "baseline_count": n,
        "baseline_median": round(med, 2),
        "baseline_mad": round(mad, 2),
        "p25": round(p25, 2),
        "p75": round(p75, 2),
        "p90": round(p90, 2),
        "anomalies": results,
    }


def export_provenance_csv(
    observations: Sequence[HarmonizedObservation],
    applied_filters: dict[str, Any],
) -> str:
    """Section 9: Exports filtered authentic observations to CSV with provenance headers."""
    authentic = [o for o in observations if o.source_type != "SYNTHETIC_DEMO_FIXTURE"]
    buf = io.StringIO()
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    buf.write("# CLEO — Unified Earth Fire Intelligence & Historical Burning Activity Platform\n")
    buf.write("# Data Source: NASA Fire Information for Resource Management System (FIRMS) (https://firms.modaps.eosdis.nasa.gov/)\n")
    buf.write(f"# Export Timestamp (UTC): {now_utc}\n")
    buf.write(f"# Applied Filters: {json.dumps(applied_filters, sort_keys=True)}\n")
    buf.write("# Processing Methodology: CLEO 8-Stage MODIS (C6.1) & VIIRS (C2 375m) Harmonization Pipeline (Synthetic fixtures excluded)\n")

    fieldnames = [
        "observation_id",
        "source_sensor",
        "satellite",
        "instrument",
        "acquisition_date",
        "acquisition_time_utc",
        "latitude",
        "longitude",
        "confidence_raw",
        "confidence_category",
        "fire_radiative_power",
        "brightness_primary_k",
        "brightness_secondary_k",
        "pixel_area_km2",
        "daynight",
        "product_version",
        "source_type",
    ]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for o in authentic:
        writer.writerow({k: getattr(o, k) for k in fieldnames})
    return buf.getvalue()


def export_provenance_geojson(
    observations: Sequence[HarmonizedObservation],
    applied_filters: dict[str, Any],
) -> dict[str, Any]:
    """Section 9: Exports authentic observations as a provenance-stamped GeoJSON FeatureCollection."""
    authentic = [o for o in observations if o.source_type != "SYNTHETIC_DEMO_FIXTURE"]
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    features = []
    for o in authentic:
        features.append({
            "type": "Feature",
            "id": o.observation_id,
            "geometry": {
                "type": "Point",
                "coordinates": [o.longitude, o.latitude],
            },
            "properties": {
                "observation_id": o.observation_id,
                "source_sensor": o.source_sensor,
                "satellite": o.satellite,
                "instrument": o.instrument,
                "acquisition_date": o.acquisition_date,
                "acquisition_time_utc": o.acquisition_time_utc,
                "confidence_raw": o.confidence_raw,
                "confidence_category": o.confidence_category,
                "fire_radiative_power": o.fire_radiative_power,
                "brightness_primary_k": o.brightness_primary_k,
                "brightness_secondary_k": o.brightness_secondary_k,
                "pixel_area_km2": o.pixel_area_km2,
                "daynight": o.daynight,
                "product_version": o.product_version,
                "source_type": o.source_type,
            },
        })
    return {
        "type": "FeatureCollection",
        "metadata": {
            "platform": "CLEO — Unified Earth Fire Intelligence Platform",
            "data_source": "NASA FIRMS (MODIS Collection 6.1 & VIIRS 375m Collection 2)",
            "source_url": "https://firms.modaps.eosdis.nasa.gov/",
            "export_timestamp_utc": now_utc,
            "applied_filters": applied_filters,
            "processing_methodology": "CLEO 8-Stage MODIS-VIIRS Harmonization Pipeline",
            "record_count": len(features),
        },
        "features": features,
    }
