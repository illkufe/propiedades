from django.contrib import admin
from .models import *

# Modelos

class ConfiguracionInline(admin.StackedInline):
	model = Configuracion

class ConfiguracionAdmin(admin.ModelAdmin):
	inlines = [ ConfiguracionInline, ]

# admin.site.register(Region)
# admin.site.register(Provincia)
# admin.site.register(Comuna)
# admin.site.register(Estado_Civil)
# admin.site.register(Moneda)
# admin.site.register(Moneda_Historial)
# admin.site.register(Tarifa_Electricidad)
admin.site.register(Empresa, ConfiguracionAdmin)
admin.site.register(Cliente)
admin.site.register(Representante)
