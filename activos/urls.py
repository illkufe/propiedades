# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	url(r'^activos/list$', views.ActivoList.as_view(), name='activo_list'),
	url(r'^activos/new$', views.ActivoNew.as_view(), name='activo_new'),
	url(r'^activos/delete/(?P<pk>\d+)$', views.ActivoDelete.as_view(), name='activo_delete'),
	url(r'^activos/update/(?P<pk>\d+)$', views.ActivoUpdate.as_view(), name='activo_update'),

	url(r'^activos/(?P<activo_id>\d+)/locales/new$', views.ActivoLocalNew.as_view(), name='activo_local_new'),
	url(r'^activos/(?P<activo_id>\d+)/locales/update/(?P<pk>\d+)$', views.ActivoLocalUpdate.as_view(), name='activo_local_update'),

	url(r'^empresa/(?P<empresa_id>\d+)/activos$', csrf_exempt(views.ACTIVOS.as_view()),name='activos'),
	url(r'^empresa/(?P<empresa_id>\d+)/activos/(?P<id>\d+)$', csrf_exempt(views.ACTIVOS.as_view()),name='activo'),

]