// Scoped solely to the separately generated research package. No production registration.
const CACHE='ammonia-flash-precision-20261013-v2';
self.addEventListener('install',event=>event.waitUntil((async()=>{const r=await fetch('./manifest.json');if(!r.ok)throw Error('Manifest unavailable');const m=await r.json(),c=await caches.open(CACHE);await c.addAll(['./','./manifest.json',...m.runtimeAssets]);await self.skipWaiting();})()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{if(event.request.method!=='GET'||!event.request.url.startsWith(self.registration.scope))return;event.respondWith((async()=>{const c=await caches.open(CACHE),match=await c.match(event.request);return match||fetch(event.request);})());});
