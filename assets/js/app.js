// Initialize the map centered on the Caucasus region
const map = L.map('map').setView([42.8, 44.0], 8);

// Define base tile layers
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

// Add default layer (topographic is better for hiking)
topoLayer.addTo(map);

// Prepare overlay layers object (will be populated after data loads)
const overlayMaps = {};

// Function to get translated layer names
function getLayerNames(lang) {
    const t = translations[lang];
    return {
        baseMaps: {
            [`🗺️ ${t['layer-topographic']}`]: topoLayer,
            [`🌍 ${t['layer-street']}`]: osmLayer,
            [`🛰️ ${t['layer-satellite']}`]: satelliteLayer
        },
        trackLabel: `🥾 ${t['layer-track']}`,
        pointsLabel: `📌 ${t['layer-points']}`,
        positionsLabel: `⛺ ${t['layer-positions']}`
    };
}

// Store references to layers for updating labels
let currentLayerControl = null;
let trackLayer = null;
let pointsLayer = null;
let positionLayer = null;

// Function to rebuild layer control with current language
function rebuildLayerControl() {
    const lang = localStorage.getItem('preferred-language') || 'en';
    const layerNames = getLayerNames(lang);

    // Remove existing control if present
    if (currentLayerControl) {
        try {
            map.removeControl(currentLayerControl);
        } catch (e) {
            // Control already removed or never added
        }
    }

    // Create new control with translated names
    const overlays = {};
    if (trackLayer) overlays[layerNames.trackLabel] = trackLayer;
    if (pointsLayer) overlays[layerNames.pointsLabel] = pointsLayer;
    if (positionLayer) overlays[layerNames.positionsLabel] = positionLayer;

    currentLayerControl = L.control.layers(layerNames.baseMaps, overlays, {
        position: 'topleft',
        collapsed: true
    }).addTo(map);

    // Force z-index to be above overnight stops panel - multiple attempts
    const forceZIndex = () => {
        const layersContainer = document.querySelector('.leaflet-control-layers');
        if (layersContainer) {
            layersContainer.style.setProperty('z-index', '9999', 'important');
        }
    };
    setTimeout(forceZIndex, 50);
    setTimeout(forceZIndex, 200);
    setTimeout(forceZIndex, 500);

    // Set button text
    setTimeout(function() {
        const layersBtn = document.querySelector('.leaflet-control-layers-toggle');
        if (layersBtn && translations[lang]['layers']) {
            layersBtn.textContent = translations[lang]['layers'];
        }
    }, 50);
}

// Initialize layer control
rebuildLayerControl();

// Create custom control for "Go to Last Position" button
L.Control.GoToLastPosition = L.Control.extend({
    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');

        const button = L.DomUtil.create('button', 'go-to-last-position-btn', container);
        button.innerHTML = '📍';

        // Get current language for title
        const lang = localStorage.getItem('preferred-language') || 'en';
        button.title = translations[lang]['go-to-last-position'];
        button.setAttribute('aria-label', translations[lang]['go-to-last-position']);

        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function() {
            goToLastPosition();
        });

        return container;
    }
});

L.control.goToLastPosition = function(opts) {
    return new L.Control.GoToLastPosition(opts);
}

// Add the control to the map (position button above layer control)
L.control.goToLastPosition({ position: 'topleft' }).addTo(map);

// Coordinate tool state
let coordinateToolActive = false;
let coordinateTooltip = null;

// Create custom control for coordinate tool button
L.Control.CoordinateTool = L.Control.extend({
    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');

        const button = L.DomUtil.create('button', 'coordinate-tool-btn', container);
        button.innerHTML = '⊕';

        // Get current language for title
        const lang = localStorage.getItem('preferred-language') || 'en';
        button.title = translations[lang]['coordinates-label'];
        button.setAttribute('aria-label', translations[lang]['coordinates-label']);

        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function() {
            toggleCoordinateTool();
        });

        return container;
    }
});

L.control.coordinateTool = function(opts) {
    return new L.Control.CoordinateTool(opts);
}

// Add coordinate tool button to map
L.control.coordinateTool({ position: 'topleft' }).addTo(map);

