from django import template
import markdown as md

register = template.Library()

@register.filter
def markdown(text):
    return md.markdown(text, extensions=["extra", "codehilite", "fenced_code"])
