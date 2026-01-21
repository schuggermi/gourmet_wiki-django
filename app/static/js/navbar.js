// static/src/js/navbar.js
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('menuToggle');

    if (toggle) {
        toggle.addEventListener('focus', () => {
            toggle.classList.add('swap-active');
            toggle.setAttribute('aria-expanded', 'true');
        });

        toggle.addEventListener('blur', () => {
            setTimeout(() => {
                if (document.activeElement !== toggle && !toggle.contains(document.activeElement)) {
                    toggle.classList.remove('swap-active');
                    toggle.setAttribute('aria-expanded', 'false');
                }
            }, 150);
        });
    }
});
