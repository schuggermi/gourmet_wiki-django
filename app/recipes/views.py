import base64
import json
from io import BytesIO
from pathlib import Path

from PIL import Image
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import ListView, DetailView
from formtools.wizard.views import SessionWizardView
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from menus.models import Menu
from recipes.forms import RecipePublishForm, RecipeForm, RecipeIngredientForm, RecipeImageForm, RecipePreparationStepForm, RecipeCreateForm, RecipeDetailsForm
from recipes.formsets import RecipeIngredientFormSet, RecipeImageFormSet, RecipePreparationStepFormSet
from recipes.models import Recipe, RecipeIngredient, RecipeImage, RecipePreparationStep, RecipeRating
from recipes.utils import calculate_scaled_ingredients_menu


User = get_user_model()


""" NEW """

def recipe_create(request):
    if request.method == "POST":
        if not request.user or not request.user.is_authenticated:
            raise PermissionDenied

        form = RecipeCreateForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            response = HttpResponse()
            response['HX-Redirect'] = reverse('recipe-edit', kwargs={'recipe_id': recipe.pk})
            return response
            # return redirect("recipe-edit", recipe_id=recipe.id)
    else:
        form = RecipeCreateForm()

    return render(request, "recipes/recipe_create.html", {"form": form})


def recipe_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    details_form = RecipeDetailsForm(instance=recipe)
    ingredient_form = RecipeIngredientForm()
    step_form = RecipePreparationStepForm()
    image_form = RecipeImageForm()

    return render(
        request,
        "recipes/recipe_edit.html",
        {
            "recipe": recipe,
            "details_form": details_form,
            "ingredient_form": ingredient_form,
            "step_form": step_form,
            "image_form": image_form,
        },
    )


