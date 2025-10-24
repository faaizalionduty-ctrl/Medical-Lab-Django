from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Test

class TestListView(ListView):
    model = Test
    template_name = 'labtests/test_list.html'
    context_object_name = 'tests'

class TestCreateView(CreateView):
    model = Test
    fields = ['name', 'price']
    template_name = 'labtests/test_form.html'
    success_url = reverse_lazy('test_list')

class TestUpdateView(UpdateView):
    model = Test
    fields = ['name', 'price']
    template_name = 'labtests/test_form.html'
    success_url = reverse_lazy('test_list')

class TestDeleteView(DeleteView):
    model = Test
    template_name = 'labtests/test_confirm_delete.html'
    success_url = reverse_lazy('test_list')