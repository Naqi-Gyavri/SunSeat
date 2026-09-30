from engine.geography import (
    calculate_bearing,
    calculate_route_bearings,
    calculate_relative_angle,
    classify_sun_position,
    calculate_route_sun_positions,
    combine_date_and_time,
    is_sun_visible,
    count_sun_positions,
    calculate_route_sun_positions,
    combine_date_and_time,
    is_sun_visible,
    count_sun_positions,
    get_dominant_sun_position,
    calculate_side_confidence,
    recommend_side,
    get_journey_recommendation,
    format_recommendation,
    analyze_trip
)
from engine.sun_position import get_sun_position
from engine.gtfs_reader import get_trip_route, find_trip_by_departure_time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "DE-RV"
STOP_TIMES_FILE = DATA_DIR / "stop_times.txt"
STOPS_FILE = DATA_DIR / "stops.txt"


def get_real_test_trip_id():
    trip = find_trip_by_departure_time(
        STOP_TIMES_FILE,
        STOPS_FILE,
        "Karlsruhe Hbf",
        "Heilbronn Hbf",
        "10:00"
    )
    assert trip is not None, "Expected a Karlsruhe → Heilbronn trip at/after 10:00"
    return trip["trip_id"]

def test_calculate_bearing():
    result = calculate_bearing(
        49.002327,
        8.462822,
        49.028180,
        8.575224
    )

    print(result)

def test_bearing_north():
    result = calculate_bearing(
        50,
        10,
        51,
        10
    )
    print("North:", result)

def test_bearing_east():
    result = calculate_bearing(
        50,
        10,
        50,
        11
    )

    print("East:", result)

def test_bearing_south():
    result = calculate_bearing(
        51,
        10,
        50,
        10
    )

    print("South:", result)

def test_bearing_west():
    result = calculate_bearing(
        50,
        11,
        50,
        10
    )

    print("West:", result)

def test_calculate_route_bearings():
    route = [
        {
            "stop_name": "Station A",
            "stop_lat": "50",
            "stop_lon": "10"
        },
        {
            "stop_name": "Station B",
            "stop_lat": "51",
            "stop_lon": "10"
        },
        {
            "stop_name": "Station C",
            "stop_lat": "51",
            "stop_lon": "11"
        }
    ]

    result = calculate_route_bearings(route)

    print("Route bearings:", result)

def test_real_train_route_bearings():
    route = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    bearings = calculate_route_bearings(route)

    for i in range(len(bearings)):
        print(
            route[i]["stop_name"],
            "→",
            route[i + 1]["stop_name"],
            "=",
            bearings[i]
        )

def test_relative_angle_same_direction():
    result = calculate_relative_angle(90, 90)
    print("Same direction:", result)


def test_relative_angle_right():
    result = calculate_relative_angle(90, 180)
    print("Right:", result)


def test_relative_angle_left():
    result = calculate_relative_angle(90, 0)
    print("Left:", result)


def test_relative_angle_wraparound():
    result = calculate_relative_angle(350, 10)
    print("Wraparound:", result)

def test_classify_sun_position():
    print("Front:", classify_sun_position(0))
    print("Right:", classify_sun_position(90))
    print("Left:", classify_sun_position(-90))
    print("Back:", classify_sun_position(180))

def test_classify_sun_position_boundaries():
    print("45°:", classify_sun_position(45))
    print("-45°:", classify_sun_position(-45))
    print("135°:", classify_sun_position(135))
    print("-135°:", classify_sun_position(-135))

def test_sun_position_relative_to_train():
    train_bearing = 70
    sun_azimuth = 120

    relative_angle = calculate_relative_angle(
        train_bearing,
        sun_azimuth
    )

    position = classify_sun_position(relative_angle)

    print("Relative angle:", relative_angle)
    print("Sun position:", position)

