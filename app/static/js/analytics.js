window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', import.meta.env.VITE_GA_ID, {
    'anonymize_ip': true,
    'cookie_flags': 'SameSite=None;Secure'
});

document.addEventListener('htmx:afterRequest', function(event) {
    const activeElement = document.activeElement;
    if (activeElement && activeElement.tagName === 'INPUT') {
        activeElement.blur();
    }
});
