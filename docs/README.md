# Caucasian Trail - Interactive Map

A web application to display your hiking trail through the Caucasus Mountains with interactive maps, photos, and information.

## � Live Site

**View the interactive map:** https://almat65.github.io/caucasian_trail/

## �🎯 Features

- Interactive map with your GPS track
- Interest points (mountain passes, river crossings, checkpoints)
- **Daily position markers** 🏕️ showing your progress with animated pulsing effect
- Photo galleries for each point
- YouTube video embedding (in popups and daily positions)
- Responsive design (works on mobile)
- Free hosting via GitHub Pages

## 🚀 Quick Start

### Testing Locally

1. **Open the site locally:**
   - Simply open `index.html` in your web browser
   - Or use a local server (recommended):
     ```
     python -m http.server 8000
     ```
   - Then visit: `http://localhost:8000`

2. **View the map:**
   - Click on "View Interactive Map" button
   - Click on any point to see information
   - Zoom and pan around the map

## 📝 Adding Information to Points

To add YouTube videos, photos, and notes to your points, edit `points.geojson`:

### Example Point with All Features:

```json
{
  "type": "Feature",
  "properties": {
    "WKT": "POINT (47.740748 41.980543)",
    "nom": "Перевал Галпай",
    "description": "1784м",
    "col3": "нк",
    "youtube_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID",
    "photos": ["day6.jpg", "IMG_20260614_063608_862.jpg"],
    "notes": "Beautiful sunrise view. Best time to cross: early morning. Water available 500m before the pass."
  },
  "geometry": {
    "type": "Point",
    "coordinates": [47.740748, 41.980543]
  }
}
```

### Properties Explained:

- **nom**: Name of the point (already exists)
- **description**: Short description (already exists)
- **col3**: Additional info (already exists)
- **youtube_url**: Full YouTube video URL (any format works)
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
- **photos**: Array of photo filenames from `volodya_photos/` folder
  - `["photo1.jpg", "photo2.jpg"]`
- **notes**: Additional detailed notes and tips

## 📸 Managing Photos

1. Place all photos in the `volodya_photos/` folder
2. Reference them in the GeoJSON by filename only
3. Photos will be displayed in popups when clicking on points
4. Clicking a photo opens it in full size in a new tab

Current photos:
- day6.jpg
- day6_.jpg
- IMG_20260614_063608_862.jpg
- IMG_20260614_063608_993.jpg
- IMG_20260614_063613_574.jpg

## 🏕️ Daily Position Tracking

Your daily progress is displayed with special 🏕️ markers that pulse to stand out. The `actual_position.geojson` file tracks:
- Day-by-day camping/accommodation locations
- YouTube videos from each day (automatically embedded in popups)
- Notes about each day's experience

To update daily positions, edit `actual_position.geojson` and add new entries with:
- **nom**: Day number (e.g., "Day 7")
- **description**: Can be a YouTube URL (will auto-embed) or text notes
- **coordinates**: GPS position for that day

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
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/caucasian-trail.git
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
Your site is live at: **https://almat65.github.io/caucasian_trail/**

**It's completely FREE! No server costs, no database needed.**

## 🔄 Updating Content

When you make changes locally, push them to GitHub to update the live site:

```bash
git add .
git commit -m "Update content"
git push
# Site updates automatically in ~1-2 minutes
```

### Adding a New Point:
1. Edit `data/points.geojson`
2. Add a new feature object with coordinates and properties
3. Commit and push to GitHub

### Adding Photos:
1. Add photos to `assets/photos/` folder
2. Reference them in the point's `photos` array
3. Commit and push to GitHub

### Updating the Track:
1. Edit `data/track.geojson` with new GPS coordinates
2. Commit and push to GitHub

## 🎨 Customization

### Updating Social Media Links
Edit `index.html` and replace:
- `https://www.youtube.com/@your-channel` with your YouTube channel
- `https://www.instagram.com/your-profile` with your Instagram profile

### Changing Map Style
In `app.js`, uncomment the OpenTopoMap layer for better topographic view:
```javascript
L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap',
    maxZoom: 17
}).addTo(map);
```

### Map Icons
Icons automatically change based on point names:
- ⛰️ Mountain passes (перевал)
- 🌊 River crossings (брод)
- ⚠️ Danger zones (опасн)
- 🚧 Checkpoints (пост, застава, пропуск)
- 📍 Other points

## 🛠️ Technologies Used

- **Leaflet.js** - Open source interactive maps
- **OpenStreetMap** - Free map tiles
- **GitHub Pages** - Free hosting
- **GeoJSON** - Geographic data format
- **HTML/CSS/JavaScript** - Web technologies

## 📱 Mobile Friendly

The site is fully responsive and works great on phones and tablets!

## 🆘 Troubleshooting

### Map doesn't show points:
- Check that `points.geojson` is valid JSON
- Open browser console (F12) to see errors

### Photos don't load:
- Ensure photos are in `volodya_photos/` folder
- Check filename spelling matches exactly
- Photos are case-sensitive on GitHub Pages

### YouTube video doesn't show:
- Ensure `youtube_url` property is included
- Check that the URL is valid
- Video must be public on YouTube

## 📧 Need Help?

- Check browser console for errors (F12 → Console)
- Validate your GeoJSON at http://geojson.io

## 🎉 Next Steps

1. ✅ Test the site locally
2. ✅ Add YouTube URLs to your favorite points
3. ✅ Link photos to relevant locations
4. ✅ Update social media links
5. ✅ Deploy to GitHub Pages
6. ✅ Share your adventure!

---

**Happy Mapping! 🗺️🏔️**
