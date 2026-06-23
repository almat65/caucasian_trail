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
PASSWORD, MENU, GET_ID, CREATE_DAY, CREATE_DATE, CREATE_LOCATION, CREATE_DISTANCE, CREATE_ELEVATION, CREATE_ACCOMMODATION, CREATE_LATITUDE, CREATE_LONGITUDE, CREATE_YOUTUBE, CREATE_NOTES, CREATE_PHOTOS, UPDATE_ID, UPDATE_FIELD, UPDATE_VALUE = range(17)


class PositionData:
    """Store position data during conversation"""
    def __init__(self):
        self.data = {}
        self.update_id = None

    def reset(self):
        self.data = {}
        self.update_id = None


# Global storage for current position being added
current_position = PositionData()


def validate_coordinates(lat, lon):
    """Check if coordinates are in the expected region (Dagestan)"""
    lat_diff = abs(lat - EXPECTED_LAT)
    lon_diff = abs(lon - EXPECTED_LON)

    if lat_diff > MAX_COORDINATE_DISTANCE or lon_diff > MAX_COORDINATE_DISTANCE:
        return False, f"⚠️ Warning: Coordinates seem far from Dagestan region.\nExpected around: {EXPECTED_LAT}, {EXPECTED_LON}\nGot: {lat}, {lon}"
    return True, "OK"


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


def update_geojson_on_github(geojson_data, sha):
    """Update geojson file on GitHub"""
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
    data = {
        'message': f'Add Day {current_position.data.get("day", "?")} position via bot',
        'content': encoded_content,
        'sha': sha,
        'branch': 'master'
    }

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start conversation and ask for password"""
    current_position.reset()
    await update.message.reply_text(
        "🏔️ Welcome to Caucasian Trail Position Manager!\n\n"
        "🔒 Please enter the password:"
    )
    return PASSWORD


async def check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify password and show menu"""
    password = update.message.text.strip()

    if password == BOT_PASSWORD:
        await update.message.reply_text(
            "✅ Access granted!\n\n"
            "Choose an option:\n"
            "1️⃣ Create a new record\n"
            "2️⃣ Update existing record\n"
            "3️⃣ Get record by ID\n\n"
            "Send the number (1, 2, or 3)"
        )
        return MENU
    else:
        await update.message.reply_text(
            "❌ Wrong password. Access denied.\n\n"
            "Use /start to try again."
        )
        return ConversationHandler.END


