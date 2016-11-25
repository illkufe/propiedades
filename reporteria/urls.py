# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	url(r'^reportes$', csrf_exempt(views.REPORTES.as_view()),name='reportes'),
	url(r'^reportes/list$', csrf_exempt(views.REPORTES.as_view()),name='reportes'),

	url(r'^reportes/ingreso-activo/$', csrf_exempt(views.REPORTE_INGRESO_ACTIVO.as_view()),name='reporte_ingreso_activo'),
	url(r'^reportes/ingreso-activo/excel/$', views.ingreso_activo_xls,name='reporte_ingreso_activo_excel'),
	url(r'^reportes/ingreso-activo/pdf/$', views.ingreso_activo_pdf, name='reporte_ingreso_activo_pdf'),

	url(r'^reportes/garantia-local/$', csrf_exempt(views.REPORTE_GARANTIA_LOCAL.as_view()),name='reporte_garantia_local'),
	url(r'^reportes/garantia-local/excel/$', views.ingreso_activo_xls,name='reporte_ingreso_activo_excel'),
	url(r'^reportes/garantia-local/pdf/$', views.ingreso_activo_pdf, name='reporte_ingreso_activo_pdf'),

	# reporte ingresos por m2
	url(r'^reportes/ingreso-activo/metros/$', csrf_exempt(views.INGRESO_ACTIVO_METROS.as_view()),name='ingreso_activo_metros'),
	url(r'^reportes/ingreso-activo/metros/excel/$', views.ingreso_activo_metros_excel,name='ingreso_activo_metros_excel'),
	url(r'^reportes/ingreso-activo/metros/pdf/$', views.ingreso_activo_metros_pdf,name='ingreso_activo_metros_pdf'),
]