from django.conf.urls import url
from facturacion.views.views import *

# app_name = 'facturacion'

urlpatterns = [

##------------------------------------TIPOS DE DOCUMENTOS---------------------------------------------------------------

    url(r'^configuracion-facturacion/list$', ConfiguracionFacturacionList.as_view(), name='configuracion_facturacion_list'),
    url(r'^configuracion-facturacion/new$', ConfiguracionFacturacionNew.as_view(), name='configuracion_facturacion_new'),
    url(r'^configuracion-facturacion/update/(?P<pk>\d+)$', ConfiguracionFacturacionUpdate.as_view(), name='configuracion_facturacion_update'),
    url(r'^configuracion-facturacion/delete/(?P<pk>\d+)$', ConfiguracionFacturacionDelete.as_view(), name='configuracion_facturacion_delete'),


    url(r'^folios-electronicos/list$', FoliosElectronicosList.as_view(), name='folios_electronicos_list'),
    url(r'^folios-electronicos/carga_caf$', carga_folios_electronicos, name='carga_folios_electronicos'),
    url(r'^folios-electronicos/autorizar_caf$', autorizar_folios_electronicos, name='autorizar_folios_electronicos'),

    url(r'^xml$', prueba_xml, name='prueba_xml'),

]