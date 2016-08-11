# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	url(r'^clientes/list$', views.ClienteList.as_view(), name='cliente_list'),
	url(r'^clientes/new$', views.ClienteNew.as_view(), name='cliente_new'),
	url(r'^clientes/delete/(?P<pk>\d+)$', views.ClienteDelete.as_view(), name='cliente_delete'),
	url(r'^clientes/update/(?P<pk>\d+)$', views.ClienteUpdate.as_view(), name='cliente_update'),

	# CONEXIÓN
	url(r'^conexion-cliente$', csrf_exempt(views.CONEXION_CLIENTE.as_view()),name='conexion_cliente'),
	url(r'^conexion-concepto$', csrf_exempt(views.CONEXION_CONCEPTO.as_view()),name='conexion_concepto'),
	url(r'^conexion-parametro$', csrf_exempt(views.CONEXION_PARAMETRO.as_view()),name='conexion_parametro'),
	url(r'^conexion-cliente/list$', csrf_exempt(views.CONEXION_CLIENTE.as_view()),name='conexion_cliente'),
	url(r'^conexion-concepto/list$', csrf_exempt(views.CONEXION_CONCEPTO.as_view()),name='conexion_concepto'),
	url(r'^conexion-parametro/list$', csrf_exempt(views.CONEXION_PARAMETRO.as_view()),name='conexion_parametro'),

]