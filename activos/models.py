from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from administrador.models import Empresa

# Modelos
class Activo(models.Model):

	# atributos (identificacion Activo)
	nombre 			= models.CharField(max_length=250)
	codigo 			= models.CharField(max_length=250)
	tipo 			= models.CharField(max_length=250, blank=True)
	direccion 		= models.CharField(max_length=250, blank=True)
	comuna 			= models.CharField(max_length=250, blank=True)
	ciudad 			= models.CharField(max_length=250, blank=True)
	cabidad_terreno = models.FloatField(null=True, blank=True)
	cabidad_construccion = models.FloatField(null=True, blank=True)

	# atributos (informacion legal)
	propietario 		= models.CharField(max_length=250)
	rut_propietario 	= models.CharField(max_length=250)
	rol_avaluo 			= models.CharField(max_length=250, blank=True)
	inscripcion 		= models.CharField(max_length=250, blank=True)
	vendedor 			= models.CharField(max_length=250, blank=True)
	rut_vendedor 		= models.CharField(max_length=250, blank=True)
	datos_escritura 	= models.CharField(max_length=250, blank=True)
	nomina_numero 		= models.CharField(max_length=250, blank=True)
	nomina_repertorio 	= models.CharField(max_length=250, blank=True)
	nomina_fojas 		= models.CharField(max_length=250, blank=True)
	fecha_firma_nomina 	= models.DateField(null=True, blank=True)

	servicio_nomina 	= models.CharField(max_length=250, blank=True)	# Servicio Bienes Raices
	servicio_repertorio = models.CharField(max_length=250, blank=True)	# Servicio Bienes Raices
	servicio_fojas 		= models.CharField(max_length=250, blank=True)	# Servicio Bienes Raices
	fecha_servicio 		= models.DateField(null=True, blank=True)		# Servicio Bienes Raices

	# atributos (datos economicos)	

	fecha_adquisicion 	= models.DateField(null=True, blank=True)
	tasacion_fiscal 	= models.FloatField()
	avaluo_comercial 	= models.FloatField(null=True, blank=True)
	contibuciones 		= models.FloatField(null=True, blank=True)
	precio_compra 		= models.FloatField(null=True, blank=True)
	valor_tasacion		= models.FloatField(null=True, blank=True)
	fecha_tasacion 		= models.DateField(null=True, blank=True)
	tasacion_por 		= models.CharField(max_length=250, blank=True)
	leasing 			= models.BooleanField(default=False)
	hipoteca 			= models.BooleanField(default=False)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 		= models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

class Sector(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=250, blank=True)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	activo 	= models.ForeignKey(Activo)

	def __str__(self):
		return self.nombre

class Nivel(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=250, blank=True)
	descripcion = models.TextField(blank=True)
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	activo = models.ForeignKey(Activo)

	def __str__(self):
		return self.nombre

class Gasto_Mensual(models.Model):

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

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	user 	= models.ForeignKey(User)
	activo 	= models.ForeignKey(Activo)

	def __str__(self):
		return self.activo.nombre
