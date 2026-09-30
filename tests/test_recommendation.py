from engine.recommendation import (
    get_recommendation,
    get_seat_side_from_sun_position
)

def test_recommendation_right():
    assert get_recommendation("RIGHT") == "LEFT"

def test_recommendation_left():
    assert get_recommendation("LEFT") == "RIGHT"


def test_recommendation_front():
    assert get_recommendation("FRONT") == "EITHER"


def test_recommendation_back():
    assert get_recommendation("BACK") == "EITHER"

def test_seat_side_from_sun_right():
    assert get_seat_side_from_sun_position("right") == "left"


def test_seat_side_from_sun_left():
    assert get_seat_side_from_sun_position("left") == "right"


def test_seat_side_from_sun_front():
    assert get_seat_side_from_sun_position("front") is None


def test_seat_side_from_sun_back():
    assert get_seat_side_from_sun_position("back") is None