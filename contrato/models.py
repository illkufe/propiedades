from __future__ import unicode_literals

from django.db import models
from administrador.models import Empresa, Cliente
from locales.models import Local
from conceptos.models import Concepto
from utilidades.models import Moneda

# modelos
class Contrato_Tipo(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=10, blank=True)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Tipo de Contrato"
		verbose_name_plural = "Tipos de Contratos"

class Contrato_Estado(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	background 	= models.CharField(max_length=7)
	color 		= models.CharField(max_length=7)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Estado de Contrato"
		verbose_name_plural = "Estados de Contratos"

class Contrato(models.Model):

	# atributos (generales)
	numero 				= models.IntegerField()
	fecha_contrato 		= models.DateField()
	nombre_local 		= models.CharField(max_length=250)
	fecha_inicio 		= models.DateField()
	fecha_termino 		= models.DateField()
	meses 				= models.IntegerField()
	fecha_habilitacion 	= models.DateField()
	fecha_activacion 	= models.DateField(null=True, blank=True)
	fecha_renovacion 	= models.DateField()
	fecha_remodelacion 	= models.DateField(null=True, blank=True)
	fecha_aviso 		= models.DateField()
	fecha_plazo 		= models.DateField(null=True, blank=True)
	dias_salida			= models.IntegerField()
	bodega 				= models.BooleanField(default=False)
	metros_bodega		= models.FloatField(default=0, null=True, blank=True)
	destino_comercial 	= models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 		= models.ForeignKey(Empresa)
	tipo 			= models.ForeignKey(Contrato_Tipo)
	estado 			= models.ForeignKey(Contrato_Estado)
	cliente 		= models.ForeignKey(Cliente)
	locales 		= models.ManyToManyField(Local)
	conceptos 		= models.ManyToManyField(Concepto)

	def __str__(self):
		return self.nombre_local

	class Meta:
		verbose_name 		= "Contrato"
		verbose_name_plural = "Contratos"

class Garantia(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	valor		= models.FloatField(default=0)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.nombre

class Multa_Tipo(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=10, blank=True)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 	= models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

# Modelos (conceptos)
class Multa(models.Model):

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
	valor		= models.FloatField()
	mes 		= models.IntegerField(choices=MESES)
	anio		= models.IntegerField()
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 	= models.ForeignKey(Empresa)
	multa_tipo 	= models.ForeignKey(Multa_Tipo)
	contrato 	= models.ForeignKey(Contrato)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.contrato.nombre_local

class Arriendo(models.Model):

	# atributos (generales
	reajuste 		= models.BooleanField(default=False)
	por_meses 		= models.BooleanField(default=False)
	meses 			= models.IntegerField(default=0)
	valor			= models.FloatField(default=0)
	fecha_inicio 	= models.DateField()
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	concepto 	= models.ForeignKey(Concepto)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.contrato.nombre_local

class Arriendo_Detalle(models.Model):

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

	# atributos (generales
	mes_inicio 		= models.IntegerField(choices=MESES)
	mes_termino		= models.IntegerField(choices=MESES)
	valor			= models.FloatField()
	metro_cuadrado 	= models.BooleanField(default=False)
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	arriendo 	= models.ForeignKey(Arriendo)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.arriendo.contrato.nombre_local

class Arriendo_Bodega(models.Model):

	PERIODICIDAD = (
		(0, 'ANUAL'),
		(1, 'SEMESTRAL'),
		(2, 'TRIMESTRAL'),
		(3, 'MENSUAL'),
	)

	# atributos (generales
	periodicidad	= models.IntegerField(choices=PERIODICIDAD)
	valor			= models.FloatField()
	fecha_inicio 	= models.DateField()
	metro_cuadrado 	= models.BooleanField(default=False)
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	concepto 	= models.ForeignKey(Concepto)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.contrato.nombre_local

class Arriendo_Variable(models.Model):

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

	# atributos (generales
	mes_inicio 		= models.IntegerField(choices=MESES)
	mes_termino		= models.IntegerField(choices=MESES)
	anio_inicio		= models.IntegerField()
	anio_termino 	= models.IntegerField()
	fecha_inicio 	= models.DateField()
	fecha_termino 	= models.DateField()

	valor			= models.FloatField()
	relacion		= models.BooleanField(default=False)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 		= models.ForeignKey(Contrato)
	moneda 			= models.ForeignKey(Moneda)
	concepto 		= models.ForeignKey(Concepto)
	arriendo_minimo = models.ForeignKey(Concepto, related_name='arriendo_minimo', null=True, blank=True)

	def __str__(self):
		return self.contrato.nombre_local

class Gasto_Comun(models.Model):

	# atributos (generales)
	valor		= models.FloatField(default=0)
	prorrateo 	= models.BooleanField(default=False)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	local 		= models.ForeignKey(Local)
	moneda 		= models.ForeignKey(Moneda)
	concepto 	= models.ForeignKey(Concepto)

	def __str__(self):
		return self.local.nombre

class Servicio_Basico(models.Model):

	# atributos (generales)
	valor_electricidad	= models.FloatField()
	valor_agua			= models.FloatField()
	valor_gas			= models.FloatField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	locales 	= models.ManyToManyField(Local)
	concepto 	= models.ForeignKey(Concepto)

	def __str__(self):
		return self.contrato.nombre_local

class Cuota_Incorporacion(models.Model):

	# atributos (generales)
	fecha 			= models.DateField()
	valor			= models.FloatField()
	metro_cuadrado 	= models.BooleanField(default=False)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	moneda 		= models.ForeignKey(Moneda)
	concepto 	= models.ForeignKey(Concepto)

	def __str__(self):
		return self.contrato.nombre_local

class Fondo_Promocion(models.Model):

	PERIODICIDAD = (
		(0, 'ANUAL'),
		(1, 'SEMESTRAL'),
		(2, 'TRIMESTRAL'),
		(3, 'MENSUAL'),
	)

	# atributos (generales)
	fecha 			= models.DateField()
	valor			= models.FloatField()
	periodicidad	= models.IntegerField(choices=PERIODICIDAD)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	concepto 	= models.ForeignKey(Concepto)
	moneda 		= models.ForeignKey(Moneda)
	vinculo 	= models.ForeignKey(Concepto, related_name='vinculo')

	def __str__(self):
		return self.contrato.nombre_local
