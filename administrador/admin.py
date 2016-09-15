from django.contrib import admin
from .models import *

# Modelos
class ConfiguracionInline(admin.StackedInline):
	model = Configuracion

class ConexionInline(admin.StackedInline):
	model = Conexion

class SettingAdmin(admin.ModelAdmin):
	inlines = [ ConfiguracionInline, ConexionInline]

admin.site.register(Empresa, SettingAdmin)
admin.site.register(Cliente)
admin.site.register(Representante)
admin.site.register(Conexion)
