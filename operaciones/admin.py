from django.contrib import admin
from .models import *

# Modelos
admin.site.register(Lectura_Electricidad)
admin.site.register(Lectura_Agua)
admin.site.register(Lectura_Gas)