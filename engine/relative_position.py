def get_relative_angle(heading, sun_azimuth):
    difference = sun_azimuth - heading
    difference = difference % 360
    if difference > 180:
        difference = difference - 360
    return difference

def get_relative_position(relative_angle):
    if 0 < relative_angle < 180:
        return "RIGHT"
    elif 0 > relative_angle > -180:
        return "LEFT"
    elif relative_angle == 180 or relative_angle == -180:
        return "BACK"
    elif relative_angle == 0:
        return "FRONT"

def get_relative_position_from_heading(heading, sun_azimuth):
    relative_angle = get_relative_angle(heading, sun_azimuth)
    return get_relative_position(relative_angle)

