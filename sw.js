/* Never Get Bored — service worker.
   Bump CACHE whenever the app shell changes so installed copies refresh. */
const CACHE = 'ngb-v14';
const PRECACHE = [
  './', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png',
  './data/books.js', './data/versions.js', './data/KJV.js', './data/chronological.js', './data/audio_kjv.js',
  './data/commentary.js', './data/refined.js', './data/dict.js'
];
/* Files that change often — always try the network first, fall back to cache offline. */
const FRESH = /\/(index\.html|manifest\.webmanifest|data\/(commentary|refined|chronological|dict|books|versions|audio_kjv|audio_kokoro)\.js|data\/commentary\.json)$/;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('message', e => { if (e.data === 'skipWaiting') self.skipWaiting(); });

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  const networkFirst = req.mode === 'navigate' || FRESH.test(url.pathname);
  if (networkFirst) {
    e.respondWith(
      fetch(req).then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req.mode==='navigate'?'./index.html':req, copy)); }
        return res;
      }).catch(() => caches.match(req.mode==='navigate'?'./index.html':req))
    );
    return;
  }
  /* Bible translations, Matthew Henry, audio, icons: rarely change — cache first. */
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    }))
  );
});
