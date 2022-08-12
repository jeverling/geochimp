"""Utility functions that aren't directly related to any 3rd-party service.

Such code is commonly placed into __init__.py but I prefer a separate module.
"""
from exif import Image


def get_choice_value_for_label(choices, label):
    # @TODO: error handling
    return next(x[0] for x in choices if x[1] == label)


def convert_latlon_to_dms(lat_lon):
    """Convert decimal GPS coordinates to degree, minute, second for exif data.

    Coordinates come from Survey123 like this, where x is longitude (E/W):
    {"x": 7.1396999999998805, "y": 50.69659999999914}
    """

    def decimal_to_dms(lat_or_lon):
        degrees = int(lat_or_lon)
        temp = 60 * abs(lat_or_lon - degrees)
        minutes = int(temp)
        seconds = 60 * (temp - minutes)
        return degrees * -1 if degrees < 0 else degrees, minutes, seconds

    gps_dms = {
        "gps_longitude": decimal_to_dms(lat_lon["x"]),
        "gps_longitude_ref": "W" if lat_lon["x"] < 0 else "E",
        "gps_latitude": decimal_to_dms(lat_lon["y"]),
        "gps_latitude_ref": "S" if lat_lon["y"] < 0 else "N",
    }

    return gps_dms


def write_gps_coordinates_to_exif(lat_lon, file_path):
    """Overwrite file with updated version.

    We have to convert decimal location to dms (degree, minute, second),
    and update exif data accordingly.
    """
    gps_dms = convert_latlon_to_dms(lat_lon)

    with open(file_path, "rb") as input_image_file:
        image = Image(input_image_file)

    with open(file_path, "wb") as output_image_file:
        image.gps_longitude = gps_dms["gps_longitude"]
        image.gps_longitude_ref = gps_dms["gps_longitude_ref"]
        image.gps_latitude = gps_dms["gps_latitude"]
        image.gps_latitude_ref = gps_dms["gps_latitude_ref"]

        output_image_file.write(image.get_file())
