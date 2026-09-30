from astral import Observer
from astral.sun import azimuth, elevation

def get_sun_position(latitude, longitude, date_time):
    observer = Observer(latitude, longitude)

    sun_azimuth = azimuth(observer, date_time)
    sun_elevation = elevation(observer, date_time)

    return {
    "azimuth": sun_azimuth,
    "elevation": sun_elevation
    }