// Create custom control for legend button
L.Control.LegendButton = L.Control.extend({
    onAdd: function(map) {
        const container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');

        const button = L.DomUtil.create('button', 'legend-btn', container);
        button.innerHTML = '📋';

        // Get current language for title
        const lang = localStorage.getItem('preferred-language') || 'en';
        button.title = translations[lang]['legend-title'];
        button.setAttribute('aria-label', translations[lang]['legend-title']);

        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', function() {
            toggleLegend();
        });

        return container;
    }
});

L.control.legendButton = function(opts) {
    return new L.Control.LegendButton(opts);
}

// Add legend button to map
L.control.legendButton({ position: 'topleft' }).addTo(map);

// Function to toggle coordinate tool
function toggleCoordinateTool() {
    coordinateToolActive = !coordinateToolActive;
    const button = document.querySelector('.coordinate-tool-btn');
    const lang = localStorage.getItem('preferred-language') || 'en';

    if (coordinateToolActive) {
        button.classList.add('active');
    } else {
        button.classList.remove('active');

        // Remove tooltip
        if (coordinateTooltip && map.hasLayer(coordinateTooltip)) {
            map.closeTooltip(coordinateTooltip);
        }
    }
}

// Update coordinates on mouse move (only when tool is active)
map.on('mousemove', function(e) {
    if (!coordinateToolActive) return;

    const lat = e.latlng.lat.toFixed(6);
    const lng = e.latlng.lng.toFixed(6);

    // Create tooltip if it doesn't exist
    if (!coordinateTooltip) {
        coordinateTooltip = L.tooltip({
            permanent: true,
            className: 'coordinate-tooltip',
            direction: 'top',
            offset: [0, -10]
        });
    }

    if (coordinateTooltip) {
        coordinateTooltip.setLatLng(e.latlng)
            .setContent(`<strong>Lat:</strong> ${lat}<br><strong>Lng:</strong> ${lng}<br><em>Click to copy</em>`);

        if (!map.hasLayer(coordinateTooltip)) {
            coordinateTooltip.addTo(map);
        }
    }
});

// Copy coordinates on map click (only when tool is active)
map.on('click', function(e) {
    if (!coordinateToolActive) return;

    // Don't copy if clicking on a marker or popup
    if (e.originalEvent.target.closest('.leaflet-marker-icon') ||
        e.originalEvent.target.closest('.leaflet-popup')) {
        return;
    }

    const lat = e.latlng.lat.toFixed(6);
    const lng = e.latlng.lng.toFixed(6);
    const coordText = `${lat}, ${lng}`;

    // Copy to clipboard
    navigator.clipboard.writeText(coordText).then(function() {
        // Show success message in tooltip
        const lang = localStorage.getItem('preferred-language') || 'en';
        if (coordinateTooltip) {
            coordinateTooltip.setContent(`<strong style="color: #4CAF50;">${translations[lang]['coordinates-copied']}</strong>`);

            // Deactivate tool after a short delay
            setTimeout(function() {
                coordinateToolActive = false;
                const button = document.querySelector('.coordinate-tool-btn');
                if (button) {
                    button.classList.remove('active');
                }
                if (map.hasLayer(coordinateTooltip)) {
                    map.closeTooltip(coordinateTooltip);
                }
            }, 1000);
        }
    }).catch(function(err) {
        console.error('Failed to copy coordinates:', err);
    });
});

// Function to create popup content
function createPopupContent(properties) {
    let content = `<div class="popup-title">${properties.nom || 'Point of Interest'}</div>`;

    if (properties.description) {
        content += `<div class="popup-description">${properties.description}</div>`;
    }

    if (properties.col3) {
        content += `<div class="popup-info"><strong>Info:</strong> ${properties.col3}</div>`;
    }

    // Media carousel (YouTube video + photos)
    if (properties.youtube_url || (properties.photos && Array.isArray(properties.photos) && properties.photos.length > 0)) {
        content += createMediaCarousel(properties.youtube_url, properties.photos);
    }

    // Additional notes (if notes property exists)
    if (properties.notes) {
        content += `<div class="popup-info"><strong>Notes:</strong> ${properties.notes}</div>`;
    }

    return content;
}

