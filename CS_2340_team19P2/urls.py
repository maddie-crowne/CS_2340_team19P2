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
from django.conf.urls.i18n import i18n_patterns, set_language

from . import views

# Main urlpatterns for non-language-specific URLs (e.g., admin)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)),
    path('i18n/setlang/', set_language, name='set_language'),
]

# Language-specific URLs using i18n_patterns
urlpatterns += i18n_patterns(
    path('auth/', include('auth.urls')),  # Auth URLs with language prefix
    path('spotify/login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('wrapped/', include('wrapped.urls')),  # Wrapped URLs with language prefix
)
