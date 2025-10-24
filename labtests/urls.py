from django.urls import path
from . import views

urlpatterns = [
    path('', views.TestListView.as_view(), name='test_list'),
    path('new/', views.TestCreateView.as_view(), name='test_create'),
    path('<int:pk>/edit/', views.TestUpdateView.as_view(), name='test_update'),
    path('<int:pk>/delete/', views.TestDeleteView.as_view(), name='test_delete'),
]