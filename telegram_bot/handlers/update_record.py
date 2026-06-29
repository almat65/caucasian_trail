"""
Update record handlers for the Caucasian Trail Telegram Bot
"""

import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import (UPDATE_ID, UPDATE_FIELD, UPDATE_VALUE, UPDATE_PHOTOS,
                   EXPECTED_LAT, EXPECTED_LON)
from models import current_position
from utils import (get_text, validate_coordinates, convert_youtube_url,
                  fetch_geojson_from_github, update_geojson_on_github,
                  upload_photo_to_github)

logger = logging.getLogger(__name__)


async def update_get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get ID of record to update"""
    try:
        record_id = int(update.message.text)

        # Fetch from GitHub to verify ID exists
        geojson_data, sha = fetch_geojson_from_github()

        # Find the record
        record = None
        for idx, feature in enumerate(geojson_data['features']):
            if feature['properties']['id'] == record_id:
                record = feature
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
