from django.template.defaultfilters import register

from recipes.models import RecipeRating


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


@register.simple_tag(takes_context=True)
def user_rating(context, recipe):
    """
    Returns the score given by the authenticated user for the given recipe.
    If the user hasn't rated, returns None.
    """
    user = context['request'].user
    if user.is_authenticated:
        rating = RecipeRating.objects.filter(recipe=recipe, user=user).first()
        if rating:
            return rating.score
    return None