@require_POST
def recipe_public_update(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Checkbox-Logik:
    # existiert der Key -> True
    # fehlt er -> False
    is_published = 'is_published' in request.POST

    recipe.is_published = is_published
    recipe.published_at = timezone.now() if is_published else None
    recipe.save(update_fields=['is_published', 'published_at'])

    html = render_to_string(
        'recipes/_recipe_publish_form.html',
        {'recipe': recipe},
        request=request,
    )
    return HttpResponse(html)


@require_POST
def recipe_details_update(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    form = RecipeDetailsForm(
        data=request.POST,
        instance=recipe,
    )

    if form.is_valid():
        form.save()
        print("SAVED FORM")
        # Create a fresh form with saved data
        form = RecipeDetailsForm(instance=recipe)

    html = render_to_string('recipes/_recipe_details_form.html', {
        'details_form': form,
        'recipe': recipe,  # Pass recipe for the URL
    })
    return HttpResponse(html)


@require_POST
def ingredient_add(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    form = RecipeIngredientForm(data=request.POST)

    if form.is_valid():
        ingredient = form.save(commit=False)
        ingredient.recipe = recipe
        ingredient.save()
        form = RecipeIngredientForm()
    else:
        print("NOT VALID", form.errors)

    html = render_to_string('recipes/_recipe_ingredients_form.html', {
        'ingredient_form': form,
        'recipe': recipe,  # Pass recipe for the URL
    })
    return HttpResponse(html)


def ingredient_edit(request, recipe_id, ingredient_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredient = get_object_or_404(RecipeIngredient, id=ingredient_id)

    if request.method == "POST":
        form = RecipeIngredientForm(data=request.POST, instance=ingredient)

        if form.is_valid():
            form.save()
            form = RecipeIngredientForm()
            html = render_to_string('recipes/_recipe_ingredients_form.html', {
                'ingredient_form': form,
                'recipe': recipe,
            })
            return HttpResponse(html)
        else:
            print("NOT VALID", form.errors)
            html = render_to_string('recipes/_recipe_ingredients_edit_form.html', {
                'ingredient_form': form,
                'recipe': recipe,
                'editing_ingredient_id': ingredient_id,
            })
            return HttpResponse(html)
    else:
        form = RecipeIngredientForm(instance=ingredient)
        html = render_to_string('recipes/_recipe_ingredients_edit_form.html', {
            'ingredient_form': form,
            'recipe': recipe,
            'editing_ingredient_id': ingredient_id,
        })
        return HttpResponse(html)


def ingredient_cancel_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = RecipeIngredientForm()

    html = render_to_string('recipes/_recipe_ingredients_form.html', {
        'ingredient_form': form,
        'recipe': recipe,
    })
    return HttpResponse(html)


@require_http_methods(["DELETE", "POST"])  # Erlaube beide
def ingredient_delete(request, recipe_id, ingredient_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    ingredient = get_object_or_404(RecipeIngredient, id=ingredient_id, recipe=recipe)
    ingredient.delete()

    # Return updated template
    form = RecipeIngredientForm()
    html = render_to_string('recipes/_recipe_ingredients_form.html', {
        'ingredient_form': form,
        'recipe': recipe,
    })
    return HttpResponse(html)


@require_POST
def step_add(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = RecipePreparationStepForm(data=request.POST)

    if form.is_valid():
        print("IS VALID")
        step = form.save(commit=False)
        step.recipe = recipe
        step.order = RecipePreparationStep.objects.filter(recipe=recipe).count() + 1
        print("SAVING STEP:", step.step_text, step.order)
        step.save()
        print("STEP SAVED:", step.id)
        print("IS SECTION: ", step.is_section)
        print("NAME: ", step.section_title)
        form = RecipePreparationStepForm()
    else:
        print("NOT VALID", form.errors)

    html = render_to_string('recipes/_recipe_steps_form.html', {
        'step_form': form,
        'recipe': recipe,  # Pass recipe for the URL
    })
    return HttpResponse(html)


@require_POST
def steps_reorder(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    print("POST DATA:", request.POST)
    print("BODY:", request.body)

    try:
        order_data = json.loads(request.POST.get('order', '[]'))

        print("ORDER DATA:", order_data)

        # Update order for each step
        for item in order_data:
            step_id = item['id']
            new_order = item['order']

            print(f"Updating step {step_id} to order {new_order}")

            RecipePreparationStep.objects.filter(
                id=step_id,
                recipe=recipe
            ).update(order=new_order)

        print("Reordering successful")
        return HttpResponse(status=204)

    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        return HttpResponse('Invalid data', status=400)
    except Exception as e:
        print(f"Error reordering steps: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse('Error', status=500)


@require_http_methods(["DELETE", "POST"])  # Erlaube beide
def step_delete(request, recipe_id, step_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    step = get_object_or_404(RecipePreparationStep, id=step_id, recipe=recipe)

    step.delete()

    # Reorder remaining steps
    steps = RecipePreparationStep.objects.filter(recipe=recipe).order_by('order')
    for index, s in enumerate(steps, start=1):
        s.order = index
        s.save()

    # Return updated template
    form = RecipePreparationStepForm()
    html = render_to_string('recipes/_recipe_steps_form.html', {
        'step_form': form,
        'recipe': recipe,
    })
    return HttpResponse(html)


@require_POST
def image_add(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Get the highest order value
    max_order = RecipeImage.objects.filter(recipe=recipe).aggregate(
        models.Max('order')
    )['order__max'] or -1

    images = request.FILES.getlist('image')

    for idx, image_file in enumerate(images):
        RecipeImage.objects.create(
            recipe=recipe,
            image=image_file,
            order=max_order + idx + 1
        )

    form = RecipeImageForm()
    html = render_to_string('recipes/_recipe_images_form.html', {
        'image_form': form,
        'recipe': recipe,
    })
    return HttpResponse(html)


@require_POST
def image_crop(request, recipe_id, image_id):
    """Handle image cropping with coordinates from frontend"""
    image_obj = get_object_or_404(RecipeImage, id=image_id, recipe_id=recipe_id)

    try:
        data = json.loads(request.body)
        cropped_data = data.get('croppedImage')

        if cropped_data:
            # Remove the data URL prefix
            format, imgstr = cropped_data.split(';base64,')
            ext = format.split('/')[-1]

            # Decode base64 image
            img_data = base64.b64decode(imgstr)
            img = Image.open(BytesIO(img_data))

            # Save cropped image
            buffer = BytesIO()
            img.save(buffer, format=ext.upper())
            buffer.seek(0)

            # Update the image file
            image_obj.image.save(
                image_obj.image.name,
                ContentFile(buffer.read()),
                save=True
            )

            return JsonResponse({'success': True})
    except Exception as e:
        print(f"Crop error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False}, status=400)


@require_POST
def image_reorder(request, recipe_id):
    """Update order of images based on drag and drop"""
    recipe = get_object_or_404(Recipe, id=recipe_id)

    try:
        data = json.loads(request.body)
        order_data = data.get('order', [])

        for idx, image_id in enumerate(order_data):
            RecipeImage.objects.filter(id=image_id, recipe=recipe).update(order=idx)

        # Return updated HTML instead of JSON
        form = RecipeImageForm()
        html = render_to_string('recipes/_recipe_images_form.html', {
            'image_form': form,
            'recipe': recipe,
        })
        return HttpResponse(html)

    except Exception as e:
        print(f"Reorder error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["DELETE", "POST"])
def image_delete(request, recipe_id, image_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    image = get_object_or_404(RecipeImage, id=image_id, recipe=recipe)

    # Delete the file from storage
    image.image.delete(save=False)
    image.delete()

    # Reorder remaining images
    images = RecipeImage.objects.filter(recipe=recipe).order_by('order')
    for idx, img in enumerate(images):
        img.order = idx
        img.save()

    form = RecipeImageForm()
    html = render_to_string('recipes/_recipe_images_form.html', {
        'image_form': form,
        'recipe': recipe,
    })
    return HttpResponse(html)

""" NEW """


class RecipeListView(ListView):
    model = Recipe

    def get_queryset(self):
        queryset = super().get_queryset()

        # queryset = queryset.filter(is_published=True)

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


def recipe_list_partial(request):
    """
    View to render the recipe list partial for htmx requests
    """
    queryset = Recipe.objects.all()

    queryset = queryset.filter(is_published=True)

    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

    context = {
        'object_list': queryset,
        'search_query': search_query,
    }

    return render(request, 'recipes/partials/recipe_list.html', context)


# def add_preparation_step_form(request):
#     form_index = int(request.GET.get("form_count", 0))
#     new_form = RecipePreparationStepForm(prefix=f'recipe_preparation_step-{form_index}')
#
#     new_form.fields['DELETE'] = forms.BooleanField(required=False)
#     new_form.fields['ORDER'] = forms.IntegerField(required=True)
#
#     context = {
#         'form': new_form,
#         'form_index': form_index,
#     }
#
#     html = render_to_string('recipes/partials/preparation_step_form_row.html', context)
#     return HttpResponse(html)
#
#
# def add_ingredient_form(request):
#     form_index = int(request.GET.get("form_count", 0))
#     new_form = RecipeIngredientForm(prefix=f'recipe_ingredient-{form_index}')
#
#     context = {
#         'form': new_form,
#         'form_index': form_index,
#     }
#
#     html = render_to_string('recipes/partials/ingredient_form_row.html', context)
#     return HttpResponse(html)


def add_image_form(request):
    form_index = int(request.GET.get("form_count", 0))
    new_form = RecipeImageForm(prefix=f'recipe_image-{form_index}')

    context = {
        'form': new_form,
        'form_index': form_index,
    }

    html = render_to_string('recipes/partials/image_form_row.html', context)
    return HttpResponse(html)


class CreateRecipeWizardView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        ('0', RecipeForm),
        ('1', RecipeIngredientFormSet),
        ('2', RecipePreparationStepFormSet),
        ('3', RecipeImageFormSet),
    ]
    template_name = 'recipes/create_recipe_wizard.html'
    file_storage = FileSystemStorage(location=Path(settings.MEDIA_ROOT).joinpath('recipes/images/temp'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recipe_id = None
        self.recipe_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.recipe_id = kwargs.get('recipe_id')
        if self.recipe_id:
            self.recipe_instance = get_object_or_404(Recipe, id=self.recipe_id, created_by=request.user.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        kwargs = {}

        if data is not None:
            kwargs['data'] = data
        if files is not None:
            kwargs['files'] = files

        if step == '0':
            if self.recipe_instance:
                kwargs['instance'] = self.recipe_instance
            return RecipeForm(**kwargs)
        elif step == '1':
            if self.recipe_instance:
                queryset = self.recipe_instance.ingredients.all()
            else:
                queryset = RecipeIngredient.objects.none()
            kwargs.update({
                'prefix': 'recipe_ingredient',
                'queryset': queryset,
            })
            formset = RecipeIngredientFormSet(**kwargs)
            # Debug: Print formset validation
            if data is not None:
                is_valid = formset.is_valid()
                print(f"RecipeIngredientFormSet is_valid: {is_valid}")
                if not is_valid:
                    print(f"RecipeIngredientFormSet errors: {formset.errors}")
                    print(f"RecipeIngredientFormSet non_form_errors: {formset.non_form_errors()}")
                    # Print individual form errors
                    for i, form in enumerate(formset.forms):
                        if form.errors:
                            print(f"Form {i} errors: {form.errors}")
            return formset
        elif step == '2':
            if self.recipe_instance:
                queryset = self.recipe_instance.steps.all().order_by('order')
            else:
                queryset = RecipePreparationStep.objects.none()
            kwargs.update({
                'queryset': queryset,
                'prefix': 'recipe_preparation_step',
            })
            return RecipePreparationStepFormSet(**kwargs)
        elif step == '3':
            if self.recipe_instance:
                queryset = self.recipe_instance.images.all()
            else:
                queryset = RecipeImage.objects.none()
            kwargs.update({
                'queryset': queryset,
                'prefix': 'recipe_image',
            })
            return RecipeImageFormSet(**kwargs)
        return super().get_form(step, data, files)

    def done(self, form_list, **kwargs):
        recipe_form = self.get_form(
            step='0',
            data=self.storage.get_step_data('0'),
            files=self.storage.get_step_files('0')
        )

        if not recipe_form.is_valid():
            return self.render_revalidation_failure(step='0', form=recipe_form)

        if self.recipe_instance:
            recipe = recipe_form.save()
        else:
            recipe = recipe_form.save(commit=False)
            recipe.created_by = self.request.user
            recipe.save()

        # Step 1 – Ingredients
        ingredient_formset = self.get_form(step='1', data=self.storage.get_step_data('1'))
        if not ingredient_formset.is_valid():
            return self.render_revalidation_failure(step='1', form=ingredient_formset)

        # for form in ingredient_formset:
        #     if form.data.get(f"{form.prefix}-DELETE") == 'on':
        #         if form.instance.pk:
        #             form.instance.delete()
        #     else:
        #         # Get the ingredient name from the form
        #         ingredient_name = form.cleaned_data.get('ingredient_name')
        #
        #         if ingredient_name:
        #             # Try to find an existing ingredient with this name
        #             ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)
        #
        #             # Set the ingredient on the instance
        #             form.instance.ingredient = ingredient
        #
        #         instance = form.save(commit=False)
        #         instance.recipe = recipe
        #
        #         # pprint(instance, indent=4)
        #
        #         if not instance.pk:
        #             instance.save()

        # Step 2 – Preparation Steps
        step_formset = self.get_form(step='2', data=self.storage.get_step_data('2'))
        if not step_formset.is_valid():
            return self.render_revalidation_failure(step='2', form=step_formset)

        for index, form in enumerate(step_formset):
            if form.data.get(f"{form.prefix}-DELETE") == 'on':
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)

                if not instance.pk:
                    instance.recipe = recipe
                instance.order = form.cleaned_data.get('order', index)
                instance.save()

        # Step 3 – Images
        image_formset = self.get_form(
            step='3',
            data=self.storage.get_step_data('3'),
            files=self.storage.get_step_files('3')
        )
        if not image_formset.is_valid():
            return self.render_revalidation_failure(step='3', form=image_formset)

        for index, form in enumerate(image_formset):
            if form.data.get(f"{form.prefix}-DELETE") == 'on':
                if form.instance.pk:
                    form.instance.delete()
            else:
                instance = form.save(commit=False)
                if not instance.pk:
                    instance.recipe = recipe
                instance.order = form.cleaned_data.get('order', index)
                instance.save()

        return redirect(reverse('recipe-detail', kwargs={'pk': recipe.pk}))


class RecipeDetailView(DetailView):
    model = Recipe


def get_calculate_scaled_ingredients(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    context = {
        'ingredients': recipe.calculate_scaled_ingredients(int(request.GET.get('portions', recipe.portions)))
    }

    html = render_to_string('recipes/partials/recipe_ingredients_list.html', context)
    return HttpResponse(html)


def get_calculate_scaled_ingredients_menu(request, menu_id):
    context = calculate_scaled_ingredients_menu(menu_id, int(request.GET.get('portions')))
    context['current_recipe_slide'] = request.GET.get('current_recipe_slide', 0)

    html = render_to_string('menus/partials/recipe_carousel.html', context)
    return HttpResponse(html)


@login_required
def toggle_favorite(request, recipe_id):
    if request.method != "POST":
        return HttpResponseForbidden()

    recipe = get_object_or_404(Recipe, pk=recipe_id)
    user = request.user

    if user in recipe.favorite_by.all():
        recipe.favorite_by.remove(user)
    else:
        recipe.favorite_by.add(user)
    html = render_to_string(
        "recipes/partials/favorite_button.html",
        {"recipe": recipe, "user": user},
        request=request
    )
    return HttpResponse(html)


@login_required
def rate_recipe(request, recipe_id, score):
    if request.method != "POST":
        return HttpResponseForbidden()

    recipe = get_object_or_404(Recipe, id=recipe_id)

    rating, created = RecipeRating.objects.update_or_create(
        recipe=recipe,
        user=request.user,
        defaults={'score': score}
    )

    average_rating = recipe.average_rating

    return render(request, "cotton/rating_action.html", {
        "recipe": recipe,
        "average_rating": average_rating,
        "score": score,
    })


@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    # Check if the user is the owner of the recipe
    if recipe.created_by != request.user:
        return HttpResponseForbidden()

    if request.method == "POST":
        # Verify the confirmation code
        confirmation_code = (request.POST.get('confirmation_code') or '').strip()
        expected_code = (request.session.get('recipe_delete_code') or '').strip()

        if confirmation_code == expected_code and expected_code:
            # Delete the recipe
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                recipe.delete()
                # Clear the code from session
                request.session.pop('recipe_delete_code', None)
                return JsonResponse({
                    "redirect_url": reverse('recipe-list')
                })

            recipe.delete()
            messages.success(request, _('Recipe successfully deleted.'))
            # Clear the code from session
            request.session.pop('recipe_delete_code', None)
            return redirect('recipe-list')
        else:
            # Invalid code
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                context = {
                    "recipe": recipe,
                    # Keep showing the expected code so the user can retry
                    "confirmation_code": expected_code,
                    "form_errors": {
                        "confirmation_code": _('Invalid confirmation code.')
                    },
                    "values": {
                        "confirmation_code": confirmation_code,
                    }
                }
                return render(request, "recipes/partials/delete_confirmation_modal.html", context=context, status=400)

            messages.error(request, _('Invalid confirmation code.'))
            return redirect('recipe-detail', pk=recipe_id)

    # Generate a random confirmation code
    import random
    import string
    confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    request.session['recipe_delete_code'] = confirmation_code

    return render(request, "recipes/partials/delete_confirmation_modal.html", {
        "recipe": recipe,
        "confirmation_code": confirmation_code,
    })
