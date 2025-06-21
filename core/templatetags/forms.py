from django.template.defaultfilters import register
from django.utils.html import format_html
from django.utils.safestring import mark_safe


@register.filter
def render_attrs(widget_attrs, reserved_attrs=""):
    """Safely render widget attributes excluding reserved ones."""
    reserved = reserved_attrs.split(',') if reserved_attrs else []
    reserved = [attr.strip() for attr in reserved]

    if not widget_attrs:
        return ''

    attrs = []
    for attr, val in widget_attrs.items():
        if attr in reserved:
            continue

        if val is None or val == "":
            continue

        if val is True:
            attrs.append(format_html('{}', attr))
        elif val is False:
            continue
        else:
            attrs.append(format_html('{}="{}"', attr, val))

    return mark_safe(' '.join(attrs))
