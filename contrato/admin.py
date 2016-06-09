from django.contrib import admin
from .models import Contrato_Tipo, Contrato, Arriendo, Arriendo_Detalle

# Register your models here.
admin.site.register(Contrato_Tipo)
admin.site.register(Contrato)
admin.site.register(Arriendo)
admin.site.register(Arriendo_Detalle)