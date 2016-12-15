# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	url(r'^propuesta/generar/list$', views.PropuestaGenerarList.as_view(), name='propuesta_generar_list'),
	url(r'^propuesta/procesar/list$', views.PropuestaProcesarList.as_view(), name='propuesta_procesar_list'),

	url(r'^procesos/propuesta/filtar$', views.propuesta_filtrar, name='propuesta_filtrar'),
	url(r'^procesos/propuesta/generar$', views.propuesta_generar ,name='propuesta_generar'),
	url(r'^procesos/propuesta/guardar$', views.propuesta_guardar ,name='propuesta_guardar'),
	url(r'^procesos/propuesta/enviar$', views.propuesta_enviar ,name='propuesta_enviar'),

	url(r'^procesos/propuesta/pdf/$', csrf_exempt(views.propuesta_pdf) ,name='propuesta_pdf'),
	url(r'^procesos/propuesta/pdf/(?P<pk>\d+)$', views.propuesta_pdf ,name='propuesta_pdf'),
	url(r'^procesos/factura/pdf/(?P<pk>\d+)$', views.factura_pdf ,name='factura_pdf'),

	
	url(r'^propuesta/consultar$', csrf_exempt(views.PROPUESTA_CONSULTAR.as_view()),name='propuesta_consultar'),

	url(r'^api/facturas/$', csrf_exempt(views.FACTURA.as_view()),name='facturas'),
	url(r'^api/factura/(?P<id>\d+)$', csrf_exempt(views.FACTURA.as_view()),name='factura'),
]