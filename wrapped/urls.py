from django.urls import path, include
from . import views

app_name = 'wrapped'

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('', views.wrapped, name='wrapped'),
    path('loginWithSpotify/', views.user_spotify_login, name='user_spotify_login'),
    path('account/', views.account, name='account'),
    path('view-saved-wrap/<int:wrap_id>', views.view_saved_wrap, name='view_saved_wrap'),
    path('delete-wrap/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('view-saved-duo-wrap/<int:wrap_id>', views.view_saved_duo_wrap, name='view_saved_duo_wrap'),
    path('delete-duo-wrap/<int:wrap_id>/', views.delete_duo_wrap, name='delete_duo_wrap'),
    path('select/', views.select, name='select'),
    path('invite/', views.invite, name='invite'),
    path('spotify/login/', views.duo_spotify_login, name='duo_spotify_login'),
    path('duo/', views.duo, name='duo'),
    path('contactTheDevelopers', views.contact_developers, name='contact_developers'),  # Updated here
]
