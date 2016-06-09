from django.contrib import admin
from .models import Empresa, Moneda, Unidad_Negocio

# Register your models here.
admin.site.register(Empresa)
admin.site.register(Moneda)
admin.site.register(Unidad_Negocio)
