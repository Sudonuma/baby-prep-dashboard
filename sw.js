// Minimal service worker: cache the static shell (data, icons, theme css) and
// serve pages network-first so updates arrive while offline still works.
const CACHE = "baby-prep-local-v1";
const SHELL = [
  "./",
  "./static/app-data.js",
  "./static/themes.css",
  "./static/icons/icon-192.png",
  "./static/icons/icon-512.png",
  "./static/icons/icon-maskable-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/static/")) {
    // cache-first for the shell
    event.respondWith(
      caches.match(event.request).then((hit) => hit || fetch(event.request).then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((c) => c.put(event.request, copy));
        return resp;
      }))
    );
  } else {
    // pages: network, falling back to cache when offline
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request).then((hit) => hit || Response.error()))
    );
  }
});
