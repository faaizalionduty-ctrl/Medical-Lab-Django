from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Doctor

class DoctorListView(ListView):
    model = Doctor
    template_name = 'doctors/doctor_list.html'
    context_object_name = 'doctors'

class DoctorCreateView(CreateView):
    model = Doctor
    fields = ['name']
    template_name = 'doctors/doctor_form.html'
    success_url = reverse_lazy('doctor_list')

class DoctorUpdateView(UpdateView):
    model = Doctor
    fields = ['name']
    template_name = 'doctors/doctor_form.html'
    success_url = reverse_lazy('doctor_list')

class DoctorDeleteView(DeleteView):
    model = Doctor
    template_name = 'doctors/doctor_confirm_delete.html'
    success_url = reverse_lazy('doctor_list')
