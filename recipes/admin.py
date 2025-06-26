from django.contrib import admin

from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeImageInline(admin.TabularInline):
    model = RecipeImage
    extra = 1


class RecipePreparationStepInline(admin.TabularInline):
    model = RecipePreparationStep
    extra = 1
    ordering = ('order',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ['get_total_cost', 'created_at']
    list_display = ['name', 'get_total_cost', 'skill_level', 'portions', 'created_by', 'created_at']
    fields = [
        'name', 'description', 'skill_level', 'thumbnail_image', 'created_by', 'created_at', 'get_total_cost',
        'portions',
        'working_time_hours', 'working_time_minutes', 'cooking_time_hours', 'cooking_time_minutes',
        'rest_time_hours', 'rest_time_minutes',
    ]
    search_fields = ('name',)
    inlines = [RecipeImageInline, RecipeIngredientInline, RecipePreparationStepInline]

    def get_total_cost(self, obj):
        return f"{obj.total_cost} €"

    get_total_cost.short_description = "Total Cost"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ['ingredient', 'quantity']


@admin.register(RecipeImage)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ['image', 'caption']
