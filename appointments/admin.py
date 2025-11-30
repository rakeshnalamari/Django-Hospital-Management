from django.contrib import admin
from .models import Slot, Appointment

# Register your models here.

admin.site.register(Slot) # registering Slot model to admin site
admin.site.register(Appointment) # registering Appointment model to admin site