async def menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu choice"""
    choice = update.message.text.strip()

    if choice == '1':
        await update.message.reply_text(
            "📝 Creating new record\n\n"
            "What day is this? (e.g., 15, 16, 17...)"
        )
        return CREATE_DAY
    elif choice == '2':
        await update.message.reply_text(
            "🔄 Update existing record\n\n"
            "What's the record ID to update?"
        )
        return UPDATE_ID
    elif choice == '3':
        await update.message.reply_text(
            "🔍 Get record\n\n"
            "What's the record ID?"
        )
        return GET_ID
    else:
        await update.message.reply_text(
            "Please send 1, 2, or 3"
        )
        return MENU


# ===== GET RECORD =====
async def get_record_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display a record by ID"""
    try:
        record_id = int(update.message.text)

        # Fetch from GitHub
        geojson_data, _ = fetch_geojson_from_github()

        # Find the record
        record = None
        for feature in geojson_data['features']:
            if feature['properties']['id'] == record_id:
                record = feature
                break

        if not record:
            await update.message.reply_text(
                f"❌ No record found with ID {record_id}\n\n"
                "Use /start to try again."
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
        await update.message.reply_text("Please enter a valid number for the ID.")
        return GET_ID
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\n\nUse /start to try again.")

    return ConversationHandler.END


# ===== CREATE RECORD =====
async def create_get_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get day number"""
    try:
        day = update.message.text.strip()
        current_position.data['day'] = day
        current_position.data['id'] = int(day) if day.isdigit() else len(day.split('-')[0])
        await update.message.reply_text(
            f"✅ Day {day}\n\n"
            "What's the date? (Format: YYYY-MM-DD, e.g., 2026-06-23)"
        )
        return CREATE_DATE
    except ValueError:
        await update.message.reply_text("Please enter a valid day.")
        return CREATE_DAY


async def create_get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get date"""
    date_text = update.message.text.strip()
    try:
        # Validate date format
        datetime.strptime(date_text, '%Y-%m-%d')
        current_position.data['date'] = date_text
        await update.message.reply_text(
            f"✅ Date: {date_text}\n\n"
            "What's the location name? (e.g., Хапцай, Гапшима)"
        )
        return CREATE_LOCATION
    except ValueError:
        await update.message.reply_text("Invalid date format. Please use YYYY-MM-DD (e.g., 2026-06-23)")
        return CREATE_DATE


async def create_get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get location name"""
    location = update.message.text.strip()
    current_position.data['location'] = location
    await update.message.reply_text(
        f"✅ Location: {location}\n\n"
        "Distance covered today in km? (e.g., 15.5)\n"
        "Send 0 if none."
    )
    return CREATE_DISTANCE


async def create_get_distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get distance"""
    try:
        distance = float(update.message.text)
        current_position.data['distance_km'] = distance
        await update.message.reply_text(
            f"✅ Distance: {distance} km\n\n"
            "Elevation gain today in meters? (e.g., 850)\n"
            "Send 0 if none."
        )
        return CREATE_ELEVATION
    except ValueError:
        await update.message.reply_text("Please enter a valid number for distance.")
        return CREATE_DISTANCE


async def create_get_elevation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get elevation gain"""
    try:
        elevation = int(update.message.text)
        current_position.data['elevation_gain'] = elevation
        await update.message.reply_text(
            f"✅ Elevation gain: {elevation} m\n\n"
            "Accommodation type?\n"
            "Options: tent, glamping, guesthouse, hotel"
        )
        return CREATE_ACCOMMODATION
    except ValueError:
        await update.message.reply_text("Please enter a valid number for elevation gain.")
        return CREATE_ELEVATION


async def create_get_accommodation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get accommodation type"""
    accom = update.message.text.strip().lower()
    valid_types = ['tent', 'glamping', 'guesthouse', 'hotel']

    if accom not in valid_types:
        await update.message.reply_text(
            f"Please choose one of: {', '.join(valid_types)}"
        )
        return CREATE_ACCOMMODATION

    current_position.data['accommodation_type'] = accom
    await update.message.reply_text(
        f"✅ Accommodation: {accom}\n\n"
        "Send your location using Telegram's location feature 📍\n"
        "Or send latitude (I'll ask for longitude next)"
    )
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
                f"{msg}\n\n"
                "Are you sure these coordinates are correct? Send /start to restart or send new location."
            )
            return CREATE_LATITUDE

        current_position.data['latitude'] = location.latitude
        current_position.data['longitude'] = location.longitude
        await update.message.reply_text(
            f"✅ Coordinates: [{location.longitude}, {location.latitude}] (lon, lat)\n\n"
            "YouTube URL? (e.g., https://youtube.com/watch?v=...)\n"
            "Send 'skip' if none."
        )
        return CREATE_YOUTUBE

    # Otherwise treat as latitude text
    try:
        latitude = float(update.message.text)
        current_position.data['latitude'] = latitude
        await update.message.reply_text(
            f"✅ Latitude: {latitude}\n\n"
            "Now send the longitude:"
        )
        return CREATE_LONGITUDE
    except ValueError:
        await update.message.reply_text("Please send a valid latitude number or use Telegram's location feature.")
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
                f"{msg}\n\n"
                "Please re-enter latitude (send /start to restart):"
            )
            return CREATE_LATITUDE

        current_position.data['longitude'] = longitude
        await update.message.reply_text(
            f"✅ Longitude: {longitude}\n"
            f"✅ Coordinates: [{longitude}, {latitude}] (lon, lat)\n\n"
            "YouTube URL? (e.g., https://youtube.com/watch?v=...)\n"
            "Send 'skip' if none."
        )
        return CREATE_YOUTUBE
    except ValueError:
        await update.message.reply_text("Please send a valid longitude number.")
        return CREATE_LONGITUDE


async def create_get_youtube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get YouTube URL"""
    youtube_text = update.message.text.strip()

    if youtube_text.lower() == 'skip':
        current_position.data['youtube_url'] = ""
    else:
        current_position.data['youtube_url'] = youtube_text

    await update.message.reply_text(
        "Any notes about this day?\n"
        "Send 'skip' if none."
    )
    return CREATE_NOTES


async def create_get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get notes"""
    notes_text = update.message.text.strip()

    if notes_text.lower() == 'skip':
        current_position.data['notes'] = ""
    else:
        current_position.data['notes'] = notes_text

    await update.message.reply_text(
        "Photo filenames? (comma separated, e.g., day15_1.jpg, day15_2.jpg)\n"
        "Send 'skip' if none."
    )
    return CREATE_PHOTOS


async def create_get_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get photos and finalize creation"""
    photos_text = update.message.text.strip()

    if photos_text.lower() == 'skip':
        current_position.data['photos'] = []
    else:
        # Split by comma and clean
        photos = [p.strip() for p in photos_text.split(',') if p.strip()]
        current_position.data['photos'] = photos

    # Show summary
    summary = f"""
