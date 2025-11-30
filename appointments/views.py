import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Slot, Appointment
from patients.models import Doctor


# Doctor view functions,only authenticated Doctors can request
"""
@csrf_exempt
def upcoming_booked_slots(request):
    if request.method !="POST":
        return JsonResponse({'error':'POST method required'}, status = 405)
    
    if hasattr(request, 'doctor') or not request.doctor:
        return JsonResponse({'error':'Only Doctor allowed'}, status = 403)
    
    upcoming_appointments = 

        """



@csrf_exempt
def delete_expired_slots(request):
    today_date = datetime.today().date()
    today_time = datetime.today().time()
    expired_slots = Slot.objects.filter(date__lt=today_date, slot_start__lt=today_time)
    count = expired_slots.count()
    expired_slots.delete()
    return count
    

# This view is used to create slots with a time_duration from certain range of dates
@csrf_exempt
def create_slots(request): 
        if request.method != 'POST':
            return JsonResponse({'error':'POST method required'}, status = 405)
        
        # Allow doctors
        if not (hasattr(request, 'doctor') and request.doctor) or request.user.is_superuser:
            return JsonResponse({'error':'Only Doctors allowed'}, status = 403)
      
        # checking that request body have required fields and values for them 
        requied_data = ["start_date", "end_date", "start_time", "end_time", "slot_duration"]
        data = json.loads(request.body)

        # checking if any of the required field or field value is missing
        if not all(field in data and data[field] for field in requied_data):
            return JsonResponse({'error':'Mandatory fields missing'}, status= 400) 
        
        try:                                   
            start_date_str = data['start_date']
            end_date_str = data['end_date']
            start_time_str = data['start_time']
            end_time_str = data['end_time']
            slot_duration=int( data['slot_duration'].split(' ')[0])
        except:
            return JsonResponse({'error':'Invalid values'}, status = 400)

            
        # checking the date and time fomats while converting datetime strings into datetime object
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%I:%M %p").time()
            end_time = datetime.strptime(end_time_str, "%I:%M %p").time()
        except:
            return JsonResponse({'error':'Ivalid formats'}, status = 400)
        
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time().replace(second=0, microsecond=0)
        
        try:
            if end_date <=current_date:
                if start_date <= current_date:
                    if start_time < current_time:
                        return JsonResponse({'error':f'Starting date time should be after {current_date} {current_time}'}, status = 400)
                return JsonResponse({'error':f'End date must greater than {current_date}'})
        except:
            return JsonResponse({'error':f'Start date and End dates must be after {current_date}'})    
            
        # storing the requested slot duration in slot_duration_time              
        slot_duration_time = timedelta(minutes= slot_duration)

        # checking if requested start date id greater then requested end date or not
        if start_date > end_date :
            return JsonResponse({'error': 'Start date must be Lessthan End date'})
        # checking if requested start_time is greater than or equal to end_time
        if datetime.combine(start_date, start_time) >= datetime.combine(end_date, end_time):
            return JsonResponse({'error': 'Start time should be Lessthan and not equal to End time'})
        
        current_date = start_date # assuming start_date as current_date
        
        slots= Slot.objects.filter(date__range=(start_date, end_date))
        
        new_slot_start_datetime = datetime.combine(start_date, start_time)
        new_slot_end_datetime = datetime.combine(start_date, end_time)

        for slot in slots:
            old_slot_start = datetime.strptime(slot.slot_start, "%I:%M %p").time()
            old_slot_start_datetime = datetime.combine(slot.date, old_slot_start) 
            old_slot_end_datetime = old_slot_start_datetime + timedelta(minutes=int(slot.slot_duration.split(" ")[0]))
            
            if(new_slot_start_datetime < old_slot_end_datetime and new_slot_end_datetime > old_slot_start_datetime):
                return JsonResponse({'error':f'You already created slots upto {old_slot_end_datetime.date()} {old_slot_end_datetime.time().strftime("%I:%M %p")}'}, status = 400)        
                #print(str(s))
                #if s:
                #return JsonResponse({'error':'Already created slots for this date, You can update them if you want'})
        current_datetime = datetime.combine(start_date, start_time)
        end_datetime = datetime.combine(end_date, end_time)
        
        if start_date != end_date: 
                if current_datetime >= end_datetime:
                    return JsonResponse({'error':'Slot duration is greater than requested slot timing'}, status = 400)
            
        while current_date <= end_date: # loop continues till current_date is equal to end_date
            current_start_datetime =datetime.combine(current_date, start_time)# combining current_date with start_time to get full datetime object
            current_end_datetime = datetime.combine(current_date, end_time) # combining current_date with end_time to get full datetime object

            # loop continues for  current_start_datetime + slot_duration_time less than or equal to current_end_datetime   
            
            while current_start_datetime + slot_duration_time <= end_datetime:
                    
                slot_start_str = current_start_datetime.strftime("%I:%M %p") # converting newly assigned current_start_datetime into string and assigning to slot_start_str
                    
                # checking if the slot object already exist for current_date and slot_start_str in this loop
                if not Slot.objects.filter(date = current_date, slot_start = slot_start_str).exists():
                        
                    #creating new slot if not already exist
                    Slot.objects.create(
                        date=current_date,
                        slot_start = slot_start_str,
                        slot_duration = f'{slot_duration} min',
                        created_by = request.user.username
                    )
                        
                current_start_datetime +=slot_duration_time # within the innerloop, current_start_datetime is getting incremented by slot_duration_time 
                        
            current_date += timedelta(days = 1) # within the outer loop, current_date is incrementing by 1 day of timedelta
            
        return JsonResponse({'message':'Slots created successfully'}, status = 201) # success message for create_slots