// Create media carousel HTML (videos + photos)
function createMediaCarousel(youtubeUrl, photos) {
    const items = [];

    // Add YouTube video as first item if available
    if (youtubeUrl) {
        const videoId = extractYouTubeID(youtubeUrl);
        if (videoId) {
            items.push({ type: 'video', id: videoId, url: youtubeUrl });
        }
    }

    // Add photos
    if (photos && Array.isArray(photos)) {
        photos.forEach(photo => {
            items.push({ type: 'photo', src: photo });
        });
    }

    // If only one item and it's a photo, show simple view
    if (items.length === 1 && items[0].type === 'photo') {
        return `<div class="popup-photos">
            <img src="assets/photos/${items[0].src}" alt="Photo" onclick="window.open(this.src, '_blank')">
        </div>`;
    }

    // If only video, show simple video view
    if (items.length === 1 && items[0].type === 'video') {
        return `<div class="popup-youtube">
            <iframe src="https://www.youtube.com/embed/${items[0].id}"
                    allowfullscreen></iframe>
        </div>`;
    }

    // Create carousel for multiple items
    const carouselId = 'carousel-' + Math.random().toString(36).substr(2, 9);
    let html = `<div class="photo-carousel" id="${carouselId}">
        <div class="carousel-container">`;

    items.forEach((item, index) => {
        if (item.type === 'video') {
            html += `<div class="carousel-item ${index === 0 ? 'active' : ''}" data-type="video">
                <iframe src="https://www.youtube.com/embed/${item.id}"
                        allowfullscreen></iframe>
            </div>`;
        } else {
            html += `<img src="assets/photos/${item.src}" alt="Media ${index + 1}"
                         class="carousel-item carousel-image ${index === 0 ? 'active' : ''}"
                         data-type="photo"
                         onclick="window.open(this.src, '_blank')">`;
        }
    });

    html += `</div>
        <button class="carousel-btn prev" onclick="changeMedia('${carouselId}', -1)">❮</button>
        <button class="carousel-btn next" onclick="changeMedia('${carouselId}', 1)">❯</button>
        <div class="carousel-dots">`;

    items.forEach((_, index) => {
        html += `<span class="dot ${index === 0 ? 'active' : ''}" onclick="showMedia('${carouselId}', ${index})"></span>`;
    });

    html += `</div></div>`;
    return html;
}

// Extract YouTube video ID from URL
function extractYouTubeID(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
}

// Style function for points
function getPointIcon(properties) {
    // Different icons based on point type
    let emoji = '📍';

    if (properties.nom) {
        const name = properties.nom.toLowerCase();
        if (name.includes('перевал')) emoji = '⛰️';
        else if (name.includes('брод')) emoji = '🌊';
        else if (name.includes('опасн')) emoji = '⚠️';
        else if (name.includes('пост') || name.includes('застава') || name.includes('пропуск')) emoji = '🚧';
    }

    return L.divIcon({
        html: `<div style="font-size: 24px;">${emoji}</div>`,
        className: 'custom-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
}

// Load all layers with Promise.all for proper synchronization
const trackPromise = fetch('data/track.geojson')
    .then(response => {
        if (!response.ok) throw new Error('Failed to load track.geojson');
        return response.json();
    })
    .then(data => {
        trackLayer = L.geoJSON(data, {
            style: {
                color: '#3388ff',
                weight: 3,
                opacity: 0.8
            }
        });
        // Add to map and rebuild layer control
        trackLayer.addTo(map);
        rebuildLayerControl();
        return trackLayer;
    })
    .catch(error => {
        console.error('Error loading track:', error);
        alert('Error loading track. Please check the console for details.');
        return null;
    });

// Load interest points
const pointsPromise = fetch('data/points.geojson')
    .then(response => {
        if (!response.ok) throw new Error('Failed to load points.geojson');
        return response.json();
    })
    .then(data => {
        pointsLayer = L.geoJSON(data, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng, {
                    icon: getPointIcon(feature.properties)
                });
            },
            onEachFeature: function(feature, layer) {
                if (feature.properties) {
                    layer.bindPopup(createPopupContent(feature.properties), {
                        maxWidth: 400
                    });
                }
            }
        });
        // Add to map and rebuild layer control
        pointsLayer.addTo(map);
        rebuildLayerControl();
        return pointsLayer;
    })
    .catch(error => {
        console.error('Error loading points:', error);
        alert('Error loading points. Please check the console for details.');
        return null;
    });

