from __future__ import unicode_literals

from django.db import models
from administrador.models import Empresa, Cliente, Moneda
from locales.models import Local
from conceptos.models import Concepto

# Modelos
class Contrato_Tipo(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	codigo 		= models.CharField(max_length=250, blank=True)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

class Contrato_Estado(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

class Contrato(models.Model):

	# atributos (generales)
	numero 				= models.IntegerField()
	fecha_contrato 		= models.DateField()
	nombre_local 		= models.CharField(max_length=250)
	fecha_inicio 		= models.DateField()
	fecha_termino 		= models.DateField()
	fecha_habilitacion 	= models.DateField()
	fecha_activacion 	= models.DateField()
	fecha_renovacion 	= models.DateField()
	fecha_remodelacion 	= models.DateField()
	fecha_aviso 		= models.DateField()
	fecha_plazo 		= models.DateField()

	comentario 			= models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 		= models.ForeignKey(Empresa)
	contrato_tipo 	= models.ForeignKey(Contrato_Tipo)
	contrato_estado = models.ForeignKey(Contrato_Estado)
	cliente 		= models.ForeignKey(Cliente)
	locales 		= models.ManyToManyField(Local)
	conceptos 		= models.ManyToManyField(Concepto)

	def __str__(self):
		return self.nombre_local

class Arriendo(models.Model):

	# atributos (generales
	reajuste 		= models.BooleanField(default=False)
	meses 			= models.IntegerField()
	valor			= models.FloatField()
	fecha_inicio 	= models.DateField()
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.contrato.nombre_local

class Arriendo_Detalle(models.Model):

	MESES = (
		('1', 'ENERO'),
		('2', 'FEBRERO'),
		('3', 'MARZO'),
		('4', 'ABRIL'),
		('5', 'MAYO'),
		('6', 'JUNIO'),
		('7', 'JULIO'),
		('8', 'AGOSTO'),
		('9', 'SEPTIEMBRE'),
		('10', 'OCTUBRE'),
		('11', 'NOVIEMBRE'),
		('12', 'DICIEMBRE'),
	)

	# atributos (generales
	mes_inicio 		= models.CharField(max_length=2, choices=MESES)
	mes_termino		= models.CharField(max_length=2, choices=MESES)
	valor			= models.FloatField()
	metro_cuadrado 	= models.BooleanField(default=False)
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	arriendo 	= models.ForeignKey(Arriendo)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.mes_inicio

class Arriendo_Variable(models.Model):

	MESES = (
		('1', 'ENERO'),
		('2', 'FEBRERO'),
		('3', 'MARZO'),
		('4', 'ABRIL'),
		('5', 'MAYO'),
		('6', 'JUNIO'),
		('7', 'JULIO'),
		('8', 'AGOSTO'),
		('9', 'SEPTIEMBRE'),
		('10', 'OCTUBRE'),
		('11', 'NOVIEMBRE'),
		('12', 'DICIEMBRE'),
	)

	PERIODICIDAD = (
		('0', 'ANUAL'),
		('1', 'SEMESTRAL'),
		('2', 'TRIMESTRAL'),
		('3', 'MENSUAL'),
		('4', 'QUINCENAL'),
		('5', 'SEMANAL'),
		('6', 'DIARIA'),
	)

	# atributos (generales
	mes_inicio 		= models.CharField(max_length=2, choices=MESES)
	mes_termino		= models.CharField(max_length=2, choices=MESES)
	periodicidad	= models.CharField(max_length=1, choices=PERIODICIDAD)
	valor			= models.FloatField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.contrato.nombre_local

class Servicio_Basico(models.Model):

	TIPO = (
		('1', 'AGUA'),
		('2', 'ELECTRICIDAD'),
		('3', 'GAS'),
	)

	MESES = (
		('1', 'ENERO'),
		('2', 'FEBRERO'),
		('3', 'MARZO'),
		('4', 'ABRIL'),
		('5', 'MAYO'),
		('6', 'JUNIO'),
		('7', 'JULIO'),
		('8', 'AGOSTO'),
		('9', 'SEPTIEMBRE'),
		('10', 'OCTUBRE'),
		('11', 'NOVIEMBRE'),
		('12', 'DICIEMBRE'),
	)

	# atributos (generales
	tipo			= models.CharField(max_length=1, choices=TIPO)
	mes_inicio 		= models.CharField(max_length=2, choices=MESES)
	mes_termino		= models.CharField(max_length=2, choices=MESES)
	valor			= models.FloatField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	local 		= models.ForeignKey(Local)

	def __str__(self):
		return self.local.nombre

class Gasto_Comun(models.Model):

	MESES = (
		('1', 'ENERO'),
		('2', 'FEBRERO'),
		('3', 'MARZO'),
		('4', 'ABRIL'),
		('5', 'MAYO'),
		('6', 'JUNIO'),
		('7', 'JULIO'),
		('8', 'AGOSTO'),
		('9', 'SEPTIEMBRE'),
		('10', 'OCTUBRE'),
		('11', 'NOVIEMBRE'),
		('12', 'DICIEMBRE'),
	)

	# atributos (generales
	mes_inicio 		= models.CharField(max_length=2, choices=MESES)
	mes_termino		= models.CharField(max_length=2, choices=MESES)
	valor			= models.FloatField()
	prorrateo 		= models.BooleanField(default=False)
	valor_prorrateo	= models.FloatField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	contrato 	= models.ForeignKey(Contrato)
	local 		= models.ForeignKey(Local)
	moneda 		= models.ForeignKey(Moneda)

	def __str__(self):
		return self.local.nombre



