from django.contrib import admin
from .models import *

# modelos: contrato
admin.site.register(Contrato_Estado)
admin.site.register(Contrato_Tipo)
admin.site.register(Contrato)
admin.site.register(Garantia)
admin.site.register(Multa_Tipo)

# modelos: conceptos
admin.site.register(Multa)
admin.site.register(Arriendo)
admin.site.register(Arriendo_Detalle)
admin.site.register(Arriendo_Bodega)
admin.site.register(Arriendo_Variable)
admin.site.register(Gasto_Comun)
admin.site.register(Servicio_Basico)
admin.site.register(Cuota_Incorporacion)
admin.site.register(Gasto_Asociado)

# modelos: propuesta
admin.site.register(Propuesta_Contrato)
admin.site.register(Propuesta_Proceso)
admin.site.register(Propuesta_Version)
admin.site.register(Propuesta_Garantia)
admin.site.register(Propuesta_Arriendo_Minimo)
admin.site.register(Propuesta_Arriendo_Minimo_Detalle)
admin.site.register(Propuesta_Arriendo_Variable)
admin.site.register(Propuesta_Arriendo_Bodega)
admin.site.register(Propuesta_Cuota_Incorporacion)
admin.site.register(Propuesta_Fondo_Promocion)
admin.site.register(Propuesta_Gasto_Comun)
