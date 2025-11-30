from django.contrib import admin
from .models import Patient, Doctor, Clinic_User
# Register your models here.

admin.site.register(Patient) # registering Patient model to admin site
admin.site.register(Doctor) # registering Doctor model to admin site
admin.site.register(Clinic_User) # registering Clinic_User model to admin site