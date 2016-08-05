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
]