# This view is used to view all the slots created by the requested admin
@csrf_exempt
def created_slots(request):
    if request.method !='GET':
        return JsonResponse({'error':'GET method required'}, status = 405)

    # Allow doctors
    if not (hasattr(request, 'doctor') and request.doctor) or request.user.is_superuser:
        return JsonResponse({'error':'Only Doctors allowed'}, status = 403)
    
    # getting all the slots created by the requested user
    s = list(Slot.objects.filter(created_by = request.user.username).values())
    
    # checking if any slots are created previously by the requested user or not  
    if s is None:
        return JsonResponse({'error':f'No slots are created by {request.user.username}'}) 

    # if created, showing all the created slots by requested user 
    return JsonResponse({f'Slots created by admin: {request.user.username}':s}, safe =False)
    


# To create a single slot     
@csrf_exempt
def create_slot(request):
    if request.method != "POST":
        return JsonResponse({'error':'POST method required'}, status = 405)

    # Allow doctors
    if not (hasattr(request, 'doctor') and request.doctor) or request.user.is_superuser:
        return JsonResponse({'error':'Only Doctors allowed'}, status = 403)
    
    data = json.loads(request.body)
    
    # checking requested data fields had valid values or not
    try:    
        date_str = data['date']
        slot_time_str = data['slot_time']
        slot_duration = int(data['slot_duration'].split(' ')[0])
    except Exception as e: 
        return JsonResponse({'error':f'Invalid values: {e}'}, status =400)  

    
    # checking the date and time formats are valid or not 
    try:
        date = datetime.strptime(date_str,"%Y-%m-%d").date()
        slot_time =  datetime.strptime(slot_time_str, "%I:%M %p").time()
    except:
        return JsonResponse({'error':'Invalid format of date or time'}, status = 400)
    
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    current_time = current_datetime.time().replace(second=0, microsecond=0)
        
    if date <= current_date:
        if slot_time < current_time:
            return JsonResponse({'error':f'Starting date time should be after {current_date} {current_time}'}, status = 400)

    
    # creating a full datetime by using given date and slot_time as slot_time_datetime
    slot_time_datetime = datetime.combine(date, slot_time)
    # adding timedelta of slot_duration to get slot_end_datetime
    slot_end_datetime = slot_time_datetime + timedelta(minutes=slot_duration)
    
    # getting all the existing slots by using the requested date
    existing_slots = Slot.objects.filter(date=date)
    
    # looping though all the slot objects
    for slot in existing_slots:
        
        existing_start = datetime.combine(slot.date, datetime.strptime(slot.slot_start, "%I:%M %p").time()) # creating full datetime from the existing slot date and slot_start in existing_start
        existing_end = existing_start+ timedelta(minutes=int(slot.slot_duration.split(' ')[0])) # adding existing slot's slot_duration to existing_start and getting existing_end 
        
        if slot_time_datetime < existing_end and existing_start < slot_end_datetime: # checking if the newly creating slot overlaping with the existing slot timing    
            return JsonResponse({'error':'Slot exists and not completed yet'}, status = 400)
        
    
    slot_time_str= slot_time.strftime("%I:%M %p")
    # checking if the slot already exist with the exact date and slot_time or not 
    if Slot.objects.filter(date = date, slot_start= slot_time_str).exists():
        return JsonResponse({'error':'Slot already exists for given date and time'}, status= 400)
    
    # creating new slot
    Slot.objects.create(
        date = date,
        slot_start = slot_time_str,
        slot_duration = f'{slot_duration} min',
        created_by = request.user.username
    )        
    return JsonResponse({'message':'Slot created successfully'}, status =200) # success message of slot created


