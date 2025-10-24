from django.db import models
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
    # --- NEW FIELD ---
    referred_by = models.ForeignKey(
        Doctor, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    # -----------------
    def __str__(self):
        return self.name

class Bill(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    tests = models.ManyToManyField(Test)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill {self.id} for {self.patient.name}"

    def save(self, *args, **kwargs):
        # We will calculate total and net amount in the view, 
        # but this is a good place to ensure net_amount is always correct
        self.net_amount = self.total_amount - self.discount
        super().save(*args, **kwargs)