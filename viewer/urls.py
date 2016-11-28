# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	# dashboard
	url(r'^$', views.dashboard, name='dashboard'),

	url(r'^flag_currencies/$', views.flag_currencies, name='flag_currencies'),
	url(r'^flag_commercial/$', views.flag_commercial, name='flag_commercial'),

	url(r'^dashboard/vacancia/$', views.chart_vacancia, name='chart_vacancia'),

	url(r'^dashboard/vacancia/tipo$', views.chart_vacancia_tipo, name='chart_vacancia_tipo'),
	url(r'^dashboard/ingreso-centro/$', views.chart_ingreso_centro, name='chart_ingreso_centro'),

	# data - ingreso por metros cuadrados
	url(r'^data/ingresos-metros/$', views.data_ingreso_metros, name='data_ingreso_metros'),
	url(r'^data/ingresos-metros/(?P<id>\d+)/$', views.data_ingreso_metros, name='data_ingreso_metros'),

	# data - garantias
	url(r'^data/garantias/activos/$', views.data_garantia, name='data_garantia'),
	url(r'^data/garantias/activos/(?P<id>\d+)/$', views.data_garantia, name='data_garantia'),

	# get - conceptos
	url(r'^get/conceptos-activo/(?P<id>\d+)$', views.get_conceptos_activo, name='get_conceptos_activo'),
]