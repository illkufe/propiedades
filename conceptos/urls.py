# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	url(r'^conceptos/list$', views.ConceptoList.as_view(), name='concepto_list'),
	url(r'^conceptos/new$', views.ConceptoNew.as_view(), name='concepto_new'),
	url(r'^conceptos/delete/(?P<pk>\d+)$', views.ConceptoDelete.as_view(), name='concepto_delete'),
	url(r'^conceptos/update/(?P<pk>\d+)$', views.ConceptoUpdate.as_view(), name='concepto_update'),
]
