// ---------------------------------------------------------------------------
// map-init.js  –  Map instance, tile layers, shared state, layer control
// ---------------------------------------------------------------------------

// Initialize the map centered on the Caucasus region
const map = L.map('map').setView([42.8, 44.0], 8);

// Base tile layers
const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19
});

const topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap',
    maxZoom: 17
});

const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles © Esri',
    maxZoom: 19
});

osmLayer.addTo(map);

// Shared layer references (written to by map-layers.js)
let currentLayerControl = null;
let trackLayer      = null;
let pointsLayer     = null;
let positionLayer   = null;
let dailyTracksLayer = null;
let positionData    = null;
let lastPositionCoords = null;
const positionMarkers = {};  // coordKey → Leaflet marker

// ---------------------------------------------------------------------------
// Layer control
// ---------------------------------------------------------------------------

function getLayerNames(lang) {
    const t = translations[lang];
    return {
        baseMaps: {
            [`🗺️ ${t['layer-topographic']}`]: topoLayer,
            [`🌍 ${t['layer-street']}`]: osmLayer,
            [`🛰️ ${t['layer-satellite']}`]: satelliteLayer
        },
        trackLabel:       `🥾 ${t['layer-track']}`,
        pointsLabel:      `📌 ${t['layer-points']}`,
        positionsLabel:   `⛺ ${t['layer-positions']}`,
        dailyTracksLabel: `🎯 ${t['layer-daily-tracks'] || 'Actual Tracks'}`
    };
}

function rebuildLayerControl() {
    const lang = localStorage.getItem('preferred-language') || 'en';
    const layerNames = getLayerNames(lang);

    if (currentLayerControl) {
        try { map.removeControl(currentLayerControl); } catch (e) {}
    }

    const overlays = {};
    if (trackLayer)       overlays[layerNames.trackLabel]       = trackLayer;
    if (dailyTracksLayer) overlays[layerNames.dailyTracksLabel] = dailyTracksLayer;
    if (pointsLayer)      overlays[layerNames.pointsLabel]      = pointsLayer;
    if (positionLayer)    overlays[layerNames.positionsLabel]   = positionLayer;

    currentLayerControl = L.control.layers(layerNames.baseMaps, overlays, {
        position: 'topleft',
        collapsed: true
    }).addTo(map);

    // Force z-index above the overnight-stops panel
    const forceZIndex = () => {
        const el = document.querySelector('.leaflet-control-layers');
        if (el) el.style.setProperty('z-index', '9999', 'important');
    };
    setTimeout(forceZIndex, 50);
    setTimeout(forceZIndex, 200);
    setTimeout(forceZIndex, 500);

    setTimeout(function() {
        const btn = document.querySelector('.leaflet-control-layers-toggle');
        if (btn && translations[lang]['layers']) {
            btn.textContent = translations[lang]['layers'];
        }
    }, 50);
}

rebuildLayerControl();
