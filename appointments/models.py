from django.db import models
from patients.models import Patient
# Slot model
class Slot(models.Model):
    
    STATUS_CHOICES = [('available','Available'),
                      ('not available','Not Available')]
    
    date = models.DateField()
    slot_start = models.CharField(max_length=20, null=False, blank= False)
    slot_duration = models.CharField(max_length=20, null=False, blank=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    #doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, default= None)
    created_by = models.CharField( max_length=60, null=False, blank= False)
    
    def __str__(self): # string representation for the Slot model
        return f'Slot_id: {self.id} Created_by: {self.created_by} For: {self.date}'
    
# Appointment model
class Appointment(models.Model):
    STATUS_CHOICES=[('booked', 'Booked'),
                    ('cancelled','Cancelled'),
                    ('rescheduled', 'Rescheduled')]
        
    patient= models.ForeignKey(Patient, on_delete=models.CASCADE)
    #doctor =models.ForeignKey(Doctor, on_delete=models.CASCADE, default =None)
    slot = models.OneToOneField(Slot,on_delete=models.CASCADE)
    slot_time = models.CharField(max_length=20, null=False, blank=False )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    created_at = models.DateTimeField(auto_now= True)
    
    def __str__(self): # string representation for the Appointment model
        return f'Patient id:{self.patient.pid} Patient name: {self.patient.first_name} Patient slot id: {self.slot.id}'