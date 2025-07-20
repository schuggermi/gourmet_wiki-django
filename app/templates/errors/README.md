# Error Pages

This directory contains custom error pages for the Gourmet Wiki project.

## Available Error Pages

- **404.html**: Displayed when a page is not found
- **500.html**: Displayed when a server error occurs
- **403.html**: Displayed when access is denied

## How It Works

Django's error handling system is configured in `gourmet_wiki/urls.py` with custom handler functions:

```python
def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)
```

## Testing

You can test these error pages by:

1. Setting `DEBUG = False` in your settings
2. Visiting a non-existent URL (for 404)
3. Creating a view that raises an exception (for 500)
4. Creating a view that returns a 403 Forbidden response (for 403)

There's also a test file at the project root (`test_error_pages.py`) that can be used to verify the error pages are working correctly.

## Customization

All error pages extend the base template and can be customized as needed. They include:

- Clear error messages
- Helpful suggestions for users
- Links to navigate back to safe parts of the site