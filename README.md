# SunSeat ☀️🚆

SunSeat is a Python desktop application that recommends which side of a train to sit on based on the direction of sunlight during a journey.

The application combines **GTFS timetable data**, **geographic route bearings**, and **solar-position calculations** to estimate whether sunlight is predominantly on the left or right side of the train.

## What it does

- Search for a journey between two stations.
- Match a suitable trip from GTFS stop-time data.
- Build the route from the selected trip's stops and coordinates.
- Calculate the train's direction for each route segment.
- Calculate the sun's azimuth and elevation for the relevant time and location.
- Classify visible sunlight relative to the train as front, right, left, or back.
- Aggregate left/right exposure and provide a seat-side recommendation with a confidence value.
- Cache GTFS data in memory to improve repeated searches.
- Provide a desktop interface built with PySide6.

## Project structure

```text
SunSeat/
├── app.py                         # Application/service layer
├── gui.py                         # PySide6 desktop interface
├── engine/
│   ├── geography.py               # Bearings and journey-level sun analysis
│   ├── gtfs_reader.py             # GTFS loading, station and trip search
│   ├── recommendation.py          # Seat-side recommendation logic
│   ├── relative_position.py       # Relative sun/train position helpers
│   └── sun_position.py            # Solar-position calculation
├── tests/
│   ├── test_app.py
│   ├── test_engine.py
│   ├── test_geography.py
│   ├── test_gtfs_reader.py
│   ├── test_recommendation.py
│   └── test_sun_position.py
├── data/
│   └── DE-RV/
│       └── README.md              # Instructions for local GTFS data
├── requirements.txt
└── README.md
```

## How the calculation works

At a high level:

1. The user selects an origin, destination, date, and departure time.
2. SunSeat searches the GTFS data for a matching trip.
3. The trip's ordered stops provide the route coordinates and segment times.
4. A geographic bearing is calculated for each consecutive pair of stops.
5. The sun's azimuth/elevation is calculated for each segment.
6. The difference between train bearing and sun azimuth is classified as front, right, left, or back.
7. Visible left/right exposure is aggregated.
8. The recommendation engine determines the dominant side and confidence.

GTFS times beyond `24:00:00` are handled explicitly because GTFS permits service times after midnight to remain associated with the service day.

## Requirements

- Python 3.x
- PySide6
- Astral
- pytest (for tests)
- A compatible GTFS dataset containing at least `stops.txt` and `stop_times.txt`

## Setup

Create a virtual environment if desired:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Add your GTFS files here:

```text
SunSeat/data/DE-RV/stops.txt
SunSeat/data/DE-RV/stop_times.txt
```

The GTFS files are not included in this repository.

## Run

Launch the desktop application with:

```bash
python gui.py
```

The underlying application/service layer can also be used directly through `app.py`.

## Tests

Run the test suite with:

```bash
python -m pytest
```

The GTFS-dependent tests require the local GTFS files described above.

## Notes

This repository contains the source code and tests for the SunSeat project. Local timetable datasets and generated build artifacts are intentionally excluded from version control.
