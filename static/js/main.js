import '@/css/main.css';
import Sortable from "sortablejs";
window.Sortable = Sortable;

if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark');
} else {
    document.documentElement.setAttribute('data-theme', 'light');
}

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    document.documentElement.setAttribute('data-theme', event.matches ? 'dark' : 'light');
});

