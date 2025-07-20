from django.contrib import admin

from ingredients.models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    fields = [field.name for field in Ingredient._meta.fields if field.name != 'id' and field.editable]
