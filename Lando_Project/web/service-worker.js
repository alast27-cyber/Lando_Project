/*
  Service Worker for offline-ready IAI runtime.
  Responsibilities:
  - Cache app shell
  - Keep model metadata in OPFS via message commands
  - Run background retraining/synchronization jobs
*/

const CACHE_NAME = 'lando-iai-shell-v1';
const APP_SHELL = [
  '/',
  '/index.html',
  '/Lando_Project/web/main.js',
  '/Lando_Project/web/iai-kernel.js',
  '/Lando_Project/web/opfs-store.js',
  '/Lando_Project/web/data-ingestion-worker.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});

self.addEventListener('message', async (event) => {
  const { type, payload } = event.data || {};

  if (type === 'SYNC_INSTINCT_TENSORS') {
    // Placeholder for background tensor merge/reduction work.
    const result = {
      ok: true,
      updatedAt: Date.now(),
      mergedVectors: payload?.count || 0,
    };
    event.source?.postMessage({ type: 'SYNC_RESULT', payload: result });
    return;
  }

  if (type === 'BACKGROUND_TRAINING_TICK') {
    // Lightweight async training tick.
    // Keep short work units to avoid long SW blocking.
    const stats = {
      epoch: payload?.epoch || 0,
      lossApprox: payload?.lossApprox || 0.0,
      ts: Date.now(),
    };
    event.source?.postMessage({ type: 'TRAINING_PROGRESS', payload: stats });
  }
});
