// This worker's scope is only the isolated research directory, never the app.
const CACHE='ammonia-eos-research-8.0.0-v1';
const ASSETS=['./','./index.html','./eos.mjs','./worker.mjs','./vendor/8.0.0/coolprop.js','./vendor/8.0.0/coolprop.wasm'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{if(event.request.method==='GET'&&event.request.url.startsWith(self.registration.scope))event.respondWith(caches.match(event.request).then(r=>r||fetch(event.request)));});
