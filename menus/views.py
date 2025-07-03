from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView
from formtools.wizard.views import SessionWizardView

from menus.forms import MenuForm
from menus.models import Menu
from recipes.utils import calculate_scaled_ingredients_menu


class MenuListView(ListView):
    model = Menu


class MenuDetailView(DetailView):
    model = Menu

    def get_context_data(self, **kwargs):
        context = super(MenuDetailView, self).get_context_data(**kwargs)
        context.update(calculate_scaled_ingredients_menu(self.object.pk, self.object.portions))
        return context


# class MenuCreateView(LoginRequiredMixin, CreateView):
#     model = Menu
#     fields = ['name', 'menu_type', 'portions']
#     template_name = 'menus/menu_form.html'


class CreateMenuWizardView(LoginRequiredMixin, SessionWizardView):
    form_list = [
        ('0', MenuForm),
    ]
    template_name = 'menus/create_menu_wizard.html'
    file_storage = FileSystemStorage(location=Path(settings.MEDIA_ROOT).joinpath('menus/images/temp'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu_id = None
        self.menu_instance = None

    def dispatch(self, request, *args, **kwargs):
        self.menu_id = kwargs.get('recipe_id')
        if self.menu_id:
            self.menu_instance = get_object_or_404(Menu, id=self.menu_id, created_by=request.user.pk)
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
            if self.menu_instance:
                kwargs['instance'] = self.menu_instance
            return MenuForm(**kwargs)
        return super().get_form(step, data, files)

    def done(self, form_list, **kwargs):
        menu_form = self.get_form(
            step='0',
            data=self.storage.get_step_data('0'),
            files=self.storage.get_step_files('0')
        )

        if not menu_form.is_valid():
            return self.render_revalidation_failure(step='0', form=menu_form)

        if self.menu_instance:
            menu = menu_form.save()
        else:
            menu = menu_form.save(commit=False)
            menu.created_by = self.request.user
            menu.save()

        return redirect(reverse('menu_detail', kwargs={'pk': menu.id}))
