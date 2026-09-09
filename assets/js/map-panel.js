// ---------------------------------------------------------------------------
// map-panel.js  –  Overnight-stops panel, zoom-to-position, mouse scrolling
// ---------------------------------------------------------------------------

// ── Panel population ────────────────────────────────────────────────────────

function populateDailyPositionsList(features) {
    const listContainer = document.getElementById('positionsList');
    if (!listContainer) return;

    const lang = localStorage.getItem('preferred-language') || 'en';
    const t    = translations[lang];

    const sorted = features.slice().sort((a, b) =>
        (a.properties.id || 0) - (b.properties.id || 0)
    );

    listContainer.innerHTML = '';

    sorted.forEach(feature => {
        const props  = feature.properties;
        const coords = feature.geometry.coordinates;

        const card = document.createElement('div');
        card.className = 'position-card';
        card.setAttribute('data-coords', JSON.stringify(coords));

        const icon = getAccommodationIcon(props.accommodation_type || 'tent');

        let html = `
            <div class="position-day">${props.day ? `${t['day']} ${props.day}` : t['day']}</div>
            <div class="position-date">${props.date || ''}</div>
        `;

        if (props.location) {
            html += `<div class="position-location">📍 ${props.location} ${icon}</div>`;
        }

        if ((props.distance_km && props.distance_km > 0) ||
            (props.elevation_gain && props.elevation_gain > 0)) {
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
        card.addEventListener('click', function() { zoomToPosition(coords, card); });
        listContainer.appendChild(card);
    });

    // Scroll to the most recent entry by default
    setTimeout(() => { listContainer.scrollLeft = listContainer.scrollWidth; }, 100);
}

// ── Update popups + panel on language change ────────────────────────────────

function updatePositionPopups() {
    if (!positionData || !positionLayer) return;
    positionLayer.eachLayer(function(layer) {
        if (layer.feature && layer.feature.properties) {
            layer.setPopupContent(buildPositionPopupContent(layer.feature.properties));
        }
    });
    populateDailyPositionsList(positionData);
}

// ── Zoom to a position card ─────────────────────────────────────────────────

function zoomToPosition(coords, card) {
    if (!coords || coords.length < 2) return;

    map.setView([coords[1], coords[0]], 14, { animate: true, duration: 1 });

    document.querySelectorAll('.position-card').forEach(c => c.classList.remove('active'));
    if (card) card.classList.add('active');

    const marker = positionMarkers[`${coords[0]},${coords[1]}`];
    if (marker) setTimeout(() => { marker.openPopup(); }, 1000);
}

// ── Init: collapse legend + enable mouse scrolling on panel ─────────────────

window.addEventListener('load', function() {
    const legend = document.querySelector('.map-legend');
    if (legend) legend.classList.add('collapsed');
});

window.addEventListener('load', function() {
    const list = document.getElementById('positionsList');
    if (!list) return;

    // Click-and-drag to scroll
    let isDragging = false;
    let startX = 0;
    let scrollStart = 0;

    list.addEventListener('mousedown', function(e) {
        isDragging  = true;
        startX      = e.clientX;
        scrollStart = list.scrollLeft;
        list.style.cursor     = 'grabbing';
        list.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        list.scrollLeft = scrollStart - (e.clientX - startX);
    });

    document.addEventListener('mouseup', function() {
        if (!isDragging) return;
        isDragging            = false;
        list.style.cursor     = 'grab';
        list.style.userSelect = '';
    });

    // Vertical mouse wheel → horizontal scroll
    list.addEventListener('wheel', function(e) {
        if (e.deltaY === 0) return;
        e.preventDefault();
        list.scrollLeft += e.deltaY;
    }, { passive: false });
});
