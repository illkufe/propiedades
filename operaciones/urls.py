# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	
	# lecturas
	url(r'^lectura-medidores/list$', views.LecturaMedidorList.as_view(), name='lectura_medidor_list'),
	url(r'^lectura-medidores/$', views.LECTURASMEDIDOR.as_view(), name='lectura_medidor_carga_masiva'),

	# lecturas electricidad
	url(r'^lectura-electricidad/new$', views.LecturaElectricidadNew.as_view(), name='lectura_electricidad_new'),
	url(r'^lectura-electricidad/delete/(?P<pk>\d+)$', views.LecturaElectricidadDelete.as_view(), name='lectura_electricidad_delete'),
	url(r'^lectura-electricidad/update/(?P<pk>\d+)$', views.LecturaElectricidadUpdate.as_view(), name='lectura_electricidad_update'),

	# lecturas agua
	url(r'^lectura-agua/new$', views.LecturaAguaNew.as_view(), name='lectura_agua_new'),
	url(r'^lectura-agua/delete/(?P<pk>\d+)$', views.LecturaAguaDelete.as_view(), name='lectura_agua_delete'),
	url(r'^lectura-agua/update/(?P<pk>\d+)$', views.LecturaAguaUpdate.as_view(), name='lectura_agua_update'),

	# lecturas gas
	url(r'^lectura-gas/new$', views.LecturaGasNew.as_view(), name='lectura_gas_new'),
	url(r'^lectura-gas/delete/(?P<pk>\d+)$', views.LecturaGasDelete.as_view(), name='lectura_gas_delete'),
	url(r'^lectura-gas/update/(?P<pk>\d+)$', views.LecturaGasUpdate.as_view(), name='lectura_gas_update'),

	# gastos servicios basicos
	url(r'^gasto-servicios-basicos/list$', views.GastoServicioBasicoList.as_view(), name='gasto_servicio_basico_list'),
	url(r'^gasto-servicios-basicos/new$', views.GastoServicioBasicoNew.as_view(), name='gasto_servicio_basico_new'),
	url(r'^gasto-servicios-basicos/delete/(?P<pk>\d+)$', views.GastoServicioBasicoDelete.as_view(), name='gasto_servicio_basico_delete'),
	url(r'^gasto-servicios-basicos/update/(?P<pk>\d+)$', views.GastoServicioBasicoUpdate.as_view(), name='gasto_servicio_basico_update'),

]
