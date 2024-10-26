from django.urls import path, include
from . import views, admin

app_name = 'wrapped'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),  # If you're using Django's auth
    path('', views.wrapped, name='wrapped'),
    path('loginWithSpotify/', views.user_spotify_login, name='user_spotify_login'),
    path('account/', views.account, name='account'),
    path('select/', views.select, name='select'),
    path('invite/', views.invite, name='invite'),
    path('duo/', views.duo, name='duo'),
]