# GTFS data

SunSeat expects a GTFS dataset in this directory.

At minimum, the application currently needs:

- `stops.txt`
- `stop_times.txt`

The files are intentionally not included in this repository. Add a GTFS feed locally under `data/DE-RV/` before running the application or the GTFS-dependent tests.

The application uses the station names, coordinates, trip IDs, and stop times from these files to search for a journey and calculate sun exposure along the route.
