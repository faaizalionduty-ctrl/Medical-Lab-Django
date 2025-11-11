from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Doctor

class DoctorListView(LoginRequiredMixin, ListView):
    model = Doctor
    template_name = 'doctors/doctor_list.html'
    context_object_name = 'doctors'
    login_url = '/auth/login/'

class DoctorCreateView(LoginRequiredMixin, CreateView):
    model = Doctor
    fields = ['name']
    template_name = 'doctors/doctor_form.html'
    success_url = reverse_lazy('doctor_list')
    login_url = '/auth/login/'

class DoctorUpdateView(LoginRequiredMixin, UpdateView):
    model = Doctor
    fields = ['name']
    template_name = 'doctors/doctor_form.html'
    success_url = reverse_lazy('doctor_list')
    login_url = '/auth/login/'

class DoctorDeleteView(LoginRequiredMixin, DeleteView):
    model = Doctor
    template_name = 'doctors/doctor_confirm_delete.html'
    success_url = reverse_lazy('doctor_list')
    login_url = '/auth/login/'
