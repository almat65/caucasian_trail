"""
Delete record handlers for the Caucasian Trail Telegram Bot
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import DELETE_ID, DELETE_CONFIRM
from models import current_position
from utils import get_text, fetch_geojson_from_github, update_geojson_on_github

logger = logging.getLogger(__name__)


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
