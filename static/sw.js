// 듀온 PWA 서비스 워커
const CACHE = 'duon-v2';
const SHELL = [
  '/static/style.css',
  '/static/logo.png',
  '/static/favicon.svg',
  '/static/icon-192.png',
  '/static/offline.html',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // 페이지 이동: 네트워크 우선(최신 내용), 오프라인이면 캐시/오프라인 안내
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).catch(() =>
        caches.match(req).then((r) => r || caches.match('/static/offline.html'))
      )
    );
    return;
  }

  // 정적 리소스: stale-while-revalidate (빠르게 캐시 제공 + 백그라운드 최신화)
  e.respondWith(
    caches.open(CACHE).then((cache) =>
      cache.match(req).then((cached) => {
        const network = fetch(req).then((res) => {
          if (res && res.status === 200 && res.type === 'basic') {
            cache.put(req, res.clone());
          }
          return res;
        }).catch(() => cached);
        return cached || network;
      })
    )
  );
});
