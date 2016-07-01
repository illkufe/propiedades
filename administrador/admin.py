from django.contrib import admin
from .models import Empresa, Cliente, Moneda, Moneda_Historial, Tarifa_Electricidad

# Modelos
admin.site.register(Empresa)
admin.site.register(Cliente)
admin.site.register(Moneda)
admin.site.register(Moneda_Historial)
admin.site.register(Tarifa_Electricidad)