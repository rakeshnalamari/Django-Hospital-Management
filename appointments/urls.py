from django.urls import path
from appointments import views 
urlpatterns = [

    # Admin urls
    path('slots/', views.created_slots, name= 'created_slots'), # path to created_slots view
    path('slots/create_all/', views.create_slots, name='create_slots'), # path to create_slots view
    path('slots/create/', views.create_slot, name = 'create_slot'), # path to created_slot view
    path('slots/update/', views.update_slot, name= 'update_slot'), # path to update_slot view
    path('slots/delete/', views.delete_slot, name='delete_slot'), # path to dalete_slot view   
    path('appointments/upcoming/', views.upcoming_appontments, name = 'upcoming_appointments')
]