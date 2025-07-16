// Houston Land Guy - Service Worker for Performance Optimization
const CACHE_NAME = 'houston-land-guy-v1.2';
const STATIC_CACHE = 'houston-land-guy-static-v1.2';
const DYNAMIC_CACHE = 'houston-land-guy-dynamic-v1.2';

// Files to cache immediately (critical resources)
const STATIC_FILES = [
    '/',
    '/index.html',
    '/style.css',
    '/app.js',
    '/favicon.ico',
    '/favicon-32x32.png',
    '/favicon-16x16.png',
    '/apple-touch-icon.png'
];

// Files to cache when accessed (optional resources)
const DYNAMIC_FILES = [
    '/api/health',
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
    'https://customer-6njalxhlz5ulnoaq.cloudflarestream.com/'
];

// Install event - cache static resources
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('Service Worker: Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Service Worker: Static files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker: Failed to cache static files', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Service Worker: Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activated successfully');
                return self.clients.claim();
            })
    );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip Chrome extension requests
    if (url.protocol === 'chrome-extension:') {
        return;
    }
    
    // API requests - Network First strategy
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(
            networkFirstStrategy(request)
        );
        return;
    }
    
    // Analytics and tracking scripts - Network Only
    if (isAnalyticsRequest(url)) {
        event.respondWith(
            networkOnlyStrategy(request)
        );
        return;
    }
    
    // Static assets - Cache First strategy
    if (isStaticAsset(url)) {
        event.respondWith(
            cacheFirstStrategy(request)
        );
        return;
    }
    
    // External resources - Stale While Revalidate
    if (isExternalResource(url)) {
        event.respondWith(
            staleWhileRevalidateStrategy(request)
        );
        return;
    }
    
    // Default - Network First for HTML pages
    event.respondWith(
        networkFirstStrategy(request)
    );
});

// Caching Strategies

// Network First - Try network, fallback to cache
async function networkFirstStrategy(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('Service Worker: Network failed, trying cache:', request.url);
        
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/index.html');
        }
        
        throw error;
    }
}

// Cache First - Try cache, fallback to network
async function cacheFirstStrategy(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('Service Worker: Failed to fetch resource:', request.url, error);
        throw error;
    }
}

// Stale While Revalidate - Return cache immediately, update in background
async function staleWhileRevalidateStrategy(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);
    
    const networkRequest = fetch(request)
        .then((response) => {
            if (response.ok) {
                cache.put(request, response.clone());
            }
            return response;
        })
        .catch((error) => {
            console.log('Service Worker: Background update failed:', request.url);
        });
    
    return cachedResponse || networkRequest;
}

// Network Only - Always use network
async function networkOnlyStrategy(request) {
    return fetch(request);
}

// Utility functions
function isStaticAsset(url) {
    return url.pathname.match(/\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$/);
}

function isExternalResource(url) {
    return url.origin !== self.location.origin && 
           (url.hostname.includes('fonts.googleapis.com') || 
            url.hostname.includes('cloudflarestream.com') ||
            url.hostname.includes('fonts.gstatic.com'));
}

function isAnalyticsRequest(url) {
    return url.hostname.includes('google-analytics.com') ||
           url.hostname.includes('googletagmanager.com') ||
           url.hostname.includes('facebook.com') ||
           url.hostname.includes('hotjar.com') ||
           url.pathname.includes('/analytics/') ||
           url.pathname.includes('/track');
}

// Background sync for lead submissions
self.addEventListener('sync', (event) => {
    if (event.tag === 'lead-submission') {
        event.waitUntil(syncLeadSubmissions());
    }
});

async function syncLeadSubmissions() {
    try {
        const pendingLeads = JSON.parse(localStorage.getItem('pendingLeads') || '[]');
        
        if (pendingLeads.length === 0) {
            return;
        }
        
        console.log('Service Worker: Syncing pending leads:', pendingLeads.length);
        
        for (const lead of pendingLeads) {
            try {
                let endpoint;
                
                switch (lead.type) {
                    case 'property-valuation':
                        endpoint = '/api/property-valuation';
                        break;
                    case 'contact-form':
                        endpoint = '/api/contact';
                        break;
                    default:
                        continue;
                }
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(lead)
                });
                
                if (response.ok) {
                    console.log('Service Worker: Lead synced successfully');
                } else {
                    console.error('Service Worker: Failed to sync lead:', response.status);
                }
            } catch (error) {
                console.error('Service Worker: Error syncing lead:', error);
            }
        }
        
        // Clear pending leads after sync attempt
        localStorage.removeItem('pendingLeads');
        
    } catch (error) {
        console.error('Service Worker: Error in sync process:', error);
    }
}

// Push notifications (future enhancement)
self.addEventListener('push', (event) => {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body || 'You have a new message from Houston Land Guy',
            icon: '/favicon-192x192.png',
            badge: '/favicon-32x32.png',
            actions: [
                {
                    action: 'view',
                    title: 'View Details'
                },
                {
                    action: 'call',
                    title: 'Call (713) 828-3701'
                }
            ],
            data: {
                url: data.url || '/',
                phone: '7138283701'
            }
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title || 'Houston Land Guy', options)
        );
    }
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    if (event.action === 'call') {
        // Open tel: link
        event.waitUntil(
            clients.openWindow(`tel:${event.notification.data.phone}`)
        );
    } else {
        // Open the app
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/')
        );
    }
});

// Performance monitoring
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'GET_CACHE_STATS') {
        getCacheStats().then((stats) => {
            event.ports[0].postMessage(stats);
        });
    }
});

async function getCacheStats() {
    const cacheNames = await caches.keys();
    const stats = {};
    
    for (const cacheName of cacheNames) {
        const cache = await caches.open(cacheName);
        const keys = await cache.keys();
        stats[cacheName] = keys.length;
    }
    
    return stats;
}

console.log('Service Worker: Registered successfully'); 