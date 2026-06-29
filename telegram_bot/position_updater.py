#!/usr/bin/env python3
"""
Telegram bot to update actual position on the Caucasian Trail map
Fetches test_position.geojson from GitHub, adds new position, and commits back
"""

import os
import json
import logging
from datetime import datetime
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from translations import TRANSLATIONS  # Assuming translations.py contains the TRANSLATIONS dictionary

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# GitHub configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')  # You'll set this
GITHUB_REPO = 'almat65/caucasian_trail'
FILE_PATH = 'data/actual_position.geojson'

# Telegram bot token
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # You'll set this

# Bot password for access control
BOT_PASSWORD = os.environ.get('BOT_PASSWORD')  # Change this!

# Coordinate validation (Dagestan region)
EXPECTED_LAT = 42.900000
EXPECTED_LON = 44.500000
MAX_COORDINATE_DISTANCE = 6.0  # degrees (roughly 500km tolerance)

# Conversation states
PASSWORD, MENU, GET_ID, CREATE_DAY, CREATE_DATE, CREATE_LOCATION, CREATE_DISTANCE, CREATE_ELEVATION, CREATE_ACCOMMODATION, CREATE_LATITUDE, CREATE_LONGITUDE, CREATE_YOUTUBE, CREATE_NOTES, CREATE_PHOTOS, UPDATE_ID, UPDATE_FIELD, UPDATE_VALUE, UPDATE_PHOTOS, DELETE_ID, DELETE_CONFIRM = range(20)

def get_text(context: ContextTypes.DEFAULT_TYPE, key: str, **kwargs) -> str:
    """Get translated text based on user's language preference"""
    lang = context.user_data.get('lang', 'en')
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'][key])
    return text.format(**kwargs) if kwargs else text


class PositionData:
    """Store position data during conversation"""
    def __init__(self):
        self.data = {}
        self.update_id = None
        self.uploaded_photos = []  # Track uploaded photo filenames
        self.photo_count = 0  # Counter for naming photos

    def reset(self):
        self.data = {}
        self.update_id = None
        self.uploaded_photos = []
        self.photo_count = 0


# Global storage for current position being added
current_position = PositionData()


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
    import re

    # Check if it's a Shorts URL
    # Pattern: youtube.com/shorts/VIDEO_ID (optionally followed by ?si=...)
    shorts_pattern = r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)'
    match = re.search(shorts_pattern, url)

    if match:
        video_id = match.group(1)
        return f"https://youtube.com/watch?v={video_id}"

    # Not a Shorts URL, return as-is
    return url

def fetch_geojson_from_github():
    """Fetch current geojson file from GitHub"""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    content = response.json()
    # Content is base64 encoded
    import base64
    file_content = base64.b64decode(content['content']).decode('utf-8')

    return json.loads(file_content), content['sha']  # Return both content and SHA for updating


