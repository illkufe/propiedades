from __future__ import unicode_literals

from django.db import models
from administrador.models import Empresa, Moneda
from activos.models import Activo

# Create your models here.
class Concepto_Tipo(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre


class Concepto(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=250)
	template 	= models.CharField(max_length=250)
	orden 		= models.IntegerField()
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 		= models.ForeignKey(Empresa)
	moneda 			= models.ForeignKey(Moneda)
	concepto_tipo 	= models.ForeignKey(Concepto_Tipo)

	def __str__(self):
		return self.nombre
