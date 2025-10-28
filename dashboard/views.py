from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count
from patients.models import Bill, PaymentTransaction # Import PaymentTransaction
from doctors.models import Doctor
from decimal import Decimal
import datetime
import calendar

def dashboard_view(request):
    today = timezone.now().date()
    
    # 1. Total patients today (counting unique bills)
    total_patients_today = Bill.objects.filter(created_at__date=today).count()
    
    # --- UPDATED INCOME LOGIC ---
    # 2. Total cash/income today (from all transactions)
    total_income_today = PaymentTransaction.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0.00
    # ---
    
    # 3. Last 5 patients (showing the 5 most recent bills)
    recent_bills = Bill.objects.order_by('-created_at')[:5].select_related(
        'patient', 
        'patient__referred_by'
    )

    context = {
        'total_patients_today': total_patients_today,
        'total_income_today': total_income_today,
        'recent_bills': recent_bills,
    }
    return render(request, 'dashboard/dashboard.html', context)


def reports_view(request):
    today = timezone.now().date()
    
    filter_type = request.GET.get('filter_type', 'today')
    start_date = None
    end_date = None
    period_description = "Today"
    
    # ... (Date range logic is unchanged) ...
    if filter_type == 'today':
        start_date = end_date = today
        period_description = f"For Today ({today.strftime('%b %d, %Y')})"
    elif filter_type == 'this_week':
        start_date = today - datetime.timedelta(days=today.weekday())
        end_date = start_date + datetime.timedelta(days=6)
        period_description = f"This Week ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    elif filter_type == 'this_month':
        start_date = today.replace(day=1)
        _, last_day_num = calendar.monthrange(today.year, today.month)
        end_date = today.replace(day=last_day_num)
        period_description = f"This Month ({today.strftime('%B %Y')})"
    elif filter_type == 'custom':
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            period_description = f"From {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
        except ValueError:
            filter_type = 'today'
            start_date = end_date = today
            period_description = f"For Today ({today.strftime('%b %d, %Y')}) (Invalid custom range)"

    # --- Perform Queries ---
    total_income = 0.00
    total_patients_served = 0
    bills_list = []

    if start_date and end_date:
        # --- UPDATED INCOME LOGIC ---
        # 1. Get all transactions within the date range
        total_income = PaymentTransaction.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or 0.00
        # ---

        # 2. Get all bills (paid or pending) within the range and annotate amount_paid
        bills_qs = Bill.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).select_related('patient', 'patient__referred_by').annotate(amount_paid=Sum('transactions__amount'))

        total_patients_served = bills_qs.count()

        # Build a simple list of dicts for template rendering (compute amount_due safely)
        from decimal import Decimal
        for b in bills_qs:
            amount_paid = b.amount_paid or Decimal('0.00')
            amount_due = (b.net_amount or Decimal('0.00')) - amount_paid
            bills_list.append({
                'id': b.id,
                'patient': b.patient,
                'referred_by': getattr(b.patient.referred_by, 'name', None),
                'visit_time': b.created_at,
                'total_amount': b.total_amount,
                'discount': b.discount,
                'net_amount': b.net_amount,
                'amount_paid': amount_paid,
                'amount_due': amount_due,
                'payment_status': b.payment_status,
            })

    context = {
        'total_income': total_income,
        'total_patients_served': total_patients_served,
        'bills_list': bills_list,
        'period_description': period_description,
        'current_filter': filter_type,
        'start_date_val': request.GET.get('start_date', ''),
        'end_date_val': request.GET.get('end_date', ''),
    }
    
    return render(request, 'dashboard/reports.html', context)


def doctor_reports_view(request):
    # ... (this view is unchanged) ...
    today = timezone.now().date()
    all_doctors = Doctor.objects.all()
    filter_type = request.GET.get('filter_type', 'today')
    doctor_id = request.GET.get('doctor_id')
    start_date = None
    end_date = None
    period_description_base = "Today"
    if filter_type == 'today':
        start_date = end_date = today
        period_description_base = f"Today ({today.strftime('%b %d, %Y')})"
    elif filter_type == 'this_week':
        start_date = today - datetime.timedelta(days=today.weekday())
        end_date = start_date + datetime.timedelta(days=6)
        period_description_base = f"This Week ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})"
    elif filter_type == 'this_month':
        start_date = today.replace(day=1)
        _, last_day_num = calendar.monthrange(today.year, today.month)
        end_date = today.replace(day=last_day_num)
        period_description_base = f"This Month ({today.strftime('%B %Y')})"
    elif filter_type == 'custom':
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            period_description_base = f"From {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
        except ValueError:
            filter_type = 'today'
            start_date = end_date = today
            period_description_base = f"For Today ({today.strftime('%b %d, %Y')}) (Invalid custom range)"

    total_patients_referred = 0
    total_bill_amount = Decimal('0.00')
    doctor_share_amount = Decimal('0.00')
    period_description = f"Please select a doctor ({period_description_base})"
    selected_doctor_name = "N/A"

    if doctor_id and start_date and end_date:
        try:
            selected_doctor = Doctor.objects.get(id=doctor_id)
            selected_doctor_name = selected_doctor.name
            filtered_bills = Bill.objects.filter(
                patient__referred_by=selected_doctor,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            total_patients_referred = filtered_bills.count()
            total_bill_amount = filtered_bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            doctor_share_amount = total_bill_amount * Decimal('0.20') # 20% share
            period_description = f"Report for Dr. {selected_doctor_name} ({period_description_base})"
        except Doctor.DoesNotExist:
            period_description = f"Doctor not found. ({period_description_base})"

    context = {
        'all_doctors': all_doctors,
        'total_patients_referred': total_patients_referred,
        'total_bill_amount': total_bill_amount,
        'doctor_share_amount': doctor_share_amount,
        'period_description': period_description,
        'current_filter': filter_type,
        'current_doctor_id': int(doctor_id) if doctor_id else None,
        'start_date_val': request.GET.get('start_date', ''),
        'end_date_val': request.GET.get('end_date', ''),
    }
    
    return render(request, 'dashboard/doctor_reports.html', context)

