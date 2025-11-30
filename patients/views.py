import json
import jwt
from django.http import JsonResponse
#from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from clinic_project import settings
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Patient, Doctor, Clinic_User
from django.contrib.auth.hashers import make_password, check_password


def check(username, password):
    try:
        user = Clinic_User.objects.get(username=username)
        
        if not check_password(password, user.password):
            return {'password_error': 'Incorrect password'}
        
        return {'user': user}
    
    except Clinic_User.DoesNotExist:
        return {'username_error': 'Incorrect username'}
    
    
# Helper function to generate payload according to user( Admin or Patient )
def generate_payload(user):
    
    # checking is the user is Admin by using is_staff and is_superuser both true
    if user.is_staff and not user.is_superuser:
        try:
            if hasattr(user, 'doctor'): # checking user object has doctor attribute or not
                doctor = user.doctor # assigning patient object linked to the user to doctor variable 
        except:
            return None, None
        
        # payload generation with user_id, if user is Doctor
        payload = {
            "did":doctor.did,
            
            # using timestamp which is usefull for international time coordnates to compare
            "iat":int(timezone.now().timestamp()), 
            "exp":int((timezone.now() + timedelta(hours = 5)).timestamp())
        } 
        return payload,"Doctor" # returning payload with role('Doctor')
    
    # checking if the user is Patient by using is_staff and is_superuser both False 
    elif not user.is_staff and not user.is_superuser:
        try:
            if hasattr(user, 'patient'): # checking user object has patient attribute or not
                patient = user.patient # assigning patient object linked to the user to patient variable 
        except:
            return None, None 
        
        payload = {
            "pid":patient.pid, #adding pid a patient's payload
            
            # using timestamp which is usefull for international time coordnates to compare
            "iat":int(timezone.now().timestamp()),
            "exp":int((timezone.now() + timedelta(hours= 5)).timestamp())
        }
     
        return payload ,"Patient" # return payload with role('Patient')
    
    elif user.is_staff and user.is_superuser:
        
        payload = {
            "user_id":user.id,
        
            # using timestamp which is usefull for international time coordnates to compare
            "iat":int(timezone.now().timestamp()), 
            "exp":int((timezone.now() + timedelta(hours = 5)).timestamp())
        } 
        return payload,"Superuser"
        
    else: 
        return None ,None # return None for both if fail to generate payload


# Create your views here.

# Doctor registration
@csrf_exempt
def superuser_registration(request):
    if request.method !="POST":
        return JsonResponse({'error':'POST method required'}, status = 405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'Improper Json format'}, status = 400)
    
    required_fields = ["first_name", "last_name", "username", "password"]
    
    if not all(field in data and  data[field] for field in required_fields ):
        return JsonResponse({'error':'Required fields missing'}, status = 400)
    
    first_name = data["first_name"]
    last_name = data["last_name"]
    username = data['username']
    password = data['password']
    
    if Clinic_User.objects.filter(username=username).exists():
        return JsonResponse({'error':'User already exists'}, status = 400)

    password = make_password(password)

    try:
        user= Clinic_User.objects.create(first_name= first_name, last_name= last_name, username= username, password= password, is_staff = True, is_superuser =True)
        return JsonResponse({'message':f'Superuser created successfully with user id: {user.id}'}, status  =200)
    except: 
        return JsonResponse({'error':'Superuser registration failed'}, status = 400) 


@csrf_exempt
def doctor_registration(request):
    
    if request.method !="POST":
        return JsonResponse({'error':'POST method required'}, status = 405)
    
    superuser = Clinic_User.objects.get(id = request.user.id)
    if request.user.username != superuser.username:
        return JsonResponse({'error':'Super user doesnt exist'}, status =  400)
    
    if not request.user.is_staff and not request.user.is_superuser:
            return JsonResponse({'error':'Only Superusers allowed to register doctors'},status = 403)
        
    required_fields = ["first_name", "last_name", "ph_number", "specialization", "email"]
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'Improper Json format'}, status = 400)
    
    if not all(field in data and  data[field] for field in required_fields ):
        return JsonResponse({'error':'Required fields missing'}, status = 400)
    first_name = data["first_name"]
    last_name = data["last_name"]
    specialization = data["specialization"]
    email = data["email"]
    ph_number = data["ph_number"]
        
    username = first_name+"_"+last_name
    if Clinic_User.objects.filter(username=username).exists():
        return JsonResponse({'error':'User already exists'}, status = 400)
        
    password = make_password(first_name+'_'+str(ph_number))
    
    try:
        user= Clinic_User.objects.create( first_name= first_name, last_name= last_name, username= first_name+"_"+last_name, password= password, is_staff = True, is_superuser =False)
        doctor = Doctor.objects.count()
        did = f'did{doctor+1}'
        
        Doctor.objects.create(
            user=user,
            did=did,
            first_name = first_name,
            last_name = last_name,
            specialization = specialization,
            ph_number=ph_number,
            email= email,
            created_at = Doctor.at()
            )
        return JsonResponse({'message':f'Doctor Registered Successfully with did: {did}'}, status = 201) #success meassage of Patient Registration

    except Exception as e:
        return JsonResponse({'error': f'Doctor registration failed: {str(e)}'}, status=400)
        
