from decimal import Decimal
from django.db import models
from django.db.models import Sum
from labtests.models import Test
from doctors.models import Doctor

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # --- NEW FIELD ---
    referred_by = models.ForeignKey(
        Doctor, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    # -----------------
    def __str__(self):
        return f"{self.name} -- referred by : {self.referred_by.name if self.referred_by else 'N/A'}"

class Bill(models.Model):
    # REMOVED payment_status
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    tests = models.ManyToManyField(Test)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bill {self.id} for {self.patient.name}"

    def save(self, *args, **kwargs):
        # Always recalculate net_amount on save
        self.net_amount = self.total_amount - self.discount
        super().save(*args, **kwargs)

    # --- NEW PROPERTIES ---
    
    @property
    def total_paid(self):
        # Calculate total paid by summing all related transactions
        total = self.transactions.aggregate(total=Sum('amount'))['total']
        return total or Decimal('0.00')

    @property
    def amount_due(self):
        # Calculate amount due based on net_amount and total_paid
        return self.net_amount - self.total_paid

    @property
    def payment_status(self):
        # Calculate status dynamically
        paid = self.total_paid
        if paid >= self.net_amount:
            return "Paid"
        elif paid > 0:
            return "Partially Paid"
        else:
            return "Pending"

# --- NEW MODEL ---

class PaymentTransaction(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rs. {self.amount} for Bill {self.bill.id}"
# ```

# **CRITICAL STEP:** After saving this, you MUST run migrations:
# ```bash


class Expense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.description} - Rs. {self.amount}"