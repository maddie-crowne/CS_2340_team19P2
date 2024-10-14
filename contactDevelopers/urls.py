from django.urls import path
from . import views

app_name = 'contactDevelopers'

urlpatterns = [
    path('', views.contactDevelopers, name='contactDevelopers'),
]
