from django.template.defaultfilters import register


@register.filter
def prev_idx(sequence, position):
    try:
        return sequence[position] if position == 0 else sequence[position - 1]
    except IndexError:
        return None


@register.filter
def next_idx(sequence, position):
    try:
        return sequence[position + 1] if position < len(sequence) - 1 else 0
    except IndexError:
        return None
