# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	url(r'^monedas/list$', views.MonedaList.as_view(), name='moneda_list'),
	url(r'^monedas/new$', views.MonedaNew.as_view(), name='moneda_new'),
	url(r'^monedas/delete/(?P<pk>\d+)$', views.MonedaDelete.as_view(), name='moneda_delete'),
	url(r'^monedas/update/(?P<pk>\d+)$', views.MonedaUpdate.as_view(), name='moneda_update'),

	url(r'^clientes/list$', views.ClienteList.as_view(), name='cliente_list'),
	url(r'^clientes/new$', views.ClienteNew.as_view(), name='cliente_new'),
	url(r'^clientes/delete/(?P<pk>\d+)$', views.ClienteDelete.as_view(), name='cliente_delete'),
	url(r'^clientes/update/(?P<pk>\d+)$', views.ClienteUpdate.as_view(), name='cliente_update'),

]