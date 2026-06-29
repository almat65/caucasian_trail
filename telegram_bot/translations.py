
# Translations dictionary
TRANSLATIONS = {
    'en': {
        'welcome': "🏔️ Welcome to Caucasian Trail Position Manager!\n\n🔒 Please enter the password:",
        'access_granted': "✅ Access granted!\n\nChoose an option:\n1️⃣ Create a new record\n2️⃣ Update existing record\n3️⃣ Get record by ID\n4️⃣ Delete record by ID\n\nSend the number (1, 2, 3, or 4)\n\n💡 Tip: Use /menu anytime to return here, /cancel to exit, /ru for Russian, /en for English",
        'wrong_password': "❌ Wrong password. Access denied.\n\nUse /start to try again.",
        'menu_invalid': "Please send 1, 2, 3, or 4",

        # Create record
        'create_start': "📝 Creating new record\n\nWhat day is this? (e.g., 15, 16, 17...)",
        'create_date': "✅ Day {day}\n\nWhat's the date? (Format: YYYY-MM-DD, e.g., 2026-06-23)",
        'create_location': "✅ Date: {date}\n\nWhat's the location name? (e.g., Хапцай, Гапшима)",
        'create_distance': "✅ Location: {location}\n\nDistance covered today in km? (e.g., 15.5)\nSend 0 if none.",
        'create_elevation': "✅ Distance: {distance} km\n\nElevation gain today in meters? (e.g., 850)\nSend 0 if none.",
        'create_accommodation': "✅ Elevation gain: {elevation} m\n\nAccommodation type?\nOptions: tent, glamping, guesthouse, hotel",
        'create_coordinates': "✅ Accommodation: {accom}\n\nSend your location using Telegram's location feature 📍\nOr send latitude (I'll ask for longitude next)",
        'create_longitude_prompt': "✅ Latitude: {latitude}\n\nNow send the longitude:",
        'create_youtube': "✅ Coordinates: [{lon}, {lat}] (lon, lat)\n\nYouTube URL? (e.g., https://youtube.com/watch?v=...)\nSend 'skip' if none.",
        'create_notes': "Any notes about this day?\nSend 'skip' if none.",
        'create_photos': "Photo filenames? (comma separated, e.g., day15_1.jpg, day15_2.jpg)\nSend 'skip' if none.",
        'create_summary': "📋 Summary:\nDay: {day}\nDate: {date}\nLocation: {location}\nDistance: {distance_km} km\nElevation: {elevation_gain} m\nAccommodation: {accommodation_type}\nCoordinates: [{longitude}, {latitude}] (lon, lat)\nYouTube: {youtube_url}\nNotes: {notes}\nPhotos: {photos_count}\n\nCreating record on GitHub...",
        'create_success': "✅ Record created successfully on GitHub!\n\nThe map will update automatically.\n\nUse /start for more options.",
        'create_error': "❌ Error updating GitHub: {error}\n\nPlease check the logs and try again with /start",

        # Validation errors
        'invalid_day': "Please enter a valid day.",
        'invalid_date': "Invalid date format. Please use YYYY-MM-DD (e.g., 2026-06-23)",
        'invalid_distance': "Please enter a valid number for distance.",
        'invalid_elevation': "Please enter a valid number for elevation gain.",
        'invalid_accommodation': "Please choose one of: {types}",
        'invalid_latitude': "Please send a valid latitude number or use Telegram's location feature.",
        'invalid_longitude': "Please send a valid longitude number.",
        'coord_warning': "⚠️ Warning: Coordinates seem far from Dagestan region.\nExpected around: {exp_lat}, {exp_lon}\nGot: {lat}, {lon}\n\nAre you sure these coordinates are correct? Send /start to restart or send new location.",

        # Update record
        'update_start': "🔄 Update existing record\n\nWhat's the record ID to update?",
        'update_fields': "Current values:\n1. day: {day}\n2. date: {date}\n3. location: {location}\n4. distance_km: {distance_km}\n5. elevation_gain: {elevation_gain}\n6. accommodation_type: {accommodation_type}\n7. coordinates: [{lon}, {lat}]\n8. youtube_url: {youtube_url}\n9. notes: {notes}\n10. photos: {photos}\n\nWhich field do you want to update? (send number 1-10)",
        'update_field_prompt': "Updating '{field}'\n\nSend the new value:",
        'update_success': "✅ Updated '{field}' successfully!\n\nNew value: {value}\n\nUse /start for more options.",
        'update_invalid_field': "Please send a number between 1 and 10.",
        'update_invalid_id': "Please enter a valid number for the ID.",
        'update_not_found': "❌ No record found with ID {id}\n\nUse /start to try again.",
        'update_error': "❌ Error: {error}\n\nUse /start to try again.",
        'update_invalid_value': "Invalid value format: {error}\n\nTry again or /start to cancel.",
        'update_invalid_accom': "Invalid accommodation type. Use: tent, glamping, guesthouse, hotel",
        'update_invalid_coords': "Please send coordinates as: lon, lat (e.g., 46.701786, 42.409953)",

        # Get/Delete
        'get_start': "🔍 Get record\n\nWhat's the record ID?\n\n💡 Tip: Type 'last' to get the most recent record",
        'get_no_records': "❌ No records found in the database.\n\nUse /start to try again.",
        'delete_start': "🗑️ Delete record\n\n⚠️ This action cannot be undone!\n\nWhat's the record ID to delete?",
        'delete_confirm': "⚠️ YOU ARE ABOUT TO DELETE THIS RECORD:\n\nRecord #{id}:\n📅 Day: {day}\n📆 Date: {date}\n📍 Location: {location}\n🚶 Distance: {distance_km} km\n⛰️ Elevation: {elevation_gain} m\n🏕️ Accommodation: {accommodation_type}\n📌 Coordinates: [{lon}, {lat}] (lon, lat)\n\n⚠️ This action CANNOT be undone!\n\nType 'YES' to confirm deletion, or anything else to cancel.",
        'delete_cancelled': "❌ Deletion cancelled.\n\nUse /menu to return to menu or /start to restart.",
        'delete_success': "✅ Record #{id} has been deleted successfully!\n\nDeleted: Day {day} - {location}\n\nUse /menu to continue or /start to restart.",

        # General
        'cancelled': "❌ Cancelled. Use /start to begin again.",
        'back_to_menu': "↩️ Returning to menu...\n\nChoose an option:\n1️⃣ Create a new record\n2️⃣ Update existing record\n3️⃣ Get record by ID\n4️⃣ Delete record by ID\n\nSend the number (1, 2, 3, or 4)",
        'lang_switched': "✅ Language switched to English",
    },
    'ru': {
        'welcome': "🏔️ Добро пожаловать в Менеджер позиций Кавказской тропы!\n\n🔒 Пожалуйста, введите пароль:",
        'access_granted': "✅ Доступ разрешён!\n\nВыберите действие:\n1️⃣ Создать новую запись\n2️⃣ Обновить существующую запись\n3️⃣ Получить запись по ID\n4️⃣ Удалить запись по ID\n\nОтправьте номер (1, 2, 3 или 4)\n\n💡 Подсказка: Используйте /menu для возврата в меню, /cancel для выхода, /ru для русского, /en для английского",
        'wrong_password': "❌ Неверный пароль. Доступ запрещён.\n\nИспользуйте /start чтобы попробовать снова.",
        'menu_invalid': "Пожалуйста отправьте 1, 2, 3 или 4",

        # Create record
        'create_start': "📝 Создание новой записи\n\nКакой это день? (например, 15, 16, 17...)",
        'create_date': "✅ День {day}\n\nКакая дата? (Формат: ГГГГ-ММ-ДД, например, 2026-06-23)",
        'create_location': "✅ Дата: {date}\n\nНазвание местоположения? (например, Хапцай, Гапшима)",
        'create_distance': "✅ Местоположение: {location}\n\nПройденное расстояние сегодня в км? (например, 15.5)\nОтправьте 0 если нет.",
        'create_elevation': "✅ Расстояние: {distance} км\n\nНабор высоты сегодня в метрах? (например, 850)\nОтправьте 0 если нет.",
        'create_accommodation': "✅ Набор высоты: {elevation} м\n\nТип размещения?\nВарианты: tent, glamping, guesthouse, hotel",
        'create_coordinates': "✅ Размещение: {accom}\n\nОтправьте свою локацию через функцию Telegram 📍\nИли отправьте широту (я спрошу долготу следующей)",
        'create_longitude_prompt': "✅ Широта: {latitude}\n\nТеперь отправьте долготу:",
        'create_youtube': "✅ Координаты: [{lon}, {lat}] (долгота, широта)\n\nСсылка на YouTube? (например, https://youtube.com/watch?v=...)\nОтправьте 'skip' если нет.",
        'create_notes': "Есть заметки об этом дне?\nОтправьте 'skip' если нет.",
        'create_photos': "Названия файлов фотографий? (через запятую, например, day15_1.jpg, day15_2.jpg)\nОтправьте 'skip' если нет.",
        'create_summary': "📋 Сводка:\nДень: {day}\nДата: {date}\nМестоположение: {location}\nРасстояние: {distance_km} км\nНабор высоты: {elevation_gain} м\nРазмещение: {accommodation_type}\nКоординаты: [{longitude}, {latitude}] (долгота, широта)\nYouTube: {youtube_url}\nЗаметки: {notes}\nФото: {photos_count}\n\nСоздаём запись на GitHub...",
        'create_success': "✅ Запись успешно создана на GitHub!\n\nКарта обновится автоматически.\n\nИспользуйте /start для дополнительных опций.",
        'create_error': "❌ Ошибка обновления GitHub: {error}\n\nПроверьте логи и попробуйте снова с /start",

        # Validation errors
        'invalid_day': "Пожалуйста введите корректный день.",
        'invalid_date': "Неверный формат даты. Пожалуйста используйте ГГГГ-ММ-ДД (например, 2026-06-23)",
        'invalid_distance': "Пожалуйста введите корректное число для расстояния.",
        'invalid_elevation': "Пожалуйста введите корректное число для набора высоты.",
        'invalid_accommodation': "Пожалуйста выберите один из: {types}",
        'invalid_latitude': "Пожалуйста отправьте корректное число широты или используйте функцию локации Telegram.",
        'invalid_longitude': "Пожалуйста отправьте корректное число долготы.",
        'coord_warning': "⚠️ Внимание: Координаты кажутся далеко от региона Дагестан.\nОжидалось около: {exp_lat}, {exp_lon}\nПолучено: {lat}, {lon}\n\nВы уверены что эти координаты правильные? Отправьте /start для перезапуска или отправьте новую локацию.",

        # Update record
        'update_start': "🔄 Обновление существующей записи\n\nКакой ID записи обновить?",
        'update_fields': "Текущие значения:\n1. день: {day}\n2. дата: {date}\n3. местоположение: {location}\n4. расстояние_км: {distance_km}\n5. набор_высоты: {elevation_gain}\n6. тип_размещения: {accommodation_type}\n7. координаты: [{lon}, {lat}]\n8. ссылка_youtube: {youtube_url}\n9. заметки: {notes}\n10. фото: {photos}\n\nКакое поле вы хотите обновить? (отправьте номер 1-10)",
        'update_field_prompt': "Обновление '{field}'\n\nОтправьте новое значение:",
        'update_success': "✅ Поле '{field}' успешно обновлено!\n\nНовое значение: {value}\n\nИспользуйте /start для дополнительных опций.",
        'update_invalid_field': "Пожалуйста отправьте номер от 1 до 10.",
        'update_invalid_id': "Пожалуйста введите корректный номер для ID.",
        'update_not_found': "❌ Запись с ID {id} не найдена\n\nИспользуйте /start чтобы попробовать снова.",
        'update_error': "❌ Ошибка: {error}\n\nИспользуйте /start чтобы попробовать снова.",
        'update_invalid_value': "Неверный формат значения: {error}\n\nПопробуйте снова или /start для отмены.",
        'update_invalid_accom': "Неверный тип размещения. Используйте: tent, glamping, guesthouse, hotel",
        'update_invalid_coords': "Пожалуйста отправьте координаты как: долгота, широта (например, 46.701786, 42.409953)",

        # Get/Delete
        'get_start': "🔍 Получить запись\n\nКакой ID записи?\n\n💡 Подсказка: Введите 'last' чтобы получить последнюю запись",
        'get_no_records': "❌ Записей не найдено в базе данных.\n\nИспользуйте /start чтобы попробовать снова.",
        'delete_start': "🗑️ Удалить запись\n\n⚠️ Это действие невозможно отменить!\n\nКакой ID записи удалить?",
        'delete_confirm': "⚠️ ВЫ СОБИРАЕТЕСЬ УДАЛИТЬ ЭТУ ЗАПИСЬ:\n\nЗапись #{id}:\n📅 День: {day}\n📆 Дата: {date}\n📍 Местоположение: {location}\n🚶 Расстояние: {distance_km} км\n⛰️ Набор высоты: {elevation_gain} м\n🏕️ Размещение: {accommodation_type}\n📌 Координаты: [{lon}, {lat}] (долгота, широта)\n\n⚠️ Это действие НЕВОЗМОЖНО отменить!\n\nНапишите 'YES' для подтверждения удаления, или что-либо другое для отмены.",
        'delete_cancelled': "❌ Удаление отменено.\n\nИспользуйте /menu для возврата в меню или /start для перезапуска.",
        'delete_success': "✅ Запись #{id} успешно удалена!\n\nУдалено: День {day} - {location}\n\nИспользуйте /menu для продолжения или /start для перезапуска.",

        # General
        'cancelled': "❌ Отменено. Используйте /start чтобы начать снова.",
        'back_to_menu': "↩️ Возврат в меню...\n\nВыберите действие:\n1️⃣ Создать новую запись\n2️⃣ Обновить существующую запись\n3️⃣ Получить запись по ID\n4️⃣ Удалить запись по ID\n\nОтправьте номер (1, 2, 3 или 4)",
        'lang_switched': "✅ Язык переключён на русский",
    }
}