# To update a slot which is already created by the requested user 
@csrf_exempt
def update_slot(request):
    if request.method != "PUT":
        return JsonResponse({'error':'PUT method required'}, status =405)

    # Allow doctors
    if not (hasattr(request, 'doctor') and request.doctor) or request.user.is_superuser:
        return JsonResponse({'error':'Only Doctors allowed'}, status = 403)
    
    # checking if the request body missing any required field or value 
    try :
        data = json.loads(request.body)
        old_date_str = data['old_date']
        new_date_str = data['new_date']
        old_slot_start_str = data['old_slot_start_time']
        new_slot_start_str = data['new_slot_start_time']
        status = data['status']
        new_slot_duration = int(data['slot_duration'].split(" ")[0])
    except :
        return JsonResponse({'error':'Invalid details'}, status=400)
    
    # checking the date and time formats of requested date and time
    try:
        old_date = datetime.strptime(old_date_str, "%Y-%m-%d").date()
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
        old_slot_start = datetime.strptime(old_slot_start_str, "%I:%M %p").time()
        old_slot_start_str = old_slot_start.strftime("%I:%M %p")
    except:
        return JsonResponse({'error':'Date or time format wrong'}, status=400)

    # getting slot object where requested date and old_slot_start exist by checking
    try:
        slot =Slot.objects.get(date= old_date, slot_start = old_slot_start_str)
    except Slot.DoesNotExist:
        return JsonResponse({'error':'Slot not exist'}, status =404)
    
    # checking if that slot is created by the requested user or not
    if slot.created_by != request.user.username:
        return JsonResponse({'error':'You are not the creater of thi slot'}, status = 401)
    

    if new_slot_start_str:
        # converting time string to datetime object 
        try:
            new_slot_start = datetime.strptime(new_slot_start_str, "%I:%M %p").time() # string to time
            new_slot_start_str = new_slot_start.strftime("%I:%M %p") # time to string
        except:
            return JsonResponse({'error':'Date or time format wrong'}, status=400)
    
    new_start_datetime = datetime.combine(new_date, new_slot_start) # assigning full datetime to new_start_datetime by combining requested date new_slot_start
    new_end_datetime = new_start_datetime + timedelta(minutes= new_slot_duration) # getting new_end_datetime by adding timedelta of new_slot_duration to new_start_datetime
    
    # getting existing_slots by using the requested date and also excluding the particular slot which is requested to update 
    existing_slots = Slot.objects.filter(date=new_date).exclude(id=slot.id)
    
    # loop through existing_slots
    for updating_slot in existing_slots:
        updating_start = datetime.strptime(updating_slot.slot_start, "%I:%M %p").time() # getting old_start's time object from existing slots
        updating_start_datetime = datetime.combine(new_date, updating_start) # combing date and old_start as full datetime in old_start_datetime
        updating_end_datetime = updating_start_datetime + timedelta(minutes=int(updating_slot.slot_duration.split(" ")[0])) # incrementing the old_start_datetime by using the timedelta of existing_slot's slot_duration to get old_end_datetime
    
        # checking if newly updating slot timing is being overlapped with the existing slot timming or not for all existing slots
        if new_start_datetime < updating_end_datetime and updating_start_datetime < new_end_datetime:
            return JsonResponse({'error':'New slot timing is already exist'}, status =400)
    
    
    #updating new date
    if new_date:
        slot.date = new_date
    # updating new slot_start if requested
    if new_slot_start_str:
        slot.slot_start = new_slot_start_str
    
    # updating status if given
    if status in['available','not available']:
        slot.status = status
        
    # updating slot_duration if given
    if new_slot_duration is not None:
        slot.slot_duration = f'{new_slot_duration} min'
    
    slot.save()
    return JsonResponse({'message':'Slot Updated succesfully'}, status =200) # success message for slot updation
    

