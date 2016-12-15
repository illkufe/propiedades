# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
	url(r'^reportes$', csrf_exempt(views.REPORTES.as_view()),name='reportes'),
	url(r'^reportes/list$', csrf_exempt(views.REPORTES.as_view()),name='reportes'),

	url(r'^reportes/ingreso-activo/$', csrf_exempt(views.REPORTE_INGRESO_ACTIVO.as_view()),name='reporte_ingreso_activo'),
	url(r'^reportes/ingreso-activo/excel/$', views.ingreso_activo_xls,name='reporte_ingreso_activo_excel'),
	url(r'^reportes/ingreso-activo/pdf/$', views.ingreso_activo_pdf, name='reporte_ingreso_activo_pdf'),

	url(r'^reportes/ingreso-clasificacion/$', csrf_exempt(views.REPORTE_INGRESO_CLASIFICACION.as_view()), name='reporte_ingreso_clasificacion'),
	url(r'^reportes/ingreso-clasificacion/excel/$', views.ingreso_clasificacion_xls, name='reporte_ingreso_clasificacion_excel'),
	url(r'^reportes/ingreso-clasificacion/pdf/$', views.ingreso_clasificacion_pdf, name='reporte_ingreso_clasificacion_pdf'),

	url(r'^reportes/vacancia-activo/$', csrf_exempt(views.REPORTE_VACANCIA.as_view()),name='reporte_vacancia_activo'),
	url(r'^reportes/vacancia-activo/excel/$', views.vacancia_xls, name='reporte_vacancia_activo_excel'),
	url(r'^reportes/vacancia-activo/pdf/$', views.vacancia_pdf, name='reporte_vacancia_activo_pdf'),

	url(r'^reportes/vencimiento-contrato/$', csrf_exempt(views.REPORTE_VENCIMIENTO_CONTRATOS.as_view()), name='reporte_vencimiento_contrato'),
	url(r'^reportes/vencimiento-contrato/excel/$', views.vencimiento_contrato_xls, name='reporte_vencimiento_contrato_excel'),
	url(r'^reportes/vencimiento-contrato/pdf/$', views.vencimiento_contrato_pdf, name='reporte_vencimiento_contrato_pdf'),

	url(r'^reportes/metros-cuadrados-clasificacion/$', csrf_exempt(views.REPORTE_METROS_CUADRADOS_CLASIFICACION.as_view()), name='reporte_m_cuadrados_clasificacion_activo'),
	url(r'^reportes/metros-cuadrados-clasificacion/excel/$', views.metros_cuadrados_clasificacion_xls, name='reporte_m_cuadrados_clasificacion_excel'),
	url(r'^reportes/metros-cuadrados-clasificacion/pdf/$', views.metros_cuadrados_clasificacion_pdf, name='reporte_m_cuadrados_clasificacion_pdf'),

	# reporte ingresos por m2
	url(r'^reportes/ingreso-activo/metros/$', csrf_exempt(views.REPORTE_INGRESO_ACTIVO_METROS.as_view()),name='ingreso_activo_metros'),
	url(r'^reportes/ingreso-activo/metros/reporte/$', views.ingreso_activo_metros_reporte,name='ingreso_activo_metros_reporte'),

	# reporte garantias por local
	url(r'^reportes/garantia-local/$', csrf_exempt(views.REPORTE_GARANTIA_LOCAL.as_view()),name='reporte_garantia_local'),
	url(r'^reportes/garantia-local/reporte/$', csrf_exempt(views.garantias_local_reporte), name='garantias_local_reporte'),
]