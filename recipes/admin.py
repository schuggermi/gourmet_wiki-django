from django.contrib import admin

from recipes.models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ['get_total_cost', 'created_at']
    list_display = ['name', 'get_total_cost', 'created_by', 'created_at']
    fields = ['name', 'description', 'created_by', 'created_at', 'get_total_cost']
    inlines = [RecipeIngredientInline]

    def get_total_cost(self, obj):
        return f"{obj.total_cost} €"

    get_total_cost.short_description = "Total Cost"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ['ingredient', 'quantity']
