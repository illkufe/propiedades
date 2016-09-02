# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	# url(r'^procesos/propuesta$', csrf_exempt(views.PROPUESTA.as_view()),name='procesos'),
	# url(r'^procesos/propuesta/(?P<id>\d+)$', csrf_exempt(views.PROPUESTA.as_view()),name='procesos'),


	url(r'^propuesta/generar/list$', views.PropuestaGenerarList.as_view(), name='propuesta_generar_list'),
	url(r'^propuesta/procesar/list$', views.PropuestaProcesarList.as_view(), name='propuesta_procesar_list'),


	url(r'^procesos/procesar/propuesta$', csrf_exempt(views.PROPUESTA_PROCESAR.as_view()),name='procesos_con_id'),

	url(r'^procesos/propuesta/filtar$', views.propuesta_filtrar, name='propuesta_filtrar'),
	url(r'^procesos/propuesta/generar$', views.propuesta_generar ,name='propuesta_generar'),
	url(r'^procesos/propuesta/guardar$', views.propuesta_guardar ,name='propuesta_guardar'),
	url(r'^procesos/propuesta/pdf/(?P<pk>\d+)$', views.propuesta_pdf ,name='propuesta_pdf'),

	
	
	


	url(r'^procesos/contratos/propuesta$', csrf_exempt(views.PROCESOS.as_view()),name='procesos'),
	url(r'^procesos/contratos/propuesta/(?P<id>\d+)$', csrf_exempt(views.PROCESOS.as_view()),name='procesos_con_id'),

	url(r'^procesos/list$', views.ProcesoList.as_view(), name='procesos_list'),
	url(r'^procesos/delete/(?P<pk>\d+)$', views.ProcesoDelete.as_view(), name='proceso_delete'),

	# url(r'^propuesta/pdf/(?P<pk>\d+)$', views.propuesta_pdf, name='propuesta_pdf'),
	

]


