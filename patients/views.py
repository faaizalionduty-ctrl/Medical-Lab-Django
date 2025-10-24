from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Patient, Bill
from labtests.models import Test
from django.db.models import Sum, Q # <-- MAKE SURE THIS Q IS IMPORTED
from django.core.paginator import Paginator # <-- Import Paginator

from doctors.models import Doctor # <-- Import Doctor
from decimal import Decimal
import json

def add_patient_bill_view(request):
    if request.method == 'POST':
        # 1. Get Patient data
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        doctor_id = request.POST.get('referred_by') # <-- New field
        
        # 2. Get Billing data
        test_ids = request.POST.getlist('tests')
        discount = Decimal(request.POST.get('discount') or 0.0)
        payment_status = request.POST.get('payment_status')

        # 3. Create Patient
        patient = Patient.objects.create(
            name=name,
            gender=gender,
            phone=phone,
            address=address,
            referred_by_id=doctor_id if doctor_id else None # <-- Assign doctor
        )
        
        # 4. Calculate totals
        selected_tests = Test.objects.filter(id__in=test_ids)
        total_amount = selected_tests.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        net_amount = total_amount - discount
        
        # 5. Create Bill
        bill = Bill.objects.create(
            patient=patient,
            payment_status=payment_status,
            total_amount=total_amount,
            discount=discount,
            net_amount=net_amount
        )
        
        # 6. Link Tests to the Bill
        bill.tests.set(selected_tests)
        
        return redirect('dashboard')

    # --- GET Request ---
    all_tests = Test.objects.all()
    all_doctors = Doctor.objects.all() # <-- Get doctors
    
    # Manually create a list of dicts, converting Decimal to string
    all_tests_list = [
        {'id': test.id, 'name': test.name, 'price': str(test.price)}
        for test in all_tests
    ]
    all_tests_json = json.dumps(all_tests_list)
    
    context = {
        'all_tests_json': all_tests_json,
        'all_doctors': all_doctors, # <-- Pass doctors to template
    }
    return render(request, 'patients/add_patient_bill.html', context)

# --- NEW VIEW ---
# This is the function that was missing and causing the error
def edit_patient_bill_view(request, bill_id):
    bill = get_object_or_404(Bill.objects.select_related('patient'), id=bill_id)
    patient = bill.patient

    if request.method == 'POST':
        # 1. Update Patient data
        patient.name = request.POST.get('name')
        patient.gender = request.POST.get('gender')
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        patient.referred_by_id = request.POST.get('referred_by') if request.POST.get('referred_by') else None
        patient.save()
        
        # 2. Update Bill data
        test_ids = request.POST.getlist('tests')
        discount = Decimal(request.POST.get('discount') or 0.0)
        payment_status = request.POST.get('payment_status')
        
        # 3. Recalculate totals
        selected_tests = Test.objects.filter(id__in=test_ids)
        total_amount = selected_tests.aggregate(total=Sum('price'))['total'] or Decimal('0.00')
        net_amount = total_amount - discount
        
        # 4. Update Bill object
        bill.payment_status = payment_status
        bill.total_amount = total_amount
        bill.discount = discount
        bill.net_amount = net_amount
        bill.save()
        
        # 5. Update Bill's tests
        bill.tests.set(selected_tests)
        
        return redirect('payment_management') # Redirect to payments page

    # --- GET Request ---
    all_tests = Test.objects.all()
    all_doctors = Doctor.objects.all()
    
    # Get IDs of tests already on this bill
    selected_test_ids = list(bill.tests.values_list('id', flat=True))

    all_tests_list = [
        {'id': test.id, 'name': test.name, 'price': str(test.price)}
        for test in all_tests
    ]
    all_tests_json = json.dumps(all_tests_list)
    
    context = {
        'bill': bill,
        'patient': patient,
        'all_tests_json': all_tests_json,
        'all_doctors': all_doctors,
        'selected_test_ids': selected_test_ids, # Pass selected test IDs
    }
    return render(request, 'patients/edit_patient_bill.html', context)
# ------------------

# def payment_management_view(request):
#     # Show all bills (pending and paid) for management
#     all_bills = Bill.objects.order_by('-created_at').select_related('patient')
#     context = {
#         'all_bills': all_bills
#     }
#     return render(request, 'patients/payment_management.html', context)

# --- UPDATED VIEW ---
def payment_management_view(request, page=1): # <-- Accept 'page' argument, default to 1
    # Get the full list of bills, ordered by most recent
    all_bills_list = Bill.objects.order_by('-created_at').select_related('patient', 'patient__referred_by')
    
    # Create a Paginator object
    paginator = Paginator(all_bills_list, 20) # Show 20 bills per page
    
    # Get the page number from the URL argument
    page_number = page
    
    # Get the Page object for the requested page
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj  # Pass the Page object to the template
    }
    # context = {
    #     'all_bills': paginator.get_page(page)
    # }
    return render(request, 'patients/payment_management.html', context)
# --------------------

def mark_as_paid_view(request, bill_id):
    if request.method == 'POST':
        bill = get_object_or_404(Bill, id=bill_id)
        bill.payment_status = 'Paid'
        bill.save()
    return redirect('payment_management')

def update_discount_view(request, bill_id):
    if request.method == 'POST':
        new_discount = Decimal(request.POST.get('discount') or 0.0)
        bill = get_object_or_404(Bill, id=bill_id)
        
        bill.discount = new_discount
        # Recalculate net amount
        bill.net_amount = bill.total_amount - bill.discount
        bill.save()
    return redirect('payment_management')

# --- THIS IS THE NEW VIEW FUNCTION ---
def search_patients_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # Search by patient name, patient phone, or referred doctor name
        results = Bill.objects.filter(
            Q(patient__name__icontains=query) |
            Q(patient__phone__icontains=query) |
            Q(patient__referred_by__name__icontains=query)
        ).select_related('patient', 'patient__referred_by').order_by('-created_at')

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'patients/patient_search.html', context)
# ------------------------------------