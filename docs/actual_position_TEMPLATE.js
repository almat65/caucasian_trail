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
    "day": "Day 7",                    // Day number (e.g., "Day 7", "Day 8", etc.)
    "date": "2026-06-15",              // Date in YYYY-MM-DD format
    "accommodation_type": "tent",       // Choose ONE: "tent", "glamping", "hotel", "guesthouse"
    "youtube_url": "",                  // Full YouTube URL (optional)
    "notes": "",                        // Any notes about this day (optional)
    "photos": []                        // Array of photo filenames from volodya_photos/ folder (optional)
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

// Example 1: Simple tent camping (no extras)
{
  "type": "Feature",
  "properties": {
    "day": "Day 7",
    "date": "2026-06-15",
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

// Example 2: Guest house with YouTube video
{
  "type": "Feature",
  "properties": {
    "day": "Day 8",
    "date": "2026-06-16",
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

// Example 3: Hotel with photos
{
  "type": "Feature",
  "properties": {
    "day": "Day 9",
    "date": "2026-06-17",
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

// Example 4: Glamping with everything
{
  "type": "Feature",
  "properties": {
    "day": "Day 10",
    "date": "2026-06-18",
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
// 1. Add your photos to the volodya_photos/ folder
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
