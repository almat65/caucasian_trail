// ---------------------------------------------------------------------------
// map-popups.js  –  Popup builders, icon/color helpers, media carousel
// ---------------------------------------------------------------------------

// ── POI popup ───────────────────────────────────────────────────────────────

function createPopupContent(properties) {
    let content = `<div class="popup-title">${properties.nom || 'Point of Interest'}</div>`;
    if (properties.description) {
        content += `<div class="popup-description">${properties.description}</div>`;
    }
    if (properties.col3) {
        content += `<div class="popup-info"><strong>Info:</strong> ${properties.col3}</div>`;
    }
    if (properties.youtube_url ||
        (properties.photos && Array.isArray(properties.photos) && properties.photos.length > 0)) {
        content += createMediaCarousel(properties.youtube_url, properties.photos);
    }
    if (properties.notes) {
        content += `<div class="popup-info"><strong>Notes:</strong> ${properties.notes}</div>`;
    }
    return content;
}

// ── Overnight-stop popup ────────────────────────────────────────────────────

function buildPositionPopupContent(props) {
    const accommodationType = props.accommodation_type || 'tent';
    const color = getAccommodationColor(accommodationType);
    const icon  = getAccommodationIcon(accommodationType);
    const lang  = localStorage.getItem('preferred-language') || 'en';
    const t     = translations[lang];

    const dayTitle = props.day ? `${t['day']} ${props.day}` : t['popup-daily-position'];
    let content = `<div class="popup-title" style="color: ${color};">${icon} ${dayTitle}</div>`;

    if (props.date)
        content += `<div class="popup-info"><strong>${t['popup-date']}</strong> ${props.date}</div>`;
    if (props.location)
        content += `<div class="popup-info"><strong>${t['popup-location']}</strong> ${props.location}</div>`;
    if (props.distance_km && props.distance_km > 0)
        content += `<div class="popup-info"><strong>${t['distance']}</strong> ${props.distance_km} ${t['unit-km']}</div>`;
    if (props.elevation_gain && props.elevation_gain > 0)
        content += `<div class="popup-info"><strong>${t['elevation-gain']}</strong> ${props.elevation_gain} ${t['unit-m']}</div>`;

    const accommodationLabel = t[`accom-${accommodationType}`] || accommodationType;
    content += `<div class="popup-info"><strong>${t['popup-accommodation']}</strong> ${accommodationLabel}</div>`;

    if (props.notes)
        content += `<div class="popup-description">${props.notes}</div>`;
    if (props.youtube_url ||
        (props.photos && Array.isArray(props.photos) && props.photos.length > 0)) {
        content += createMediaCarousel(props.youtube_url, props.photos);
    }
    return content;
}

// ── Media carousel ──────────────────────────────────────────────────────────

function createMediaCarousel(youtubeUrl, photos) {
    const items = [];

    if (youtubeUrl) {
        const videoId = extractYouTubeID(youtubeUrl);
        if (videoId) items.push({ type: 'video', id: videoId });
    }
    if (photos && Array.isArray(photos)) {
        photos.forEach(photo => items.push({ type: 'photo', src: photo }));
    }

    // Single photo
    if (items.length === 1 && items[0].type === 'photo') {
        return `<div class="popup-photos">
            <img src="assets/photos/${items[0].src}" alt="Photo" onclick="window.open(this.src, '_blank')">
        </div>`;
    }
    // Single video
    if (items.length === 1 && items[0].type === 'video') {
        return `<div class="popup-youtube">
            <iframe src="https://www.youtube.com/embed/${items[0].id}" allowfullscreen></iframe>
        </div>`;
    }

    // Multi-item carousel
    const id = 'carousel-' + Math.random().toString(36).substr(2, 9);
    let html = `<div class="photo-carousel" id="${id}"><div class="carousel-container">`;

    items.forEach((item, i) => {
        if (item.type === 'video') {
            html += `<div class="carousel-item ${i === 0 ? 'active' : ''}" data-type="video">
                <iframe src="https://www.youtube.com/embed/${item.id}" allowfullscreen></iframe>
            </div>`;
        } else {
            html += `<img src="assets/photos/${item.src}" alt="Media ${i + 1}"
                         class="carousel-item carousel-image ${i === 0 ? 'active' : ''}"
                         data-type="photo"
                         onclick="window.open(this.src, '_blank')">`;
        }
    });

    html += `</div>
        <button class="carousel-btn prev" onclick="changeMedia('${id}', -1)">❮</button>
        <button class="carousel-btn next" onclick="changeMedia('${id}', 1)">❯</button>
        <div class="carousel-dots">`;
    items.forEach((_, i) => {
        html += `<span class="dot ${i === 0 ? 'active' : ''}" onclick="showMedia('${id}', ${i})"></span>`;
    });
    html += `</div></div>`;
    return html;
}

function extractYouTubeID(url) {
    const match = url.match(/^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/);
    return (match && match[2].length === 11) ? match[2] : null;
}

// ── Icon / colour helpers ───────────────────────────────────────────────────

function getPointIcon(properties) {
    let emoji = '📍';
    if (properties.nom) {
        const name = properties.nom.toLowerCase();
        if (name.includes('перевал'))                                              emoji = '⛰️';
        else if (name.includes('брод'))                                            emoji = '🌊';
        else if (name.includes('опасн'))                                           emoji = '⚠️';
        else if (name.includes('пост') || name.includes('застава') ||
                 name.includes('пропуск'))                                         emoji = '🚧';
    }
    return L.divIcon({
        html: `<div style="font-size: 24px;">${emoji}</div>`,
        className: 'custom-marker',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
}

function getAccommodationIcon(type) {
    return { tent: '⛺', glamping: '🏕️', hotel: '🏨', guesthouse: '🏠' }[type] || '📍';
}

function getAccommodationColor(type) {
    return { tent: '#27ae60', glamping: '#e67e22', hotel: '#3498db', guesthouse: '#9b59b6' }[type]
        || '#e74c3c';
}

// ── Carousel navigation ─────────────────────────────────────────────────────

function changeMedia(carouselId, direction) {
    const carousel = document.getElementById(carouselId);
    const items = carousel.querySelectorAll('.carousel-item');
    const dots  = carousel.querySelectorAll('.dot');
    let idx = Array.from(items).findIndex(el => el.classList.contains('active'));
    items[idx].classList.remove('active');
    dots[idx].classList.remove('active');
    idx = (idx + direction + items.length) % items.length;
    items[idx].classList.add('active');
    dots[idx].classList.add('active');
}

function showMedia(carouselId, index) {
    const carousel = document.getElementById(carouselId);
    carousel.querySelectorAll('.carousel-item').forEach(el => el.classList.remove('active'));
    carousel.querySelectorAll('.dot').forEach(el => el.classList.remove('active'));
    carousel.querySelectorAll('.carousel-item')[index].classList.add('active');
    carousel.querySelectorAll('.dot')[index].classList.add('active');
}

// Legacy aliases (kept for any old inline onclick references)
function changePhoto(carouselId, direction) { changeMedia(carouselId, direction); }
function showPhoto(carouselId, index)        { showMedia(carouselId, index); }
