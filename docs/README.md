# Caucasian Trail - Interactive Map

A bilingual (EN/RU) web application to display Vladimir Piskunov's epic 1600+ km hiking journey through the Caucasus Mountains from Derbent to Sochi, with interactive maps, real-time progress tracking, photos, and videos.

## 🌐 Live Site

**View the interactive map:** https://almat65.github.io/caucasian_trail/

## ✨ Features

### Main Page
- **Bilingual interface** 🌍 (English/Russian) with instant language switching
- **Real-time progress statistics** showing:
  - Days on trail
  - Total distance covered
  - Total elevation gained
- Journey overview with complete route details:
  - Total planned distance: 1600+ km
  - Total elevation gain: 74,000+ m
  - Highest point: 3692 m
- Social media integration (YouTube, Instagram)

### Interactive Map
- **Full GPS track** of the hiking route
- **Points of interest** (mountain passes, river crossings, checkpoints, danger zones)
- **Overnight stops** 🏕️ tracking with:
  - Accommodation types (tent, glamping, guesthouse, hotel)
  - Daily distance and elevation statistics
  - Day numbers (supports multi-day stays like "10-12")
- **Media carousel** combining YouTube videos and photos for each location
- **Responsive design** (works perfectly on mobile devices)
- **Multiple map layers**:
  - 🗺️ Topographic (default, best for hiking)
  - 🌍 Street map
  - 🛰️ Satellite view
- **Scrollable bottom panel** with all overnight stops for quick navigation

## 🚀 Quick Start

### Testing Locally

1. **Open the site locally:**
   - Simply open `index.html` in your web browser
   - Or use a local server (recommended):
     ```bash
     python -m http.server 8000
     ```
   - Then visit: `http://localhost:8000`

2. **View the map:**
   - Click on "View Interactive Map" button
   - Switch between English and Russian using the language toggle (top right)
   - Click on any point to see detailed information
   - Zoom and pan around the map
   - Use the "Layers" control to switch map views
   - Click on overnight stops in the bottom panel for quick navigation

## 📝 Adding Daily Progress (Overnight Stops)

Edit `data/actual_position.geojson` to add new overnight stops with complete statistics:

### Complete Example with All Features:

```json
{
  "type": "Feature",
  "properties": {
    "id": 7,
    "day": "7",
    "date": "2026-06-16",
    "location": "Village Name",
    "distance_km": 28,
    "elevation_gain": 1450,
    "accommodation_type": "tent",
    "youtube_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    "notes": "Beautiful views. Water available near the camping spot.",
    "photos": ["day7_photo1.jpg", "day7_photo2.jpg"]
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.1234567, 42.9876543]
  }
}
```

### Properties Explained:

#### Required Fields:
- **id**: Unique sequential number (1, 2, 3, etc.)
- **day**: Day number as string (supports ranges like "10-12" for multi-day stays)
- **date**: Date in format "YYYY-MM-DD"
- **location**: Place name where you spent the night
- **accommodation_type**: Type of accommodation
  - `"tent"` - Tent camping ⛺
  - `"glamping"` - Glamping 🏕️
  - `"guesthouse"` - Guest house 🏠
  - `"hotel"` - Hotel 🏨
- **coordinates**: GPS position `[longitude, latitude]`

#### Optional Fields (but highly recommended):
- **distance_km**: Distance covered that day in kilometers (number, can be 0)
- **elevation_gain**: Elevation gained that day in meters (number, can be 0)
- **youtube_url**: Full YouTube video URL (any format works)
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
- **photos**: Array of photo filenames from `assets/photos/` folder
  - `["photo1.jpg", "photo2.jpg", "photo3.jpg"]`
- **notes**: Additional detailed notes, tips, or warnings

### Multi-day Stays:
If you stay multiple days in the same location, use day ranges:
```json
"day": "10-12",
"date": "2026-06-20",
"notes": "Rest days in village. Restocking supplies."
```

## 📸 Managing Photos

1. Place all photos in the `assets/photos/` folder
2. Reference them in the GeoJSON by filename only (no path)
3. Photos appear in the media carousel (swipeable with videos)
4. Clicking a photo opens it full-size in a new tab

### Media Carousel:
The carousel displays both videos and photos:
- **YouTube video** (if provided) appears as first slide
- **Photos** appear as subsequent slides
- Navigate using:
  - ← → Arrow buttons
  - Dots below the carousel
  - Click any dot to jump to that item

Current photos:
- day6.jpg
- day6_.jpg
- IMG_20260614_063608_862.jpg
- IMG_20260614_063608_993.jpg

## 🗺️ Adding Points of Interest

Edit `data/points.geojson` to add mountain passes, river crossings, checkpoints, etc.:

### Example Point:

```json
{
  "type": "Feature",
  "properties": {
    "nom": "Перевал Галпай",
    "description": "1784м",
    "col3": "нк",
    "youtube_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    "photos": ["pass_view.jpg"],
    "notes": "Beautiful sunrise view. Best time to cross: early morning. Water available 500m before the pass."
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.740748, 41.980543]
  }
}
```

### Automatic Icon Assignment:
Icons automatically change based on point names:
- ⛰️ Mountain passes (contains "перевал")
- 🌊 River crossings (contains "брод")
- ⚠️ Danger zones (contains "опасн")
- 🚧 Checkpoints (contains "пост", "застава", "пропуск")
- 📍 Other points (default)

## 📊 Progress Statistics

The main page automatically calculates and displays:
- **Days on trail**: Total number of overnight stops
- **Distance covered**: Sum of all `distance_km` values
- **Elevation gained**: Sum of all `elevation_gain` values

These update automatically when you add new entries to `actual_position.geojson`!

## 🌐 Deploying to GitHub Pages (FREE!)

