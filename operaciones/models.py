from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from locales.models import Medidor_Electricidad, Medidor_Agua, Medidor_Gas

# Modelos
class Lectura_Electricidad(models.Model):

	MESES = (
		(1, 'ENERO'),
		(2, 'FEBRERO'),
		(3, 'MARZO'),
		(4, 'ABRIL'),
		(5, 'MAYO'),
		(6, 'JUNIO'),
		(7, 'JULIO'),
		(8, 'AGOSTO'),
		(9, 'SEPTIEMBRE'),
		(10, 'OCTUBRE'),
		(11, 'NOVIEMBRE'),
		(12, 'DICIEMBRE'),
	)

	mes 			= models.IntegerField(choices=MESES)
	anio			= models.IntegerField()
	valor 			= models.FloatField()
	imagen_file 	= models.FileField(upload_to='lectura-medidor', blank=True)
	imagen_type 	= models.CharField(max_length=250, blank=True)
	imagen_size 	= models.CharField(max_length=250, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	user 					= models.ForeignKey(User)
	medidor_electricidad 	= models.ForeignKey(Medidor_Electricidad)

	def __str__(self):
		return self.medidor_electricidad.nombre

	class Meta:
		verbose_name 		= "Lectura de Electricidad"
		verbose_name_plural = "Lecturas de Electricidad"

class Lectura_Agua(models.Model):

	MESES = (
		(1, 'ENERO'),
		(2, 'FEBRERO'),
		(3, 'MARZO'),
		(4, 'ABRIL'),
		(5, 'MAYO'),
		(6, 'JUNIO'),
		(7, 'JULIO'),
		(8, 'AGOSTO'),
		(9, 'SEPTIEMBRE'),
		(10, 'OCTUBRE'),
		(11, 'NOVIEMBRE'),
		(12, 'DICIEMBRE'),
	)

	mes 			= models.IntegerField(choices=MESES)
	anio			= models.IntegerField()
	valor 			= models.FloatField()
	imagen_file 	= models.FileField(upload_to='lectura-medidor', blank=True)
	imagen_type 	= models.CharField(max_length=250, blank=True)
	imagen_size 	= models.CharField(max_length=250, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	user 			= models.ForeignKey(User)
	medidor_agua 	= models.ForeignKey(Medidor_Agua)

	def __str__(self):
		return self.medidor_agua.nombre

	class Meta:
		verbose_name 		= "Lectura de Agua"
		verbose_name_plural = "Lecturas de Agua"

class Lectura_Gas(models.Model):

	MESES = (
		(1, 'ENERO'),
		(2, 'FEBRERO'),
		(3, 'MARZO'),
		(4, 'ABRIL'),
		(5, 'MAYO'),
		(6, 'JUNIO'),
		(7, 'JULIO'),
		(8, 'AGOSTO'),
		(9, 'SEPTIEMBRE'),
		(10, 'OCTUBRE'),
		(11, 'NOVIEMBRE'),
		(12, 'DICIEMBRE'),
	)

	mes 			= models.IntegerField(choices=MESES)
	anio			= models.IntegerField()
	valor 			= models.FloatField()
	imagen_file 	= models.FileField(upload_to='lectura-medidor', blank=True)
	imagen_type 	= models.CharField(max_length=250, blank=True)
	imagen_size 	= models.CharField(max_length=250, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	user 			= models.ForeignKey(User)
	medidor_gas 	= models.ForeignKey(Medidor_Gas)

	def __str__(self):
		return self.medidor_gas.nombre

	class Meta:
		verbose_name 		= "Lectura de Gas"
		verbose_name_plural = "Lecturas de Gas"
