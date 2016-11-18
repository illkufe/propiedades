from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from administrador.models import Empresa, Clasificacion_Detalle
from activos.models import Activo, Sector, Nivel
from utilidades.models import Tarifa_Electricidad

# modelos
class Local_Tipo(models.Model):

	# atributos (generales)
	nombre  		= models.CharField(max_length=250)
	descripcion 	= models.TextField(blank=True)
	prorrateo 		= models.BooleanField(default=False) #{falta: sacar campo}

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Tipo de Local'
		verbose_name_plural = 'Tipos de Locales'

class Local(models.Model):

	# atributos (generales)
	nombre  			= models.CharField(max_length=250)
	codigo  			= models.CharField(max_length=10)
	prorrateo 			= models.BooleanField(default=False)
	metros_cuadrados 	= models.DecimalField(max_digits=24, decimal_places=4)
	metros_lineales 	= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	metros_compartidos 	= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	descripcion 		= models.TextField(blank=True)

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now_add=True)
	modificado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	activo 				= models.ForeignKey(Activo)
	sector 				= models.ForeignKey(Sector)
	nivel 				= models.ForeignKey(Nivel)
	local_tipo 			= models.ForeignKey(Local_Tipo)
	clasificaciones  	= models.ManyToManyField(Clasificacion_Detalle)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Local'
		verbose_name_plural = 'Locales'

class Venta(models.Model):

	PERIODICIDAD = (
		(1, 'DIARIA'),
		(2, 'MENSUAL'),
	)

	# atributos (generales)
	fecha_inicio 	= models.DateTimeField()
	fecha_termino 	= models.DateTimeField()
	periodicidad	= models.IntegerField(choices=PERIODICIDAD)
	valor 			= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	
	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	local = models.ForeignKey(Local)

	def __str__(self):
		return self.local.nombre

	class Meta:
		verbose_name 		= 'Venta'
		verbose_name_plural = 'Ventas'

class Medidor_Electricidad(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	numero_rotulo 		= models.CharField(max_length=250)
	potencia			= models.FloatField(default=0, null=True, blank=True)
	potencia_presente	= models.FloatField(default=0, null=True, blank=True)
	potencia_fuera		= models.FloatField(default=0, null=True, blank=True)

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now_add=True)
	modificado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	local 				= models.ForeignKey(Local)
	tarifa_electricidad	= models.ForeignKey(Tarifa_Electricidad)
	
	def __str__(self):
		return self.local.nombre+' - '+self.nombre

	class Meta:
		verbose_name 		= 'Medidor de Electricidad'
		verbose_name_plural = 'Medidores de Electricidad'

class Medidor_Agua(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	numero_rotulo 	= models.CharField(max_length=250)
	potencia		= models.FloatField(default=0, null=True, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	local = models.ForeignKey(Local)

	def __str__(self):
		return self.local.nombre+' - '+self.nombre

	class Meta:
		verbose_name 		= 'Medidor de Agua'
		verbose_name_plural = 'Medidores de Agua'

class Medidor_Gas(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	numero_rotulo 	= models.CharField(max_length=250)
	potencia		= models.FloatField(default=0, null=True, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	local = models.ForeignKey(Local)

	def __str__(self):
		return self.local.nombre+' - '+self.nombre

	class Meta:
		verbose_name 		= 'Medidor de Gas'
		verbose_name_plural = 'Medidores de Gas'

class Gasto_Servicio(models.Model):

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

	# atributos (por defecto)
	nombre 			= models.CharField(max_length=250)
	mes 			= models.IntegerField(choices=MESES)
	anio			= models.IntegerField()
	valor 			= models.DecimalField(max_digits=24, decimal_places=4)
	imagen_file 	= models.FileField(upload_to='gastos-servicios', blank=True)
	imagen_type 	= models.CharField(max_length=250, blank=True)
	imagen_size 	= models.CharField(max_length=250, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user 	= models.ForeignKey(User)
	locales = models.ManyToManyField(Local)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Gasto de Servicio'
		verbose_name_plural = 'Gastos de Servicios'
