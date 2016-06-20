from django.contrib import admin
from .models import Lectura_Electricidad, Lectura_Agua, Lectura_Gas

# Modelos
admin.site.register(Lectura_Electricidad)
admin.site.register(Lectura_Agua)
admin.site.register(Lectura_Gas)