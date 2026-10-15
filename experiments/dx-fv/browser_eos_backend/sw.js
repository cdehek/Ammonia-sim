const CACHE='ammonia-b1-20261015-v2';
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const manifest=await (await fetch('./offline-manifest.json',{cache:'no-store'})).json();
 const urls=[...new Set(['./','./index.html','./offline-manifest.json',...Object.keys(manifest)].map(path=>new URL(path,self.location.href).href))];
 const cache=await caches.open(CACHE);await cache.addAll(urls);await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>event.respondWith((async()=>{
 const found=await caches.match(event.request);if(found)return found;return fetch(event.request);
})()));
