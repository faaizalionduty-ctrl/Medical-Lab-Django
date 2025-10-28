from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_patient_bill_view, name='add_patient_bill'),
    path('bill/<int:bill_id>/edit/', views.edit_patient_bill_view, name='edit_patient_bill'),
    path('payments/<int:page>', views.payment_management_view, name='payment_management'),
    path('payments/', views.payment_management_view, {'page': 1}, name='payment_management'),
    # --- NEW AND REMOVED URLS ---
    # path('payments/add/<int:bill_id>/', views.add_payment_view, name='add_payment'), # NEW
    # path('payments/mark-paid/<int:bill_id>/', views.mark_as_paid_view, name='mark_as_paid'), # REMOVED
    path('payments/update-discount/<int:bill_id>/', views.update_discount_view, name='update_discount'),
    # --- NEW & REMOVED URLS ---
    path('bill/<int:bill_id>/manage_payments/', views.manage_bill_payments_view, name='manage_bill_payments'), # NEW
    path('payment/delete/<int:pk>/', views.delete_payment_view, name='delete_payment'), # NEW
    
    # path('payments/add/<int:bill_id>/', views.add_payment_view, name='add_payment'), # REMOVED
    path('search/', views.search_patients_view, name='patient_search'),
    path('bill/<int:bill_id>/delete/', views.delete_patient_view, name='delete_patient'),  # NEW: Delete patient URL
]