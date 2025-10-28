from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('reports/', views.reports_view, name='reports'), # <-- ADD THIS LINE
    path('doctor-reports/', views.doctor_reports_view, name='doctor_reports'), # <-- ADD THIS LINE

]