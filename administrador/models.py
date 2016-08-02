from __future__ import unicode_literals
from django.db import models

# Modelos
class Region(models.Model):

	# atributos (generales)
	nombre      = models.CharField(max_length=250)
	ordinal     = models.CharField(max_length=250)

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

class Provincia(models.Model):

	# atributos (generales)
	nombre      = models.CharField(max_length=250)

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	# relaciones
	region = models.ForeignKey(Region)

	def __str__(self):
		return self.nombre

class Comuna(models.Model):

	# atributos (generales)
	nombre      = models.CharField(max_length=250)

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	# relaciones
	provincia = models.ForeignKey(Provincia)

	def __str__(self):
		return self.nombre

class Estado_Civil(models.Model):

	# atributos (generales)
	nombre      = models.CharField(max_length=250)
	codigo     	= models.CharField(max_length=250)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

class Tarifa_Electricidad(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=250)
	valor		= models.FloatField()
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.codigo

class Moneda(models.Model):

	# atributos (generales)
	nombre      = models.CharField(max_length=250)
	simbolo     = models.CharField(max_length=250)
	abrev       = models.CharField(max_length=250)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.abrev

class Moneda_Historial(models.Model):

	# atributos (generales)
	valor   = models.FloatField()
	fecha   = models.DateTimeField(auto_now=True)

	# relaciones
	moneda = models.ForeignKey(Moneda)

	def __str__(self):
		return self.moneda.nombre

class Empresa(models.Model):

	# atributos (generales)
	nombre 						= models.CharField(max_length=250)
	rut 						= models.CharField(max_length=250)
	cuidad 						= models.CharField(max_length=250)
	comuna 						= models.CharField(max_length=250)
	direccion 					= models.CharField(max_length=250)
	representante 				= models.CharField(max_length=250)
	representante_rut 			= models.CharField(max_length=250)
	representante_profesion 	= models.CharField(max_length=250)
	representante_nacionalidad 	= models.CharField(max_length=250)
	descripcion 				= models.TextField(blank=True)

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

class Cliente(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	rut             = models.CharField(max_length=250)
	razon_social 	= models.CharField(max_length=250, blank=True)
	giro 			= models.CharField(max_length=250, blank=True)
	region        	= models.CharField(max_length=250, blank=True)
	comuna        	= models.CharField(max_length=250, blank=True)
	direccion       = models.CharField(max_length=250)
	telefono        = models.CharField(max_length=250)
	cliente_tipo    = models.IntegerField()

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

class Representante(models.Model):

	# atributos (generales)
	nombre          = models.CharField(max_length=250)
	rut             = models.CharField(max_length=250)
	nacionalidad    = models.CharField(max_length=250)
	profesion       = models.CharField(max_length=250)
	domicilio       = models.CharField(max_length=250)

	# atributos (por defecto)
	visible     = models.BooleanField(default=True)
	creado_en   = models.DateTimeField(auto_now=True)

	# relaciones
	cliente 		= models.ForeignKey(Cliente)
	estado_civil 	= models.ForeignKey(Estado_Civil)
	

	def __str__(self):
		return self.nombre

class Configuracion(models.Model):

	FORMATO_DECIMAL = (
		(1, ','),
		(2, '.'),
	)

	# atributos (generales)
	formato_decimales	= models.IntegerField(choices=FORMATO_DECIMAL)
	cantidad_decimales	= models.IntegerField()

	# relaciones
	empresa = models.OneToOneField(Empresa)
	moneda 	= models.ForeignKey(Moneda)

	def __str__(self):
		return self.empresa.nombre
