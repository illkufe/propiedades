from django.conf.urls import url
from facturacion.views.views import *

app_name = 'facturacion'

urlpatterns = [

##------------------------------------TIPOS DE DOCUMENTOS---------------------------------------------------------------

    url(r'^configuracion/visualizar/$', visualizar_configuracion, name='visualizar_configuracion'),
    url(r'^configuracion/crear/$', crear_configuracion, name='crear_configuracion'),
    url(r'^configuracion/busca_persona/$', busca_personas, name='busca_personas'),
    url(r'^configuracion/editar/(?P<pk>[0-9]+)$$', editar_configuracion, name='editar_configuracion'),
    url(r'^configuracion/recupera_data_parametros/(?P<pk>[0-9]+)$$', recupera_data_parametros, name='recupera_data_parametros'),
    url(r'^configuracion/eliminar/$', eliminar_configuracion, name='eliminar_configuracion'),

    url(r'^folios_electronicos/carga_caf/$', carga_folios_electronicos, name='carga_folios_electronicos'),
    url(r'^folios_electronicos/visualizar/$', visualizar_folios_electronicos, name='visualizar_folios_electronicos'),
    url(r'^folios_electronicos/autorizar_caf/$', autorizar_folios_electronicos, name='autorizar_folios_electronicos'),

    url(r'^xml$', prueba_xml, name='prueba_xml'),


]