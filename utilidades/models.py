from __future__ import unicode_literals

from django.db import models

# modelos
class Moneda(models.Model):

	# atributos (generales)
	nombre      	= models.CharField(max_length=250)
	simbolo     	= models.CharField(max_length=250)
	abrev       	= models.CharField(max_length=250)
	descripcion 	= models.TextField(blank=True)

	# atributos (por defecto)
	visible     	= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.abrev

	class Meta:
		verbose_name 		= 'Moneda'
		verbose_name_plural = 'Monedas'

class Moneda_Historial(models.Model):

	# atributos (generales)
	valor   = models.DecimalField(max_digits=24, decimal_places=4)
	fecha   = models.DateTimeField(auto_now=True)

	# relaciones
	moneda = models.ForeignKey(Moneda)

	def __str__(self):
		return self.moneda.nombre

	class Meta:
		verbose_name 		= 'Historial de Moneda'
		verbose_name_plural = 'Historial de Monedas'

class Region(models.Model):

	# atributos (generales)
	nombre      	= models.CharField(max_length=250)
	ordinal     	= models.CharField(max_length=250)

	# atributos (por defecto)
	visible     	= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Región'
		verbose_name_plural = 'Regiones'

class Provincia(models.Model):

	# atributos (generales)
	nombre      	= models.CharField(max_length=250)

	# atributos (por defecto)
	visible     	= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	region = models.ForeignKey(Region)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Provincia'
		verbose_name_plural = 'Provincias'

class Comuna(models.Model):

	# atributos (generales)
	nombre      	= models.CharField(max_length=250)

	# atributos (por defecto)
	visible     	= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	provincia = models.ForeignKey(Provincia)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Comuna'
		verbose_name_plural = 'Comunas'

class Estado_Civil(models.Model):

	# atributos (generales)
	nombre      	= models.CharField(max_length=250)
	codigo     		= models.CharField(max_length=250)
	descripcion 	= models.TextField(blank=True)

	# atributos (por defecto)
	visible     	= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Estado Civil'
		verbose_name_plural = 'Estados Civiles'

class Tarifa_Electricidad(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	codigo 			= models.CharField(max_length=250)
	valor			= models.FloatField()
	descripcion 	= models.TextField(blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.codigo

	class Meta:
		verbose_name 		= 'Tarifa de Electricidad'
		verbose_name_plural = 'Tarifas de Electricidad'

class Giro(models.Model):

	# atributos (generales)
	codigo 					= models.IntegerField()
	descripcion 			= models.TextField(blank=True)
	afecto_iva 				= models.BooleanField(default=False)
	categoria_tributaria 	= models.CharField(max_length=250)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.codigo)+' - '+str(self.descripcion)

	class Meta:
		verbose_name 		= 'Giro'
		verbose_name_plural = 'Giros'
