# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	
	# activos
	url(r'^activos/list$', views.ActivoList.as_view(), name='activo_list'),
	url(r'^activos/new$', views.ActivoNew.as_view(), name='activo_new'),
	url(r'^activos/delete/(?P<pk>\d+)$', views.ActivoDelete.as_view(), name='activo_delete'),
	url(r'^activos/update/(?P<pk>\d+)$', views.ActivoUpdate.as_view(), name='activo_update'),

	# gasto mensual (gasto común)
	url(r'^gastos-mensual/list$', views.GastoMensualList.as_view(), name='gasto_mensual_list'),
	url(r'^gastos-mensual/new$', views.GastoMensualNew.as_view(), name='gasto_mensual_new'),
	url(r'^gastos-mensual/delete/(?P<pk>\d+)$', views.GastoMensualDelete.as_view(), name='gasto_mensual_delete'),
	url(r'^gastos-mensual/update/(?P<pk>\d+)$', views.GastoMensualUpdate.as_view(), name='gasto_mensual_update'),

	# gasto servicio (otros gastos)
	url(r'^gastos-servicios/list$', views.GastoServicioList.as_view(), name='gasto_servicio_list'),
	url(r'^gastos-servicios/new$', views.GastoServicioNew.as_view(), name='gasto_servicio_new'),
	url(r'^gastos-servicios/delete/(?P<pk>\d+)$', views.GastoServicioDelete.as_view(), name='gasto_servicio_delete'),
	url(r'^gastos-servicios/update/(?P<pk>\d+)$', views.GastoServicioUpdate.as_view(), name='gasto_servicio_update'),

	# api
	url(r'^empresa/(?P<empresa_id>\d+)/activos$', csrf_exempt(views.ACTIVOS.as_view()),name='api_activos'),
	url(r'^empresa/(?P<empresa_id>\d+)/activos/(?P<id>\d+)$', csrf_exempt(views.ACTIVOS.as_view()),name='api_activos'),

	url(r'^activos/documentos/(?P<id>\d+)$', csrf_exempt(views.ACTIVO_DOCUMENTOS.as_view()),name='activo_documento_list'),

]