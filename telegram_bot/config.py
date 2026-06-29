"""
Configuration and constants for the Caucasian Trail Telegram Bot
"""

import os

# GitHub configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = 'almat65/caucasian_trail'
FILE_PATH = 'data/actual_position.geojson'

# Telegram bot token
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Bot password for access control
BOT_PASSWORD = os.environ.get('BOT_PASSWORD')

# Coordinate validation (Dagestan region)
EXPECTED_LAT = 42.900000
EXPECTED_LON = 44.500000
MAX_COORDINATE_DISTANCE = 6.0  # degrees (roughly 500km tolerance)

# Conversation states
(PASSWORD, MENU, GET_ID, CREATE_DAY, CREATE_DATE, CREATE_LOCATION, CREATE_DISTANCE,
 CREATE_ELEVATION, CREATE_ACCOMMODATION, CREATE_LATITUDE, CREATE_LONGITUDE, CREATE_YOUTUBE,
 CREATE_NOTES, CREATE_PHOTOS, UPDATE_ID, UPDATE_FIELD, UPDATE_VALUE, UPDATE_PHOTOS,
 DELETE_ID, DELETE_CONFIRM) = range(20)
