from django.contrib import admin
from .models import Activo, Sector, Nivel

# Modelos Disponibles en Admin
admin.site.register(Activo)
admin.site.register(Sector)
admin.site.register(Nivel)