def update_geojson_on_github(geojson_data, sha, commit_message=None):
    """Update geojson file on GitHub with optional custom commit message"""
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Encode content
    import base64
    content = json.dumps(geojson_data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    # Prepare commit
    if commit_message is None:
        commit_message = f'Bot: Add Day {current_position.data.get("day", "?")} position'

    data = {
        'message': commit_message,
        'content': encoded_content,
        'sha': sha,
        'branch': 'master'
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


async def upload_photo_to_github(photo_bytes, filename, commit_message='Bot: Upload photo'):
    """Upload a photo file to GitHub assets/photos/ folder"""
    file_path = f'assets/photos/{filename}'
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Encode photo as base64
    import base64
    encoded_content = base64.b64encode(photo_bytes).decode('utf-8')

    # Check if file already exists (to get SHA if updating)
    check_response = requests.get(url, headers=headers)
    sha = None
    if check_response.status_code == 200:
        sha = check_response.json()['sha']

    # Prepare commit
    data = {
        'message': commit_message,
        'content': encoded_content,
        'branch': 'master'
    }

    if sha:
        data['sha'] = sha  # Update existing file

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation and ask for password"""
    current_position.reset()
    # Set default language if not set
    if 'lang' not in context.user_data:
        context.user_data['lang'] = 'en'
    await update.message.reply_text(get_text(context, 'welcome'))
    return PASSWORD


async def set_language_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch to English"""
    context.user_data['lang'] = 'en'
    await update.message.reply_text(get_text(context, 'lang_switched'))


async def set_language_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch to Russian"""
    context.user_data['lang'] = 'ru'
    await update.message.reply_text(get_text(context, 'lang_switched'))


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify password and show menu"""
    password = update.message.text.strip()

    if password == BOT_PASSWORD:
        await update.message.reply_text(get_text(context, 'access_granted'))
        return MENU
    else:
        await update.message.reply_text(get_text(context, 'wrong_password'))
        return ConversationHandler.END


async def menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu choice"""
    choice = update.message.text.strip()

    if choice == '1':
        await update.message.reply_text(get_text(context, 'create_start'))
        return CREATE_DAY
    elif choice == '2':
        await update.message.reply_text(get_text(context, 'update_start'))
        return UPDATE_ID
    elif choice == '3':
        await update.message.reply_text(get_text(context, 'get_start'))
        return GET_ID
    elif choice == '4':
        await update.message.reply_text(get_text(context, 'delete_start'))
        return DELETE_ID
    else:
        await update.message.reply_text(get_text(context, 'menu_invalid'))
        return MENU


# ===== GET RECORD =====
async def get_record_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display a record by ID or 'last' for most recent"""
    try:
        user_input = update.message.text.strip().lower()

        # Fetch from GitHub
        geojson_data, _ = fetch_geojson_from_github()

        # Check if user wants the last record
        if user_input == 'last':
            if not geojson_data['features']:
                await update.message.reply_text(get_text(context, 'get_no_records'))
                return ConversationHandler.END

            # Get the record with the highest ID
            record = max(geojson_data['features'], key=lambda f: f['properties']['id'])
        else:
            # Try to parse as integer
            record_id = int(user_input)

            # Find the record
            record = None
            for feature in geojson_data['features']:
                if feature['properties']['id'] == record_id:
                    record = feature
                    break

            if not record:
                await update.message.reply_text(
                    get_text(context, 'update_not_found', id=record_id)
                )
                return ConversationHandler.END

        # Format and send
        props = record['properties']
        coords = record['geometry']['coordinates']

        response = f"""
✅ Record #{props['id']}:

📅 Day: {props['day']}
📆 Date: {props['date']}
📍 Location: {props['location']}
🚶 Distance: {props['distance_km']} km
⛰️ Elevation: {props['elevation_gain']} m
🏕️ Accommodation: {props['accommodation_type']}
📌 Coordinates: [{coords[0]}, {coords[1]}] (lon, lat)
🎥 YouTube: {props.get('youtube_url', 'None')}
📝 Notes: {props.get('notes', 'None')}
📸 Photos: {', '.join(props.get('photos', [])) if props.get('photos') else 'None'}

JSON:
```json
{json.dumps(record, ensure_ascii=False, indent=2)}
```

Use /start for more options.
        """

        await update.message.reply_text(response)

    except ValueError:
        await update.message.reply_text(get_text(context, 'update_invalid_id'))
        return GET_ID
    except Exception as e:
        await update.message.reply_text(get_text(context, 'update_error', error=str(e)))

    return ConversationHandler.END


# ===== CREATE RECORD =====
async def create_get_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get day number"""
    try:
        day = update.message.text.strip()
        current_position.data['day'] = day
        current_position.data['id'] = int(day) if day.isdigit() else len(day.split('-')[0])
        await update.message.reply_text(get_text(context, 'create_date', day=day))
        return CREATE_DATE
    except ValueError:
        await update.message.reply_text(get_text(context, 'invalid_day'))
        return CREATE_DAY


async def create_get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get date"""
    date_text = update.message.text.strip()
    try:
        # Validate date format
        datetime.strptime(date_text, '%Y-%m-%d')
        current_position.data['date'] = date_text
        await update.message.reply_text(get_text(context, 'create_location', date=date_text))
        return CREATE_LOCATION
    except ValueError:
        await update.message.reply_text(get_text(context, 'invalid_date'))
        return CREATE_DATE


async def create_get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get location name"""
    location = update.message.text.strip()
    current_position.data['location'] = location
    await update.message.reply_text(get_text(context, 'create_distance', location=location))
    return CREATE_DISTANCE


async def create_get_distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get distance"""
    try:
        distance = float(update.message.text)
        current_position.data['distance_km'] = distance
        await update.message.reply_text(get_text(context, 'create_elevation', distance=distance))
        return CREATE_ELEVATION
    except ValueError:
        await update.message.reply_text(get_text(context, 'invalid_distance'))
        return CREATE_DISTANCE


async def create_get_elevation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get elevation gain"""
    try:
        elevation = int(update.message.text)
        current_position.data['elevation_gain'] = elevation
        await update.message.reply_text(get_text(context, 'create_accommodation', elevation=elevation))
        return CREATE_ACCOMMODATION
    except ValueError:
        await update.message.reply_text(get_text(context, 'invalid_elevation'))
        return CREATE_ELEVATION


async def create_get_accommodation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get accommodation type"""
    accom = update.message.text.strip().lower()
    valid_types = ['tent', 'glamping', 'guesthouse', 'hotel']

    if accom not in valid_types:
        await update.message.reply_text(get_text(context, 'invalid_accommodation', types=', '.join(valid_types)))
        return CREATE_ACCOMMODATION

    current_position.data['accommodation_type'] = accom
    await update.message.reply_text(get_text(context, 'create_coordinates', accom=accom))
    return CREATE_LATITUDE


async def create_get_latitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get latitude or location"""
    # Check if it's a location message
    if update.message.location:
        location = update.message.location

        # Validate coordinates
        is_valid, msg = validate_coordinates(location.latitude, location.longitude)
        if not is_valid:
            await update.message.reply_text(
                get_text(context, 'coord_warning',
                        exp_lat=EXPECTED_LAT, exp_lon=EXPECTED_LON,
                        lat=location.latitude, lon=location.longitude)
            )
            return CREATE_LATITUDE

        current_position.data['latitude'] = location.latitude
        current_position.data['longitude'] = location.longitude
        await update.message.reply_text(
            get_text(context, 'create_youtube',
                    lon=location.longitude, lat=location.latitude)
        )
        return CREATE_YOUTUBE

    # Otherwise treat as latitude text
    try:
        latitude = float(update.message.text)
        current_position.data['latitude'] = latitude
        await update.message.reply_text(
            get_text(context, 'create_longitude_prompt', latitude=latitude)
        )
        return CREATE_LONGITUDE
    except ValueError:
        await update.message.reply_text(get_text(context, 'invalid_latitude'))
        return CREATE_LATITUDE


async def create_get_longitude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get longitude"""
    try:
        longitude = float(update.message.text)

        # Validate coordinates
        latitude = current_position.data['latitude']
        is_valid, msg = validate_coordinates(latitude, longitude)
        if not is_valid:
            await update.message.reply_text(
                get_text(context, 'coord_warning',
                        exp_lat=EXPECTED_LAT, exp_lon=EXPECTED_LON,
                        lat=latitude, lon=longitude)
            )
            return CREATE_LATITUDE

        current_position.data['longitude'] = longitude
        await update.message.reply_text(
            get_text(context, 'create_youtube', lon=longitude, lat=latitude)
        )
        return CREATE_YOUTUBE
    except ValueError:
        await update.message.reply_text(get_text(context, 'invalid_longitude'))
        return CREATE_LONGITUDE


async def create_get_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get YouTube URL"""
    youtube_text = update.message.text.strip()

    if youtube_text.lower() == 'skip':
        current_position.data['youtube_url'] = ""
    else:
        # Convert Shorts URL to standard watch URL
        converted_url = convert_youtube_url(youtube_text)
        current_position.data['youtube_url'] = converted_url

    await update.message.reply_text(get_text(context, 'create_notes'))
    return CREATE_NOTES


async def create_get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get notes"""
    notes_text = update.message.text.strip()

    if notes_text.lower() == 'skip':
        current_position.data['notes'] = ""
    else:
        current_position.data['notes'] = notes_text

    # Initialize photo tracking
    current_position.uploaded_photos = []
    current_position.photo_count = 0

    await update.message.reply_text(get_text(context, 'create_photos', day=current_position.data['day']))
    return CREATE_PHOTOS


async def create_get_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads or finish creation"""

    # Check if user sent a photo
    if update.message.photo:
        try:
            # Get the highest quality photo
            photo = update.message.photo[-1]

            # Download photo
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()

            # Generate filename with zero-padded counter
            current_position.photo_count += 1
            filename = f"day_{current_position.data['day']}_{current_position.photo_count:02d}.jpg"

            # Upload to GitHub
            commit_msg = f"Bot: Add photo {filename} for Day {current_position.data['day']}"
            await upload_photo_to_github(bytes(photo_bytes), filename, commit_msg)

            # Track the filename
            current_position.uploaded_photos.append(filename)

            await update.message.reply_text(
                get_text(context, 'photo_uploaded',
                        filename=filename,
                        count=len(current_position.uploaded_photos))
            )

            return CREATE_PHOTOS  # Stay in this state for more photos

        except Exception as e:
            logger.error(f"Error uploading photo: {e}")
            await update.message.reply_text(
                get_text(context, 'photo_upload_error', error=str(e))
            )
            return CREATE_PHOTOS

    # Handle text commands
    if update.message.text:
        text = update.message.text.strip().lower()

        if text == 'skip':
            current_position.data['photos'] = []
        elif text == 'done':
            current_position.data['photos'] = current_position.uploaded_photos
        else:
            await update.message.reply_text(
                get_text(context, 'photo_invalid_command')
            )
            return CREATE_PHOTOS

    # Finalize - set photos list
    current_position.data['photos'] = current_position.uploaded_photos

    # Show summary
    await update.message.reply_text(
        get_text(context, 'create_summary',
                day=current_position.data['day'],
                date=current_position.data['date'],
                location=current_position.data['location'],
                distance_km=current_position.data['distance_km'],
                elevation_gain=current_position.data['elevation_gain'],
                accommodation_type=current_position.data['accommodation_type'],
                longitude=current_position.data['longitude'],
                latitude=current_position.data['latitude'],
                youtube_url=current_position.data.get('youtube_url', 'None'),
                notes=current_position.data.get('notes', 'None'),
                photos_count=len(current_position.data['photos']))
    )

    # Now update GitHub
    try:
        # Fetch current file
        geojson_data, sha = fetch_geojson_from_github()

        # Create new feature
        new_feature = {
            "type": "Feature",
            "properties": {
                "id": current_position.data['id'],
                "day": current_position.data['day'],
                "date": current_position.data['date'],
                "location": current_position.data['location'],
                "distance_km": current_position.data['distance_km'],
                "elevation_gain": current_position.data['elevation_gain'],
                "accommodation_type": current_position.data['accommodation_type'],
                "youtube_url": current_position.data.get('youtube_url', ''),
                "notes": current_position.data.get('notes', ''),
                "photos": current_position.data.get('photos', [])
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    current_position.data['longitude'],
                    current_position.data['latitude']
                ]
            }
        }

        # Add to features
        geojson_data['features'].append(new_feature)

        # Update on GitHub with descriptive commit message
        commit_msg = f"Bot: Add Day {current_position.data['day']} - {current_position.data['location']}"
        update_geojson_on_github(geojson_data, sha, commit_msg)

        await update.message.reply_text(get_text(context, 'create_success'))

    except Exception as e:
        logger.error(f"Error updating GitHub: {e}")
        await update.message.reply_text(get_text(context, 'create_error', error=str(e)))

    return ConversationHandler.END


# ===== UPDATE RECORD =====
async def update_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get ID of record to update"""
    try:
        record_id = int(update.message.text)

        # Fetch from GitHub to verify ID exists
        geojson_data, sha = fetch_geojson_from_github()

        # Find the record
        record = None
        record_index = None
        for idx, feature in enumerate(geojson_data['features']):
            if feature['properties']['id'] == record_id:
                record = feature
                record_index = idx
                break

        if not record:
            await update.message.reply_text(
                get_text(context, 'update_not_found', id=record_id)
            )
            return ConversationHandler.END

        # Store for update
        current_position.update_id = record_id
        current_position.data = record

        # Show current values
        props = record['properties']
        coords = record['geometry']['coordinates']

        await update.message.reply_text(
            get_text(context, 'update_fields',
                    day=props['day'],
                    date=props['date'],
                    location=props['location'],
                    distance_km=props['distance_km'],
                    elevation_gain=props['elevation_gain'],
                    accommodation_type=props['accommodation_type'],
                    lon=coords[0],
                    lat=coords[1],
                    youtube_url=props.get('youtube_url', 'None'),
                    notes=props.get('notes', 'None'),
                    photos=', '.join(props.get('photos', [])) if props.get('photos') else 'None')
        )
        return UPDATE_FIELD

    except ValueError:
        await update.message.reply_text(get_text(context, 'update_invalid_id'))
        return UPDATE_ID
    except Exception as e:
        await update.message.reply_text(get_text(context, 'update_error', error=str(e)))
        return ConversationHandler.END


async def update_get_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get which field to update"""
    field_num = update.message.text.strip()

    field_map = {
        '1': 'day',
        '2': 'date',
        '3': 'location',
        '4': 'distance_km',
        '5': 'elevation_gain',
        '6': 'accommodation_type',
        '7': 'coordinates',
        '8': 'youtube_url',
        '9': 'notes',
        '10': 'photos'
    }

    if field_num not in field_map:
        await update.message.reply_text(get_text(context, 'update_invalid_field'))
        return UPDATE_FIELD

    current_position.data['update_field'] = field_map[field_num]

    # Special handling for photos - initialize upload tracking
    if field_map[field_num] == 'photos':
        current_position.uploaded_photos = []
        current_position.photo_count = 0

        await update.message.reply_text(
            get_text(context, 'update_photos_prompt',
                    day=current_position.data['properties']['day'])
        )
        return UPDATE_PHOTOS

    await update.message.reply_text(
        get_text(context, 'update_field_prompt', field=field_map[field_num])
    )
    return UPDATE_VALUE


async def update_get_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get new value and update the record"""
    field = current_position.data['update_field']
    new_value = update.message.text.strip()

    try:
        # Fetch current data from GitHub
        geojson_data, sha = fetch_geojson_from_github()

        # Find the record
        record_index = None
        for idx, feature in enumerate(geojson_data['features']):
            if feature['properties']['id'] == current_position.update_id:
                record_index = idx
                break

        if record_index is None:
            await update.message.reply_text(get_text(context, 'update_error', error="Record not found anymore"))
            return ConversationHandler.END

        # Update the field
        if field == 'day':
            geojson_data['features'][record_index]['properties']['day'] = new_value
        elif field == 'date':
            datetime.strptime(new_value, '%Y-%m-%d')  # Validate
            geojson_data['features'][record_index]['properties']['date'] = new_value
        elif field == 'location':
            geojson_data['features'][record_index]['properties']['location'] = new_value
        elif field == 'distance_km':
            geojson_data['features'][record_index]['properties']['distance_km'] = float(new_value)
        elif field == 'elevation_gain':
            geojson_data['features'][record_index]['properties']['elevation_gain'] = int(new_value)
        elif field == 'accommodation_type':
            if new_value.lower() not in ['tent', 'glamping', 'guesthouse', 'hotel']:
                await update.message.reply_text(get_text(context, 'update_invalid_accom'))
                return UPDATE_VALUE
            geojson_data['features'][record_index]['properties']['accommodation_type'] = new_value.lower()
        elif field == 'coordinates':
            # Expected format: "lon, lat" or "[lon, lat]"
            coords_str = new_value.strip('[]')
            coords = [float(x.strip()) for x in coords_str.split(',')]
            if len(coords) != 2:
                await update.message.reply_text(get_text(context, 'update_invalid_coords'))
                return UPDATE_VALUE
            # Validate
            is_valid, msg = validate_coordinates(coords[1], coords[0])
            if not is_valid:
                await update.message.reply_text(
                    get_text(context, 'coord_warning',
                            exp_lat=EXPECTED_LAT, exp_lon=EXPECTED_LON,
                            lat=coords[1], lon=coords[0])
                )
                return UPDATE_VALUE
            geojson_data['features'][record_index]['geometry']['coordinates'] = coords
        elif field == 'youtube_url':
            # Convert Shorts URL to standard watch URL
            converted_url = convert_youtube_url(new_value)
            geojson_data['features'][record_index]['properties']['youtube_url'] = converted_url
            # Update the new_value for the success message
            if converted_url != new_value:
                new_value = f"{new_value} → {converted_url}"
        elif field == 'notes':
            geojson_data['features'][record_index]['properties']['notes'] = new_value
        elif field == 'photos':
            photos = [p.strip() for p in new_value.split(',') if p.strip()] if new_value.lower() != 'skip' else []
            geojson_data['features'][record_index]['properties']['photos'] = photos

        # Update on GitHub
        update_geojson_on_github(geojson_data, sha)

        await update.message.reply_text(
            get_text(context, 'update_success', field=field, value=new_value)
        )

    except ValueError as e:
        await update.message.reply_text(get_text(context, 'update_invalid_value', error=str(e)))
        return UPDATE_VALUE
    except Exception as e:
        logger.error(f"Error updating GitHub: {e}")
        await update.message.reply_text(get_text(context, 'update_error', error=str(e)))

    return ConversationHandler.END


async def update_get_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads for update"""

    # Handle photo upload
    if update.message.photo:
        try:
            # Get the highest quality photo
            photo = update.message.photo[-1]

            # Download photo
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()

            # Generate filename with zero-padded counter
            current_position.photo_count += 1
            day = current_position.data['properties']['day']
            filename = f"day_{day}_{current_position.photo_count:02d}.jpg"

            # Upload to GitHub
            commit_msg = f"Bot: Add photo {filename} for Day {day}"
            await upload_photo_to_github(bytes(photo_bytes), filename, commit_msg)

            # Track the filename
            current_position.uploaded_photos.append(filename)

            await update.message.reply_text(
                get_text(context, 'photo_uploaded',
                        filename=filename,
                        count=len(current_position.uploaded_photos))
            )

            return UPDATE_PHOTOS

        except Exception as e:
            logger.error(f"Error uploading photo: {e}")
            await update.message.reply_text(
                get_text(context, 'photo_upload_error', error=str(e))
            )
            return UPDATE_PHOTOS

    # Handle text commands
    if update.message.text:
        text = update.message.text.strip().lower()

        if text == 'skip':
            # Keep existing photos unchanged
            await update.message.reply_text(get_text(context, 'update_cancelled'))
            return ConversationHandler.END
        elif text == 'done':
            # Update with new photos list
            try:
                # Fetch current data from GitHub
                geojson_data, sha = fetch_geojson_from_github()

                # Find the record
                record_index = None
                for idx, feature in enumerate(geojson_data['features']):
                    if feature['properties']['id'] == current_position.update_id:
                        record_index = idx
                        break

                if record_index is None:
                    await update.message.reply_text(get_text(context, 'update_error', error="Record not found anymore"))
                    return ConversationHandler.END

                # Update photos
                geojson_data['features'][record_index]['properties']['photos'] = current_position.uploaded_photos

                # Update on GitHub
                commit_msg = f"Bot: Update photos for Day {current_position.data['properties']['day']}"
                update_geojson_on_github(geojson_data, sha, commit_msg)

                await update.message.reply_text(
                    get_text(context, 'update_success',
                            field='photos',
                            value=', '.join(current_position.uploaded_photos) if current_position.uploaded_photos else 'None')
                )

            except Exception as e:
                logger.error(f"Error updating GitHub: {e}")
                await update.message.reply_text(get_text(context, 'update_error', error=str(e)))

            return ConversationHandler.END
        else:
            await update.message.reply_text(
                get_text(context, 'photo_invalid_command')
            )
            return UPDATE_PHOTOS

    return UPDATE_PHOTOS


# ===== DELETE RECORD =====
async def delete_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get record ID to delete and show it for confirmation"""
    try:
        record_id = int(update.message.text)

        # Fetch from GitHub
        geojson_data, sha = fetch_geojson_from_github()

        # Find the record
        record = None
        for feature in geojson_data['features']:
            if feature['properties']['id'] == record_id:
                record = feature
                break

        if not record:
            await update.message.reply_text(
                get_text(context, 'update_not_found', id=record_id)
            )
            return ConversationHandler.END

        # Store the ID for deletion
        current_position.update_id = record_id

        # Format and send for confirmation
        props = record['properties']
        coords = record['geometry']['coordinates']

        await update.message.reply_text(
            get_text(context, 'delete_confirm',
                    id=props['id'],
                    day=props['day'],
                    date=props['date'],
                    location=props['location'],
                    distance_km=props['distance_km'],
                    elevation_gain=props['elevation_gain'],
                    accommodation_type=props['accommodation_type'],
                    lon=coords[0],
                    lat=coords[1])
        )
        return DELETE_CONFIRM

    except ValueError:
        await update.message.reply_text(get_text(context, 'update_invalid_id'))
        return DELETE_ID
    except Exception as e:
        logger.error(f"Error fetching record for deletion: {e}")
        await update.message.reply_text(get_text(context, 'update_error', error=str(e)))
        return ConversationHandler.END


async def delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and execute deletion"""
    confirmation = update.message.text.strip().upper()

    if confirmation != 'YES':
        await update.message.reply_text(get_text(context, 'delete_cancelled'))
        return ConversationHandler.END

    try:
        # Fetch current data from GitHub
        geojson_data, sha = fetch_geojson_from_github()

        # Find and remove the record
        record_deleted = None
        for idx, feature in enumerate(geojson_data['features']):
            if feature['properties']['id'] == current_position.update_id:
                record_deleted = geojson_data['features'].pop(idx)
                break

        if not record_deleted:
            await update.message.reply_text(
                get_text(context, 'update_error', error="Record not found anymore. It may have been already deleted.")
            )
            return ConversationHandler.END

        # Update on GitHub
        update_geojson_on_github(geojson_data, sha)

        await update.message.reply_text(
            get_text(context, 'delete_success',
                    id=current_position.update_id,
                    day=record_deleted['properties']['day'],
                    location=record_deleted['properties']['location'])
        )

    except Exception as e:
        logger.error(f"Error deleting record from GitHub: {e}")
        await update.message.reply_text(get_text(context, 'update_error', error=str(e)))

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    current_position.reset()
    await update.message.reply_text(get_text(context, 'cancelled'))
    return ConversationHandler.END


async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    current_position.reset()
    await update.message.reply_text(get_text(context, 'back_to_menu'))
    return MENU


def main():
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
        return

    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN environment variable not set!")
        return

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add language switch commands (available anytime)
    application.add_handler(CommandHandler('en', set_language_en))
    application.add_handler(CommandHandler('ru', set_language_ru))

    # Setup conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_password)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_choice)],

            # Get record
            GET_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_record_by_id)],

            # Create record
            CREATE_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_day)],
            CREATE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_date)],
            CREATE_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_location)],
            CREATE_DISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_distance)],
            CREATE_ELEVATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_elevation)],
            CREATE_ACCOMMODATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_accommodation)],
            CREATE_LATITUDE: [
                MessageHandler(filters.LOCATION, create_get_latitude),
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_latitude)
            ],
            CREATE_LONGITUDE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_longitude)],
            CREATE_YOUTUBE: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_youtube)],
            CREATE_NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_notes)],
            CREATE_PHOTOS: [
                MessageHandler(filters.PHOTO, create_get_photos),
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_photos)
            ],

            # Update record
            UPDATE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_id)],
            UPDATE_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_field)],
            UPDATE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_value)],
            UPDATE_PHOTOS: [
                MessageHandler(filters.PHOTO, update_get_photos),
                MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_photos)
            ],

            # Delete record
            DELETE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_get_id)],
            DELETE_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_confirm)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('menu', back_to_menu),
        ]
    )

    application.add_handler(conv_handler)

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
