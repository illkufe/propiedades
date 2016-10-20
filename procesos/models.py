from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from conceptos.models import Concepto
from contrato.models import Contrato
from facturacion.models import MotorFacturacion
from locales.models import Local, Medidor_Electricidad, Medidor_Agua, Medidor_Gas

# modelos
class Propuesta(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)
	uf_valor 		= models.FloatField()
	uf_modificada 	= models.BooleanField(default=False)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user = models.ForeignKey(User)

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
    numero_pedido 	    = models.IntegerField(null=True, blank=True)
    fecha_inicio 	    = models.DateField()
    fecha_termino 	    = models.DateField()
    total 			    = models.FloatField()
    url_documento       = models.CharField(max_length=300, null=True, blank=True)
    numero_documento    = models.IntegerField(null=True, blank=True)


    # atributos (por defecto)
    visible 	= models.BooleanField(default=True)
    creado_en 	= models.DateTimeField(auto_now=True)

    # relaciones
    propuesta	    = models.ForeignKey(Propuesta)
    estado		    = models.ForeignKey(Factura_Estado)
    contrato	    = models.ForeignKey(Contrato)
    motor_emision   = models.ForeignKey(MotorFacturacion, on_delete=models.PROTECT)

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

