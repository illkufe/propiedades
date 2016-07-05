from django.contrib import admin
from .models import Contrato_Tipo, Contrato, Arriendo, Arriendo_Detalle, Arriendo_Variable, Gasto_Comun, Servicio_Basico, Cuota_Incorporacion, Fondo_Promocion

# Modelos
admin.site.register(Contrato_Tipo)
admin.site.register(Contrato)
admin.site.register(Arriendo)
admin.site.register(Arriendo_Detalle)
admin.site.register(Arriendo_Variable)
admin.site.register(Gasto_Comun)
admin.site.register(Servicio_Basico)
admin.site.register(Cuota_Incorporacion)
admin.site.register(Fondo_Promocion)