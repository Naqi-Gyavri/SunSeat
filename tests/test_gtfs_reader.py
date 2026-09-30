from engine.gtfs_reader import find_stop_by_name
from pathlib import Path
from engine.gtfs_reader import find_stop_by_name, get_trip_stops
from engine.gtfs_reader import find_stop_by_name, get_trip_stops, get_stop_details
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "DE-RV"
STOP_TIMES_FILE = DATA_DIR / "stop_times.txt"
STOPS_FILE = DATA_DIR / "stops.txt"


from engine.gtfs_reader import (
    find_stop_by_name,
    get_trip_stops,
    get_stop_details,
    get_trip_route,
    find_trips_between_stops,
    find_trip_by_departure_time,
    get_stop_names
)


def get_real_test_trip_id():
    trip = find_trip_by_departure_time(
        STOP_TIMES_FILE,
        STOPS_FILE,
        "Karlsruhe Hbf",
        "Heilbronn Hbf",
        "10:00"
    )
    assert trip is not None
    return trip["trip_id"]


def test_find_stop_by_name():
    result = find_stop_by_name(
        STOPS_FILE,
        "Ilmenau"
    )

    print(result["stop_lat"])
    print(result["stop_lon"])

def test_get_trip_stops():
    result = get_trip_stops(
        STOP_TIMES_FILE,
        get_real_test_trip_id()
    )

    for stop in result:
        print(stop)


def test_get_stop_details():
    result = get_stop_details(
        STOPS_FILE,
        "81992"
    )

    print(result)


def test_get_trip_route():
    result = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    for stop in result:
        print(stop["stop_name"], stop["stop_lat"], stop["stop_lon"])

def test_find_trips_between_stops():
    result = find_trips_between_stops(
        STOP_TIMES_FILE,
        STOPS_FILE,
        "Karlsruhe Hbf",
        "Heilbronn Hbf"
    )

    print(result)

    assert result


def test_find_trip_by_departure_time():
    result = find_trip_by_departure_time(
        STOP_TIMES_FILE,
        STOPS_FILE,
        "Karlsruhe Hbf",
        "Heilbronn Hbf",
        "10:00"
    )

    print(result)

    assert result is not None
    assert result["trip_id"]
    assert result["departure_time"] >= "10:00:00"

def test_find_trip_by_departure_time_no_match():
    result = find_trip_by_departure_time(
        STOP_TIMES_FILE,
        STOPS_FILE,
        "Ilmenau",
        "Heilbronn Hbf",
        "10:00"
    )

    assert result is None

def test_get_stop_names():
    stops_file = STOPS_FILE

    stop_names = get_stop_names(stops_file)

    assert "Karlsruhe Hbf" in stop_names
    assert "Heilbronn Hbf" in stop_names
    assert stop_names == sorted(stop_names)