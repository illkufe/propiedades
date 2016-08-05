# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	
	# api
	url(r'^contratos/$', csrf_exempt(views.CONTRATO.as_view()),name='contrato'),
	url(r'^contratos/(?P<id>\d+)$', csrf_exempt(views.CONTRATO.as_view()),name='contrato_con_id'),

	# contrato_tipo
	url(r'^contrato/list$', views.ContratoList.as_view(), name='contrato_list'),
	url(r'^contrato/new$', views.ContratoNew.as_view(), name='contrato_new'),
	url(r'^contrato/delete/(?P<pk>\d+)$', views.ContratoDelete.as_view(), name='contrato_delete'),
	url(r'^contrato/update/(?P<pk>\d+)$', views.ContratoUpdate.as_view(), name='contrato_update'),

	# contrato
	url(r'^contrato-tipo/list$', views.ContratoTipoList.as_view(), name='contrato_tipo_list'),
	url(r'^contrato-tipo/new$', views.ContratoTipoNew.as_view(), name='contrato_tipo_new'),
	url(r'^contrato-tipo/delete/(?P<pk>\d+)$', views.ContratoTipoDelete.as_view(), name='contrato_tipo_delete'),
	url(r'^contrato-tipo/update/(?P<pk>\d+)$', views.ContratoTipoUpdate.as_view(), name='contrato_tipo_update'),

	# multa_tipo
	url(r'^contrato-multa-tipo/list$',views.ContratoMultaTipoList.as_view(), name='contrato_multa_tipo_list'),
	url(r'^contrato-multa-tipo/new$', views.ContratoMultaTipoNew.as_view(), name='contrato_multa_tipo_new'),
	url(r'^contrato-multa-tipo/delete/(?P<pk>\d+)$',views.ContratoMultaTipoDelete.as_view(), name='contrato_multa_tipo_delete'),
	url(r'^contrato-multa-tipo/update/(?P<pk>\d+)$',views.ContratoMultaTipoUpdate.as_view(), name='contrato_multa_tipo_update'),

	# multa
	url(r'^contrato-multa/list$',views.ContratoMultaList.as_view(), name='contrato_multa_list'),
	url(r'^contrato-multa/new$', views.ContratoMultaNew.as_view(), name='contrato_multa_new'),
	url(r'^contrato-multa/delete/(?P<pk>\d+)$',views.ContratoMultaDelete.as_view(), name='contrato_multa_delete'),
	url(r'^contrato-multa/update/(?P<pk>\d+)$',views.ContratoMultaUpdate.as_view(), name='contrato_multa_update'),

	# contrato_concepto
	url(r'^contrato-concepto/(?P<contrato_id>\d+)$', views.ContratoConceptoNew.as_view(), name='contrato_concepto_new'),

	

	# funciones
	url(r'^contratos/inactivos/list$', views.ContratosInactivosList.as_view(), name='contratos_inactivos_list'),
	url(r'^contratos/(?P<contrato_id>\d+)/pdf$', views.contrato_pdf, name='contrato_pdf'),
	url(r'^contratos/(?P<contrato_id>\d+)/activar$', views.contrato_activar, name='contrato_activar'),

]
