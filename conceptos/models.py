from __future__ import unicode_literals

from django.db import models
from administrador.models import *
from activos.models import Activo

# modelos
class Concepto_Tipo(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	codigo 			= models.CharField(max_length=10)
	template 		= models.CharField(max_length=250, null=True, blank=True)
	descripcion 	= models.TextField(blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresas 		= models.ManyToManyField(Empresa, blank=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Tipo de Concepto'
		verbose_name_plural = 'Tipos de Conceptos'

class Concepto(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	codigo 				= models.CharField(max_length=10)
	iva 				= models.BooleanField(default=False)
	descripcion 		= models.TextField(blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	concepto_tipo 	= models.ForeignKey(Concepto_Tipo)
	empresa 		= models.ForeignKey(Empresa)
	configuracion 	= models.ManyToManyField(Cliente, through='Configuracion_Concepto')

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Concepto'
		verbose_name_plural = 'Conceptos'

class Configuracion_Concepto(models.Model):

	# atributos (generales)
	estado 				= models.BooleanField(default=False)
	codigo_documento 	= models.CharField(max_length=100)
	codigo_producto 	= models.CharField(max_length=100)
	codigo_1 			= models.CharField(max_length=100, blank=True) # cuenta contable
	codigo_2 			= models.CharField(max_length=100, blank=True) # area
	codigo_3 			= models.CharField(max_length=100, blank=True) # centro de costo
	codigo_4 			= models.CharField(max_length=100, blank=True) # item

	# relaciones
	concepto 	= models.ForeignKey(Concepto)
	cliente 	= models.ForeignKey(Cliente)

	def __str__(self):
		return self.cliente.nombre+' - '+self.concepto.nombre

	class Meta:
		verbose_name 		= 'Configuración de Concepto'
		verbose_name_plural = 'Configuración de Conceptos'


