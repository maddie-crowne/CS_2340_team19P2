"""
URL configuration for CS_2340_team19P2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from . import views
from .views import spotify_login, spotify_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)),
    path('auth/', include('auth.urls')),
    path('wrapped/', views.wrapped, name='wrapped'),
    path('wrapped', include('wrapped.urls')),
    path('contactTheDevelopers', views.contactDevelopers, name='contactDevelopers'),
    path('spotify/login/', spotify_login, name='spotify_login'),
    path('callback/', spotify_callback, name='spotify_callback'),
    path('account/', views.account, name='account')
]
