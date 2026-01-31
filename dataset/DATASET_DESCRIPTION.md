# Dataset & Column Descriptions 📋

This document describes the datasets present in the `dataset/` folder and the columns available in each CSV. Synthetic files are clearly marked and include generation notes and recommended usage tips.

---

## Files Overview ✅
- **US_Accidents_March23.csv** — Real accidents dataset (7,728,394 rows, 46 columns). Good for safety, hotspot, and weather-related analyses.
- **synthetic_traffic_counts.csv** — Synthetic hourly traffic counts per station (1,092,000 rows).
- **synthetic_probe_data.csv** — Synthetic probe vehicle observations (speed + location) (~16.4M rows) — *large*.
- **synthetic_signal_timings.csv** — Signal timing records per station (157 rows).
- **synthetic_road_network.csv** — Road segment attributes connecting stations (300 rows).

---

## 1) US_Accidents_March23.csv (real)
Columns (46) and short descriptions:
- `ID` — unique event identifier
- `Source` — source of the report
- `Severity` — accident severity (integer scale)
- `Start_Time`, `End_Time` — event start/end timestamps (strings, parse to datetime)
- `Start_Lat`, `Start_Lng`, `End_Lat`, `End_Lng` — coordinates
- `Distance(mi)` — reported distance of incident in miles
- `Description` — textual description of the incident
- `Street`, `City`, `County`, `State`, `Zipcode`, `Country` — location fields
- `Timezone`, `Airport_Code` — auxiliary locational context
- `Weather_Timestamp` — weather observation time (string)
- `Temperature(F)`, `Wind_Chill(F)`, `Humidity(%)`, `Pressure(in)`, `Visibility(mi)`, `Wind_Direction`, `Wind_Speed(mph)`, `Precipitation(in)`, `Weather_Condition` — weather measurements
- `Amenity`, `Bump`, `Crossing`, `Give_Way`, `Junction`, `No_Exit`, `Railway`, `Roundabout`, `Station`, `Stop`, `Traffic_Calming`, `Traffic_Signal`, `Turning_Loop` — boolean flags for infrastructure features
- `Sunrise_Sunset`, `Civil_Twilight`, `Nautical_Twilight`, `Astronomical_Twilight` — day/night context fields

Notes & tips:
- Parse `Start_Time`, `End_Time`, and `Weather_Timestamp` to `datetime` for temporal analyses (pandas `pd.to_datetime`).
- Memory: dataset uses ~2 GB in-memory; consider reading with `usecols`, `dtype` downcasting, or `chunksize` for heavy operations.

---

## 2) synthetic_traffic_counts.csv (synthetic)
Purpose: hourly vehicle counts at `station_id` locations (suitable as traffic volume proxy).
Columns:
- `station_id` — synthetic station identifier (e.g., `STN_001`)
- `city` — city name (chosen from accidents data)
- `timestamp` — hourly timestamp (UTC/local depending on processing)
- `count` — integer hourly vehicle count
- `lat`, `lng` — station coordinates (approx. city centroid with small jitter)

Generation notes:
- Modeled diurnal patterns (morning/evening peaks), weekday/weekend effects, and monthly seasonality.
- Random event spikes were injected to mimic special events / anomalies.

Usage tips:
- Aggregate to daily/hourly peaks or merge with accidents by nearest station/time for exposure modeling.

---

## 3) synthetic_probe_data.csv (synthetic) ⚠️ large
Purpose: per-vehicle sampled observations (speed + geo) to approximate probe/GPS data.
Columns:
- `station_id` — station where probe observation is located
- `timestamp` — timestamp of observation
- `speed_mph` — observed speed in mph (float)
- `lat`, `lng` — jittered GPS coordinates around station
- `speed_limit` — assigned speed limit (simulated)

Generation notes:
- Created by sampling a fraction (probe penetration) of counts and assigning speeds that decrease with congestion.
- Jitter added to lat/lng simulates GPS noise. Contains ~16.4M rows; sampling or downscaling recommended for quick experiments.

Usage tips:
- Use to compute speed distributions, travel-time approximations, or to validate congestion at station/time windows.
- To reduce memory: `pd.read_csv(..., usecols=[...], parse_dates=['timestamp'], nrows=... )` or sample rows by time range.

---

## 4) synthetic_signal_timings.csv (synthetic)
Purpose: intersection signal cycle and phase green times for signal timing analysis.
Columns:
- `station_id` — signal/intersection id (aligned with stations)
- `phase` — phase number (1..N)
- `cycle_length_s` — cycle length in seconds
- `green_s` — green time for the phase in seconds

Usage tips:
- Useful for modeling delay, intersection capacity, or simulating signal optimization effects.

---

## 5) synthetic_road_network.csv (synthetic)
Purpose: simple road segment attributes linking stations; useful for segment-level aggregations and building simple graph-based flows.
Columns:
- `road_id` — unique road segment id
- `city` — city where the segment is located
- `start_lat`, `start_lng`, `end_lat`, `end_lng` — segment endpoints
- `length_mi` — length of segment in miles
- `lanes` — number of lanes
- `speed_limit` — posted speed limit for segment (mph)

Usage tips:
- Use `length_mi` and `speed_limit` to estimate free-flow travel times, and combine with probe-derived speeds to estimate congestion delays.

---

## Recommended next steps 🚀
- If you plan to run interactive analysis, use the included sample `dataset/sampled_probe.csv` (100,000 rows) for faster iteration. This file contains the header + first 100k rows of `synthetic_probe_data.csv`. For reproducible sampling use the script: `python tools/sample_probe.py --input dataset/synthetic_probe_data.csv --output dataset/sampled_probe.csv --n 100000 --seed 42` (if Python is available; a header+head fallback was used when Python was not present).
- Consider enriching the road network with OSM links (way IDs) and lane geometry for advanced modeling.
- Document synthetic generation parameters (seed, penetration rate) in version control for reproducibility.

---

**License / provenance**
- `US_Accidents_March23.csv` is an external dataset (see project README / source for original license). The other `synthetic_*.csv` files are generated for the project and **do not reflect real vehicles or private data**.

---

If you want, I can:
- Produce a smaller sampled version of `synthetic_probe_data.csv` for quick experiments ✅
- Add a short example notebook cell that loads and demonstrates merging `synthetic_traffic_counts.csv` with the accidents dataset ✅

Which one would you like next?