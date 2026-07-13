const CACHE_NAME = 'sadat-depot-mobile-v20260713071555';
const SHELL_FILES = ['./index.html', './manifest.json', './icon.svg'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE_NAME).then(function(cache){ return cache.addAll(SHELL_FILES); }));
  self.skipWaiting();
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.filter(function(k){ return k!==CACHE_NAME; }).map(function(k){ return caches.delete(k); }));
    })
  );
  self.clients.claim();
});

// App-shell only: يخدم من الكاش لو النت واقع، غير كده يفضّل الشبكة (بيانات المخزون لازم تكون حية)
self.addEventListener('fetch', function(e){
  if(e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  const isShellFile = SHELL_FILES.some(function(f){ return url.pathname.endsWith(f.replace('./','/')); });
  if(!isShellFile) return; // سيب أي حاجة تانية (خط Tesseract، Supabase) تروح للشبكة عادي
  e.respondWith(
    fetch(e.request).catch(function(){ return caches.match(e.request); })
  );
});
