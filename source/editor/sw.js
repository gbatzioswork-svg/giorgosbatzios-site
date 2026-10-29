// GB EDITOR instant preview: serves the pages the editor just rendered (in this browser) under /preview/.
// Pages use relative links, so /preview/theater/ links to /preview/assets/… — those come from the real site,
// except new pictures that are not saved yet (kept in the same cache by the editor).
const CACHE = "gb-preview";
const BASE = new URL(self.registration.scope).pathname.replace(/\/$/, ""); // "/preview" (or "/editor/preview")

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin || !url.pathname.startsWith(BASE + "/") || e.request.method !== "GET") return;
  e.respondWith(serve(url));
});

async function serve(url) {
  const cache = await caches.open(CACHE);
  let p = url.pathname.slice(BASE.length);
  if (p.startsWith("/assets/")) {
    const mine = await cache.match(BASE + p);
    return mine || fetch(p + url.search);
  }
  if (!p.endsWith("/") && !/\.[a-z0-9]+$/i.test(p)) return Response.redirect(url.pathname + "/" + url.search, 302);
  if (p.endsWith("/")) p += "index.html";
  const hit = await cache.match(BASE + p);
  if (hit) return hit;
  const nf = await cache.match(BASE + "/404.html");
  if (nf) return new Response(nf.body, { status: 404, headers: nf.headers });
  return new Response("<!doctype html><meta charset=utf-8><body style='background:#0d0d0e;color:#f3f3f4;font:16px system-ui;padding:40px'>Press Preview in GB EDITOR again.", { status: 404, headers: { "Content-Type": "text/html; charset=utf-8" } });
}
