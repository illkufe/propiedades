from django.contrib import admin
from .models import Activo, Sector, Nivel, Medidor, Medidor_Tipo

# Register your models here.
admin.site.register(Activo)
admin.site.register(Sector)
admin.site.register(Nivel)
admin.site.register(Medidor)
admin.site.register(Medidor_Tipo)

