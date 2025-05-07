from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),
    path('category/<slug:category_slug>/', views.service_list_by_category, name='service_list_by_category'),
    path('search/', views.service_search, name='service_search'),
    path('<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<slug:slug>/submit-review/', views.submit_review, name='submit_review'),
]