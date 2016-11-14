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
]