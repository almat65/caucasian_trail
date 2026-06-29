"""
Handler modules for the Caucasian Trail Telegram Bot
"""

from .auth import start, set_language_en, set_language_ru, check_password
from .menu import menu_choice, cancel, back_to_menu
from .get_record import get_record_by_id
from .create_record import (create_get_day, create_get_date, create_get_location,
                           create_get_distance, create_get_elevation, create_get_accommodation,
                           create_get_latitude, create_get_longitude, create_get_youtube,
                           create_get_notes, create_get_photos)
from .update_record import update_get_id, update_get_field, update_get_value, update_get_photos
from .delete_record import delete_get_id, delete_confirm

__all__ = [
    # Auth
    'start', 'set_language_en', 'set_language_ru', 'check_password',
    # Menu
    'menu_choice', 'cancel', 'back_to_menu',
    # Get
    'get_record_by_id',
    # Create
    'create_get_day', 'create_get_date', 'create_get_location',
    'create_get_distance', 'create_get_elevation', 'create_get_accommodation',
    'create_get_latitude', 'create_get_longitude', 'create_get_youtube',
    'create_get_notes', 'create_get_photos',
    # Update
    'update_get_id', 'update_get_field', 'update_get_value', 'update_get_photos',
    # Delete
    'delete_get_id', 'delete_confirm',
]
