from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import (
    TemplateView,
    CreateView,
    RedirectView,
    UpdateView,
    ListView,
    DetailView
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    StudentSignUpForm, UserUpdateForm, TeacherUpdateForm)
from .models import User


class LoginRedirectView(LoginRequiredMixin, RedirectView):
    http_method_names = ['get']

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        if user.is_superuser:
            return reverse_lazy('admin:index')
        elif user.is_teacher:
            if user.is_external:
                return reverse_lazy('thesis:external_group_list')
            return reverse_lazy('thesis:group_list')
        if user.studentgroup:
            return reverse_lazy('thesis:document_list')
        return reverse_lazy('registration:teacher_list')


class AboutView(TemplateView):
    http_method_names = ['get']
    template_name = 'registration/about.html'


class UserCreateView(CreateView):
    model = User
    template_name = 'registration/user_create.html'
    form_class = StudentSignUpForm
    success_url = reverse_lazy('registration:teacher_list')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            'User Created Successfully!',
            extra_tags='is-success')
        return response


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "registration/user_update.html"
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('registration:user_update')

    def get_form_class(self):
        if self.request.user.is_teacher:
            return TeacherUpdateForm
        else:
            return UserUpdateForm

    def get_object(self, *args, **kwargs):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Update Successful!',
            extra_tags='is-success')
        return response


class UserDeleteView(LoginRequiredMixin, TemplateView):
    template_name = "registration/user_delete.html"
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user.delete()
        messages.success(
            request,
            'Account deleted successfully!',
            extra_tags='is-success')
        return HttpResponseRedirect(reverse_lazy('registration:login'))


class TeachersListView(LoginRequiredMixin, ListView):
    template_name = 'registration/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        department_name = self.kwargs.get('department_name', '')
        queryset = User.objects.filter(is_teacher=True).order_by('full_name')
        if department_name:
            return queryset.filter(department=department_name)
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        context_data = super().get_context_data(
            *args, object_list=object_list, **kwargs)
        context_data['department_name'] = self.kwargs.get(
            'department_name', '')
        return context_data


class TeacherDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'teacher'
    template_name = 'registration/teacher_detail.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        if username is not None:
            obj = get_object_or_404(User, username=username, is_teacher=True)
            return obj
        else:
            raise Http404("No Teachers found matching the query")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request,
                'Your password was successfully updated!',
                extra_tags='is-success')
            return redirect(reverse_lazy('registration:change_password'))
        else:
            messages.error(
                request,
                'Please correct the error below.',
                extra_tags='is-danger')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})
