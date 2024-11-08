from django.urls import path, include
from . import views

app_name = 'wrapped'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('', views.wrapped, name='wrapped'),
    path('spotify-login', views.user_spotify_login, name='spotify_login'),
    path('due-login', views.user_spotify_login_duo, name='due_login'),
    path('loginWithSpotify/', views.user_spotify_login, name='user_spotify_login'),
    path('loginWithSpotifyDuo/', views.user_spotify_login_duo, name='user_spotify_login_duo'),
    path('account/', views.account, name='account'),
    path('view-saved-wrap/<int:wrap_id>', views.view_saved_wrap, name='view_saved_wrap'),
    path('delete-wrap/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('select/', views.select, name='select'),
    path('invite/', views.invite, name='wrappedInvite'),
    path('duo/', views.duo, name='duo'),
]