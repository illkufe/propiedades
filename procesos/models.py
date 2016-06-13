from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User, Group
from conceptos.models import Concepto
from contrato.models import Contrato


# Create your models here.
class Proceso_Estado(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

class Proceso(models.Model):

	# atributos (generales)
	fecha_inicio 		= models.DateField()
	fecha_termino 		= models.DateField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user 			= models.ForeignKey(User)
	concepto 		= models.ForeignKey(Concepto)
	proceso_estado 	= models.ForeignKey(Proceso_Estado)


	def __str__(self):
		return self.proceso_estado.nombre

class Proceso_Detalle(models.Model):
	
	total 			= models.FloatField()
	fecha_inicio 	= models.DateField()
	fecha_termino 	= models.DateField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	proceso 	= models.ForeignKey(Proceso)
	contrato 	= models.ForeignKey(Contrato)
	

	def __str__(self):
		return self.contrato.nombre_local

