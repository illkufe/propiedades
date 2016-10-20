# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	# get - currency last
	url(r'^get/currency-last/(?P<id>\d+)$', csrf_exempt(views.CURRENCIES_LAST.as_view()),name='get_currencies_last_id'),
	url(r'^get/currency-last/$', csrf_exempt(views.CURRENCIES_LAST.as_view()),name='get_currencies_last'),
]