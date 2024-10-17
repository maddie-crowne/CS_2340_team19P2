from django.urls import path
from . import views

app_name = 'wrapped'

urlpatterns = [
    path('select', views.select, name='select'),
    path('', views.wrapped, name='wrapped'),
    path('duo', views.duo, name='duo'),
    path('invite', views.invite, name='invite'),
    path('account', views.account, name='accountInfo'),
]
