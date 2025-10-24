from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_patient_bill_view, name='add_patient_bill'),
    path('payments/<int:page>', views.payment_management_view, name='payment_management'),
    path('payments/', views.payment_management_view, {'page': 1}, name='payment_management'),
    path('payments/mark-paid/<int:bill_id>/', views.mark_as_paid_view, name='mark_as_paid'),
    path('payments/update-discount/<int:bill_id>/', views.update_discount_view, name='update_discount'),
    path('bill/<int:bill_id>/edit/', views.edit_patient_bill_view, name='edit_patient_bill'),
    path('search/', views.search_patients_view, name='patient_search'),
]