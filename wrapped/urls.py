from django.urls import path, include
from . import views

app_name = 'wrapped'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('', views.wrapped, name='wrapped'),
    path('loginWithSpotify/', views.user_spotify_login, name='user_spotify_login'),
    path('account/', views.account, name='account'),
    path('delete-wrap/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('select/', views.select, name='select'),
    path('invite/', views.invite, name='invite'),
    path('duo/', views.duo, name='duo'),
]