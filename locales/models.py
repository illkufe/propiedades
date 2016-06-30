# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from administrador.models import Empresa, Tarifa_Electricidad
from activos.models import Activo, Sector, Nivel

# Modelos
class Local_Tipo(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

class Local(models.Model):

	# atributos (generales)
	nombre  			= models.CharField(max_length=250)
	codigo  			= models.CharField(max_length=250)
	metros_cuadrados 	= models.FloatField()
	metros_lineales 	= models.FloatField(null=True, blank=True)
	metros_compartidos 	= models.FloatField(null=True, blank=True)
	descripcion 		= models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	activo 					= models.ForeignKey(Activo)
	sector 					= models.ForeignKey(Sector)
	nivel 					= models.ForeignKey(Nivel)
	local_tipo 				= models.ForeignKey(Local_Tipo)

	def __str__(self):
		return self.nombre

class Venta(models.Model):

	PERIODICIDAD = (
		(0, 'ANUAL'),
		(1, 'SEMESTRAL'),
		(2, 'TRIMESTRAL'),
		(3, 'MENSUAL'),
		(4, 'QUINCENAL'),
		(5, 'SEMANAL'),
		(6, 'DIARIA'),
	)

	# atributos (generales)
	fecha_inicio 	= models.DateTimeField()
	fecha_termino 	= models.DateTimeField()
	periodicidad	= models.IntegerField(choices=PERIODICIDAD)
	valor 			= models.FloatField()
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	local 		= models.ForeignKey(Local)

	def __str__(self):
		return self.local.nombre

class Medidor_Electricidad(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	numero_rotulo 		= models.CharField(max_length=250)
	potencia			= models.FloatField(default=0, null=True, blank=True)
	potencia_presente	= models.FloatField(default=0, null=True, blank=True)
	potencia_fuera		= models.FloatField(default=0, null=True, blank=True)

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now=True)

	# relaciones
	local 				= models.ForeignKey(Local)
	tarifa_electricidad	= models.ForeignKey(Tarifa_Electricidad)
	
	def __str__(self):
		return self.nombre

class Medidor_Agua(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	numero_rotulo 		= models.CharField(max_length=250)
	potencia			= models.FloatField(default=0, null=True, blank=True)

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now=True)

	# relaciones
	local 			= models.ForeignKey(Local)

	def __str__(self):
		return self.nombre

class Medidor_Gas(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	numero_rotulo 		= models.CharField(max_length=250)
	potencia			= models.FloatField(default=0, null=True, blank=True)

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now=True)

	# relaciones
	local 	= models.ForeignKey(Local)

	def __str__(self):
		return self.nombre
