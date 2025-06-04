from django.contrib import admin

from recipes.models import Recipe, RecipeIngredient, RecipeImage


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeImageInline(admin.TabularInline):
    model = RecipeImage
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ['get_total_cost', 'created_at']
    list_display = ['name', 'get_total_cost', 'created_by', 'created_at']
    fields = ['name', 'description', 'thumbnail_image', 'created_by', 'created_at', 'get_total_cost']
    inlines = [RecipeImageInline, RecipeIngredientInline]

    def get_total_cost(self, obj):
        return f"{obj.total_cost} €"

    get_total_cost.short_description = "Total Cost"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ['ingredient', 'quantity']


@admin.register(RecipeImage)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ['image', 'caption']
