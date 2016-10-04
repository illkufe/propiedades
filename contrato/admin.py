from django.contrib import admin
from .models import *

# Modelos
admin.site.register(Contrato_Estado)
admin.site.register(Contrato_Tipo)
admin.site.register(Contrato)
admin.site.register(Propuesta_Contrato)
admin.site.register(Propuesta_Version)