# To delete a slot which is created by the requested user
@csrf_exempt
def delete_slot(request):
    if request.method != 'DELETE':
        return JsonResponse({'error':'DELETE method required'}, status= 405)

    # Allow doctors
    if not (hasattr(request, 'doctor') and request.doctor) or request.user.is_superuser:
        return JsonResponse({'error':'Only Doctors allowed'}, status = 403)
    
    data = json.loads(request.body)
    # checking request body have required fields and related values or not
    try:
        date_str = data['date']
        slot_starts_str =data['slot_starts']
    except:
        return JsonResponse({'error':'Required data(date or slot_starts) missing'}, status = 400)
    
    if not isinstance(slot_starts_str, list):
        slot_starts_str= list(slot_starts_str)
        
    count = 0
    # checking if the date and time format is valid or not
    for i in slot_starts_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slot_start =datetime.strptime(i, "%I:%M %p").time()
        except:
            return JsonResponse({'error':f'Date or time format wrong for {date} {i}'}, status=400)
            
                
        slot_start_str= slot_start.strftime("%I:%M %p") # time object to string

        # checking if slot exist with the requested date and slot_start or not
        try:
            slot= Slot.objects.get(date = date, slot_start=slot_start_str)
        except Slot.DoesNotExist:
            continue
        # checking if the requested slot is created by the requested user or not
        if slot.created_by != request.user.username:
            return JsonResponse({'error':'You are not the creater of these slots'}, status = 401)
        count+=1
        slot.delete() 
            
    if count == 1:
        return JsonResponse({'message':'Slot deleted Successfully'}, status =200) # success message of slot deletion
    else:
        return JsonResponse({'message':'Selected and existing slots deleted successfully'}, status = 200)


@csrf_exempt
def upcoming_appontments(request):
    if request.method != 'GET':
        return JsonResponse({'error':'GET method required'}, status= 405)

    # checking if the requested user is a doctor or not (by using OneToOne user)
    if not (hasattr(request, 'doctor') and request.doctor) or request.user.is_superuser:
        return JsonResponse({'error':'Only Doctors allowed'}, status = 403)
    
    doctor =  Doctor.objects.get(did = request.doctor.did)
    appointments = Appointment.objects.filter( slot__created_by=doctor.user.username, status__in=['booked', 'rescheduled'])
    data = []
    for app in appointments:
        data.append({
            "patient_name": f"{app.patient.first_name} {app.patient.last_name}",
            "slot_id": app.slot.id,
            "slot_date": app.slot.date,
            "slot_start": app.slot.slot_start,
            "status": app.status,
        })
    return JsonResponse({f"Upcoming appointments for {doctor.user.username}": data}, status = 200)


