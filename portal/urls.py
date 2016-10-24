# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from portal.views import views_portal_cliente

urlpatterns = [

    #ventas
	url(r'^portal-cliente/ventas/list$', views_portal_cliente.VentaList.as_view(), name='portal_cliente_ventas_list'),
	url(r'^portal-cliente/ventas/$', views_portal_cliente.VENTAS.as_view(), name='portal_cliente_venta_list'),
    url(r'^portal-cliente/ventas/diaria$', csrf_exempt(views_portal_cliente.VentaDiaria.as_view()), name='portal_cliente_venta_diaria'),

    #cliente
    url(r'^portal-cliente/cliente/(?P<pk>\d+)$', views_portal_cliente.ClienteUpdatePortal.as_view(), name='portal_cliente_list'),

    #facturas/pedidos
    url(r'^portal-cliente/propuesta/facturas/list$', views_portal_cliente.PropuestaProcesarPortalClienteList.as_view(),name='portal_cliente_propuesta_list'),
]
