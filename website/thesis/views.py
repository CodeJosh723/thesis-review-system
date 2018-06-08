from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    TemplateView,
    FormView,
    ListView
)

from .mixins import (
    UserIsStudentMixin,
    UserIsTeacherMixin,
    UserHasGroupAccessMixin,
    StudentGroupContextMixin,
)
from .forms import (
    StudentGroupForm,
    StudentGroupJoinForm,
    DocumentUploadForm,
)
from .models import StudentGroup, Document


class GroupCreateJoinView(LoginRequiredMixin, UserIsStudentMixin,
                          TemplateView):
    http_method_names = ['get']
    template_name = 'thesis/group_create_join.html'


class GroupCreateView(LoginRequiredMixin, UserIsStudentMixin,
                      CreateView):
    model = StudentGroup
    form_class = StudentGroupForm
    success_url = reverse_lazy('thesis:document_list')
    template_name = 'thesis/group_create.html'
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        self.object = studentgroup = form.save()
        user = self.request.user
        user.studentgroup = studentgroup
        user.save()
        messages.success(self.request, 'Created Group Successfully!')
        return HttpResponseRedirect(self.get_success_url())


class GroupJoinView(LoginRequiredMixin, UserIsStudentMixin,
                    FormView):
    model = StudentGroup
    form_class = StudentGroupJoinForm
    success_url = reverse_lazy('thesis:document_list')
    template_name = 'thesis/group_join.html'
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        md5hash = form.cleaned_data.get('md5hash')
        studentgroup = get_object_or_404(StudentGroup, md5hash=md5hash)
        user = self.request.user
        user.studentgroup = studentgroup
        user.save()
        messages.success(self.request, 'You joined the Group successfully!')
        return HttpResponseRedirect(self.get_success_url())


class DocumentListView(LoginRequiredMixin, UserHasGroupAccessMixin,
                       StudentGroupContextMixin, ListView):
    template_name = 'thesis/document_list.html'
    http_method_names = ['get']
    context_object_name = 'documents'

    def get_queryset(self):
        queryset = self.studentgroup.documents.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.studentgroup.comments.order_by(
            '-created_at')
        return context


class DocumentUploadView(LoginRequiredMixin, UserIsStudentMixin,
                         StudentGroupContextMixin, CreateView):
    model = Document
    template_name = 'thesis/document_upload.html'
    form_class = DocumentUploadForm
    success_url = reverse_lazy('thesis:document_list')
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        self.object = document = form.save(commit=False)
        document.studentgroup = self.request.user.studentgroup
        document.save()
        messages.success(self.request, 'Document Uploaded successfully!')
        return HttpResponseRedirect(self.get_success_url())


class GroupListView(LoginRequiredMixin, UserIsTeacherMixin,
                    ListView):
    template_name = "thesis/group_list.html"
    http_method_names = ['get']
    context_object_name = 'groups'

    def get_queryset(self):
        user = self.request.user
        queryset = user.studentgroups.order_by('title')
        return queryset
