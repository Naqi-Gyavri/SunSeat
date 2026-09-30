from engine.relative_position import get_relative_position_from_heading

def get_recommendation(relative_position):
    if relative_position == "RIGHT":
        return "LEFT"
    elif relative_position == "LEFT":
        return "RIGHT"
    elif relative_position in ("FRONT", "BACK"):
        return "EITHER"



def get_recommendation_from_heading(heading, sun_azimuth):
    relative_position = get_relative_position_from_heading(heading, sun_azimuth)
    return get_recommendation(relative_position)


def get_seat_side_from_sun_position(sun_position):
    if sun_position == "right":
        return "left"
    elif sun_position == "left":
        return "right"
    elif sun_position in ("front", "back"):
        return None
    else:
        return None

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

    max_count = max(visible_counts.values())

    dominant_positions = [
        position
        for position, count in visible_counts.items()
        if count == max_count
    ]

    if len(dominant_positions) > 1:
        return None

    return dominant_positions[0]


def calculate_side_confidence(counts):
    total_visible = (
    counts["left"] +
    counts["right"]
)

    if total_visible == 0:
        return None

    left = counts["left"]
    right = counts["right"]

    if left == right:
        return None

    dominant_count = max(left, right)

    return dominant_count / total_visible


def recommend_side(counts, threshold=0.6):
    dominant_side = get_dominant_sun_position(counts)

    if dominant_side is None:
        return None

    confidence = calculate_side_confidence(counts)

    if confidence < threshold:
        return None

    return dominant_side


def get_journey_recommendation(counts):
    sun_side = recommend_side(counts)

    if sun_side is None:
        return {
            "side": None,
            "confidence": None
        }

    confidence = calculate_side_confidence(counts)
    seat_side = get_seat_side_from_sun_position(sun_side)

    return {
        "side": seat_side,
        "confidence": confidence
    }


def format_recommendation(recommendation):
    if recommendation["side"] is None:
        return "No clear side recommendation."

    side = recommendation["side"].upper()
    confidence = recommendation["confidence"] * 100

    return f"Recommended side: {side} | Confidence: {confidence:.0f}%"