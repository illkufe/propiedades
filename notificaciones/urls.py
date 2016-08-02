# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	url(r'^alertas/list$', views.AlertasList.as_view(), name='alertas_list'),
	url(r'^alerta/new$', views.AlertaNew.as_view(), name='alerta_new'),
	url(r'^alerta/delete/(?P<pk>\d+)$', views.AlertaDelete.as_view(), name='alerta_delete'),
	url(r'^alerta/update/(?P<pk>\d+)$', views.AlertaUpdate.as_view(), name='alerta_update'),

]
