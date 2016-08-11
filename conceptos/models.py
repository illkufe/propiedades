from __future__ import unicode_literals

from django.db import models
from administrador.models import Empresa
from activos.models import Activo

# Modelos
class Concepto_Tipo(models.Model):

	nombre 		= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=250)
	template 	= models.CharField(max_length=250, null=True, blank=True)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresas = models.ManyToManyField(Empresa, blank=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Tipo de Concepto"
		verbose_name_plural = "Tipos de Conceptos"

class Concepto(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	codigo 				= models.CharField(max_length=250)
	iva 				= models.BooleanField(default=False)
	codigo_documento 	= models.CharField(max_length=100, blank=True)
	codigo_producto 	= models.CharField(max_length=100, blank=True)
	codigo_1 			= models.CharField(max_length=100, blank=True) # cuenta contable
	codigo_2 			= models.CharField(max_length=100, blank=True) # area
	codigo_3 			= models.CharField(max_length=100, blank=True) # centro de costo
	codigo_4 			= models.CharField(max_length=100, blank=True) # item
	descripcion 		= models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	concepto_tipo 	= models.ForeignKey(Concepto_Tipo)
	empresa 		= models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Concepto"
		verbose_name_plural = "Conceptos"


