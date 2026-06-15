// Initialize the map centered on the Caucasus region
const map = L.map('map').setView([42.8, 44.0], 8);

// Add OpenStreetMap tile layer (free and open source)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

// Alternative tile layers (uncomment to use):
// Topographic map (better for hiking):
// L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
//     attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap',
//     maxZoom: 17
// }).addTo(map);

// Function to create popup content
function createPopupContent(properties) {
    let content = `<div class="popup-title">${properties.nom || 'Point of Interest'}</div>`;

    if (properties.description) {
        content += `<div class="popup-description">${properties.description}</div>`;
    }

    if (properties.col3) {
        content += `<div class="popup-info"><strong>Info:</strong> ${properties.col3}</div>`;
    }

    // YouTube video embed (if youtube_url property exists)
    if (properties.youtube_url) {
        // Extract video ID from various YouTube URL formats
        const videoId = extractYouTubeID(properties.youtube_url);
        if (videoId) {
            content += `<div class="popup-youtube">
                <iframe src="https://www.youtube.com/embed/${videoId}"
                        allowfullscreen></iframe>
            </div>`;
        }
    }

    // Photos (if photos property exists - array of photo filenames)
    if (properties.photos && Array.isArray(properties.photos) && properties.photos.length > 0) {
        content += createPhotoCarousel(properties.photos);
    }

    // Additional notes (if notes property exists)
    if (properties.notes) {
        content += `<div class="popup-info"><strong>Notes:</strong> ${properties.notes}</div>`;
    }

    return content;
}

// Create photo carousel HTML
function createPhotoCarousel(photos) {
    if (photos.length === 1) {
        return `<div class="popup-photos">
            <img src="assets/photos/${photos[0]}" alt="Photo" onclick="window.open(this.src, '_blank')">
        </div>`;
    }

    const carouselId = 'carousel-' + Math.random().toString(36).substr(2, 9);
    let html = `<div class="photo-carousel" id="${carouselId}">
        <div class="carousel-container">`;

    photos.forEach((photo, index) => {
        html += `<img src="assets/photos/${photo}" alt="Photo ${index + 1}"
                     class="carousel-image ${index === 0 ? 'active' : ''}"
                     onclick="window.open(this.src, '_blank')">`;
    });

    html += `</div>
        <button class="carousel-btn prev" onclick="changePhoto('${carouselId}', -1)">❮</button>
        <button class="carousel-btn next" onclick="changePhoto('${carouselId}', 1)">❯</button>
        <div class="carousel-dots">`;

    photos.forEach((_, index) => {
        html += `<span class="dot ${index === 0 ? 'active' : ''}" onclick="showPhoto('${carouselId}', ${index})"></span>`;
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
        const trackLayer = L.geoJSON(data, {
            style: {
                color: '#3388ff',
                weight: 3,
                opacity: 0.8
            }
        }).addTo(map);
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
        const pointsLayer = L.geoJSON(data, {
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
        }).addTo(map);
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
const positionPromise = fetch('data/actual_position.geojson')
    .then(response => {
        if (!response.ok) throw new Error('Failed to load actual_position.geojson');
        return response.json();
    })
    .then(data => {
        const validFeatures = data.features.filter(f => f.geometry && f.geometry.coordinates);

        const positionLayer = L.geoJSON({ type: 'FeatureCollection', features: validFeatures }, {
            pointToLayer: function(feature, latlng) {
                const accommodationType = feature.properties.accommodation_type || 'tent';
                const icon = getAccommodationIcon(accommodationType);

                return L.marker(latlng, {
                    icon: L.divIcon({
                        html: `<div style="font-size: 24px;">${icon}</div>`,
                        className: 'custom-marker',
                        iconSize: [30, 30],
                        iconAnchor: [15, 15]
                    })
                });
            },
            onEachFeature: function(feature, layer) {
                if (feature.properties) {
                    const props = feature.properties;
                    const accommodationType = props.accommodation_type || 'tent';
                    const color = getAccommodationColor(accommodationType);
                    const icon = getAccommodationIcon(accommodationType);

                    // Build popup content
                    let content = `<div class="popup-title" style="color: ${color};">${icon} ${props.day || 'Daily Position'}</div>`;

                    if (props.date) {
                        content += `<div class="popup-info"><strong>Date:</strong> ${props.date}</div>`;
                    }

                    const accommodationLabels = {
                        'tent': 'Tent Camping',
                        'glamping': 'Glamping',
                        'hotel': 'Hotel',
                        'guesthouse': 'Guest House'
                    };
                    content += `<div class="popup-info"><strong>Accommodation:</strong> ${accommodationLabels[accommodationType] || accommodationType}</div>`;

                    if (props.notes) {
                        content += `<div class="popup-description">${props.notes}</div>`;
                    }

                    if (props.youtube_url) {
                        const videoId = extractYouTubeID(props.youtube_url);
                        if (videoId) {
                            content += `<div class="popup-youtube">
                                <iframe src="https://www.youtube.com/embed/${videoId}"
                                        allowfullscreen></iframe>
                            </div>`;
                        }
                        content += `<div class="popup-info"><strong>YouTube:</strong> <a href="${props.youtube_url}" target="_blank">Watch on YouTube</a></div>`;
                    }

                    if (props.photos && Array.isArray(props.photos) && props.photos.length > 0) {
                        content += createPhotoCarousel(props.photos);
                    }

                    layer.bindPopup(content, {
                        maxWidth: 400
                    });
                }
            }
        }).addTo(map);
        return positionLayer;
    })
    .catch(error => {
        console.error('Error loading actual position:', error);
        return null;
    });

// Wait for all layers to load, then fit map bounds to show everything
Promise.all([trackPromise, pointsPromise, positionPromise]).then(layers => {
    const validLayers = layers.filter(layer => layer !== null);

    if (validLayers.length > 0) {
        try {
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
        } catch (e) {
            console.error('Could not fit bounds:', e);
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
