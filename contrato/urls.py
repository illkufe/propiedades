# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	# propuesta
	url(r'^propuesta/list$', views.PropuestaList.as_view(), name='propuesta_list'),
	url(r'^propuesta/new$', views.PropuestaNew.as_view(), name='propuesta_new'),
	url(r'^propuesta/delete/(?P<pk>\d+)$', views.PropuestaDelete.as_view(), name='propuesta_delete'),
	url(r'^propuesta/update/(?P<pk>\d+)$', views.PropuestaUpdate.as_view(), name='propuesta_update'),

	# propuesta historial
	url(r'^propuesta/historial/(?P<pk>\d+)$', views.PropuestaHistorialList.as_view(), name='propuesta_historial'),

	# contrato
	url(r'^contrato/list/$', views.ContratoList.as_view(), name='contrato_list'),
	url(r'^contrato/new/$', views.ContratoNew.as_view(), name='contrato_new'),
	url(r'^contrato/delete/(?P<pk>\d+)/$', views.ContratoDelete.as_view(), name='contrato_delete'),
	url(r'^contrato/update/(?P<pk>\d+)/$', views.ContratoUpdate.as_view(), name='contrato_update'),
	url(r'^contrato/documents/(?P<pk>\d+)/$', views.ContratoDocuments.as_view(),name='contrato_documents'),

	# contrato_tipo
	url(r'^contrato-tipo/list$', views.ContratoTipoList.as_view(), name='contrato_tipo_list'),
	url(r'^contrato-tipo/new$', views.ContratoTipoNew.as_view(), name='contrato_tipo_new'),
	url(r'^contrato-tipo/delete/(?P<pk>\d+)$', views.ContratoTipoDelete.as_view(), name='contrato_tipo_delete'),
	url(r'^contrato-tipo/update/(?P<pk>\d+)$', views.ContratoTipoUpdate.as_view(), name='contrato_tipo_update'),

	# tipo de multa
	url(r'^multa-tipo/list$',views.MultaTipoList.as_view(), name='multa_tipo_list'),
	url(r'^multa-tipo/new$', views.MultaTipoNew.as_view(), name='multa_tipo_new'),
	url(r'^multa-tipo/delete/(?P<pk>\d+)$',views.MultaTipoDelete.as_view(), name='multa_tipo_delete'),
	url(r'^multa-tipo/update/(?P<pk>\d+)$',views.MultaTipoUpdate.as_view(), name='multa_tipo_update'),

	# multa
	url(r'^multa/list$',views.MultaList.as_view(), name='multa_list'),
	url(r'^multa/new$', views.MultaNew.as_view(), name='multa_new'),
	url(r'^multa/delete/(?P<pk>\d+)$',views.MultaDelete.as_view(), name='multa_delete'),
	url(r'^multa/update/(?P<pk>\d+)$',views.MultaUpdate.as_view(), name='multa_update'),

	# conceptos contrato
	url(r'^contrato-concepto/(?P<contrato_id>\d+)$', views.ContratoConceptoNew.as_view(), name='contrato_concepto_new'),

	# funciones
	url(r'^contratos/inactivos/list$', views.ContratosInactivosList.as_view(), name='contratos_inactivos_list'),
	url(r'^contratos/(?P<contrato_id>\d+)/pdf$', views.contrato_pdf, name='contrato_pdf'),
	url(r'^contratos/(?P<contrato_id>\d+)/activar$', views.contrato_activar, name='contrato_activar'),
	url(r'^funcion/activar/contrato/(?P<contrato_id>\d+)$', views.contrato_activar, name='contrato_activar'),

	url(r'^funcion/propuesta/enviar_correo$', views.propuesta_enviar_correo, name='propuesta_enviar_correo'),
	url(r'^funcion/propuesta/restaurar_version/(?P<id>\d+)$', views.propuesta_restaurar_version, name='propuesta_restaurar_version'),
	url(r'^funcion/propuesta/historial/(?P<id>\d+)$', views.propuesta_historial_tabla, name='propuesta_historial_tabla'),
	url(r'^funcion/propuesta/pdf/(?P<id>\d+)$', views.propuesta_generar_pdf, name='propuesta_generar_pdf'),
	url(r'^funcion/propuesta/workflow$', views.propuesta_workflow, name='propuesta_workflow'),

	

	# get - contratos
	url(r'^get/contratos/$', csrf_exempt(views.CONTRATO.as_view()),name='get_contratos'),
	url(r'^get/contratos/(?P<id>\d+)$', csrf_exempt(views.CONTRATO.as_view()),name='get_contratos'),
	url(r'^get/contrato/documents/(?P<pk>\d+)/$', csrf_exempt(views.GET_CONTRATO_DOCUMENTS.as_view()),name='get_contrato_documents'),

	

	# get - propuestas contrato
	url(r'^get/propuestas-contrato$', csrf_exempt(views.PROPUESTA_CONTRATO.as_view()),name='get_propuestas'),
	url(r'^get/propuestas-contrato/(?P<id>\d+)$', csrf_exempt(views.PROPUESTA_CONTRATO.as_view()),name='get_propuestas'),
	url(r'^get/propuestas-contrato/workflow$', csrf_exempt(views.PROPUESTA_CONTRATO_WORKFLOW.as_view()),name='get_propuesta_workflow'),
	url(r'^get/propuestas-contrato/workflow/(?P<id>\d+)$', csrf_exempt(views.PROPUESTA_CONTRATO_WORKFLOW.as_view()),name='get_propuesta_workflow'),

	

]
