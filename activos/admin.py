from django.contrib import admin
from .models import *

# modelos
class SectorInline(admin.StackedInline):
	model = Sector

class NivelInline(admin.StackedInline):
	model = Nivel

class ActivoInlineAdmin(admin.ModelAdmin):
	inlines = [ SectorInline, NivelInline]

admin.site.register(Activo, ActivoInlineAdmin)
admin.site.register(Gasto_Mensual)
admin.site.register(Configuracion_Activo)
