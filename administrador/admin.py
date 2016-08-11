from django.contrib import admin
from .models import *

# Modelos
class ConfiguracionInline(admin.StackedInline):
	model = Configuracion

class ConfiguracionAdmin(admin.ModelAdmin):
	inlines = [ ConfiguracionInline, ]

admin.site.register(Empresa, ConfiguracionAdmin)
admin.site.register(Cliente)
admin.site.register(Representante)
admin.site.register(Conexion)
