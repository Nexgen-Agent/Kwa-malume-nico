const CACHE = "malume-v1";
const CORE = [
  "/menu.html",
  "/assets/css/menu.css",
  "/assets/js/menu.js",
  "/assets/img/poster.jpg"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)));
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/assets/") || url.pathname.endsWith(".jpg")) {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(net => {
      caches.open(CACHE).then(c => c.put(e.request, net.clone())); return net;
    })));
    return;
  }

  if (url.pathname.startsWith("/api/")) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const cached = await cache.match(e.request);
      try {
        const net = await fetch(e.request);
        cache.put(e.request, net.clone());
        return net;
      } catch (err) {
        return cached || new Response(JSON.stringify({error:"offline"}), {status:503, headers:{"Content-Type":"application/json"}});
      }
    })());
    return;
  }
});