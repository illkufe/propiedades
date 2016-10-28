# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	
	# clientes
	url(r'^clientes/list$', views.ClienteList.as_view(), name='cliente_list'),
	url(r'^clientes/new$', views.ClienteNew.as_view(), name='cliente_new'),
	url(r'^clientes/delete/(?P<pk>\d+)$', views.ClienteDelete.as_view(), name='cliente_delete'),
	url(r'^clientes/update/(?P<pk>\d+)$', views.ClienteUpdate.as_view(), name='cliente_update'),


	# conexion
	url(r'^conexion-cliente$', csrf_exempt(views.CONEXION_CLIENTE.as_view()),name='conexion_cliente_update'),
	url(r'^conexion-concepto$', csrf_exempt(views.CONEXION_CONCEPTO.as_view()),name='conexion_concepto_update'),
	url(r'^conexion-parametro$', csrf_exempt(views.CONEXION_PARAMETRO.as_view()),name='conexion_parametro_update'),
	url(r'^conexion-cliente/list$', csrf_exempt(views.CONEXION_CLIENTE.as_view()),name='conexion_cliente_list'),
	url(r'^conexion-concepto/list$', csrf_exempt(views.CONEXION_CONCEPTO.as_view()),name='conexion_concepto_list'),
	url(r'^conexion-parametro/list$', csrf_exempt(views.CONEXION_PARAMETRO.as_view()),name='conexion_parametro_list'),

    # clasificacion
    url(r'^clasificacion/list$', views.ClasificacionList.as_view(), name='clasificacion_list'),
    url(r'^clasificacion/new$', views.ClasificacionNew.as_view(), name='clasificacion_new'),
    url(r'^clasificacion/delete/(?P<pk>\d+)$', views.ClasificacionDelete.as_view(), name='clasificacion_delete'),
    url(r'^clasificacion/update/(?P<pk>\d+)$', views.ClasificacionUpdate.as_view(), name='clasificacion_update'),

	#workflow
	url(r'^workflow/condicion$',csrf_exempt(views.WORKFLOW_CONDICION.as_view()), name='workflow_condicion_new'),
	url(r'^workflow$', csrf_exempt(views.WORKFLOW.as_view()), name='workflow_update'),
	url(r'^workflow/validar$', views.validar_workflow, name='validar_workflow'),

	#configuracion moneda
	url(r'^configuracion-moneda', views.CONFIGURACION_MONEDA.as_view(), name='configuracion_moneda_update'),

]