def test_real_sun_position_relative_to_train():
    route = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    train_bearing = calculate_bearing(
        float(route[0]["stop_lat"]),
        float(route[0]["stop_lon"]),
        float(route[1]["stop_lat"]),
        float(route[1]["stop_lon"])
    )

    sun = get_sun_position(
        float(route[0]["stop_lat"]),
        float(route[0]["stop_lon"]),
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    relative_angle = calculate_relative_angle(
        train_bearing,
        sun["azimuth"]
    )

    position = classify_sun_position(relative_angle)

    print("Train bearing:", train_bearing)
    print("Sun azimuth:", sun["azimuth"])
    print("Relative angle:", relative_angle)
    print("Sun position:", position)


def test_real_route_sun_positions():
    route = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    assert len(results) == len(route) - 1

    for result in results:

        assert set(result.keys()) == {
            "stop_name",
            "sun_elevation",
            "next_stop_name",
            "bearing",
            "sun_azimuth",
            "sun_visible",
            "relative_angle",
            "position"
}
        assert result["sun_visible"] in {True, False}
        assert result["position"] in {"front", "right", "left", "back", None}

        print(
            result["stop_name"],
            "→",
            result["next_stop_name"],
            "| bearing:",
            result["bearing"],
            "| sun:",
            result["sun_azimuth"],
            "| elevation:",
            result["sun_elevation"],
            "| visible:",
            result["sun_visible"],
            "| relative:",
            result["relative_angle"],
            "| position:",
            result["position"]
        )

def test_combine_date_and_time():
    date_time = datetime(
        2026,
        8,
        11,
        10,
        0,
        tzinfo=ZoneInfo("Europe/Berlin")
    )

    result = combine_date_and_time(
        date_time,
        "22:13:00"
    )

    assert result == datetime(
        2026,
        8,
        11,
        22,
        13,
        0,
        tzinfo=ZoneInfo("Europe/Berlin")
    )

def test_combine_date_and_time_after_midnight():
    date_time = datetime(
        2026, 8, 18, 23, 0,
        tzinfo=ZoneInfo("Europe/Berlin")
    )

    result = combine_date_and_time(date_time, "24:21:00")

    assert result == datetime(
        2026, 8, 19, 0, 21,
        tzinfo=ZoneInfo("Europe/Berlin")
    )


def test_combine_date_and_time_beyond_25_hours():
    date_time = datetime(
        2026, 8, 18, 23, 0,
        tzinfo=ZoneInfo("Europe/Berlin")
    )

    result = combine_date_and_time(date_time, "25:24:00")

    assert result == datetime(
        2026, 8, 19, 1, 24,
        tzinfo=ZoneInfo("Europe/Berlin")
    )


def test_is_sun_visible():
    assert is_sun_visible(10) is True
    assert is_sun_visible(-10) is False

def test_daytime_sun_position():
    route = [
        {
            "stop_name": "Karlsruhe Hbf",
            "stop_lat": "48.993515",
            "stop_lon": "8.402181",
            "departure_time": "10:00:00"
        },
        {
            "stop_name": "Karlsruhe-Durlach",
            "stop_lat": "49.002327",
            "stop_lon": "8.462822",
            "departure_time": "10:05:00"
        }
    ]

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    assert len(results) == 1

    result = results[0]

    assert result["sun_visible"] is True
    assert result["position"] in {"front", "right", "left", "back"}

    print(
        "Train bearing:", result["bearing"],
        "| Sun azimuth:", result["sun_azimuth"],
        "| Elevation:", result["sun_elevation"],
        "| Position:", result["position"]
    )

def test_count_sun_positions():
    results = [
        {"position": "right"},
        {"position": "right"},
        {"position": "left"},
        {"position": "front"},
        {"position": None},
        {"position": "back"},
        {"position": None}
    ]

    counts = count_sun_positions(results)

    assert counts == {
        "front": 1,
        "right": 2,
        "left": 1,
        "back": 1
    }

def test_real_route_sun_position_counts():
    route = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    counts = count_sun_positions(results)

    print("Sun position counts:", counts)

    assert set(counts.keys()) == {
        "front",
        "right",
        "left",
        "back"
    }

def test_get_dominant_sun_position():
    counts = {
        "front": 2,
        "right": 3,
        "left": 7,
        "back": 1
    }

    result = get_dominant_sun_position(counts)

    assert result == "left"

def test_get_dominant_sun_position_no_side():
    counts = {
        "front": 4,
        "right": 0,
        "left": 0,
        "back": 2
    }

    result = get_dominant_sun_position(counts)

    assert result is None


def test_real_route_dominant_sun_position():
    route = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    counts = count_sun_positions(results)
    dominant = get_dominant_sun_position(counts)

    print("Sun position counts:", counts)
    print("Dominant sun position:", dominant)

    side_counts = {"left": counts["left"], "right": counts["right"]}
    if side_counts["left"] == side_counts["right"]:
        assert dominant is None
    else:
        assert dominant == max(side_counts, key=side_counts.get)

def test_get_dominant_sun_position_tie():
    counts = {
        "front": 1,
        "right": 4,
        "left": 4,
        "back": 0
    }

    result = get_dominant_sun_position(counts)

    assert result is None

def test_daytime_route_dominant_sun_position():
    route = [
        {
            "stop_name": "Stop A",
            "stop_lat": "48.993515",
            "stop_lon": "8.402181",
            "departure_time": "10:00:00"
        },
        {
            "stop_name": "Stop B",
            "stop_lat": "49.002327",
            "stop_lon": "8.462822",
            "departure_time": "10:10:00"
        },
        {
            "stop_name": "Stop C",
            "stop_lat": "49.028180",
            "stop_lon": "8.575224",
            "departure_time": "10:20:00"
        },
        {
            "stop_name": "Stop D",
            "stop_lat": "49.015785",
            "stop_lon": "8.609981",
            "departure_time": "10:30:00"
        },
        {
            "stop_name": "Stop E",
            "stop_lat": "49.036900",
            "stop_lon": "8.693448",
            "departure_time": "10:40:00"
        }
    ]

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    counts = count_sun_positions(results)
    dominant = get_dominant_sun_position(counts)

    print("Sun position counts:", counts)
    print("Dominant sun position:", dominant)

    assert dominant in {"left", "right"}

def test_calculate_side_confidence():
    counts = {
        "front": 2,
        "right": 8,
        "left": 2,
        "back": 1
    }

    confidence = calculate_side_confidence(counts)

    assert confidence == 0.8

def test_calculate_side_confidence_tie():
    counts = {
        "front": 2,
        "right": 5,
        "left": 5,
        "back": 1
    }

    confidence = calculate_side_confidence(counts)

    assert confidence is None

def test_calculate_side_confidence_no_side():
    counts = {
        "front": 5,
        "right": 0,
        "left": 0,
        "back": 2
    }

    confidence = calculate_side_confidence(counts)

    assert confidence is None

def test_recommend_side_strong():
    counts = {
        "front": 2,
        "right": 8,
        "left": 2,
        "back": 1
    }

    result = recommend_side(counts)

    assert result == "right"

def test_recommend_side_weak():
    counts = {
        "front": 2,
        "right": 6,
        "left": 5,
        "back": 1
    }

    result = recommend_side(counts)

    assert result is None

def test_recommend_side_tie():
    counts = {
        "front": 2,
        "right": 5,
        "left": 5,
        "back": 1
    }

    result = recommend_side(counts)

    assert result is None

def test_real_route_recommendation():
    route = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    counts = count_sun_positions(results)
    recommendation = recommend_side(counts)

    print("Sun position counts:", counts)
    print("Recommendation:", recommendation)

    if recommendation is None:
        assert counts["left"] == counts["right"] or counts["left"] + counts["right"] == 0
    else:
        assert recommendation in {"left", "right"}
        assert calculate_side_confidence(counts) >= 0.6

def test_daytime_route_recommendation():
    route = [
        {
            "stop_name": "Stop A",
            "stop_lat": "48.993515",
            "stop_lon": "8.402181",
            "departure_time": "10:00:00"
        },
        {
            "stop_name": "Stop B",
            "stop_lat": "49.002327",
            "stop_lon": "8.462822",
            "departure_time": "10:10:00"
        },
        {
            "stop_name": "Stop C",
            "stop_lat": "49.028180",
            "stop_lon": "8.575224",
            "departure_time": "10:20:00"
        },
        {
            "stop_name": "Stop D",
            "stop_lat": "49.015785",
            "stop_lon": "8.609981",
            "departure_time": "10:30:00"
        },
        {
            "stop_name": "Stop E",
            "stop_lat": "49.036900",
            "stop_lon": "8.693448",
            "departure_time": "10:40:00"
        }
    ]

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    counts = count_sun_positions(results)
    recommendation = recommend_side(counts)

    print("Sun position counts:", counts)
    print("Recommendation:", recommendation)

    assert recommendation in {"left", "right"}

def test_strong_daytime_route_recommendation():
    counts = {
        "front": 1,
        "right": 4,
        "left": 0,
        "back": 0
    }

    recommendation = recommend_side(counts)
    confidence = calculate_side_confidence(counts)

    print("Sun position counts:", counts)
    print("Confidence:", confidence)
    print("Recommendation:", recommendation)

    assert confidence == 1.0
    assert recommendation == "right"

def test_get_recommendation_strong():
    counts = {
        "front": 1,
        "right": 4,
        "left": 0,
        "back": 0
    }

    result = get_journey_recommendation(counts)

    assert result == {
        "side": "left",
        "confidence": 1.0
    }

def test_get_recommendation_weak():
    counts = {
        "front": 3,
        "right": 1,
        "left": 0,
        "back": 0
    }

    result = get_journey_recommendation(counts)

    assert result == {
        "side": "left",
        "confidence": 1.0
    }

def test_real_route_get_recommendation():
    route = get_trip_route(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id()
    )

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    counts = count_sun_positions(results)
    recommendation = get_journey_recommendation(counts)

    print("Sun position counts:", counts)
    print("Recommendation:", recommendation)

    if recommendation["side"] is None:
        assert recommendation["confidence"] is None
    else:
        assert recommendation["side"] in {"left", "right"}
        assert 0.6 <= recommendation["confidence"] <= 1.0

def test_daytime_get_recommendation():
    counts = {
        "front": 1,
        "right": 4,
        "left": 0,
        "back": 0
    }

    recommendation = get_journey_recommendation(counts)

    print("Recommendation:", recommendation)

    assert recommendation == {
        "side": "left",
        "confidence": 1.0
    }

def test_format_recommendation():
    recommendation = {
        "side": "right",
        "confidence": 0.8
    }

    result = format_recommendation(recommendation)

    assert result == "Recommended side: RIGHT | Confidence: 80%"

def test_format_recommendation_no_side():
    recommendation = {
        "side": None,
        "confidence": None
    }

    result = format_recommendation(recommendation)

    assert result == "No clear side recommendation."

def test_analyze_trip_real_route():
    result = analyze_trip(
        STOP_TIMES_FILE,
        STOPS_FILE,
        get_real_test_trip_id(),
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    print("Recommendation:", result["recommendation"])
    print("Formatted:", result["formatted"])

    assert result["route"]
    assert len(result["sun_positions"]) == len(result["route"]) - 1

    recommendation = result["recommendation"]
    if recommendation["side"] is None:
        assert recommendation["confidence"] is None
        assert result["formatted"] == "No clear side recommendation."
    else:
        assert recommendation["side"] in {"left", "right"}
        assert 0.6 <= recommendation["confidence"] <= 1.0
        assert "Recommended side:" in result["formatted"]

def test_analyze_trip_daytime(monkeypatch):
    route = [
        {
            "stop_name": "Stop A",
            "stop_lat": "48.993515",
            "stop_lon": "8.402181",
            "departure_time": "10:00:00"
        },
        {
            "stop_name": "Stop B",
            "stop_lat": "49.002327",
            "stop_lon": "8.402181",
            "departure_time": "10:10:00"
        },
        {
            "stop_name": "Stop C",
            "stop_lat": "49.011139",
            "stop_lon": "8.402181",
            "departure_time": "10:20:00"
        },
        {
            "stop_name": "Stop D",
            "stop_lat": "49.019950",
            "stop_lon": "8.402181",
            "departure_time": "10:30:00"
        },
        {
            "stop_name": "Stop E",
            "stop_lat": "49.028760",
            "stop_lon": "8.402181",
            "departure_time": "10:40:00"
        }
    ]

    monkeypatch.setattr(
        "engine.geography.get_trip_route",
        lambda stop_times_file, stops_file, trip_id: route
    )

    result = analyze_trip(
        "dummy_stop_times.txt",
        "dummy_stops.txt",
        "test_trip",
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    print("Sun position counts:", result["counts"])
    print("Recommendation:", result["recommendation"])
    print("Formatted:", result["formatted"])

    assert result["recommendation"]["side"] == "left"
    assert result["recommendation"]["confidence"] >= 0.6

def test_calculate_bearing_same_point():
    bearing = calculate_bearing(
        48.993515,
        8.402181,
        48.993515,
        8.402181
    )

    print("Same-point bearing:", bearing)

    assert bearing == 0

def test_zero_distance_route_segment():
    route = [
        {
            "stop_name": "Stop A",
            "stop_lat": "48.993515",
            "stop_lon": "8.402181",
            "departure_time": "10:00:00"
        },
        {
            "stop_name": "Stop B",
            "stop_lat": "48.993515",
            "stop_lon": "8.402181",
            "departure_time": "10:05:00"
        }
    ]

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    print("Zero-distance result:", results)

    assert len(results) == 1
    assert results[0]["bearing"] == 0

def test_single_segment_route():
    route = [
        {
            "stop_name": "Stop A",
            "stop_lat": "48.993515",
            "stop_lon": "8.402181",
            "departure_time": "10:00:00"
        },
        {
            "stop_name": "Stop B",
            "stop_lat": "49.002327",
            "stop_lon": "8.462822",
            "departure_time": "10:05:00"
        }
    ]

    results = calculate_route_sun_positions(
        route,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    counts = count_sun_positions(results)
    recommendation = get_journey_recommendation(counts)

    print("Single-segment counts:", counts)
    print("Single-segment recommendation:", recommendation)

    assert len(results) == 1
    assert sum(counts.values()) <= 1

def test_empty_route():
    results = calculate_route_sun_positions(
        [],
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    assert results == []