"""BillDesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from Predictions.views import showPredict

urlpatterns = [
    url(r'^admin/', admin.site.urls),
 	url(r'^DashBoard/', include('DashBoard.urls')),
	url(r'^Accounts/', include('Accounts.urls')),
	url(r'^Accounts/', include('Accounts.urls_django_auth')),
	url(r'^adminpanel/', include('adminpanel.urls')),
	url(r'^DashBoard/showPrediction', showPredict),
]
