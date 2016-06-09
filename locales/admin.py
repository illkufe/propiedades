from django.contrib import admin
from .models import Local, Local_Tipo, Venta

# Register your models here.
admin.site.register(Local)
admin.site.register(Local_Tipo)
admin.site.register(Venta)