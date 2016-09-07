from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from conceptos.models import Concepto
from contrato.models import Contrato
from locales.models import Local, Medidor_Electricidad, Medidor_Agua, Medidor_Gas

# Modelos
class Propuesta(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)
	borrar 		= models.CharField(max_length=250)

	# relaciones
	user 		= models.ForeignKey(User)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Propuesta"
		verbose_name_plural = "Propuestas"

class Factura_Estado(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	color 		= models.CharField(max_length=7)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Estado de Factura"
		verbose_name_plural = "Estados de Factura"

class Factura(models.Model):

	# atributos (generales)
	numero_pedido 	= models.IntegerField(null=True, blank=True)
	fecha_inicio 	= models.DateField()
	fecha_termino 	= models.DateField()
	total 			= models.FloatField()


	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	propuesta	= models.ForeignKey(Propuesta)
	estado		= models.ForeignKey(Factura_Estado)
	contrato	= models.ForeignKey(Contrato)

	def __str__(self):
		return self.propuesta.nombre+' - '+self.contrato.nombre_local

	class Meta:
		verbose_name 		= "Factura"
		verbose_name_plural = "Facturas"

class Factura_Detalle(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	total 		= models.FloatField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	factura		= models.ForeignKey(Factura)
	concepto	= models.ForeignKey(Concepto)
	
	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Detalle de Factura"
		verbose_name_plural = "Detalles de Factura"


# Modelos (detalle conceptos)
# class Detalle_Arriendo_Minimo(models.Model):
	
# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()
# 	valor 			= models.FloatField(null=True, blank=True)
# 	metro_cuadrado 	= models.BooleanField(default=False)
# 	metros_local 	= models.FloatField(null=True, blank=True)
# 	reajuste 		= models.BooleanField(default=False)
# 	reajuste_valor 	= models.FloatField(null=True, blank=True)
# 	total 			= models.FloatField(null=True, blank=True)

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)
# 	# concepto 	= models.ForeignKey(Concepto)

# 	def __str__(self):
# 		return str(self.fecha_inicio)+' - '+str(self.fecha_termino)+' - '+ str(self.contrato.numero)

# class Detalle_Arriendo_Variable(models.Model):
	
# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()
# 	valor 			= models.FloatField(null=True, blank=True)
# 	ventas 			= models.FloatField(null=True, blank=True)
# 	arriendo_minimo = models.FloatField(null=True, blank=True)
# 	total 			= models.FloatField(null=True, blank=True)

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)

# 	def __str__(self):
# 		return str(self.fecha_inicio)+' - '+str(self.fecha_termino)+' - '+ str(self.contrato.numero)

# class Detalle_Arriendo_Bodega(models.Model):
	
# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()
# 	total 			= models.FloatField(null=True, blank=True)

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)

# 	def __str__(self):
# 		return str(self.fecha_inicio)+' - '+str(self.fecha_termino)+' - '+ str(self.contrato.numero)

# class Detalle_Gasto_Servicio(models.Model):

# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()
# 	total 			= models.FloatField(null=True, blank=True)

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)
# 	local 		= models.ForeignKey(Local)

# 	def __str__(self):
# 		return str(self.contrato.numero)

# class Detalle_Gasto_Comun(models.Model):

# 	valor 			= models.FloatField(null=True, blank=True)
# 	prorrateo 		= models.BooleanField(default=False)
# 	gasto_mensual 	= models.FloatField(null=True, blank=True)
# 	metros_total 	= models.FloatField(null=True, blank=True)
# 	total 		 	= models.FloatField(null=True, blank=True)

# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)
# 	local 		= models.ForeignKey(Local)

# 	def __str__(self):
# 		return str(self.contrato.numero)

# class Detalle_Electricidad(models.Model):

# 	valor 			= models.FloatField(null=True, blank=True)
# 	valor_anterior	= models.FloatField(null=True, blank=True)
# 	valor_actual 	= models.FloatField(null=True, blank=True)
# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)
# 	medidor 	= models.ForeignKey(Medidor_Electricidad)

# 	def __str__(self):
# 		return medidor.nombre+' '+self.contrato.numero

# class Detalle_Agua(models.Model):

# 	valor 			= models.FloatField(null=True, blank=True)
# 	valor_anterior	= models.FloatField(null=True, blank=True)
# 	valor_actual 	= models.FloatField(null=True, blank=True)
# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)
# 	medidor 	= models.ForeignKey(Medidor_Agua)

# 	def __str__(self):
# 		return medidor.nombre+' '+self.contrato.numero

# class Detalle_Gas(models.Model):

# 	valor 			= models.FloatField(null=True, blank=True)
# 	valor_anterior	= models.FloatField(null=True, blank=True)
# 	valor_actual 	= models.FloatField(null=True, blank=True)
# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)
# 	medidor 	= models.ForeignKey(Medidor_Gas)
	
# 	def __str__(self):
# 		return medidor.nombre+' '+self.contrato.numero

# class Detalle_Cuota_Incorporacion(models.Model):

# 	valor 			= models.FloatField(null=True, blank=True)
# 	factor 		 	= models.FloatField(null=True, blank=True)
# 	total 		 	= models.FloatField(null=True, blank=True)

# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)

# 	def __str__(self):
# 		return str(self.fecha_inicio)+' - '+str(self.fecha_termino)+' - '+ str(self.contrato.numero)

# class Detalle_Fondo_Promocion(models.Model):

# 	valor 			= models.FloatField(null=True, blank=True)
# 	factor 		 	= models.FloatField(null=True, blank=True)
# 	total 		 	= models.FloatField(null=True, blank=True)

# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)

# 	def __str__(self):
# 		return str(self.fecha_inicio)+' - '+str(self.fecha_termino)+' - '+ str(self.contrato.numero)

# class Detalle_Multa(models.Model):

# 	total = models.FloatField(null=True, blank=True)

# 	fecha_inicio 	= models.DateField()
# 	fecha_termino 	= models.DateField()

# 	# atributos (por defecto)
# 	visible 	= models.BooleanField(default=True)
# 	creado_en 	= models.DateTimeField(auto_now=True)

# 	# relaciones
# 	proceso 	= models.ForeignKey(Proceso)
# 	contrato 	= models.ForeignKey(Contrato)

# 	def __str__(self):
# 		return str(self.fecha_inicio)+' - '+str(self.fecha_termino)+' - '+ str(self.contrato.numero)
