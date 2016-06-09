# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views
# import views

urlpatterns = [

	url(r'^lectura-medidores/list$', views.LecturaMedidorList.as_view(), name='lectura_medidor_list'),
	url(r'^lectura-medidores/new$', views.LecturaMedidorNew.as_view(), name='lectura_medidor_new'),
	url(r'^lectura-medidores/delete/(?P<pk>\d+)$', views.LecturaMedidorDelete.as_view(), name='lectura_medidor_delete'),
	url(r'^lectura-medidores/update/(?P<pk>\d+)$', views.LecturaMedidorUpdate.as_view(), name='lectura_medidor_update'),

]
