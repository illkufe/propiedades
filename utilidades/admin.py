from django.contrib import admin
from .models import *

# Modelos
admin.site.register(Moneda)
admin.site.register(Moneda_Historial)
admin.site.register(Region)
admin.site.register(Provincia)
admin.site.register(Comuna)
admin.site.register(Estado_Civil)
admin.site.register(Tarifa_Electricidad)