from __future__ import unicode_literals

from django.db import models
from accounts.models import User

# modelos
class ParametrosFacturacion(models.Model):

	codigo_conexion     = models.CharField(max_length=100)
	motor_emision       = models.ForeignKey('MotorFacturacion', on_delete=models.PROTECT)

	class Meta:
		ordering            = ['codigo_conexion']
		verbose_name        = 'Parametro de Facturación'
		verbose_name_plural = 'Parametros de Facturación'

	def __str__(self):
		return self.codigo_conexion

class ConexionFacturacion(models.Model):

	parametro_facturacion   = models.ForeignKey(ParametrosFacturacion, on_delete=models.PROTECT)
	codigo_contexto         = models.CharField(max_length=100)
	host                    = models.CharField(max_length=100)
	url                     = models.CharField(max_length=100)
	puerto                  = models.IntegerField(null=True, blank=True)

	class Meta:
		ordering            = ['codigo_contexto']
		verbose_name        = 'Conexión de Facturación'
		verbose_name_plural = 'Conexiones de Facturación'

	def __str__(self):
		return self.codigo_contexto

class FoliosDocumentosElectronicos(models.Model):

	tipo_dte           	= models.IntegerField()
	secuencia_caf       = models.IntegerField()
	rango_inicial       = models.IntegerField()
	rango_final         = models.IntegerField()
	folio_actual        = models.IntegerField()
	xml_caf             = models.TextField()
	fecha_ingreso_caf   = models.DateTimeField()
	operativo           = models.BooleanField(default=False)
	usuario_creacion    = models.ForeignKey(User, blank=True, null=True)

	class Meta:
		ordering            = ['tipo_dte']
		verbose_name        = 'Folio de Documento Electrónico'
		verbose_name_plural = 'Folios de Documentos Electrónicos'

	def __str__(self):
		return str(self.folio_actual)

class MotorFacturacion(models.Model):

	nombre      = models.CharField(max_length=250)
	descripcion = models.CharField(max_length=250)
	activo      = models.BooleanField(default=False)

	class Meta:
		ordering            = ['nombre']
		verbose_name        = 'Motor de Facturación'
		verbose_name_plural = 'Motores de Facturación'

	def __str__(self):
		return self.nombre

class CodigoConcepto(models.Model):

	codigo      = models.IntegerField()
	nombre      = models.CharField(max_length=250)
	descripcion = models.CharField(max_length=250)

	class Meta:
		ordering            = ['nombre']
		verbose_name        = 'Codigo de Concepto'
		verbose_name_plural = 'Codigos de Conceptos'

	def __str__(self):
		return self.nombre
