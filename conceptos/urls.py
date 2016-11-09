# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
	
	# conceptos
	url(r'^conceptos/list$', views.ConceptoList.as_view(), name='concepto_list'),
	url(r'^conceptos/new$', views.ConceptoNew.as_view(), name='concepto_new'),
	url(r'^conceptos/delete/(?P<pk>\d+)$', views.ConceptoDelete.as_view(), name='concepto_delete'),
	url(r'^conceptos/update/(?P<pk>\d+)$', views.ConceptoUpdate.as_view(), name='concepto_update'),

	# get - conceptos
	url(r'^get/conceptos/$', views.CONCEPTO.as_view(), name='get_concepto'),

]
