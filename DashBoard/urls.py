
from django.conf.urls import url,include
from django.contrib import admin
from . import views
app_name = 'DashBoard'

urlpatterns = [
    url(r'^$',views.index,name='index'),
    url(r'^test/$',views.test,name='test'),
    url(r'^modify/$',views.modify,name='modify'),
    url(r'^add/$',views.add,name='add'),
    url(r'^addinven/$',views.addinven,name='addinven'),
    url(r'^register/$',views.register,name='register'),
    url(r'^placeorder/$',views.placeorder,name='placeorder'),
    url(r'^autocompleteinven/$',views.autocompleteinven,name='autocompleteinven'),
    url(r'^autocompletecusto/$',views.autocompletecusto,name='autocompletecusto'),
    url(r'^confirm/(?P<w_id>[0-9]+)/$',views.confirm,name='confirm'),
	url(r'^adduser/confirm/(?P<w_id>[0-9]+)/$',views.confirm,name='confirm'),
	url(r'^changeData/$',views.changedata,name='changedata'),
]
