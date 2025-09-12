const CACHE = "malume-v1";
const CORE = [
  "/menu.html",
  "/assets/css/menu.css",
  "/assets/js/menu.js", 
  "/assets/img/poster.jpg"
];

// Install event - cache core assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(CORE))
      .catch(error => console.error('Cache installation failed:', error))
  );
});

// Fetch event - handle requests
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  
  // Handle asset requests (CSS, JS, images)
  if (url.pathname.startsWith("/assets/") || url.pathname.endsWith(".jpg")) {
    event.respondWith(handleAssetRequest(event));
    return;
  }

  // Handle API requests
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(handleApiRequest(event));
    return;
  }
});

// Asset request handler
async function handleAssetRequest(event) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(event.request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Fetch from network and cache
    const networkResponse = await fetch(event.request);
    const cache = await caches.open(CACHE);
    cache.put(event.request, networkResponse.clone());
    return networkResponse;
    
  } catch (error) {
    console.error('Asset fetch failed:', error);
    return new Response('Offline', { status: 503 });
  }
}

// API request handler
async function handleApiRequest(event) {
  const cache = await caches.open(CACHE);
  
  try {
    // Try network first for API calls
    const networkResponse = await fetch(event.request);
    
    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(event.request, networkResponse.clone());
    }
    
    return networkResponse;
    
  } catch (error) {
    console.error('API fetch failed:', error);
    
    // Fall back to cache if available
    const cachedResponse = await cache.match(event.request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    return new Response(
      JSON.stringify({ error: "offline" }),
      {
        status: 503,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}
