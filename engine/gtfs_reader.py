import csv


# =========================================================
# GTFS CACHE
# =========================================================

_stops_cache = {}
_stop_times_cache = {}


def _load_stops(file_path):
    if file_path in _stops_cache:
        return _stops_cache[file_path]

    stops_by_id = {}
    stops_by_name = {}
    children_by_parent = {}

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            stop_id = row["stop_id"]
            stop_name = row["stop_name"]
            parent_station = row.get("parent_station", "").strip()

            stops_by_id[stop_id] = row

            if stop_name not in stops_by_name:
                stops_by_name[stop_name] = row

            if parent_station:
                children_by_parent.setdefault(parent_station, []).append(row)

    _stops_cache[file_path] = {
        "by_id": stops_by_id,
        "by_name": stops_by_name,
        "children_by_parent": children_by_parent
    }

    return _stops_cache[file_path]


def _load_stop_times(file_path):
    if file_path in _stop_times_cache:
        return _stop_times_cache[file_path]

    trips = {}

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            trip_id = row["trip_id"]

            if trip_id not in trips:
                trips[trip_id] = []

            trips[trip_id].append(row)

    _stop_times_cache[file_path] = trips
    return trips


def preload_gtfs_data(stop_times_file, stops_file):
    """Load the static GTFS datasets into memory once."""
    _load_stops(stops_file)
    _load_stop_times(stop_times_file)


def find_stop_by_name(file_path, stop_name):
    stops = _load_stops(file_path)

    # First try the exact station name.
    exact_match = stops["by_name"].get(stop_name)

    if exact_match is not None:
        return exact_match

    # If there is no exact match, try case-insensitive matching.
    normalized_name = stop_name.strip().casefold()

    for name, stop in stops["by_name"].items():
        if name.strip().casefold() == normalized_name:
            return stop

    return None


def get_trip_stops(file_path, trip_id):
    trips = _load_stop_times(file_path)
    return trips.get(trip_id, [])


def get_stop_details(file_path, stop_id):
    stops = _load_stops(file_path)
    return stops["by_id"].get(stop_id)


def get_trip_route(stop_times_file, stops_file, trip_id):
    trip_stops = get_trip_stops(stop_times_file, trip_id)
    stops = _load_stops(stops_file)
    stops_by_id = stops["by_id"]

    route = []

    for stop in trip_stops:
        stop_details = stops_by_id.get(stop["stop_id"])

        if stop_details is None:
            continue

        route.append({
            **stop_details,
            "arrival_time": stop["arrival_time"],
            "departure_time": stop["departure_time"]
        })

    return route


def find_trips_between_stops(stop_times_file, stops_file, origin_name, destination_name):
    origin = find_stop_by_name(stops_file, origin_name)
    destination = find_stop_by_name(stops_file, destination_name)

    if origin is None or destination is None:
        return []

    origin_stop_id = origin["stop_id"]
    destination_stop_id = destination["stop_id"]
    trips = _load_stop_times(stop_times_file)
    matching_trips = []

    for trip_id, stops in trips.items():
        origin_index = None
        destination_index = None

        for index, stop in enumerate(stops):
            if stop["stop_id"] == origin_stop_id:
                origin_index = index
            if stop["stop_id"] == destination_stop_id:
                destination_index = index

        if (origin_index is not None and destination_index is not None
                and origin_index < destination_index):
            matching_trips.append(trip_id)

    return matching_trips


def find_trip_by_departure_time(
    stop_times_file,
    stops_file,
    origin_name,
    destination_name,
    requested_time
):
    stops = _load_stops(stops_file)

    origin_stop_ids = _get_candidate_stop_ids(
        stops,
        origin_name
    )

    destination_stop_ids = _get_candidate_stop_ids(
        stops,
        destination_name
    )

    if not origin_stop_ids or not destination_stop_ids:
        return None

    trips = _load_stop_times(stop_times_file)

    best_trip = None
    best_departure = None

    for trip_id, trip_stops in trips.items():
        origin_index = None
        destination_index = None
        origin_departure = None

        for index, stop in enumerate(trip_stops):
            stop_id = stop["stop_id"]

            if stop_id in origin_stop_ids:
                origin_index = index
                origin_departure = stop["departure_time"]

            if stop_id in destination_stop_ids:
                destination_index = index

        if (
            origin_index is not None
            and destination_index is not None
            and origin_index < destination_index
            and origin_departure is not None
            and origin_departure >= requested_time
        ):
            if (
                best_departure is None
                or origin_departure < best_departure
            ):
                best_trip = trip_id
                best_departure = origin_departure

    if best_trip is None:
        return None

    return {
        "trip_id": best_trip,
        "departure_time": best_departure
    }

def load_stop_times(file_path):
    return _load_stop_times(file_path)


def get_stop_names(stops_file):
    stops = _load_stops(stops_file)
    return sorted(stops["by_name"].keys())

def _get_candidate_stop_ids(stops, station_name):
    """
    Return all stop IDs that can represent a requested station.

    Handles:
    - exact station matches
    - case-insensitive matches
    - parent_station -> child stops
    - Hbf / Hauptbahnhof naming differences
    """

    def normalize_name(name):
        name = name.strip().casefold()
        name = name.replace(",", " ")
        name = " ".join(name.split())

        # Treat Hbf and Hauptbahnhof as equivalent.
        name = name.replace("hauptbahnhof", "hbf")

        return name

    requested_normalized = normalize_name(station_name)

    candidate_parent_ids = set()

    # Find all station records matching the requested name.
    for name, row in stops["by_name"].items():
        if normalize_name(name) == requested_normalized:
            candidate_parent_ids.add(row["stop_id"])

    # Also include the exact result if available.
    exact = stops["by_name"].get(station_name)
    if exact is not None:
        candidate_parent_ids.add(exact["stop_id"])

    candidate_stop_ids = set(candidate_parent_ids)

    # Include child stops.
    for parent_id in list(candidate_parent_ids):
        for child in stops["children_by_parent"].get(parent_id, []):
            candidate_stop_ids.add(child["stop_id"])

    return candidate_stop_ids