// Function to get accommodation icon
function getAccommodationIcon(accommodationType) {
    const icons = {
        'tent': '⛺',
        'glamping': '🏕️',
        'hotel': '🏨',
        'guesthouse': '🏠'
    };
    return icons[accommodationType] || '📍';
}

// Function to get accommodation color
function getAccommodationColor(accommodationType) {
    const colors = {
        'tent': '#27ae60',      // green
        'glamping': '#e67e22',  // orange
        'hotel': '#3498db',     // blue
        'guesthouse': '#9b59b6' // purple
    };
    return colors[accommodationType] || '#e74c3c'; // default red
}

// Load actual position (daily progress markers)
let lastPositionCoords = null;
const positionMarkers = {}; // Store markers by coordinates for popup access

const positionPromise = fetch('data/actual_position.geojson')
    .then(response => {
        if (!response.ok) throw new Error('Failed to load actual_position.geojson');
        return response.json();
    })
    .then(data => {
        const validFeatures = data.features.filter(f => f.geometry && f.geometry.coordinates);

        // Find the last position (highest id number)
        if (validFeatures.length > 0) {
            const sortedFeatures = validFeatures.sort((a, b) => {
                const idA = a.properties.id || 0;
                const idB = b.properties.id || 0;
                return idB - idA;
            });
            const lastFeature = sortedFeatures[0];
            lastPositionCoords = lastFeature.geometry.coordinates;
        }

        positionLayer = L.geoJSON({ type: 'FeatureCollection', features: validFeatures }, {
            pointToLayer: function(feature, latlng) {
                const accommodationType = feature.properties.accommodation_type || 'tent';
                const icon = getAccommodationIcon(accommodationType);

                const marker = L.marker(latlng, {
                    icon: L.divIcon({
                        html: `<div style="font-size: 24px;">${icon}</div>`,
                        className: 'custom-marker',
                        iconSize: [30, 30],
                        iconAnchor: [15, 15]
                    })
                });

                // Store marker by coordinates for later access
                const coordKey = `${feature.geometry.coordinates[0]},${feature.geometry.coordinates[1]}`;
                positionMarkers[coordKey] = marker;

                return marker;
            },
            onEachFeature: function(feature, layer) {
                if (feature.properties) {
                    const props = feature.properties;
                    const accommodationType = props.accommodation_type || 'tent';
                    const color = getAccommodationColor(accommodationType);
                    const icon = getAccommodationIcon(accommodationType);

                    // Get current language
                    const lang = localStorage.getItem('preferred-language') || 'en';
                    const t = translations[lang];

                    // Build popup content
                    const dayTitle = props.day ? `${t['day']} ${props.day}` : t['popup-daily-position'];
                    let content = `<div class="popup-title" style="color: ${color};">${icon} ${dayTitle}</div>`;

                    if (props.date) {
                        content += `<div class="popup-info"><strong>${t['popup-date']}</strong> ${props.date}</div>`;
                    }

                    if (props.location) {
                        content += `<div class="popup-info"><strong>${t['popup-location']}</strong> ${props.location}</div>`;
                    }

                    // Display distance if available
                    if (props.distance_km && props.distance_km > 0) {
                        content += `<div class="popup-info"><strong>${t['distance']}</strong> ${props.distance_km} ${t['unit-km']}</div>`;
                    }

                    // Display elevation gain if available
                    if (props.elevation_gain && props.elevation_gain > 0) {
                        content += `<div class="popup-info"><strong>${t['elevation-gain']}</strong> ${props.elevation_gain} ${t['unit-m']}</div>`;
                    }

                    const accommodationLabel = t[`accom-${accommodationType}`] || accommodationType;
                    content += `<div class="popup-info"><strong>${t['popup-accommodation']}</strong> ${accommodationLabel}</div>`;

                    if (props.notes) {
                        content += `<div class="popup-description">${props.notes}</div>`;
                    }

                    // Media carousel (YouTube video + photos)
                    if (props.youtube_url || (props.photos && Array.isArray(props.photos) && props.photos.length > 0)) {
                        content += createMediaCarousel(props.youtube_url, props.photos);
                    }

                    layer.bindPopup(content, {
                        maxWidth: 400
                    });
                }
            }
        });
        // Add to map and rebuild layer control
        positionLayer.addTo(map);
        rebuildLayerControl();

        // Populate daily positions list
        populateDailyPositionsList(validFeatures);

        return positionLayer;
    })
    .catch(error => {
        console.error('Error loading actual position:', error);
        return null;
    });

