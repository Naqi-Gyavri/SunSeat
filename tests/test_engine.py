import pytest
from engine.recommendation import get_recommendation_from_heading

@pytest.mark.parametrize(
    "heading, sun_azimuth, expected",
    [
        (180, 90, "RIGHT"),
        (350, 10, "LEFT"),
        (10, 350, "RIGHT"),
        (0, 180, "EITHER"),
        (90, 90, "EITHER"),
        (0, 181, "RIGHT"),
    ]
)

def test_recommendation_from_heading(heading, sun_azimuth, expected):
    assert get_recommendation_from_heading(heading, sun_azimuth) == expected