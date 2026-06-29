"""
Get record handlers for the Caucasian Trail Telegram Bot
"""

import json
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import GET_ID
from utils import get_text, fetch_geojson_from_github


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