# Patient registration
# using csrf_exempt to exclude django default session authetication for some view functions  
@csrf_exempt 
def patient_registration(request):
    if request.method !="POST": 
        return JsonResponse({"error":"POST method required"}, status=405)
    
    required_fields = ["first_name", "last_name", "ph_number", "email"]
    data = json.loads(request.body)
    
    # checking if the request body have required fields and values realtively or not 
    if not all(field in data and  data[field] for field in required_fields ):
        return JsonResponse({'error':'Required fields missing'}, status = 400)

    try:    
            # getting the values from request body
            first_name = data["first_name"]
            last_name = data["last_name"]
            dob_str = data["dob"]
            email = data["email"]
            ph_number = data["ph_number"]
            blood_group = data["blood_group"]
            
            username = first_name+"_"+last_name # using first_name and last_name fro username
            if Clinic_User.objects.filter(username=username).exists(): # checking if the user already exist
                return JsonResponse({'error':'Clinic_User already exists'}, status = 400)
            
            password = make_password(first_name+'_'+str(ph_number))
                
            # creating a user object newly registered for patient taking email as password 
            user= Clinic_User.objects.create( first_name= first_name, last_name = last_name, username = first_name+"_"+last_name, password = password, is_staff = False, is_superuser = False)
            
            # generating pid
            patients = Patient.objects.count()  
            pid = f'pid{1000+patients}'
            
            # checking dob format
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date() #dob string to date object
            except:
                return JsonResponse({'error':'Wrong dob format'}, status = 400)

            # creating new patient record 
            Patient.objects.create(
                pid = pid,
                first_name= first_name,
                last_name = last_name,
                user=user,
                dob = dob,
                age= Patient.calculate_age(dob), # calling calculate_age to calculate age by passing dob
                ph_number = ph_number,
                email = email,
                blood_group = blood_group,
                created_at =Patient.at() #calling at() to get current datetime
                
            )
            return JsonResponse({'message':f'Patient Registered Successfully with pid: {pid}'}, status = 201) #success meassage of Patient Registration
        
    except Exception as e:
        return JsonResponse({'error':f'Patient registration failed : {str(e)}'}, status = 400) # Registration fails if required fields missed or Invalid
                 
        
    
# To get logged in using user credentials, create session and generate get token
@csrf_exempt  
def user_login(request):
    if request.method != 'POST':
        return JsonResponse({'error':'POST method required'}, status = 405)
    

    # checking if the request body have the required credentials or not 
    try:
        
        data = json.loads(request.body)
        
        username = data['username']
        password = data['password']
        
        if not username or not password: # checking both username and password exist or not         
            return JsonResponse({'error':'username and password required'}, status = 400)
    except:
        return JsonResponse({'error':'credentials missing'}, status=400)
    
    result = check(username= username, password= password)

    if result and 'username_error' in result:
        print(result['username_error'])
        return JsonResponse({'error': result['username_error']},status=401)

    elif result and 'password_error' in result:
        print(result['password_error'])
        return JsonResponse({'error': result['password_error']},status=401)
    else:
        user = result.get('user')

        if not user:
            print('Unknown user : ',request.user.username)
            
        if Patient.objects.filter(user=user).exists():
            print('Patient :', user)

        elif Doctor.objects.filter(user=user).exists():
            print('Doctor :', user)
            
        elif Clinic_User.objects.filter(username=user.username).exists():
            print('Superuser :', username)
    
    check_user_login = Clinic_User.objects.get(username = user.username)
    if check_user_login.is_logged_in:
        check_user_login.request_count += 1
        if check_user_login.request_count > 1:
            check_user_login.is_logged_in = False
            check_user_login.request_count = 0
            check_user_login.save(update_fields=["is_logged_in", "request_count"])
            return JsonResponse({'message': 'It seems you didn\'t stored the token, login again'}, status=200)

        check_user_login.save(update_fields=["request_count"])
        return JsonResponse({'message': 'You are already logged in'}, status=200)

    login(request, user) # session creation
    if not check_user_login.is_logged_in:
        check_user_login.is_logged_in = True
        check_user_login.request_count = 0  
        check_user_login.save(update_fields=["is_logged_in", "request_count"])

    payload, role = generate_payload(user) # getting generated payload and role usign generate_payload(user) helping function
    
    # checking the payload generated accord to user or None       
    if payload is None:
        return JsonResponse({'error':'Payload not matched'}, status = 400)                            
    
    # if payload generated, here we encode that using secret_key and alogorithm to get a token generated              
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
                                                            
    return JsonResponse({'message':'Logged in Successfully',  # success message, authenticated and token generated successfully
                        'role': role,
                        'username':username,
                        'token':token}, status=200)


