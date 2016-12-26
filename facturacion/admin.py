from django.contrib import admin
from facturacion.models import *

# modelos
admin.site.register(Parametro_Factura)
admin.site.register(Conexion_Factura)
admin.site.register(Folio_Documento_Electronico)
admin.site.register(Motor_Factura)
admin.site.register(Codigo_Concepto)
admin.site.register(Parametro_Factura_Estado)