### Step 1: Create a GitHub Account
- Go to https://github.com and sign up (free)

### Step 2: Create a Repository
1. Click "New repository"
2. Name it: `caucasian_trail` (or any name you like)
3. Make it **public**
4. Don't initialize with README (we already have files)

### Step 3: Push Your Files
```bash
git init
git add .
git commit -m "Initial commit - Caucasian Trail website"
git remote add origin https://github.com/your-username/caucasian_trail.git
git push -u origin master
```

Or use GitHub Desktop for a visual interface.

### Step 4: Enable GitHub Pages
1. Go to repository "Settings"
2. Scroll to "Pages" in left sidebar
3. Under "Source", select "master" branch
4. Click "Save"
5. Wait 1-2 minutes

### Step 5: Access Your Site
Your site is live at: **https://your-username.github.io/caucasian_trail/**

**It's completely FREE! No server costs, no database needed.**

## 🔄 Updating Content

When you make changes locally, push them to GitHub to update the live site:

```bash
git add .
git commit -m "Add Day 7 progress with photos"
git push
# Site updates automatically in ~1-2 minutes
```

### Daily Update Workflow:
1. Add new entry to `data/actual_position.geojson` with day's stats
2. Upload day's photos to `assets/photos/` folder
3. Commit and push to GitHub
4. Progress stats on main page update automatically!

## 🎨 Customization

### Updating Social Media Links
Edit `index.html` and replace:
```html
<a href="https://www.youtube.com/@Hiking_is_cool" target="_blank" ...>
<a href="https://www.instagram.com/voven4egg" target="_blank" ...>
```

### Changing Map Center
Edit `assets/js/app.js`:
```javascript
const map = L.map('map').setView([42.8, 44.0], 8);
// [latitude, longitude], zoom level
```

### Updating Journey Details
Edit `assets/js/translations.js` to change:
- Total distance
- Total elevation gain
- Start date
- Route description

## 🌍 Bilingual Support

The site supports English and Russian with instant switching:

### Adding New Translations:
Edit `assets/js/translations.js` and add entries to both `en` and `ru` sections:

```javascript
translations = {
    en: {
        'your-key': 'English text',
        // ... more translations
    },
    ru: {
        'your-key': 'Русский текст',
        // ... more translations
    }
}
```

Use in HTML:
```html
<element data-i18n="your-key">Default text</element>
```

The language preference is saved in browser storage and persists between sessions.

## 🛠️ Technologies Used

- **Leaflet.js** - Open source interactive maps
- **OpenStreetMap / OpenTopoMap** - Free map tiles
- **GitHub Pages** - Free hosting
- **GeoJSON** - Geographic data format
- **HTML/CSS/JavaScript** - Web technologies
- **No frameworks** - Pure vanilla JavaScript for performance

## 📱 Mobile Responsive

The site is fully responsive with:
- Collapsible legend and bottom panel
- Touch-friendly navigation
- Optimized layout for small screens
- Swipeable media carousel

## 🆘 Troubleshooting

### Map doesn't show points:
- Check that GeoJSON files are valid (use http://geojson.io)
- Open browser console (F12) to see errors
- Ensure coordinates are `[longitude, latitude]` not reversed

### Photos don't load:
- Ensure photos are in `assets/photos/` folder
- Check filename spelling matches exactly
- Photos are case-sensitive on GitHub Pages
- File extensions must match (`.jpg` vs `.JPG`)

### YouTube video doesn't show:
- Ensure `youtube_url` property is included
- Check that the URL is valid and video is public
- Any YouTube URL format works (watch, youtu.be, embed)

### Progress stats show "-":
- Ensure `distance_km` and `elevation_gain` have numeric values
- Use `0` for rest days, not empty strings
- Check that `actual_position.geojson` is valid JSON

### Language switching doesn't work:
- Clear browser cache and reload
- Check browser console for JavaScript errors
- Ensure `translations.js` is loaded correctly

## 📁 Project Structure

```
caucasian_trail/
├── index.html              # Main landing page
├── map.html                # Interactive map page
├── assets/
│   ├── css/
│   │   └── style.css       # All styles
│   ├── js/
│   │   ├── app.js          # Map functionality
│   │   └── translations.js # Bilingual support
│   └── photos/             # All photos
├── data/
│   ├── actual_position.geojson  # Overnight stops
│   ├── points.geojson           # Points of interest
│   └── track.geojson            # GPS track
└── docs/
    ├── README.md           # This file
    ├── SUMMARY.md          # Project summary
    └── DAILY_POSITIONS_GUIDE.md  # Detailed guide
```

## 🎉 Tips for Best Results

1. **Keep daily updates**:
   - Add each day's entry with distance and elevation
   - Progress stats update automatically

2. **Use meaningful day numbers**:
   - Single day: `"7"`
   - Multi-day stay: `"10-12"`
   - Makes the journey story clear

3. **Add media content**:
   - Combine YouTube video + multiple photos per day
   - Creates rich storytelling

4. **Write helpful notes**:
   - Water sources
   - Camping spots
   - Warnings and tips
   - Trail conditions

5. **Test locally first**:
   - Always test changes before pushing
   - Use browser console to catch errors
   - Validate JSON files

## 📧 Need Help?

- Check browser console for errors (F12 → Console)
- Validate your GeoJSON at http://geojson.io
- Check GitHub Pages deployment status in repository settings

## 🎊 Next Steps

1. ✅ Test the site locally
2. ✅ Add daily progress entries
3. ✅ Upload photos for each day
4. ✅ Include YouTube videos
5. ✅ Update social media links
6. ✅ Deploy to GitHub Pages
7. ✅ Share your adventure with the world!

---

**Happy Mapping! 🗺️🏔️ Счастливого Пути! 🥾**
