# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views
# import views

urlpatterns = [

	url(r'^contratos/$', csrf_exempt(views.CONTRATO.as_view()),name='contrato'),
	url(r'^contratos/(?P<id>\d+)$', csrf_exempt(views.CONTRATO.as_view()),name='contrato_con_id'),
	
	url(r'^contratos/list$', views.ContratoList.as_view(), name='contrato_list'),
	url(r'^contratos/new$', views.ContratoNew.as_view(), name='contrato_new'),
	url(r'^contratos/delete/(?P<pk>\d+)$', views.ContratoDelete.as_view(), name='contrato_delete'),
	url(r'^contratos/update/(?P<pk>\d+)$', views.ContratoUpdate.as_view(), name='contrato_update'),

	url(r'^contratos-tipo/list$', views.ContratoTipoList.as_view(), name='contrato_tipo_list'),
	url(r'^contratos-tipo/new$', views.ContratoTipoNew.as_view(), name='contrato_tipo_new'),
	url(r'^contratos-tipo/delete/(?P<pk>\d+)$', views.ContratoTipoDelete.as_view(), name='contrato_tipo_delete'),
	url(r'^contratos-tipo/update/(?P<pk>\d+)$', views.ContratoTipoUpdate.as_view(), name='contrato_tipo_update'),

	# url(r'^contratos/arriendo/$', views.ContratoArriendo.as_view(), name='contrato_arriendo'),
	# url(r'^contratos/(?P<contrato_id>\d+)/arriendo/new$', views.ArriendoNew.as_view(), name='arriendo_new'),
	# url(r'^contratos/(?P<contrato_id>\d+)/arriendo/update/(?P<arriendo_id>\d+)$', views.ArriendoUpdate.as_view(), name='arriendo_update'),
	# url(r'^contratos/(?P<contrato_id>\d+)/informacion$', views.ArriendoPruebaNew.as_view(), name='arriendo_prueba_new'),

	url(r'^contratos/(?P<contrato_id>\d+)/conceptos$', views.ArriendoPruebaNew.as_view(), name='arriendo_prueba_new'),

	url(r'^contrato/pdf/(?P<pk>\d+)$', views.contratoPdf, name='contrato_pdf'),
	url(r'^generar_contrato_pdf/(?P<contrato_id>\d+)$', views.generar_contrato_pdf, name='generar_contrato_pdf'),

]
