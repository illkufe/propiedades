from django.contrib import admin
from .models import Proceso, Proceso_Estado, Detalle_Arriendo_Minimo, Detalle_Gasto_Comun, Detalle_Electricidad, Detalle_Agua, Detalle_Gas

# Register your models here.
admin.site.register(Proceso)
admin.site.register(Proceso_Estado)
admin.site.register(Detalle_Arriendo_Minimo)
admin.site.register(Detalle_Gasto_Comun)
admin.site.register(Detalle_Electricidad)
admin.site.register(Detalle_Agua)
admin.site.register(Detalle_Gas)