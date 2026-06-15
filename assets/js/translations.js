// Translations for the Caucasian Trail website
const translations = {
    en: {
        // Index page
        'site-title': 'Caucasian Trail',
        'site-subtitle': 'Derbent to Sochi | 1000+ km Solo Hiking Adventure',
        'about-title': 'About This Journey',
        'about-text': 'Follow Vladimir Piskunov\'s epic solo hike across the Caucasus Mountains. Starting from Derbent on the Caspian Sea, traversing mountain passes up to 3692m, and finishing in Sochi on the Black Sea coast. This is a real-time documentation of an ongoing adventure.',
        'view-map-btn': '🗺️ View Interactive Map',
        'trail-info-title': 'Journey Details',
        'trail-info-1': '📍 Route: Derbent (Dagestan) → Sochi (Krasnodar)',
        'trail-info-2': '🥾 Distance: 1000+ kilometers on foot',
        'trail-info-3': '⛰️ Altitude: Passes up to 3692m elevation',
        'trail-info-4': '🗓️ Started: June 2026 | Status: In Progress',
        'follow-title': 'Follow Vladimir\'s Journey',
        'youtube-btn': '📺 @Hiking_is_cool',
        'instagram-btn': '📷 @voven4egg',
        'map-features-title': 'What You\'ll Find on the Map',
        'feature-track-title': '🥾 Hiking Track',
        'feature-track-desc': 'Complete GPS track of the entire route',
        'feature-points-title': '📌 Interest Points',
        'feature-points-desc': 'Mountain passes, river crossings, checkpoints, and danger zones',
        'feature-photos-title': '📸 Photos',
        'feature-photos-desc': 'Visual documentation of the journey',
        'feature-notes-title': 'ℹ️ Notes & Tips',
        'feature-notes-desc': 'Practical information and safety warnings',
        'footer-text': 'Vladimir Piskunov\'s Caucasian Trail | June 2026',

        // Map page
        'back-link': '← Back to Home',
        'map-title': 'Interactive Trail Map',
        'legend-title': 'Legend',
        'legend-track': 'Hiking Track',
        'legend-accommodations': 'Daily Accommodations:',
        'legend-tent': 'Tent',
        'legend-glamping': 'Glamping',
        'legend-guesthouse': 'Guest House',
        'legend-hotel': 'Hotel',
        'legend-poi': 'Points of Interest:',
        'legend-passes': 'Passes',
        'legend-rivers': 'River Crossings',
        'legend-danger': 'Danger Zones',
        'legend-checkpoints': 'Checkpoints',

        // Popup labels
        'popup-date': 'Date:',
        'popup-accommodation': 'Accommodation:',
        'popup-daily-position': 'Daily Position',

        // Map controls
        'go-to-last-position': 'Go to Last Position',

        // Accommodation types
        'accom-tent': 'Tent Camping',
        'accom-glamping': 'Glamping',
        'accom-hotel': 'Hotel',
        'accom-guesthouse': 'Guest House'
    },
    ru: {
        // Index page
        'site-title': 'Кавказская Тропа',
        'site-subtitle': 'Дербент — Сочи | 1000+ км Пешее Путешествие',
        'about-title': 'О Путешествии',
        'about-text': 'Следите за эпическим пешим походом Владимира Пискунова через Кавказские горы. Начало из Дербента на Каспийском море, через горные перевалы до 3692м, финиш в Сочи на Чёрном море. Это документация продолжающегося приключения в реальном времени.',
        'view-map-btn': '🗺️ Открыть Интерактивную Карту',
        'trail-info-title': 'Детали Путешествия',
        'trail-info-1': '📍 Маршрут: Дербент (Дагестан) → Сочи (Краснодар)',
        'trail-info-2': '🥾 Расстояние: 1000+ километров пешком',
        'trail-info-3': '⛰️ Высота: Перевалы до 3692м',
        'trail-info-4': '🗓️ Старт: июнь 2026 | Статус: В Процессе',
        'follow-title': 'Следите за Путешествием Владимира',
        'youtube-btn': '📺 @Hiking_is_cool',
        'instagram-btn': '📷 @voven4egg',
        'map-features-title': 'Что Вы Найдёте на Карте',
        'feature-track-title': '🥾 Пешеходный Маршрут',
        'feature-track-desc': 'Полный GPS трек всего маршрута',
        'feature-points-title': '📌 Точки Интереса',
        'feature-points-desc': 'Горные перевалы, переправы через реки, контрольные точки и опасные зоны',
        'feature-photos-title': '📸 Фотографии',
        'feature-photos-desc': 'Визуальная документация путешествия',
        'feature-notes-title': 'ℹ️ Заметки и Советы',
        'feature-notes-desc': 'Практическая информация и предупреждения о безопасности',
        'footer-text': 'Кавказская Тропа Владимира Пискунова | Июнь 2026',

        // Map page
        'back-link': '← Назад на Главную',
        'map-title': 'Интерактивная Карта Маршрута',
        'legend-title': 'Легенда',
        'legend-track': 'Пешеходный Маршрут',
        'legend-accommodations': 'Ежедневное Размещение:',
        'legend-tent': 'Палатка',
        'legend-glamping': 'Глемпинг',
        'legend-guesthouse': 'Гостевой Дом',
        'legend-hotel': 'Отель',
        'legend-poi': 'Точки Интереса:',
        'legend-passes': 'Перевалы',
        'legend-rivers': 'Переправы',
        'legend-danger': 'Опасные Зоны',
        'legend-checkpoints': 'Контрольные Точки',

        // Popup labels
        'popup-date': 'Дата:',
        'popup-accommodation': 'Размещение:',
        'popup-daily-position': 'Дневная Позиция',

        // Map controls
        'go-to-last-position': 'Перейти к Последней Позиции',

        // Accommodation types
        'accom-tent': 'Палатка',
        'accom-glamping': 'Глемпинг',
        'accom-hotel': 'Отель',
        'accom-guesthouse': 'Гостевой Дом'
    }
};

// Language switching functionality
function setLanguage(lang) {
    // Store preference
    localStorage.setItem('preferred-language', lang);

    // Update document language attribute
    document.documentElement.lang = lang;

    // Update all translatable elements
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            // Handle different element types
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });

    // Update active language button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });

    // Update go to last position button title
    const goToBtn = document.querySelector('.go-to-last-position-btn');
    if (goToBtn && translations[lang]['go-to-last-position']) {
        goToBtn.title = translations[lang]['go-to-last-position'];
        goToBtn.setAttribute('aria-label', translations[lang]['go-to-last-position']);
    }

    // Close any open popups so they can be reopened with new language
    if (typeof map !== 'undefined') {
        map.closePopup();
    }
}

// Initialize language on page load
function initLanguage() {
    const savedLang = localStorage.getItem('preferred-language') || 'en';
    setLanguage(savedLang);
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLanguage);
} else {
    initLanguage();
}
