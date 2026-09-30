from app import run_sunseat


def test_run_sunseat_success():
    result = run_sunseat(
        "Karlsruhe Hbf",
        "Heilbronn Hbf",
        "2026-08-11",
        "10:00"
    )

    assert result["success"] is True
    assert result["trip_id"]
    assert result["scheduled_departure"] >= "10:00:00"

def test_run_sunseat_invalid_date():
    result = run_sunseat(
        "Karlsruhe Hbf",
        "Heilbronn Hbf",
        "2026-99-99",
        "10:00"
    )

    assert result["success"] is False
    assert result["message"] == "Invalid date. Please use YYYY-MM-DD."

def test_run_sunseat_invalid_departure_time():
    result = run_sunseat(
        "Karlsruhe Hbf",
        "Heilbronn Hbf",
        "2026-08-11",
        "25:90"
    )

    assert result["success"] is False
    assert result["message"] == "Invalid departure time. Please use HH:MM."

def test_run_sunseat_unknown_origin():
    result = run_sunseat(
        "Hogwarts Hbf",
        "Heilbronn Hbf",
        "2026-08-11",
        "10:00"
    )

    assert result["success"] is False
    assert result["message"] == "Origin station not found: Hogwarts Hbf"

def test_run_sunseat_unknown_destination():
    result = run_sunseat(
        "Karlsruhe Hbf",
        "Hogwarts Hbf",
        "2026-08-11",
        "10:00"
    )

    assert result["success"] is False
    assert result["message"] == "Destination station not found: Hogwarts Hbf"

def test_run_sunseat_no_matching_trip():
    result = run_sunseat(
        "Ilmenau",
        "Heilbronn Hbf",
        "2026-08-11",
        "10:00"
    )

    assert result["success"] is False
    assert result["message"] == "No matching trip found."