"""
Create record handlers for the Caucasian Trail Telegram Bot
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import (CREATE_DAY, CREATE_DATE, CREATE_LOCATION, CREATE_DISTANCE,
                   CREATE_ELEVATION, CREATE_ACCOMMODATION, CREATE_LATITUDE,
                   CREATE_LONGITUDE, CREATE_YOUTUBE, CREATE_NOTES, CREATE_PHOTOS,
                   EXPECTED_LAT, EXPECTED_LON)
from models import current_position
from utils import (get_text, validate_coordinates, convert_youtube_url,
                  fetch_geojson_from_github, update_geojson_on_github,
                  upload_photo_to_github)

logger = logging.getLogger(__name__)


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
