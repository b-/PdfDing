"""
URL configuration for pdfding project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.urls import include, path
from pdf.views.pdf_views import redirect_overview

# to do exclude not needed allauth urls
urlpatterns = [
    path('admin/', include('admin.urls')),
    path('account', include('allauth.urls')),
    path('', redirect_overview, name='home'),
    path('profile/', include('users.urls')),
    path('pdf/', include('pdf.urls')),
]
