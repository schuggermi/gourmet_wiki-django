function loadCookiebot() {
    const script = document.createElement('script');
    script.id = 'Cookiebot';
    script.src = 'https://consent.cookiebot.com/uc.js';
    script.setAttribute('data-cbid', import.meta.env.VITE_CB_ID);
    script.type = 'text/javascript';
    document.head.appendChild(script);
}

// Load after page is fully loaded
if (document.readyState === 'complete') {
    loadCookiebot();
} else {
    window.addEventListener('load', loadCookiebot);
}
