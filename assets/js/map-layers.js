// ---------------------------------------------------------------------------
// map-layers.js  –  GeoJSON data loading and layer creation
// ---------------------------------------------------------------------------

// ── Planned route ───────────────────────────────────────────────────────────

const trackPromise = fetch('data/track.geojson')
    .then(response => {
        if (!response.ok) throw new Error('Failed to load track.geojson');
        return response.json();
    })
    .then(data => {
        trackLayer = L.geoJSON(data, {
            style: { color: '#3388ff', weight: 3, opacity: 0.8 }
        });
        trackLayer.addTo(map);
        rebuildLayerControl();
        return trackLayer;
    })
    .catch(error => {
        console.error('Error loading track:', error);
        alert('Error loading track. Please check the console for details.');
        return null;
    });

// ── Daily GPS tracks (smartwatch) ──────────────────────────────────────────

async function loadDailyTracks(existingDays) {
    const allTracks = [];

    for (const day of existingDays) {
        const candidates = [
            `data/daily_tracks/day_${day}.geojson`,
            `data/daily_tracks/day_${String(day).padStart(2, '0')}.geojson`
        ];
        for (const filename of candidates) {
            try {
                const response = await fetch(filename);
                if (response.ok) {
                    const data = await response.json();
                    if (data.features && data.features.length > 0) {
                        allTracks.push(...data.features);
                        console.log(`Loaded ${filename}`);
                    }
                    break; // found this day's file — stop trying other formats
                }
            } catch {
                // silently skip missing files
            }
        }
    }

    if (allTracks.length > 0) {
        dailyTracksLayer = L.geoJSON(
            { type: 'FeatureCollection', features: allTracks },
            { style: { color: '#ff6b35', weight: 3, opacity: 0.9 } }
        );
        dailyTracksLayer.addTo(map);
        rebuildLayerControl();
        console.log(`Loaded ${allTracks.length} daily track segment(s)`);
        return dailyTracksLayer;
    }
    return null;
}

// ── Points of interest ──────────────────────────────────────────────────────

const pointsPromise = fetch('data/points.geojson')
    .then(response => {
        if (!response.ok) throw new Error('Failed to load points.geojson');
        return response.json();
    })
    .then(data => {
        pointsLayer = L.geoJSON(data, {
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng, { icon: getPointIcon(feature.properties) });
            },
            onEachFeature: function(feature, layer) {
                if (feature.properties) {
                    layer.bindPopup(createPopupContent(feature.properties), { maxWidth: 400 });
                }
            }
        });
        pointsLayer.addTo(map);
        rebuildLayerControl();
        return pointsLayer;
    })
    .catch(error => {
        console.error('Error loading points:', error);
        alert('Error loading points. Please check the console for details.');
        return null;
    });

// ── Overnight stops (actual position) ──────────────────────────────────────

const positionPromise = fetch('data/actual_position.geojson')
    .then(response => {
        if (!response.ok) throw new Error('Failed to load actual_position.geojson');
        return response.json();
    })
    .then(data => {
        const validFeatures = data.features.filter(f => f.geometry && f.geometry.coordinates);
        positionData = validFeatures;

        // Remember the last (highest-id) position for the "go to" button
        if (validFeatures.length > 0) {
            const sorted = validFeatures.slice().sort(
                (a, b) => (b.properties.id || 0) - (a.properties.id || 0)
            );
            lastPositionCoords = sorted[0].geometry.coordinates;
        }

        positionLayer = L.geoJSON(
            { type: 'FeatureCollection', features: validFeatures },
            {
                pointToLayer: function(feature, latlng) {
                    const type = feature.properties.accommodation_type || 'tent';
                    const marker = L.marker(latlng, {
                        icon: L.divIcon({
                            html: `<div style="font-size: 24px;">${getAccommodationIcon(type)}</div>`,
                            className: 'custom-marker',
                            iconSize: [30, 30],
                            iconAnchor: [15, 15]
                        })
                    });
                    const key = `${feature.geometry.coordinates[0]},${feature.geometry.coordinates[1]}`;
                    positionMarkers[key] = marker;
                    return marker;
                },
                onEachFeature: function(feature, layer) {
                    if (feature.properties) {
                        layer.bindPopup(buildPositionPopupContent(feature.properties), { maxWidth: 400 });
                    }
                }
            }
        );
        positionLayer.addTo(map);
        rebuildLayerControl();
        populateDailyPositionsList(validFeatures);

        // Load daily GPS tracks for every day that has an overnight stop
        const existingDays = validFeatures
            .map(f => f.properties.day)
            .filter(d => d != null)
            .map(d => parseInt(d));
        if (existingDays.length > 0) loadDailyTracks(existingDays);

        return positionLayer;
    })
    .catch(error => {
        console.error('Error loading actual position:', error);
        return null;
    });

// ── Initial map view after all layers load ──────────────────────────────────

Promise.all([trackPromise, pointsPromise, positionPromise]).then(layers => {
    const valid = layers.filter(l => l !== null);
    if (valid.length === 0) return;

    try {
        if (lastPositionCoords && lastPositionCoords.length >= 2) {
            map.setView([lastPositionCoords[1], lastPositionCoords[0]], 13);
        } else {
            let bounds = null;
            valid.forEach(layer => {
                if (layer && layer.getBounds) {
                    const b = layer.getBounds();
                    bounds = bounds ? bounds.extend(b) : b;
                }
            });
            if (bounds) map.fitBounds(bounds, { padding: [50, 50] });
        }
    } catch (e) {
        console.error('Could not set map view:', e);
    }
});