# To get logged out
@csrf_exempt
def user_logout(request):
    if request.method !='POST': # POST method is required to logout 
        return JsonResponse({'errror':'POST method required'}, status=405)
    
    requested_user = json.loads(request.body)["username"]
    
    # checking if the requested user is patient or not
    if hasattr(request, 'patient'):
        role ='Patient'
        patient_username= Clinic_User.objects.get(id= request.patient.id).username 
        print(f'JWT belongs to Patient with username : {patient_username}')   
        if patient_username == requested_user:    
            logged_out_user =patient_username
        else:
            return JsonResponse({'error':f'JWT does not belongs to requested Patient with username : {requested_user}'}, status = 403)

    # checking if the requested user is doctor or not
    elif hasattr(request, 'doctor'):    
        role = 'Doctor'
        d=Doctor.objects.get(id= request.doctor.id)
        doctor_username= d.user.username
        print(f'JWT belongs to Doctor with username : {doctor_username}')
        print(f'Requested user\'s username : {requested_user}')
        if doctor_username == requested_user:    
            logged_out_user = doctor_username
        else:
            return JsonResponse({'error':f'JWT does not belongs to requested Doctor with username : {requested_user}'}, status = 403)
    
    else:    
        role = 'Superuser'
        s=Clinic_User.objects.get(id= request.user.id)
        superuser_username = s.username
        print(f'JWT belongs to Superuser with username : {superuser_username}')
        print(f'Requested user\'s username : {requested_user}')
        if superuser_username == requested_user:    
            logged_out_user = superuser_username
        else:
            return JsonResponse({'error':f'JWT does not belongs to requested Superuser with username : {requested_user}'}, status = 403)
    check_user_login = Clinic_User.objects.get(username = request.user.username)
    if not check_user_login.is_logged_in:
        return JsonResponse({'error':'Already logged out, Please try login again',
                             'previous token':request.headers.get('Authorization').split(" ")[1]})
    logout(request) # session logout
    request.session.flush()


    if check_user_login.is_logged_in == True:
        check_user_login.is_logged_in = False
        check_user_login.save()
    
    if logged_out_user:
        print(logged_out_user)
        return JsonResponse({'message': 'Logged out Successfully',
                             'role':role,
                             'username':f'{logged_out_user}'}, status=200)
        
        
@csrf_exempt
def remove_doctor(request):
    
    if request.method !="DELETE":
        return JsonResponse({'error':'DELETE method required'}, status = 405)
    
    superuser = Clinic_User.objects.get(id = request.user.id)
    if request.user.username != superuser.username:
        return JsonResponse({'error':'Superuser doesnt exist'}, status =  400)
    
    if not request.user.is_staff and not request.user.is_superuser:
            return JsonResponse({'error':'Only Superusers allowed to delete doctors'},status = 403)
    data = json.loads(request.body)
    if 'did' in data and not data['did'] or 'username' in data and not data['username']:
        return JsonResponse({'error':'Either did or username must be provided'}, status = 400)
    
    try:
        if data.get('did') and not data.get('username'):
            did = data['did']
            doctor = Doctor.objects.filter(did=did).first()
            if doctor:
                clinic_user = Clinic_User.objects.filter(id=doctor.user.id).first()
                if clinic_user:
                    doctor.delete()
                    clinic_user.delete()
                    return JsonResponse({'message': 'Doctor deleted successfully'}, status=200)
            return JsonResponse({'error': 'Doctor not found, check the details'}, status=404)
        
        elif data.get('username'):
            username = data['username']
            clinic_user = Clinic_User.objects.filter(username=username).first()
            if clinic_user:
                doctor = Doctor.objects.filter(user=clinic_user).first()
                if doctor:
                    doctor.delete()
                clinic_user.delete()
                return JsonResponse({'message': 'Doctor deleted successfully'}, status=200)
            return JsonResponse({'error': 'Doctor not found, check the details'}, status=404)


        elif data.get('did') and data.get('username'):
            did = data['did']
            username = data['username']
            clinic_user = Clinic_User.objects.filter(username=username).first()
            doctor = Doctor.objects.filter(did=did).first()

            if doctor and clinic_user and doctor.user.id == clinic_user.id:
                doctor.delete()
                clinic_user.delete()
                return JsonResponse({'message': 'Doctor deleted successfully'}, status=200)
            return JsonResponse({'error': 'Doctor not found, check the details'}, status=404)
        

        else:
            return JsonResponse({'error': 'did or username must be provided'}, status=400)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)


@csrf_exempt
def doctors_list(request):
    if request.method != "GET":
        return JsonResponse({'error':'GET method required'}, status = 405)
    
    if not request.user.is_superuser:
        return JsonResponse({'error':'Only superusers allowed'}, status = 403)
    
    doctors = Doctor.objects.values().all()
    
    return JsonResponse({'Doctors list:':list(doctors)}, status = 200)
    
        
    