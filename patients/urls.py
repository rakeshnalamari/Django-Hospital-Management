from django.urls import path
from patients import views
from appointments import views

urlpatterns = [
    # patients urls 
    path('slots/available/', views.available_slots, name='available_slots'), # path to available_slots view
    path('appointments/book/', views.book_appointment, name='book_appointment'), # path to book_appointment view
    path('appointments/my_bookings/', views.booked_appointments, name='booked_appointments'), # path to booked_appointments view
    path('appointments/cancel/', views.cancel_appointment, name='cancel_appointment'), # path to cancel_appointment view
    path('appointments/reschedule/', views.reschedule_appointment, name='reschedule_appointment') # path to reschedule_appointment view
]