from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from engine.geography import analyze_trip
from engine.gtfs_reader import (
    find_stop_by_name,
    find_trip_by_departure_time
)


# =========================================================
# SUNSEAT DATA PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "DE-RV"

STOP_TIMES_FILE = DATA_DIR / "stop_times.txt"
STOPS_FILE = DATA_DIR / "stops.txt"


def run_sunseat(origin, destination, date, departure_time):

    try:
        datetime.strptime(
            date,
            "%Y-%m-%d"
        )
    except ValueError:
        return {
            "success": False,
            "message": "Invalid date. Please use YYYY-MM-DD."
        }

    try:
        datetime.strptime(
            departure_time,
            "%H:%M"
        )
    except ValueError:
        return {
            "success": False,
            "message": "Invalid departure time. Please use HH:MM."
        }

    origin_stop = find_stop_by_name(
        STOPS_FILE,
        origin
    )

    destination_stop = find_stop_by_name(
        STOPS_FILE,
        destination
    )

    if origin_stop is None:
        return {
            "success": False,
            "message": f"Origin station not found: {origin}"
        }

    if destination_stop is None:
        return {
            "success": False,
            "message": f"Destination station not found: {destination}"
        }

    trip = find_trip_by_departure_time(
        STOP_TIMES_FILE,
        STOPS_FILE,
        origin,
        destination,
        departure_time
    )

    if trip is None:
        return {
            "success": False,
            "message": "No matching trip found."
        }

    # GTFS allows times beyond 24:00:00 for services
    # continuing after midnight. Python's strptime() does not,
    # so convert the GTFS time manually while preserving the
    # correct calendar day for the sun-position analysis.
    gtfs_time = trip["departure_time"]
    hours, minutes, seconds = map(int, gtfs_time.split(":"))

    date_time = datetime.strptime(
        date,
        "%Y-%m-%d"
    )

    date_time += timedelta(
        days=hours // 24,
        hours=hours % 24,
        minutes=minutes,
        seconds=seconds
    )

    date_time = date_time.replace(
        tzinfo=ZoneInfo("Europe/Berlin")
    )

    result = analyze_trip(
        STOP_TIMES_FILE,
        STOPS_FILE,
        trip["trip_id"],
        date_time
    )

    return {
        "success": True,
        "origin": origin,
        "destination": destination,
        "requested_departure": departure_time,
        "trip_id": trip["trip_id"],
        "scheduled_departure": trip["departure_time"],
        "result": result
    }


def main():
    print("Welcome to SunSeat!")

    origin = input("Enter origin station: ")
    destination = input("Enter destination station: ")
    date = input("Enter date (YYYY-MM-DD): ")
    departure_time = input("Enter departure time (HH:MM): ")

    response = run_sunseat(
        origin,
        destination,
        date,
        departure_time
    )

    if not response["success"]:
        print(response["message"])
        return

    result = response["result"]

    print()
    print("=" * 40)
    print("              SUNSEAT")
    print("=" * 40)

    print()
    print(f"{origin} → {destination}")
    print(f"Requested departure: {departure_time}")

    print()
    print("Sun exposure:")
    print(f"  Front: {result['counts']['front']}")
    print(f"  Right: {result['counts']['right']}")
    print(f"  Left:  {result['counts']['left']}")
    print(f"  Back:  {result['counts']['back']}")

    print()
    print(result["formatted"])
    print("=" * 40)


if __name__ == "__main__":
    main()