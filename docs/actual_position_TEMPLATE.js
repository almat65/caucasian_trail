// ========================================
// TEMPLATE FOR actual_position.geojson
// ========================================
//
// Copy this template for each day and add it to the "features" array
// in actual_position.geojson
//
// ========================================

{
  "type": "Feature",
  "properties": {
    "id": 7,                            // Unique sequential number (1, 2, 3, etc.)
    "day": "7",                         // Day number as string. Use "7" or "10-12" for multi-day stays
    "date": "2026-06-15",               // Date in YYYY-MM-DD format
    "location": "Village Name",         // Place name where you spent the night
    "distance_km": 28,                  // Distance covered that day in km (number, can be 0 for rest days)
    "elevation_gain": 1450,             // Elevation gained that day in meters (number, can be 0)
    "accommodation_type": "tent",       // Choose ONE: "tent", "glamping", "hotel", "guesthouse"
    "youtube_url": "",                  // Full YouTube URL (optional)
    "notes": "",                        // Any notes about this day (optional)
    "photos": []                        // Array of photo filenames from assets/photos/ folder (optional)
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.123456, 42.654321]  // [longitude, latitude] - REQUIRED
  }
}

// ========================================
// ACCOMMODATION TYPES & ICONS
// ========================================
// "tent"       → ⛺ (green color)
// "glamping"   → 🏕️ (orange color)
// "hotel"      → 🏨 (blue color)
// "guesthouse" → 🏠 (purple color)

// ========================================
// COMPLETE EXAMPLES:
// ========================================

// Example 1: Simple tent camping with statistics
{
  "type": "Feature",
  "properties": {
    "id": 7,
    "day": "7",
    "date": "2026-06-15",
    "location": "Mountain Campsite",
    "distance_km": 28,
    "elevation_gain": 1450,
    "accommodation_type": "tent",
    "youtube_url": "",
    "notes": "Beautiful mountain campsite. Clear night, saw stars.",
    "photos": []
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.123456, 42.654321]
  }
}

// Example 2: Guest house with YouTube video and daily stats
{
  "type": "Feature",
  "properties": {
    "id": 8,
    "day": "8",
    "date": "2026-06-16",
    "location": "Local Family Guesthouse",
    "distance_km": 24,
    "elevation_gain": 890,
    "accommodation_type": "guesthouse",
    "youtube_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    "notes": "Stayed with a local family. Amazing hospitality. Traditional dinner included.",
    "photos": []
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.234567, 42.765432]
  }
}

// Example 3: Hotel rest day with photos
{
  "type": "Feature",
  "properties": {
    "id": 9,
    "day": "9",
    "date": "2026-06-17",
    "location": "Town Hotel",
    "distance_km": 0,
    "elevation_gain": 0,
    "accommodation_type": "hotel",
    "youtube_url": "",
    "notes": "Rest day in town. Hot shower and good food!",
    "photos": ["day9_hotel.jpg", "day9_view.jpg"]
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.345678, 42.876543]
  }
}

// Example 4: Glamping with everything (video + photos + stats)
{
  "type": "Feature",
  "properties": {
    "id": 10,
    "day": "10",
    "date": "2026-06-18",
    "location": "Luxury Glamping Site",
    "distance_km": 32,
    "elevation_gain": 1680,
    "accommodation_type": "glamping",
    "youtube_url": "https://youtu.be/VIDEO_ID",
    "notes": "Luxury camping setup with proper beds and electricity. Worth the extra cost!",
    "photos": ["glamping_tent.jpg", "glamping_view.jpg", "sunset.jpg"]
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.456789, 42.987654]
  }
}

// Example 5: Multi-day stay (3 days in same location)
{
  "type": "Feature",
  "properties": {
    "id": 11,
    "day": "11-13",
    "date": "2026-06-19",
    "location": "Mountain Village",
    "distance_km": 0,
    "elevation_gain": 0,
    "accommodation_type": "guesthouse",
    "youtube_url": "",
    "notes": "Rest days. Waiting for weather to improve before crossing the next pass. Explored the village.",
    "photos": ["village_life.jpg"]
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.567890, 43.098765]
  }
}

// ========================================
// HOW TO GET COORDINATES:
// ========================================
// 1. Open Google Maps
// 2. Right-click on the location
// 3. Click "What's here?"
// 4. Copy the coordinates (they appear at the bottom)
// 5. Format: [longitude, latitude] - longitude first!

// Example from Google Maps: 42.123456, 47.654321
// In GeoJSON format: [47.654321, 42.123456]  ← SWAP THEM!

// ========================================
// YOUTUBE URL FORMATS (all work):
// ========================================
// https://www.youtube.com/watch?v=VIDEO_ID
// https://youtu.be/VIDEO_ID
// https://www.youtube.com/shorts/VIDEO_ID

// ========================================
// PHOTOS:
// ========================================
// 1. Add your photos to the assets/photos/ folder
// 2. Reference them by filename only (no path)
// 3. Multiple photos: ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
// 4. No photos: []

// ========================================
// ADDING TO actual_position.geojson:
// ========================================
// 1. Open actual_position.geojson
// 2. Find the "features" array
// 3. Add a comma after the last entry
// 4. Paste your new day entry
// 5. Save the file
// 6. Refresh the map

// ========================================
// IMPORTANT REMINDERS:
// ========================================
// ✅ Use double quotes (") not single quotes (')
// ✅ Don't forget commas between array items
// ✅ Coordinates are [longitude, latitude] - longitude first!
// ✅ accommodation_type must be exactly: "tent", "glamping", "hotel", or "guesthouse"
// ✅ Each feature must have valid geometry with coordinates
// ✅ Date format: YYYY-MM-DD (e.g., "2026-06-15")
