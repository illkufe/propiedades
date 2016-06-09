from django.contrib import admin
from .models import Proceso, Proceso_Estado, Proceso_Detalle

# Register your models here.
admin.site.register(Proceso)
admin.site.register(Proceso_Estado)
admin.site.register(Proceso_Detalle)