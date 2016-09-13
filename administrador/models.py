from __future__ import unicode_literals

from django.db import models


from utilidades.models import *
from facturacion.models import MotorFacturacion

# modelos
class Empresa(models.Model):

	# atributos (generales)
	nombre 						= models.CharField(max_length=250)
	rut 						= models.CharField(max_length=250)
	ciudad 						= models.CharField(max_length=250)
	comuna 						= models.CharField(max_length=250)
	direccion 					= models.CharField(max_length=250)
	email 						= models.EmailField(max_length=250)
	telefono 					= models.CharField(max_length=250)
	representante 				= models.CharField(max_length=250)
	representante_rut 			= models.CharField(max_length=250)
	representante_profesion 	= models.CharField(max_length=250)
	representante_nacionalidad 	= models.CharField(max_length=250)
	descripcion 				= models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	giro = models.ForeignKey(Giro)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Empresa"
		verbose_name_plural = "Empresas"

class Cliente(models.Model):

	TIPO = (
		(1, 'Persona Jurídica'),
		(2, 'Persona Natural'),
	)

	# atributos (generales)
	tipo			= models.IntegerField(choices=TIPO)
	nombre 			= models.CharField(max_length=250)
	rut 			= models.CharField(max_length=250)
	email 			= models.EmailField(max_length=250)
	razon_social 	= models.CharField(max_length=250, blank=True)
	region 			= models.CharField(max_length=250, blank=True)
	comuna 			= models.CharField(max_length=250)
	ciudad 			= models.CharField(max_length=250)
	direccion 		= models.CharField(max_length=250)
	telefono 		= models.CharField(max_length=250)

	# atributos (conexión)
	codigo_1 	= models.CharField(max_length=100, null=True, blank=True) # cuenta contable
	codigo_2 	= models.CharField(max_length=100, null=True, blank=True) # area
	codigo_3 	= models.CharField(max_length=100, null=True, blank=True) # centro de costo
	codigo_4 	= models.CharField(max_length=100, null=True, blank=True) # item

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.ForeignKey(Empresa)
	giro 	= models.ForeignKey(Giro, null=True, blank=True)

	def __str__(self):
		return self.nombre

class Representante(models.Model):

	# atributos (generales)
	nombre			= models.CharField(max_length=250)
	rut 			= models.CharField(max_length=250)
	nacionalidad 	= models.CharField(max_length=250)
	profesion 		= models.CharField(max_length=250)
	domicilio 		= models.CharField(max_length=250)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	cliente 		= models.ForeignKey(Cliente)
	estado_civil 	= models.ForeignKey(Estado_Civil)

	class Meta:
		verbose_name 		= "Representante"
		verbose_name_plural = "Representantes"

	def __str__(self):
		return self.nombre

class Configuracion(models.Model):

    FORMATO_DECIMAL = (
        (1, ','),
        (2, '.'),
    )

    # atributos (generales)
    formato_decimales	= models.IntegerField(choices=FORMATO_DECIMAL)
    cantidad_decimales	= models.IntegerField()


    # relaciones
    motor_factura   = models.ForeignKey(MotorFacturacion)
    empresa         = models.OneToOneField(Empresa)

    def __str__(self):
        return self.empresa.nombre

    class Meta:
        verbose_name 		= "Configuración de Empresa"
        verbose_name_plural = "Configuración de Empresa"

class Conexion(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=100)
	codigo 		= models.CharField(max_length=100)
	codigo_1 	= models.CharField(max_length=100, null=True, blank=True) # cuenta contable
	codigo_2 	= models.CharField(max_length=100, null=True, blank=True) # area
	codigo_3 	= models.CharField(max_length=100, null=True, blank=True) # centro de costo
	codigo_4 	= models.CharField(max_length=100, null=True, blank=True) # item
	eliminar	= models.BooleanField(default=True)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 	= models.ForeignKey(Empresa)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Parametro de Conexion"
		verbose_name_plural = "Parametros de Conexion"

