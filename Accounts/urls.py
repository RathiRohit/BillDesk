from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

app_name = 'Accounts'
urlpatterns = [
    url(r'^login/$',auth_views.login,{'template_name': 'Accounts/login.html'},name='login'),
	url(r'^logout/$',auth_views.logout, name='logout', kwargs={'next_page': '/Accounts/login'}),
	url(r'^signup/$', views.signup, name='signup'),
	url(r'^adminsignup/$', views.adminsignup, name='adminsignup'),
	url(r'^profile/(?P<username>\w+)$', views.profile, name='profile'),
	url(r'^profileUpdate/$', views.profileUpdate, name='profileUpdate'),
	url(r'^password/$', views.change_password, name='change_password'),
]