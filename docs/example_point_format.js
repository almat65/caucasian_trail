// EXAMPLE: How to add YouTube videos and photos to your points
// This shows how to modify your points.geojson file

// ========================================
// BEFORE (current format):
// ========================================
{
  "type": "Feature",
  "properties": {
    "WKT": "POINT (47.740748 41.980543)",
    "nom": "Перевал Галпай",
    "description": " 1784м",
    "col3": " нк"
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.740748, 41.980543]
  }
}

// ========================================
// AFTER (with YouTube, photos, and notes):
// ========================================
{
  "type": "Feature",
  "properties": {
    "WKT": "POINT (47.740748 41.980543)",
    "nom": "Перевал Галпай",
    "description": " 1784м",
    "col3": " нк",
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "photos": ["day6.jpg", "day6_.jpg"],
    "notes": "Stunning views at sunrise. Trail is well-marked. Water source 200m before the pass."
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.740748, 41.980543]
  }
}

// ========================================
// MULTIPLE EXAMPLES:
// ========================================

// Example 1: Point with just photos
{
  "type": "Feature",
  "properties": {
    "WKT": "POINT (46.901367 42.442935)",
    "nom": "Броды",
    "description": " опасно в дождь - сель",
    "col3": "",
    "photos": ["IMG_20260614_063608_862.jpg", "IMG_20260614_063608_993.jpg"]
  },
  "geometry": {
    "type": "Point",
    "coordinates": [46.901367, 42.442935]
  }
}

// Example 2: Point with YouTube only
{
  "type": "Feature",
  "properties": {
    "WKT": "POINT (42.513273 43.433078)",
    "nom": "Первый брод",
    "description": " проходить рано утром",
    "col3": "",
    "youtube_url": "https://youtu.be/VIDEO_ID_HERE"
  },
  "geometry": {
    "type": "Point",
    "coordinates": [42.513273, 43.433078]
  }
}

// Example 3: Point with everything
{
  "type": "Feature",
  "properties": {
    "WKT": "POINT (43.691299 43.015661)",
    "nom": "Перевал Восточный Уаза",
    "description": " 2978м",
    "col3": " нк",
    "youtube_url": "https://www.youtube.com/watch?v=YOUR_VIDEO",
    "photos": ["day6.jpg", "IMG_20260614_063613_574.jpg"],
    "notes": "Challenging ascent. Best weather window in July-August. Amazing panoramic views from the top. Camping spot available 1km after the pass."
  },
  "geometry": {
    "type": "Point",
    "coordinates": [43.691299, 43.015661]
  }
}

// ========================================
// YOUTUBE URL FORMATS (all supported):
// ========================================
"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
"youtube_url": "https://youtu.be/VIDEO_ID"
"youtube_url": "https://www.youtube.com/embed/VIDEO_ID"

// ========================================
// PHOTOS ARRAY FORMAT:
// ========================================
// Just the filename - photos must be in volodya_photos/ folder
"photos": ["photo1.jpg"]                    // One photo
"photos": ["photo1.jpg", "photo2.jpg"]      // Multiple photos
"photos": []                                 // No photos (or omit property)

// ========================================
// NOTES FORMAT:
// ========================================
"notes": "Any text you want. Can include tips, warnings, descriptions, etc."

// ========================================
// IMPORTANT REMINDERS:
// ========================================
// 1. Use double quotes (") not single quotes (')
// 2. Don't forget commas between properties
// 3. Photo filenames are case-sensitive
// 4. YouTube videos must be public
// 5. You can omit any property if you don't need it
