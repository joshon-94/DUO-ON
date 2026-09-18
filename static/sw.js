// 듀온 PWA 서비스 워커
const CACHE = 'duon-v1';
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

  // 정적 리소스: 캐시 우선
  e.respondWith(
    caches.match(req).then((cached) =>
      cached ||
      fetch(req).then((res) => {
        if (res && res.status === 200 && res.type === 'basic') {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => cached)
    )
  );
});
