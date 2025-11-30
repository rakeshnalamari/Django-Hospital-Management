"""
URL configuration for clinic_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from patients import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.user_login, name = "user_login"),
    path('logout/', views.user_logout, name= "user_logout"),
    
    # Redirecting to patients.urls
    path('patients/', include('patients.urls')),
    path('patient/register/',views.patient_registration, name='patient_registration'),

    # superuser view paths 
    path('superuser/register/', views.superuser_registration, name = "superuser_registration"),
    path('doctors/delete/', views.remove_doctor, name = 'remove_doctor'),
    path('doctors/list/', views.doctors_list, name = 'doctors_list'),
    
    # Redirect to appointments.urls
    path('doctors/', include('appointments.urls')),
    path('doctor/register/',views.doctor_registration, name='doctor_registration'),
    
]



