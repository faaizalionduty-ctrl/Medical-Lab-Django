from django.contrib import admin

# Register your models here.
from .models import Patient, Bill

admin.site.register(Patient)
admin.site.register(Bill)