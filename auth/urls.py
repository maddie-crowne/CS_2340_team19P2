from django.urls import path
from . import views
app_name = 'auth'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
]
