from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from .models import Patient, Bill, PaymentTransaction
from labtests.models import Test
from doctors.models import Doctor
from decimal import Decimal
import json
from django.core.paginator import Paginator


def add_patient_bill_view(request):
    if request.method == 'POST':
        # ... (Get Patient data is unchanged) ...
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        referred_by_id = request.POST.get('referred_by')
        
        test_ids = request.POST.getlist('tests')
        discount = Decimal(request.POST.get('discount') or 0.0)
        initial_payment = Decimal(request.POST.get('initial_payment') or 0.0)
        
        doctor_instance = None
        if referred_by_id:
            doctor_instance = get_object_or_404(Doctor, id=referred_by_id)

        patient = Patient.objects.create(
            name=name,
            gender=gender,
            phone=phone,
            address=address,
            referred_by=doctor_instance
        )
        
        selected_tests = Test.objects.filter(id__in=test_ids)
        total_amount = selected_tests.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        net_amount = total_amount - discount
        
        bill = Bill.objects.create(
            patient=patient,
            total_amount=total_amount,
            discount=discount,
            net_amount=net_amount
        )
        bill.tests.set(selected_tests)
        
        # --- NEW OVERPAYMENT PREVENTION ---
        if initial_payment > net_amount:
            initial_payment = net_amount  # Cap payment at the net amount
        
        if initial_payment > 0:
            PaymentTransaction.objects.create(
                bill=bill,
                amount=initial_payment
            )
        
        return redirect('dashboard')

    # ... (GET request logic is unchanged) ...
    all_doctors = Doctor.objects.all()
    all_tests = Test.objects.all()
    all_tests_list = [{'id': test.id, 'name': test.name, 'price': str(test.price)} for test in all_tests]
    all_tests_json = json.dumps(all_tests_list)
    
    context = {
        'all_tests_json': all_tests_json,
        'all_doctors': all_doctors
    }
    return render(request, 'patients/add_patient_bill.html', context)

# ... (edit_patient_bill_view is unchanged) ...
def edit_patient_bill_view(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    patient = bill.patient
    
    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.gender = request.POST.get('gender')
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        referred_by_id = request.POST.get('referred_by')
        patient.referred_by = get_object_or_404(Doctor, id=referred_by_id) if referred_by_id else None
        patient.save()
        
        test_ids = request.POST.getlist('tests')
        discount = Decimal(request.POST.get('discount') or 0.0)
        
        selected_tests = Test.objects.filter(id__in=test_ids)
        total_amount = selected_tests.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        net_amount = total_amount - discount
        
        bill.tests.set(selected_tests)
        bill.total_amount = total_amount
        bill.discount = discount
        bill.net_amount = net_amount
        bill.save()
        
        return redirect('payment_management_root')

    all_doctors = Doctor.objects.all()
    all_tests = Test.objects.all()
    all_tests_list = [{'id': test.id, 'name': test.name, 'price': str(test.price)} for test in all_tests]
    selected_test_ids = list(bill.tests.values_list('id', flat=True))

    context = {
        'bill': bill,
        'patient': patient,
        'all_doctors': all_doctors,
        'all_tests_json': json.dumps(all_tests_list),
        'selected_test_ids': json.dumps(selected_test_ids),
    }
    return render(request, 'patients/edit_patient_bill.html', context)


# ... (payment_management_view is unchanged) ...
def payment_management_view(request, page=1):
    all_bills_list = Bill.objects.order_by('-created_at').select_related('patient')
    paginator = Paginator(all_bills_list, 20)
    page_obj = paginator.get_page(page)
    context = {'page_obj': page_obj}
    return render(request, 'patients/payment_management.html', context)

# --- 'add_payment_view' is REMOVED ---

# --- NEW VIEW ---
def manage_bill_payments_view(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    
    if request.method == 'POST':
        # This view now handles ADDING new payments
        amount = Decimal(request.POST.get('amount') or 0.0)
        
        if amount > 0:
            # --- NEW OVERPAYMENT PREVENTION ---
            amount_due = bill.amount_due
            if amount > amount_due:
                amount = amount_due  # Cap the payment at the amount due
            
            if amount > 0: # Check again in case amount_due was 0
                PaymentTransaction.objects.create(
                    bill=bill,
                    amount=amount
                )
        # Redirect back to this same page
        return redirect('manage_bill_payments', bill_id=bill.id)

    # GET request:
    transactions = bill.transactions.all().order_by('-created_at')
    context = {
        'bill': bill,
        'transactions': transactions,
    }
    return render(request, 'patients/manage_bill_payments.html', context)

# --- NEW VIEW ---
def delete_payment_view(request, pk):
    # 'pk' is the ID of the PaymentTransaction
    transaction = get_object_or_404(PaymentTransaction, pk=pk)
    bill_id = transaction.bill.id  # Save the bill ID before deleting
    
    if request.method == 'POST':
        transaction.delete()
    
    # Redirect back to the manage page for that bill
    return redirect('manage_bill_payments', bill_id=bill_id)

# ... (update_discount_view is unchanged) ...
def update_discount_view(request, bill_id):
    if request.method == 'POST':
        new_discount = Decimal(request.POST.get('discount') or 0.0)
        bill = get_object_or_404(Bill, id=bill_id)
        
        bill.discount = new_discount
        bill.save()
    return redirect('payment_management_root')

# ... (search_patients_view is unchanged) ...
# --- NEW DELETE VIEW ---
def delete_patient_view(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    patient = bill.patient

    if request.method == 'POST':
        # Delete the patient (this will cascade delete the bill as well)
        patient.delete()
        return redirect('dashboard')
    
    context = {
        'bill': bill,
        'patient': patient,
    }
    return render(request, 'patients/patient_confirm_delete.html', context)

def search_patients_view(request, page=1):
    query = request.GET.get('q', '')
    bill_list = []
    
    if query:
        bill_list = Bill.objects.filter(
            Q(patient__name__icontains=query) |
            Q(patient__phone__icontains=query) |
            Q(patient__referred_by__name__icontains=query)
        ).select_related('patient', 'patient__referred_by').order_by('-created_at').distinct()

    paginator = Paginator(bill_list, 20)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'patients/patient_search.html', context)

