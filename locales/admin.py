from django.contrib import admin
from .models import Local, Local_Tipo, Venta, Medidor_Electricidad, Medidor_Agua, Medidor_Gas

# Modelos
admin.site.register(Local)
admin.site.register(Local_Tipo)
admin.site.register(Venta)
admin.site.register(Medidor_Electricidad)
admin.site.register(Medidor_Agua)
admin.site.register(Medidor_Gas)