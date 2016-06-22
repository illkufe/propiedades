# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	url(r'^locales/$', csrf_exempt(views.LOCAL.as_view()),name='local'),
	url(r'^locales/(?P<id>\d+)$', csrf_exempt(views.LOCAL.as_view()),name='local_con_id'),

	url(r'^ventas/list$', views.VentaList.as_view(), name='ventas_list'),

	url(r'^ventas/$', views.VENTAS.as_view(), name='venta_list'),
	url(r'^ventas/(?P<id>\d+)$', views.VENTAS.as_view(), name='venta_list_id'),
	# url(r'^ventas/new$', views.VentasNew.as_view(), name='ventas_new'),
	# url(r'^ventas/delete/(?P<pk>\d+)$', views.VentasDelete.as_view(), name='ventas_delete'),
	# url(r'^ventas/update/(?P<pk>\d+)$', views.VentasUpdate.as_view(), name='ventas_update'),

	url(r'^locales/list$', views.LocalList.as_view(), name='local_list'),
	url(r'^locales/new$', views.LocalNew.as_view(), name='local_new'),
	url(r'^locales/delete/(?P<pk>\d+)$', views.LocalDelete.as_view(), name='local_delete'),
	url(r'^locales/update/(?P<pk>\d+)$', views.LocalUpdate.as_view(), name='local_update'),

	url(r'^locales-tipo/list$', views.LocalTipoList.as_view(), name='local_tipo_list'),
	url(r'^locales-tipo/new$', views.LocalTipoNew.as_view(), name='local_tipo_new'),
	url(r'^locales-tipo/delete/(?P<pk>\d+)$', views.LocalTipoDelete.as_view(), name='local_tipo_delete'),
	url(r'^locales-tipo/update/(?P<pk>\d+)$', views.LocalTipoUpdate.as_view(), name='local_tipo_update'),

]