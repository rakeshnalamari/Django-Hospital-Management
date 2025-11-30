import jwt
from clinic_project import settings
from django.http import JsonResponse
from patients.models import Doctor, Patient, Clinic_User
from appointments.views import delete_expired_slots


# JWTMiddleware helper fuctions 
# to get bearer token
def get_token_from_request(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and  auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        return token
    return None

def validate_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload:
            return payload
        return None
    except jwt.ExpiredSignatureError as e:
        return e
    except jwt.InvalidTokenError as e:
        return e
    except jwt.DecodeError as e:
        return e

# JWT Middleware  
class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        
    
        # excluding all paths from JWT token authentication
        excluded_paths =("/admin/", "/login/", "/patient/register/", "/superuser/register/")
        if any(request.path.startswith(path) for path in excluded_paths): # checking if requested paths are starting with exluded paths or not
            return self.get_response(request)
        
        deleted_count = delete_expired_slots(request)
        print(f"Deleted {deleted_count} expired slots.")
        
        # getting token from the request using get_token_from_request function
        token = get_token_from_request(request)
        
        # chekcing if token is none or not 
        if token is None:
            return JsonResponse({'error':'Auth header or Token misising'}, status= 401)
        
        payload= validate_token(token)
        print(payload)
        
        if isinstance(payload, Exception):
            return JsonResponse({'error':f'{payload}'}, status = 401)    
        if 'pid' in payload:
            try:
                patient = Patient.objects.get(pid=payload['pid'])
                request.patient = patient
                request.user = patient.user
                
            except Patient.DoesNotExist:
                return JsonResponse({'error':'Patient not found'}, status = 404)
            return self.get_response(request)
        
        elif 'did' in payload:
            try:
                doctor = Doctor.objects.get(did=payload['did'])
                request.doctor = doctor
                request.user = doctor.user
            except Doctor.DoesNotExist:
                return JsonResponse({'error':'Doctor not found'}, status = 404)
            return self.get_response(request)
        
        elif 'user_id' in payload:
            try:
                user = Clinic_User.objects.get(id = payload['user_id'])
                request.user = user
            except Clinic_User.DoesNotExist:
                return JsonResponse({'error':'Super User not found'}, status = 404)
            return self.get_response(request)
        
        else:
            return JsonResponse({'error': 'Invalid token payload. No user identity found.'}, status=401)

        
