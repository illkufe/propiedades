# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	# get - currency last
	url(r'^get/currency-last/(?P<id>\d+)$', csrf_exempt(views.CURRENCIES_LAST.as_view()),name='get_currencies_last_id'),
	url(r'^get/currency-last/$', csrf_exempt(views.CURRENCIES_LAST.as_view()),name='get_currencies_last'),
	url(r'^get/configuracion-monedas/(?P<pk>\d+)$', views.configuracion_monedas,name='configuracion_monedas'),

	url(r'^documentos/create-folder/$', views.owncloud_create_folder, name='owncloud_create_folder'),
	url(r'^documentos/upload-file/$', views.owncloud_upload_file, name='owncloud_upload_file'),
	url(r'^documentos/delete/$', views.owncloud_delete, name='owncloud_delete'),
]