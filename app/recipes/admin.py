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
    readonly_fields = ['created_at']
    list_display = ['name', 'course_type', 'skill_level', 'portions', 'author', 'created_at']
    fields = [
        'name', 'description', 'course_type', 'skill_level', 'thumbnail_image', 'author', 'created_at',
        'portions',
        'working_time_hours', 'working_time_minutes', 'cooking_time_minutes',
        'rest_time_hours', 'rest_time_minutes',
    ]
    search_fields = ('name', 'course_type')
    inlines = [RecipeImageInline, RecipeIngredientInline, RecipePreparationStepInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ['name', 'quantity', 'unit']


@admin.register(RecipeImage)
class RecipeIngredientAdmin(admin.ModelAdmin):
    fields = ['image', 'caption']
