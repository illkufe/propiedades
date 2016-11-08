from django.contrib import admin
from .models import *

# modelos
admin.site.register(Factura_Estado)
admin.site.register(Factura)
admin.site.register(Factura_Detalle)