# Patient views functions, only authenticated Patients can request 
# To get the available slots in a range of dates
@csrf_exempt
def available_slots(request):
    if request.method != "POST":
        return JsonResponse({'error':'POST method required'}, status = 405)

    # checking if the requested user is a patient or not (by using OneToOne user)
    if not hasattr(request, 'patient') or not request.patient:
        return JsonResponse({'error':'Only Patient allowed'}, status = 403)

    data = json.loads(request.body)
    # checking if the requested data have required fields and values relatively
    try:
        start_date_str = data['start_date']
        end_date_str = data['end_date']
    except:
        return JsonResponse({'error':'Missing required data'}, status =400)
    
    # checking the format of requested date and time is valid or not
    try:
        start_date = datetime.strptime(start_date_str,"%Y-%m-%d").date() # string to date obj
        end_date = datetime.strptime(end_date_str,"%Y-%m-%d").date()  # string to date object
    except:
        return JsonResponse({'error':'Invalid Foramat of date or time'}, status = 400)
    
    if not start_date > datetime.today().date():
        return JsonResponse({'error':f'Checking for the expired slots, please check from {datetime.today().now()}'}, status = 400) 
    
    
    # filtering all the values of all the slots from a date range between requested dates wiht status having available
    slots= Slot.objects.filter(date__range =[start_date, end_date], status = 'available').values()
    
    # checking if there are no slots available for the requested dates 
    if not slots:
        return JsonResponse({'error':'No slots are available for the requested date'}, status= 400)
    
    # if available, they are displayed in list format
    return JsonResponse({f'Available slots between {start_date} and {end_date} are ': list(slots)}, safe= False, status=200)


# To book an appointment 
@csrf_exempt
def book_appointment(request):
    if request.method!="POST":
        return JsonResponse({'error':'POST method required'}, status = 405)
    
    # checking if the requested user is a patient or not (by using OneToOne user)
    if not hasattr(request, 'patient') or not request.patient:
        return JsonResponse({'error':'Only Patient allowed'}, status = 403)

    data = json.loads(request.body)
    
    # checking if the requested body have required fields and values relatively 
    try:
        date_str= data['date']
        slot_start_str = data['slot_start']
    except:
        return JsonResponse({'error':'Invalid request data'}, status = 400)
    
    # checking the format of requested dates and times valid or not 
    try: 
        date = datetime.strptime(date_str, "%Y-%m-%d").date() # string to date object
        slot_start = datetime.strptime(slot_start_str, "%I:%M %p").time() # string to time object
        slot_start_str=slot_start.strftime("%I:%M %p") # time object to string
    except:
        return JsonResponse({'error':'Formmat missing'}, status =400)
    
    if not date > datetime.today().date() and not slot_start > datetime.today().time():
        return JsonResponse({'error':f'Booking for the expired slots, please check from {datetime.today().date()}'}, status = 400) 

    
    # checking the slot exists or not
    try:
        slot = Slot.objects.get(date= date, slot_start=slot_start_str, status = 'available') # getting slot object using the requested date, slot_start and with status, available
    except:
        return JsonResponse({'error':'slot not available'}, status = 404)
    
    # creating new appointment with selected available slot with status booked
    Appointment.objects.create(
        patient=request.patient,
        slot=slot,
        slot_time= slot_start_str,
        status='booked'
    )
    slot.status ='not available' # booked slot status updated to 'not available'
    slot.save()
    return JsonResponse({'message':'Slot booked successfully'}, status = 200) # success mesasage when slot is booked successfully

# To get all the booked appointments by the patient
@csrf_exempt
def booked_appointments(request):
    if request.method !="GET":
        return JsonResponse({'error':'GET method required'}, status = 401)
    
    # checking if the requested user is patient or not
    if not hasattr(request, 'patient')or not request.patient:
        return JsonResponse({'error':'Only Patient allowed'}, status = 403)
    
    # getting all the appointments with status 'booked' and booked by the requested user(patient)
    appointments = Appointment.objects.filter(patient = request.patient, status ='booked').values()
    
    # checking whether no slots are booked
    if appointments is None:
        return JsonResponse({'error':'No slots booked'}, status = 404)
    
    # returning all the booked slots by the user(patient)
    return JsonResponse({f'These are all slots booked by Patient {request.user.username}': list(appointments)}, status= 200, safe = False)
    