// Wait for all layers to load, then zoom to last actual position
Promise.all([trackPromise, pointsPromise, positionPromise]).then(layers => {
    const validLayers = layers.filter(layer => layer !== null);

    if (validLayers.length > 0) {
        try {
            // If we have a last position, zoom to it
            if (lastPositionCoords && lastPositionCoords.length >= 2) {
                // GeoJSON coordinates are [longitude, latitude], Leaflet uses [latitude, longitude]
                map.setView([lastPositionCoords[1], lastPositionCoords[0]], 13);
            } else {
                // Fallback: fit bounds to show everything
                let combinedBounds = null;

                validLayers.forEach(layer => {
                    if (layer && layer.getBounds) {
                        const layerBounds = layer.getBounds();
                        if (combinedBounds) {
                            combinedBounds.extend(layerBounds);
                        } else {
                            combinedBounds = layerBounds;
                        }
                    }
                });

                if (combinedBounds) {
                    map.fitBounds(combinedBounds, { padding: [50, 50] });
                }
            }
        } catch (e) {
            console.error('Could not set map view:', e);
        }
    }
});

// Photo carousel navigation functions
function changePhoto(carouselId, direction) {
    const carousel = document.getElementById(carouselId);
    const images = carousel.querySelectorAll('.carousel-image');
    const dots = carousel.querySelectorAll('.dot');

    let currentIndex = Array.from(images).findIndex(img => img.classList.contains('active'));

    images[currentIndex].classList.remove('active');
    dots[currentIndex].classList.remove('active');

    currentIndex = (currentIndex + direction + images.length) % images.length;

    images[currentIndex].classList.add('active');
    dots[currentIndex].classList.add('active');
}

