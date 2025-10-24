from django.urls import path
from . import views

urlpatterns = [
    path('', views.DoctorListView.as_view(), name='doctor_list'),
    path('new/', views.DoctorCreateView.as_view(), name='doctor_create'),
    path('<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor_update'),
    path('<int:pk>/delete/', views.DoctorDeleteView.as_view(), name='doctor_delete'),
]
