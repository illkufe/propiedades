from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from administrador.models import Empresa

# Modelos
class Reporte_Tipo(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=250, blank=True)
	descripcion = models.TextField(blank=True)
	borrar 		= models.CharField(max_length=250)

	# atributos de configuración
	color 		= models.CharField(max_length=7)
	icono 		= models.CharField(max_length=250)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresas 	= models.ManyToManyField(Empresa, blank=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Tipo de Reporte"
		verbose_name_plural = "Tipos de Reportes"

class Reporte(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	nombre_pdf 	= models.CharField(max_length=250)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user 			= models.ForeignKey(User)
	empresa 		= models.ForeignKey(Empresa)
	reporte_tipo 	= models.ForeignKey(Reporte_Tipo)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Reporte"
		verbose_name_plural = "Reportes"