function showPhoto(carouselId, index) {
    const carousel = document.getElementById(carouselId);
    const images = carousel.querySelectorAll('.carousel-image');
    const dots = carousel.querySelectorAll('.dot');

    images.forEach(img => img.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    images[index].classList.add('active');
    dots[index].classList.add('active');
}

// Media carousel navigation functions (for videos + photos)
function changeMedia(carouselId, direction) {
    const carousel = document.getElementById(carouselId);
    const items = carousel.querySelectorAll('.carousel-item');
    const dots = carousel.querySelectorAll('.dot');

    let currentIndex = Array.from(items).findIndex(item => item.classList.contains('active'));

    items[currentIndex].classList.remove('active');
    dots[currentIndex].classList.remove('active');

    currentIndex = (currentIndex + direction + items.length) % items.length;

    items[currentIndex].classList.add('active');
    dots[currentIndex].classList.add('active');
}

function showMedia(carouselId, index) {
    const carousel = document.getElementById(carouselId);
    const items = carousel.querySelectorAll('.carousel-item');
    const dots = carousel.querySelectorAll('.dot');

    items.forEach(item => item.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    items[index].classList.add('active');
    dots[index].classList.add('active');
}

// Toggle legend visibility
function toggleLegend() {
    const legend = document.querySelector('.map-legend');
    const button = document.querySelector('.legend-btn');

    legend.classList.toggle('collapsed');

    if (button) {
        if (legend.classList.contains('collapsed')) {
            button.classList.remove('active');
        } else {
            button.classList.add('active');
        }
    }
}

// Zoom to last actual position
function goToLastPosition() {
    if (lastPositionCoords && lastPositionCoords.length >= 2) {
        // GeoJSON coordinates are [longitude, latitude], Leaflet uses [latitude, longitude]
        map.setView([lastPositionCoords[1], lastPositionCoords[0]], 13, {
            animate: true,
            duration: 1
        });
    }
}

// Populate daily positions list
function populateDailyPositionsList(features) {
    const listContainer = document.getElementById('positionsList');
    if (!listContainer) return;

    // Get current language
    const lang = localStorage.getItem('preferred-language') || 'en';
    const t = translations[lang];

    // Sort by id
    const sortedFeatures = features.sort((a, b) => {
        return (a.properties.id || 0) - (b.properties.id || 0);
    });

    listContainer.innerHTML = '';

    sortedFeatures.forEach(feature => {
        const props = feature.properties;
        const coords = feature.geometry.coordinates;

        const card = document.createElement('div');
        card.className = 'position-card';
        card.setAttribute('data-coords', JSON.stringify(coords));

        const icon = getAccommodationIcon(props.accommodation_type || 'tent');

        let html = `
            <div class="position-day">${props.day ? `${t['day']} ${props.day}` : 'Day'}</div>
            <div class="position-date">${props.date || ''}</div>
        `;

        if (props.location) {
            html += `<div class="position-location">📍 ${props.location} ${icon}</div>`;
        }

        // Distance and elevation on same line
        if ((props.distance_km && props.distance_km > 0) || (props.elevation_gain && props.elevation_gain > 0)) {
            html += `<div class="position-stats">`;
            if (props.distance_km && props.distance_km > 0) {
                html += `🥾 ${props.distance_km} ${t['unit-km']}`;
            }
            if (props.elevation_gain && props.elevation_gain > 0) {
                if (props.distance_km && props.distance_km > 0) html += ` • `;
                html += `⛰️ ${props.elevation_gain} ${t['unit-m']}`;
            }
            html += `</div>`;
        }

        card.innerHTML = html;

        card.addEventListener('click', function() {
            zoomToPosition(coords, card);
        });

        listContainer.appendChild(card);
    });

    // Scroll to show the last (most recent) position by default
    setTimeout(() => {
        listContainer.scrollLeft = listContainer.scrollWidth;
    }, 100);
}

// Zoom to a specific position and open popup
function zoomToPosition(coords, card) {
    if (coords && coords.length >= 2) {
        // GeoJSON coordinates are [longitude, latitude], Leaflet uses [latitude, longitude]
        map.setView([coords[1], coords[0]], 14, {
            animate: true,
            duration: 1
        });

        // Highlight active card
        document.querySelectorAll('.position-card').forEach(c => c.classList.remove('active'));
        if (card) {
            card.classList.add('active');
        }

        // Open the marker's popup
        const coordKey = `${coords[0]},${coords[1]}`;
        const marker = positionMarkers[coordKey];
        if (marker) {
            setTimeout(() => {
                marker.openPopup();
            }, 1000); // Wait for zoom animation to complete
        }
    }
}

// Toggle daily positions panel
function togglePanel() {
    const panel = document.querySelector('.daily-positions-panel');
    const button = document.querySelector('.panel-toggle');
    const legend = document.querySelector('.map-legend');

    panel.classList.toggle('collapsed');
    button.textContent = panel.classList.contains('collapsed') ? '+' : '−';

    // Adjust legend position
    if (panel.classList.contains('collapsed')) {
        legend.classList.add('panel-collapsed');
    } else {
        legend.classList.remove('panel-collapsed');
    }
}

// Remove card highlight when popup closes
map.on('popupclose', function() {
    document.querySelectorAll('.position-card').forEach(c => c.classList.remove('active'));
});

// Collapse legend by default
window.addEventListener('load', function() {
    const legend = document.querySelector('.map-legend');
    const button = document.querySelector('.legend-toggle');
    legend.classList.add('collapsed');
    button.textContent = '+';
});
