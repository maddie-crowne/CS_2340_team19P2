from django.urls import path, include
from . import views, admin
from .views import (
    spotify_login,
    spotify_callback,
    wrapped,
    select,
    invite,
    duo,
    account,
)

app_name = 'wrapped'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),  # If you're using Django's auth
    path('wrapped/', views.wrapped, name='wrapped'),
    path('spotify/login/', views.spotify_login, name='spotify_login'),  # Ensure this matches the login URL
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),  # Callback URL pattern
    path('account/', views.account, name='account'),
    path('select/', views.select, name='select'),
    path('invite/', views.invite, name='invite'),
    path('duo/', duo, name='duo'),
]