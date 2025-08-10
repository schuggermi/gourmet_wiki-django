from django import template

register = template.Library()


@register.filter
def dict_length(value):
    """
    Returns the length of a dictionary or iterable.
    """
    try:
        return len(value)
    except Exception:
        return 0


@register.filter
def half_length(value):
    """
    Returns half the length (rounded up) of a dict or iterable.
    """
    try:
        length = len(value)
        return (length + 1) // 2
    except Exception:
        return 0
