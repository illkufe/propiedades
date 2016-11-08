from django.contrib import admin
from .models import *

# modelos
class ConfiguracionInline(admin.StackedInline):
	model = Configuracion

class ConexionInline(admin.StackedInline):
	model = Conexion

class ConfiguracionMonedaInline(admin.StackedInline):
	model = Configuracion_Monedas

class RepresentanteInline(admin.StackedInline):
	model = Representante

class EmpresaInlineAdmin(admin.ModelAdmin):
	inlines = [ ConfiguracionInline, ConexionInline, ConfiguracionMonedaInline]

class ClienteInlineAdmin(admin.ModelAdmin):
	inlines = [ RepresentanteInline]

admin.site.register(Empresa, EmpresaInlineAdmin)
admin.site.register(Cliente, ClienteInlineAdmin)
admin.site.register(Clasificacion)
admin.site.register(Clasificacion_Detalle)
admin.site.register(Tipo_Clasificacion)
admin.site.register(Tipo_Operacion)
admin.site.register(Entidad_Asociacion)
admin.site.register(Tipo_Estado_Proceso)
admin.site.register(Proceso)
admin.site.register(Proceso_Condicion)
admin.site.register(Workflow)