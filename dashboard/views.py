from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count
from patients.models import Bill

def dashboard_view(request):
    today = timezone.now().date()
    
    # 1. Total patients today (counting unique bills)
    total_patients_today = Bill.objects.filter(created_at__date=today).count()
    
    # 2. Total cash/income today (only for 'Paid' bills)
    total_income_today = Bill.objects.filter(
        created_at__date=today, 
        payment_status='Paid'
    ).aggregate(total=Sum('net_amount'))['total'] or 0.00
    
    # 3. Last 5 patients (showing the 5 most recent bills)
    # --- UPDATED QUERY ---
    recent_bills = Bill.objects.order_by('-created_at')[:5].select_related(
        'patient', 
        'patient__referred_by'
    )
    # ---------------------

    context = {
        'total_patients_today': total_patients_today,
        'total_income_today': total_income_today,
        'recent_bills': recent_bills,
    }
    return render(request, 'dashboard/dashboard.html', context)
