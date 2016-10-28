from django.contrib import admin
from .models import *

# Modelos
class ConfiguracionInline(admin.StackedInline):
	model = Configuracion

class ConexionInline(admin.StackedInline):
	model = Conexion

class ConfiguracionMonedaInline(admin.StackedInline):
	model = Configuracion_Monedas

class SettingAdmin(admin.ModelAdmin):
	inlines = [ ConfiguracionInline, ConexionInline, ConfiguracionMonedaInline]





admin.site.register(Empresa, SettingAdmin)
admin.site.register(Cliente)
admin.site.register(Representante)
admin.site.register(Conexion)
admin.site.register(Clasificacion)
admin.site.register(Clasificacion_Detalle)
admin.site.register(Tipo_Clasificacion)
admin.site.register(Tipo_Operacion)
admin.site.register(Entidad_Asociacion)
admin.site.register(Tipo_Estado_Proceso)
admin.site.register(Proceso)
admin.site.register(Proceso_Condicion)
admin.site.register(Workflow)
admin.site.register(Configuracion_Monedas)