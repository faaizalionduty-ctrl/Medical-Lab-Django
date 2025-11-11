from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Test

class TestListView(LoginRequiredMixin, ListView):
    model = Test
    template_name = 'labtests/test_list.html'
    context_object_name = 'tests'
    login_url = '/auth/login/'

class TestCreateView(LoginRequiredMixin, CreateView):
    model = Test
    fields = ['name', 'price']
    template_name = 'labtests/test_form.html'
    success_url = reverse_lazy('test_list')
    login_url = '/auth/login/'

class TestUpdateView(LoginRequiredMixin, UpdateView):
    model = Test
    fields = ['name', 'price']
    template_name = 'labtests/test_form.html'
    success_url = reverse_lazy('test_list')
    login_url = '/auth/login/'

class TestDeleteView(LoginRequiredMixin, DeleteView):
    model = Test
    template_name = 'labtests/test_confirm_delete.html'
    success_url = reverse_lazy('test_list')
    login_url = '/auth/login/'
