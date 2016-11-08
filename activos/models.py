from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from administrador.models import Empresa

# modelos
class Activo(models.Model):

	# atributos (identificacion Activo)
	nombre 					= models.CharField(max_length=250)
	codigo 					= models.CharField(max_length=10)
	tipo 					= models.CharField(max_length=250, blank=True)
	direccion 				= models.CharField(max_length=250, blank=True)
	comuna 					= models.CharField(max_length=250, blank=True)
	ciudad 					= models.CharField(max_length=250, blank=True)
	cabidad_terreno 		= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	cabidad_construccion 	= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)

	# atributos (informacion legal)
	propietario 		= models.CharField(max_length=250)
	rut_propietario 	= models.CharField(max_length=250)
	rol_avaluo 			= models.CharField(max_length=250, blank=True)

	# atributos (inscripcion vigente)
	inscripcion 		= models.CharField(max_length=250, blank=True)
	foja 				= models.CharField(max_length=250, blank=True)
	numero_inscripcion 	= models.IntegerField(null=True, blank=True)
	año 				= models.IntegerField(null=True, blank=True)
	conservador_bienes	= models.CharField(max_length=250, blank=True)
	
	# atributos (datos de escritura)
	fecha_escritura 	= models.DateField(null=True, blank=True)
	repertorio 			= models.CharField(max_length=250, blank=True)
	notaria 			= models.CharField(max_length=250, blank=True)
	vendedor 			= models.CharField(max_length=250, blank=True)
	rut_vendedor 		= models.CharField(max_length=250, blank=True)

	# atributos (datos economicos)
	fecha_adquisicion 	= models.DateField(null=True, blank=True)
	tasacion_fiscal 	= models.DecimalField(max_digits=24, decimal_places=4)
	avaluo_comercial 	= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	contribuciones 		= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	precio_compra 		= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	valor_tasacion		= models.DecimalField(max_digits=24, decimal_places=4, null=True, blank=True)
	fecha_tasacion 		= models.DateField(null=True, blank=True)
	tasacion_por 		= models.CharField(max_length=250, blank=True)
	leasing 			= models.BooleanField(default=False)
	hipoteca 			= models.BooleanField(default=False)

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now_add=True)
	modificado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Activo'
		verbose_name_plural = 'Activos'

class Sector(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	codigo 			= models.CharField(max_length=8, blank=True)
	descripcion 	= models.TextField(blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	activo = models.ForeignKey(Activo)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Sector'
		verbose_name_plural = 'Sectores'

class Nivel(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	codigo 			= models.CharField(max_length=8, blank=True)
	descripcion 	= models.TextField(blank=True)
	
	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	activo = models.ForeignKey(Activo)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Nivel'
		verbose_name_plural = 'Niveles'

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

	# atributos (generales)
	mes 			= models.IntegerField(choices=MESES)
	anio			= models.IntegerField()
	valor 			= models.DecimalField(max_digits=24, decimal_places=4)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user 	= models.ForeignKey(User)
	activo 	= models.ForeignKey(Activo)

	def __str__(self):
		return self.activo.nombre+' - '+str(self.mes)+' - '+str(self.anio)

	class Meta:
		verbose_name 		= 'Gasto Mensual'
		verbose_name_plural = 'Gastos Mensuales'
