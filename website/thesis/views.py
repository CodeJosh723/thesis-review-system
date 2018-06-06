from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.views import View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import date

import json

from .mixins import UserIsStudentMixin, UserIsTeacherMixin
from .forms import (
    StudentGroupForm, StudentGroupJoinForm, DocumentUploadForm)
from .models import StudentGroup, Document, Comment
from .decorators import is_student, is_teacher, has_group


def return_json(data):
    return HttpResponse(json.dumps(data), content_type='application/json')


class AccountRedirectView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        if request.user.is_teacher:
            return redirect('thesis:groups_home')
        if request.user.studentgroup:
            return redirect('thesis:group_home')
        return redirect('thesis:group_create_join')


class GroupCreateJoinView(LoginRequiredMixin, UserIsStudentMixin,
                          TemplateView):
    http_method_names = ['get']
    template_name = 'thesis/group_create_join.html'


class GroupCreateView(LoginRequiredMixin, UserIsStudentMixin,
                      CreateView):
    model = StudentGroup
    form_class = StudentGroupForm
    success_url = reverse_lazy('thesis:group_home')
    template_name = 'thesis/group_create.html'
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        self.object = studentgroup = form.save()
        user = self.request.user
        user.studentgroup = studentgroup
        user.save()
        return HttpResponseRedirect(self.get_success_url())


@login_required
@is_student
def group_join(request):
    if request.method == 'POST':
        form = StudentGroupJoinForm(data=request.POST)
        if form.is_valid():
            md5hash = form.cleaned_data.get('md5hash')
            u = request.user
            s = StudentGroup.objects.get(md5hash=md5hash)
            u.studentgroup = s
            u.save()
            return redirect('/')
    else:
        form = StudentGroupJoinForm()
    return render(request, 'thesis/group_join.html', {'form': form})


@login_required
@is_student
@has_group
def group_home(request):
    studentgroup = request.user.studentgroup
    return render(
        request, 'thesis/group_home.html', {'studentgroup': studentgroup})


@login_required
@require_POST
def create_comment(request, group_code):
    studentgroup = get_object_or_404(StudentGroup, md5hash=group_code)
    user = request.user
    if (user.studentgroup != studentgroup) or user.is_teacher is False:
        return return_json({'created': False})
    req = json.loads(request.body.decode('utf-8'))
    content = req.get('content')
    comment = Comment(content=content, user=user, studentgroup=studentgroup)
    try:
        comment.save()
        d = comment.created_at
        response = {
            'created': True,
            'created_at': date(d, 'd M Y') + ' at ' + date(d, 'H:i'),
        }
        return return_json(response)
    except:
        return return_json({'created': False})


class DocumentUploadView(LoginRequiredMixin, UserIsStudentMixin, CreateView):
    model = Document
    template_name = 'thesis/document_upload.html'
    form_class = DocumentUploadForm
    success_url = reverse_lazy('thesis:group_home')
    http_method_names = ['get', 'post']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['studentgroup'] = self.request.user.studentgroup
        return context

    def form_valid(self, form):
        self.object = document = form.save(commit=False)
        document.studentgroup = self.request.user.studentgroup
        document.save()
        return HttpResponseRedirect(self.get_success_url())


@login_required
@is_teacher
def groups_home(request):
    return render(request, 'thesis/groups_home.html')