# To cancel the appointment booked by the user(patient)
@csrf_exempt
def cancel_appointment(request):
    if request.method !="PUT":
        return JsonResponse({'error':'PUT method required'}, status = 401)
    
    # checking if the requested user is patient or not
    if not hasattr(request, 'patient') or not request.patient:
        return JsonResponse({'error':'Only Patient allowed'}, status = 403)
    
    data = json.loads(request.body)
    
    # checking the requested body have required fields and values relatively or not
    try:        
        date_str = data['date']
        slot_start_str= data['slot_start']
    except :
        return JsonResponse({'error':'Missing required data'}, status= 400)
    
    # checking the requested date and time formats valid or not
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date() # string to date object
        slot_start = datetime.strptime(slot_start_str, "%I:%M %p").time() # string to time object
        slot_start_str =slot_start.strftime("%I:%M %p") # time obj to string
    except:
        return JsonResponse({'error':'Invalid format of data'}, status= 400)
    
    # checking the appointment exists or not
    try:
        # getting appointment all the conditions mathched with
        appointment = Appointment.objects.get(patient= request.patient, slot__date= date, slot_time= slot_start_str, status = 'booked' )
    except:
        return JsonResponse({'error':'Appointment not exists'}, status =404)
     
    # after getting appointed object successfully 
    appointment.status = 'cancelled' # status updated to cancelled
    appointment.save()
    
    # also updating the slot linked to the cancelled appointment        
    slot=appointment.slot 
    slot.status = 'available' # updating satus to 'available'
    slot.save()
    return JsonResponse({'message':'Appointment cancelled successfully'}, status= 200) # success message of Appointment Cancellation
        

# To reschedule the booked appointment to other available dates        
@csrf_exempt
def reschedule_appointment(request):
    if request.method !="PUT":
        return JsonResponse({'error':'PUT method required'}, status =401)
    
    # checking if the requested user is patient or not
    if not hasattr(request, 'patient') or not request.patient:
        return JsonResponse({'error':'Olny Patient allowed'})
    
    data = json.loads(request.body)
    
    # checking the requested data have required fields and values reltively or not
    try:
        old_date_str= data['old_date']
        old_slot_start_str= data['old_slot_start']
        new_date_str = data['new_date']
        new_slot_start_str = data['new_slot_start'] 
    except:
        return JsonResponse({'error':'Required data missing'}, status = 400)
    
    # checking requseted date and time formats valid or not 
    try:
        old_date = datetime.strptime(old_date_str, "%Y-%m-%d").date() # string to date object
        old_slot_start = datetime.strptime(old_slot_start_str, "%I:%M %p").time() # string to time object 
        old_slot_start_str = old_slot_start.strftime("%I:%M %p") # time object to string
    except:
        return JsonResponse({'error':'Invalid Format for old date or time'}, status = 400)
    
    # checking if the appoinment exist or not
    try:
        # getting appointmet object with all the conditions
        appointment =Appointment.objects.get(patient = request.patient, slot__date = old_date, slot_time= old_slot_start_str, status ='booked', slot__status='not available')
    except:
        return JsonResponse({'error':'Appointment not exist'}, status = 404)
    
    # checking date and time formats valid or not
    try:
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date() # string to date object
        new_slot_start = datetime.strptime(new_slot_start_str, "%I:%M %p").time() # string to time object
        new_slot_start_str = new_slot_start.strftime("%I:%M %p") # time object to string
    except:
        return JsonResponse({'error':'Invalid Format for new date and time'}, status = 400)
    
    # checking slot exists or not
    try:
        # getting new_slot object from Slot model with all the conditions
        new_slot = Slot.objects.get(date= new_date, slot_start=new_slot_start_str, status ='available')
    except:
        return JsonResponse({'error':'slot not available'}, status = 404)
    
    old_slot = appointment.slot #assigning slot linked with appointment fetched as old_slot
    
    old_slot.status = 'available' # updated old_slot's status with 'available'
    old_slot.save()
    
    new_slot.status = 'not available' # updating new_slot's status with 'not available'
    new_slot.save()

    # upadating selected appointment
    appointment.slot_time = new_slot_start_str # upadating slot_time new slot_start
    appointment.slot= new_slot  # updating new_slot with old_slot
    appointment.status = 'rescheduled' # updating status with 'rescheduled' 
    appointment.save()

    return JsonResponse({'message':'Rescheduled successfully'}, status = 200) # success message of Appointment Rescheduling 
    
    