📋 Summary:
Day: {current_position.data['day']}
Date: {current_position.data['date']}
Location: {current_position.data['location']}
Distance: {current_position.data['distance_km']} km
Elevation: {current_position.data['elevation_gain']} m
Accommodation: {current_position.data['accommodation_type']}
Coordinates: [{current_position.data['longitude']}, {current_position.data['latitude']}] (lon, lat)
YouTube: {current_position.data.get('youtube_url', 'None')}
Notes: {current_position.data.get('notes', 'None')}
Photos: {len(current_position.data['photos'])}

Creating record on GitHub...
    """

    await update.message.reply_text(summary)

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

        # Update on GitHub
        update_geojson_on_github(geojson_data, sha)

        await update.message.reply_text(
            "✅ Record created successfully on GitHub!\n\n"
            "The map will update automatically.\n\n"
            "Use /start for more options."
        )

    except Exception as e:
        logger.error(f"Error updating GitHub: {e}")
        await update.message.reply_text(
            f"❌ Error updating GitHub: {str(e)}\n\n"
            "Please check the logs and try again with /start"
        )

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
                f"❌ No record found with ID {record_id}\n\n"
                "Use /start to try again."
            )
            return ConversationHandler.END

        # Store for update
        current_position.update_id = record_id
        current_position.data = record

        # Show current values
        props = record['properties']
        coords = record['geometry']['coordinates']

        fields_text = """
Current values:
1. day: {day}
2. date: {date}
3. location: {location}
4. distance_km: {distance_km}
5. elevation_gain: {elevation_gain}
6. accommodation_type: {accommodation_type}
7. coordinates: [{lon}, {lat}]
8. youtube_url: {youtube_url}
9. notes: {notes}
10. photos: {photos}

Which field do you want to update? (send number 1-10)
        """.format(
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
            photos=', '.join(props.get('photos', [])) if props.get('photos') else 'None'
        )

        await update.message.reply_text(fields_text)
        return UPDATE_FIELD

    except ValueError:
        await update.message.reply_text("Please enter a valid number for the ID.")
        return UPDATE_ID
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\n\nUse /start to try again.")
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
        await update.message.reply_text("Please send a number between 1 and 10.")
        return UPDATE_FIELD

    current_position.data['update_field'] = field_map[field_num]

    await update.message.reply_text(
        f"Updating '{field_map[field_num]}'\n\n"
        f"Send the new value:"
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
            await update.message.reply_text("❌ Record not found anymore. Use /start to try again.")
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
                await update.message.reply_text("Invalid accommodation type. Use: tent, glamping, guesthouse, hotel")
                return UPDATE_VALUE
            geojson_data['features'][record_index]['properties']['accommodation_type'] = new_value.lower()
        elif field == 'coordinates':
            # Expected format: "lon, lat" or "[lon, lat]"
            coords_str = new_value.strip('[]')
            coords = [float(x.strip()) for x in coords_str.split(',')]
            if len(coords) != 2:
                await update.message.reply_text("Please send coordinates as: lon, lat (e.g., 46.701786, 42.409953)")
                return UPDATE_VALUE
            # Validate
            is_valid, msg = validate_coordinates(coords[1], coords[0])
            if not is_valid:
                await update.message.reply_text(f"{msg}\n\nTry again or /start to cancel.")
                return UPDATE_VALUE
            geojson_data['features'][record_index]['geometry']['coordinates'] = coords
        elif field == 'youtube_url':
            geojson_data['features'][record_index]['properties']['youtube_url'] = new_value
        elif field == 'notes':
            geojson_data['features'][record_index]['properties']['notes'] = new_value
        elif field == 'photos':
            photos = [p.strip() for p in new_value.split(',') if p.strip()] if new_value.lower() != 'skip' else []
            geojson_data['features'][record_index]['properties']['photos'] = photos

        # Update on GitHub
        update_geojson_on_github(geojson_data, sha)

        await update.message.reply_text(
            f"✅ Updated '{field}' successfully!\n\n"
            f"New value: {new_value}\n\n"
            "Use /start for more options."
        )

    except ValueError as e:
        await update.message.reply_text(f"Invalid value format: {str(e)}\n\nTry again or /start to cancel.")
        return UPDATE_VALUE
    except Exception as e:
        logger.error(f"Error updating GitHub: {e}")
        await update.message.reply_text(
            f"❌ Error updating GitHub: {str(e)}\n\n"
            "Use /start to try again."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    current_position.reset()
    await update.message.reply_text(
        "❌ Cancelled. Use /start to begin again."
    )
    return ConversationHandler.END


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
            CREATE_PHOTOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_get_photos)],

            # Update record
            UPDATE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_id)],
            UPDATE_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_field)],
            UPDATE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_get_value)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start bot
    logger.info("Bot started! Send /start to begin.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
