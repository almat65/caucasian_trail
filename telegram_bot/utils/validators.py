"""
Validation utilities for the Caucasian Trail Telegram Bot
"""

import re
from config import EXPECTED_LAT, EXPECTED_LON, MAX_COORDINATE_DISTANCE


def validate_coordinates(lat, lon):
    """Check if coordinates are in the expected region (Dagestan)"""
    lat_diff = abs(lat - EXPECTED_LAT)
    lon_diff = abs(lon - EXPECTED_LON)

    if lat_diff > MAX_COORDINATE_DISTANCE or lon_diff > MAX_COORDINATE_DISTANCE:
        return False, f"⚠️ Warning: Coordinates seem far from Dagestan region.\nExpected around: {EXPECTED_LAT}, {EXPECTED_LON}\nGot: {lat}, {lon}"
    return True, "OK"


def convert_youtube_url(url):
    """Convert YouTube Shorts URL to standard watch URL

    Converts:
        https://youtube.com/shorts/hhRyYlOuq4o?si=1fCAoOiUe4n_980c
    To:
        https://youtube.com/watch?v=hhRyYlOuq4o

    Also handles:
        - https://www.youtube.com/shorts/...
        - http://youtube.com/shorts/...
        - Shorts URLs without query parameters
        - Already converted URLs (returns as-is)
    """
    # Check if it's a Shorts URL
    # Pattern: youtube.com/shorts/VIDEO_ID (optionally followed by ?si=...)
    shorts_pattern = r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)'
    match = re.search(shorts_pattern, url)

    if match:
        video_id = match.group(1)
        return f"https://youtube.com/watch?v={video_id}"

    # Not a Shorts URL, return as-is
    return url
