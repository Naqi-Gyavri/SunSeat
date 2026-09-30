import math

from datetime import datetime, timedelta

from engine.sun_position import get_sun_position
from engine.gtfs_reader import get_trip_route
from engine.recommendation import (
    get_seat_side_from_sun_position,
    get_dominant_sun_position,
    calculate_side_confidence,
    recommend_side,
    get_journey_recommendation,
    format_recommendation
)


def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    x = math.sin(lon2 - lon1) * math.cos(lat2)

    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2)
        * math.cos(lon2 - lon1)
    )

    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = bearing % 360

    return bearing


def calculate_route_bearings(route):
    bearings = []

    for i in range(len(route) - 1):
        current_stop = route[i]
        next_stop = route[i + 1]

        lat1 = float(current_stop["stop_lat"])
        lon1 = float(current_stop["stop_lon"])

        lat2 = float(next_stop["stop_lat"])
        lon2 = float(next_stop["stop_lon"])

        bearing = calculate_bearing(
            lat1,
            lon1,
            lat2,
            lon2
        )

        bearings.append(bearing)

    return bearings


def calculate_relative_angle(train_bearing, sun_azimuth):
    difference = sun_azimuth - train_bearing
    difference = (difference + 180) % 360 - 180

    return difference


def classify_sun_position(relative_angle):
    if -45 <= relative_angle <= 45:
        return "front"

    if 45 < relative_angle < 135:
        return "right"

    if -135 < relative_angle < -45:
        return "left"

    return "back"


def combine_date_and_time(date_time, time_string):
    # GTFS permits service times beyond 24:00:00 for journeys
    # continuing after midnight. Python's strptime() does not.
    hours, minutes, seconds = map(
        int,
        time_string.split(":")
    )

    combined = datetime.combine(
        date_time.date(),
        datetime.min.time()
    )

    combined += timedelta(
        days=hours // 24,
        hours=hours % 24,
        minutes=minutes,
        seconds=seconds
    )

    combined = combined.replace(
        tzinfo=date_time.tzinfo
    )

    return combined


def is_sun_visible(elevation):
    return elevation > 0


def count_sun_positions(results):
    counts = {
        "front": 0,
        "right": 0,
        "left": 0,
        "back": 0
    }

    for result in results:
        position = result["position"]

        if position is not None:
            counts[position] += 1

    return counts


def calculate_route_sun_positions(route, date_time):
    sun_positions = []

    for i in range(len(route) - 1):
        current_stop = route[i]
        next_stop = route[i + 1]

        bearing = calculate_bearing(
            float(current_stop["stop_lat"]),
            float(current_stop["stop_lon"]),
            float(next_stop["stop_lat"]),
            float(next_stop["stop_lon"])
        )

        segment_time = combine_date_and_time(
            date_time,
            current_stop["departure_time"]
        )

        sun = get_sun_position(
            float(current_stop["stop_lat"]),
            float(current_stop["stop_lon"]),
            segment_time
        )

        sun_visible = is_sun_visible(
            sun["elevation"]
        )

        relative_angle = calculate_relative_angle(
            bearing,
            sun["azimuth"]
        )

        if sun_visible:
            position = classify_sun_position(
                relative_angle
            )
        else:
            position = None

        sun_positions.append({
            "stop_name": current_stop["stop_name"],
            "next_stop_name": next_stop["stop_name"],
            "bearing": bearing,
            "sun_azimuth": sun["azimuth"],
            "sun_elevation": sun["elevation"],
            "sun_visible": sun_visible,
            "relative_angle": relative_angle,
            "position": position
        })

    return sun_positions


def get_dominant_sun_position(counts):
    visible_counts = {
        position: count
        for position, count in counts.items()
        if position != "front"
        and position != "back"
        and count > 0
    }

    if not visible_counts:
        return None

    max_count = max(
        visible_counts.values()
    )

    dominant_positions = [
        position
        for position, count in visible_counts.items()
        if count == max_count
    ]

    if len(dominant_positions) > 1:
        return None

    return dominant_positions[0]


def calculate_side_confidence(counts):
    left = counts["left"]
    right = counts["right"]

    total_side_exposure = left + right

    if total_side_exposure == 0:
        return None

    if left == right:
        return None

    dominant_count = max(
        left,
        right
    )

    return dominant_count / total_side_exposure


def recommend_side(counts, threshold=0.6):
    dominant_side = get_dominant_sun_position(
        counts
    )

    if dominant_side is None:
        return None

    confidence = calculate_side_confidence(
        counts
    )

    if confidence < threshold:
        return None

    return dominant_side


def get_journey_recommendation(counts):
    sun_side = recommend_side(
        counts
    )

    if sun_side is None:
        return {
            "side": None,
            "confidence": None
        }

    confidence = calculate_side_confidence(
        counts
    )

    seat_side = get_seat_side_from_sun_position(
        sun_side
    )

    return {
        "side": seat_side,
        "confidence": confidence
    }


def format_recommendation(recommendation):
    if recommendation["side"] is None:
        return "No clear side recommendation."

    side = recommendation["side"].upper()
    confidence = recommendation["confidence"] * 100

    return (
        f"Recommended side: {side} | "
        f"Confidence: {confidence:.0f}%"
    )


def analyze_trip(
    stop_times_file,
    stops_file,
    trip_id,
    date_time
):
    route = get_trip_route(
        stop_times_file,
        stops_file,
        trip_id
    )

    results = calculate_route_sun_positions(
        route,
        date_time
    )

    counts = count_sun_positions(
        results
    )

    recommendation = get_journey_recommendation(
        counts
    )

    formatted = format_recommendation(
        recommendation
    )

    return {
        "route": route,
        "sun_positions": results,
        "counts": counts,
        "recommendation": recommendation,
        "formatted": formatted
    }