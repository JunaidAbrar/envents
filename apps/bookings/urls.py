from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    # Service booking should come before venue booking to avoid conflicts
    path('create/service/', views.create_service_booking, name='create_service_booking'),
    path('create/<slug:venue_slug>/', views.create_booking, name='create_booking'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/add-services/', views.add_services, name='add_services'),
    path('<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('<int:booking_id>/accept-quotation/', views.accept_quotation, name='accept_quotation'),
]