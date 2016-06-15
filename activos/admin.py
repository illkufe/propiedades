from django.contrib import admin
from .models import Activo, Sector, Nivel, Tarifa_Electricidad, Medidor_Electricidad, Medidor_Agua, Medidor_Gas

# Modelos Disponibles en Admin
admin.site.register(Activo)
admin.site.register(Sector)
admin.site.register(Nivel)
admin.site.register(Tarifa_Electricidad)
admin.site.register(Medidor_Electricidad)
admin.site.register(Medidor_Agua)
admin.site.register(Medidor_Gas)

