# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from administrador.models import Empresa
from activos.models import Activo, Medidor, Sector, Nivel

# Create your models here.
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

	VOLUMEN = (
		('0', 'ANCLA'),
		('1', 'TAMAÑO INTERMEDIO'),
		('2', 'TAMAÑO MENOR'),
	)

	# atributos (generales)
	nombre  			= models.CharField(max_length=250)
	codigo  			= models.CharField(max_length=250)
	metros_cuadrados 	= models.FloatField(null=True, blank=True)
	metros_lineales 	= models.FloatField(null=True, blank=True)
	metros_compartidos 	= models.FloatField(null=True, blank=True)
	metros_bodega 		= models.FloatField(null=True, blank=True)
	local_tipo_volumen 	= models.CharField(max_length=1, choices=VOLUMEN)
	descripcion 		= models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	activo 		= models.ForeignKey(Activo)
	sector 		= models.ForeignKey(Sector)
	nivel 		= models.ForeignKey(Nivel)
	local_tipo 	= models.ForeignKey(Local_Tipo)
	medidores 	= models.ManyToManyField(Medidor)

	def __str__(self):
		return self.nombre

class Venta(models.Model):

	PERIODICIDAD = (
		('0', 'ANUAL'),
		('1', 'SEMESTRAL'),
		('2', 'TRIMESTRAL'),
		('3', 'MENSUAL'),
		('4', 'QUINCENAL'),
		('5', 'SEMANAL'),
		('6', 'DIARIA'),
	)

	# atributos (generales)
	fecha_inicio 	= models.DateTimeField()
	fecha_termino 	= models.DateTimeField()
	periodicidad	= models.CharField(max_length=1, choices=PERIODICIDAD)
	valor 			= models.FloatField()
	
	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	local 		= models.ForeignKey(Local)

	def __str__(self):
		return self.local.nombre
