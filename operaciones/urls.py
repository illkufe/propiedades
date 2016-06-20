# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [

	# url(r'^local-ventas/list$', views.LocalVentaList.as_view(), name='local_venta_list'),
	# url(r'^local-ventas/new$', views.LocalVentaNew.as_view(), name='local_venta_new'),
	# url(r'^local-ventas/delete/(?P<pk>\d+)$', views.LocalVentaDelete.as_view(), name='local_venta_delete'),
	# url(r'^local-ventas/update/(?P<pk>\d+)$', views.LocalVentaUpdate.as_view(), name='local_venta_update'),

	url(r'^lectura-medidores/list$', views.LecturaMedidorList.as_view(), name='lectura_medidor_list'),

	url(r'^lectura-electricidad/new$', views.LecturaElectricidadNew.as_view(), name='lectura_electricidad_new'),
	url(r'^lectura-electricidad/delete/(?P<pk>\d+)$', views.LecturaElectricidadDelete.as_view(), name='lectura_electricidad_delete'),
	url(r'^lectura-electricidad/update/(?P<pk>\d+)$', views.LecturaElectricidadUpdate.as_view(), name='lectura_electricidad_update'),

	url(r'^lectura-agua/new$', views.LecturaAguaNew.as_view(), name='lectura_agua_new'),
	url(r'^lectura-agua/delete/(?P<pk>\d+)$', views.LecturaAguaDelete.as_view(), name='lectura_agua_delete'),
	url(r'^lectura-agua/update/(?P<pk>\d+)$', views.LecturaAguaUpdate.as_view(), name='lectura_agua_update'),

	url(r'^lectura-gas/new$', views.LecturaGasNew.as_view(), name='lectura_gas_new'),
	url(r'^lectura-gas/delete/(?P<pk>\d+)$', views.LecturaGasDelete.as_view(), name='lectura_gas_delete'),
	url(r'^lectura-gas/update/(?P<pk>\d+)$', views.LecturaGasUpdate.as_view(), name='lectura_gas_update'),

]
