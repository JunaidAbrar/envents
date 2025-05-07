from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    path('', views.venue_list, name='venue_list'),
    path('<slug:slug>/', views.venue_detail, name='venue_detail'),
    path('category/<slug:category_slug>/', views.venue_list_by_category, name='venue_list_by_category'),
    path('search/', views.venue_search, name='venue_search'),
    path('<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<slug:slug>/submit-review/', views.submit_review, name='submit_review'),
]