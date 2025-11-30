from django.db import models
from datetime import datetime
#from django.contrib.auth.models import User


class Clinic_User(models.Model):
    
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    username = models.CharField(max_length = 60 , unique= True, null=False, blank=False)
    password =models.CharField(max_length = 100, unique= True, null=False, blank=False)
    is_staff = models.BooleanField(default= False)
    is_superuser = models.BooleanField(default= False)
    date_joined = models.DateTimeField(auto_now= True, null=True)
    is_logged_in = models.BooleanField(default=False,null=True)
    request_count = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.username    
    
class Doctor(models.Model):
    did = models.CharField(max_length=10,unique=True)
    user = models.OneToOneField(Clinic_User, on_delete=models.CASCADE, related_name='doctor')
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    specialization = models.CharField(max_length= 50, null=False, blank= False)
    ph_number = models.BigIntegerField(unique=True, null=False)
    email = models.EmailField(max_length= 100, null= False, blank= False)
    created_at = models.DateField()
    
    
    # generates created_at by using datetime
    @staticmethod   
    def at():
        return datetime.today().replace(microsecond=0) # replacing milliseconds with 0 from datetime.today()--> (generate current date and time)

        
# Create your models here.
# Patient model
class Patient(models.Model):
    
    pid = models.CharField(max_length=10,unique=True)
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    user=models.OneToOneField(Clinic_User, on_delete=models.CASCADE, related_name='patient')
    dob = models.DateField(null=True, blank=True)
    age = models.IntegerField()
    ph_number = models.BigIntegerField(unique=True, null=False)
    email = models.EmailField(unique=True ,null=False, blank= False)
    blood_group = models.CharField(max_length=5, default=None, null=False, blank=False)
    created_at= models.DateField()
    
    # generates created_at by using datetime
    @staticmethod   
    def at():
        return datetime.today().replace(microsecond=0) # replacing milliseconds with 0 from datetime.today()--> (generate current date and time)
          
    
    # generates age using dob
    def calculate_age(dob):
        today = datetime.today()
        
        # dob exists or not
        if dob:
            # calculating the age by comparing dob and request date time
            age = today.year - dob.year -((today.month, today.day) < (dob.month, dob.day)) #if the month and day at the time of request is less than that of dob is taken as 0 
            return age
        return None
    
    # string representation for Patient model
    def __str__(self):
        return f'Patient id: {self. pid} Name: {self.first_name + " " + self.last_name}'
    