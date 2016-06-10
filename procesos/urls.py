# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	
	url(r'^procesos/contratos/propuesta$', csrf_exempt(views.PROCESOS.as_view()),name='procesos'),
	url(r'^procesos/contratos/propuesta/(?P<id>\d+)$', csrf_exempt(views.PROCESOS.as_view()),name='procesos_con_id'),
	url(r'^procesos/list/$', views.procesos_list, name='procesos_list'),
	url(r'^propuesta/pdf/(?P<pk>\d+)$', views.propuesta_pdf, name='propuesta_pdf'),

]


