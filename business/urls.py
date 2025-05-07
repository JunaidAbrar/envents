from django.urls import path
from . import views

app_name = 'business'

urlpatterns = [
    path('', views.BusinessDashboardView.as_view(), name='dashboard'),
    path('venue/submit/', views.VenueSubmissionView.as_view(), name='submit_venue'),
    path('service/submit/', views.ServiceSubmissionView.as_view(), name='submit_service'),
]