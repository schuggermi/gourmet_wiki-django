import 'vite/modulepreload-polyfill';
import '@/css/main.css';
import Sortable from "sortablejs";
import {reindexFormset} from './formset-utils';

window.Sortable = Sortable;
window.reindexFormset = reindexFormset;

// if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
//     document.documentElement.setAttribute('data-theme', 'dark');
// } else {
//     document.documentElement.setAttribute('data-theme', 'light');
// }

// Listen for system theme changes
//window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
//    document.documentElement.setAttribute('data-theme', event.matches ? 'dark' : 'light');
//});


// -----------------------------
// Global helpers and listeners
// -----------------------------

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Intercept submit of dynamically injected user delete modal form
document.addEventListener('submit', function (e) {
  const form = e.target;
  if (!(form instanceof HTMLFormElement)) return;
  const handles = new Set(['user-delete-form', 'recipe-delete-form']);
  if (!handles.has(form.id)) return;

  e.preventDefault();

  const formData = new FormData(form);
  fetch(form.action, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: formData,
  }).then(async (response) => {
    const contentType = response.headers.get('content-type') || '';
    if (response.ok) {
      if (contentType.includes('application/json')) {
        const data = await response.json();
        if (data.redirect_url) window.location.href = data.redirect_url;
        else window.location.reload();
      } else {
        // Fallback: reload
        window.location.reload();
      }
    } else if (response.status === 400) {
      // Replace the modal with the updated HTML containing field errors
      const html = await response.text();
      const dialog = document.getElementById('delete_confirmation_modal');
      const container = dialog ? dialog.parentElement : null;
      if (container) {
        container.innerHTML = html;
      } else {
        // If dialog not found, append received HTML to body as a fallback
        const wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        document.body.appendChild(wrapper);
      }
    } else {
      // Unexpected response: log and do nothing
      // eslint-disable-next-line no-console
      console.error('Unexpected response submitting delete form', response.status);
    }
  }).catch(err => {
    // eslint-disable-next-line no-console
    console.error('Error submitting delete form', err);
  });
});

