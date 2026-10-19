const CACHE_NAME = 'tohoku-itinerary-v99';
const PRECACHE_URLS = [
  './',
  './index.html',
  './itinerary.html',
  './itinerary_data.json',
  './maps_places.html',
  './calendar_export.html',
  './tohoku_itinerary_full.ics',
  './tohoku_itinerary_essential.ics',
  './tohoku_calendar_google.csv',
  './tohoku_google_maps_places.csv',
  './tohoku_google_maps_all_stops.csv',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  
  const url = new URL(event.request.url);
  
  // For same-origin HTML and JSON, try network first, fallback to cache
  if (url.origin === location.origin) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response.status === 200) {
            const respClone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, respClone));
          }
          return response;
        })
        .catch(() => caches.match(event.request).then(cached => cached || caches.match('./index.html')))
    );
  } else {
    // For external resources (Google fonts, etc.), try cache first, fallback to network
    event.respondWith(
      caches.match(event.request).then(cached => {
        return cached || fetch(event.request).then(response => {
          if (response.status === 200) {
            const respClone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, respClone));
          }
          return response;
        }).catch(() => null);
      })
    );
  }
});
