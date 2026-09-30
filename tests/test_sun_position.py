import pytest
from datetime import datetime
from datetime import datetime
from zoneinfo import ZoneInfo
from engine.sun_position import get_sun_position

def test_get_sun_position():
    result = get_sun_position(
        52.52,
        13.405,
        datetime(2026, 8, 10, 16, 0)
    )

    assert result["azimuth"] == pytest.approx(265.40164879630834)
    assert result["elevation"] == pytest.approx(23.093619494589035)

def test_sun_below_horizon():
    result = get_sun_position(
        52.52,
        13.405,
        datetime(2026, 8, 10, 0, 0)
    )

    assert result["elevation"] < 0

def test_get_sun_position_with_timezone():
    result = get_sun_position(
        49.0,
        8.4,
        datetime(
            2026,
            8,
            11,
            10,
            0,
            tzinfo=ZoneInfo("Europe/Berlin")
        )
    )

    print("Timezone-aware sun position:", result)
