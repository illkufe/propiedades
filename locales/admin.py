from django.contrib import admin
from .models import *

# Modelos
admin.site.register(Local)
admin.site.register(Local_Tipo)
admin.site.register(Medidor_Electricidad)
admin.site.register(Medidor_Agua)
admin.site.register(Medidor_Gas)
admin.site.register(Gasto_Servicio)