from __future__ import unicode_literals

from django.db import models
from utilidades.models import *
from facturacion.models import Motor_Factura


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
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	giro 			= models.ForeignKey(Giro)
	moneda 			= models.ManyToManyField(Moneda, through='Configuracion_Monedas')

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Empresa'
		verbose_name_plural = 'Empresas'

class Configuracion_Monedas(models.Model):

	# atributos (generales)
	cantidad_decimales	= models.IntegerField()
	moneda_local		= models.BooleanField(default=False)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 		= models.ForeignKey(Empresa)
	moneda 			= models.ForeignKey(Moneda)

	def __str__(self):
		return  self.empresa.nombre+ '' +self.moneda.nombre

	class Meta:
		verbose_name 		= 'Configuración de Moneda'
		verbose_name_plural = 'Configuraciones de Monedas'

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
	codigo_1 		= models.CharField(max_length=100, null=True, blank=True) # cuenta contable
	codigo_2 		= models.CharField(max_length=100, null=True, blank=True) # area
	codigo_3 		= models.CharField(max_length=100, null=True, blank=True) # centro de costo
	codigo_4 		= models.CharField(max_length=100, null=True, blank=True) # item

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 		= models.ForeignKey(Empresa)
	giro 			= models.ForeignKey(Giro, null=True, blank=True)
	clasificaciones = models.ManyToManyField('Clasificacion_Detalle')

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Cliente'
		verbose_name_plural = 'Clientes'

class Representante(models.Model):

	# atributos (generales)
	nombre			= models.CharField(max_length=250)
	rut 			= models.CharField(max_length=250)
	nacionalidad 	= models.CharField(max_length=250)
	profesion 		= models.CharField(max_length=250)
	domicilio 		= models.CharField(max_length=250)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	cliente 		= models.ForeignKey(Cliente)
	estado_civil 	= models.ForeignKey(Estado_Civil)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Representante'
		verbose_name_plural = 'Representantes'

class Configuracion(models.Model):

    FORMATO_DECIMAL = (
        (1, ','),
        (2, '.'),
    )

    # atributos (generales)
    formato_decimales	= models.IntegerField(choices=FORMATO_DECIMAL)
    cantidad_decimales	= models.IntegerField()

    # relaciones
    motor_factura   	= models.ForeignKey(Motor_Factura)
    empresa         	= models.OneToOneField(Empresa)

    def __str__(self):
        return self.empresa.nombre

    class Meta:
        verbose_name 		= 'Configuración de Empresa'
        verbose_name_plural = 'Configuraciónes de Empresas'

class Conexion(models.Model):

	# atributos (generales)
	cod_condicion_venta	= models.IntegerField()
	cod_bodega_salida 	= models.IntegerField()
	cod_vendedor 		= models.IntegerField()
	cod_sucursal 		= models.IntegerField()
	cod_lista_precio 	= models.IntegerField()

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now_add=True)
	modificado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	empresa = models.OneToOneField(Empresa)

	def __str__(self):
		return self.empresa.nombre

	class Meta:
		verbose_name 		= 'Parametro de Conexion'
		verbose_name_plural = 'Parametros de Conexion'

class Tipo_Clasificacion(models.Model):

	# atributos (generales)
	nombre = models.CharField(max_length=250)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Tipo de Clasificación'
		verbose_name_plural = 'Tipos de Clasificaciones'

class Clasificacion(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	descripcion 		= models.TextField(blank=True)

	# atributos (por defecto)
	visible 			= models.BooleanField(default=True)
	creado_en 			= models.DateTimeField(auto_now_add=True)
	modificado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	empresa 			= models.ForeignKey(Empresa)
	tipo_clasificacion	= models.ForeignKey(Tipo_Clasificacion)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Clasificación'
		verbose_name_plural = 'Clasificaciones'

class Clasificacion_Detalle(models.Model):

	# atributos (generales)
	nombre = models.CharField(max_length=250)

	# relaciones
	clasificacion = models.ForeignKey(Clasificacion)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Detalle de Clasificación'
		verbose_name_plural = 'Detalles de Clasificaciones'

class Tipo_Operacion(models.Model):

	# atributos (generales)
	descripcion	= models.CharField(max_length=250)
	simbolo		= models.CharField(max_length=250)

	def __str__(self):
		return self.simbolo

	class Meta:
		verbose_name 		= 'Tipo de Operación'
		verbose_name_plural = 'Tipos de Operaciones'

class Entidad_Asociacion(models.Model):

	# atributos (generales)
	nombre 				= models.CharField(max_length=250)
	nombre_campo_tabla	= models.CharField(max_length=250)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Entidad Asociación'
		verbose_name_plural = 'Entidades Asociaciones'

class Tipo_Estado_Proceso(models.Model):

	# atributos (generales)
	nombre 		= models.CharField(max_length=250)
	background 	= models.CharField(max_length=7)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Tipo de Estado Proceso'
		verbose_name_plural = 'Tipos de Estados Procesos'

class Workflow(models.Model):

	descripcion = models.CharField(max_length=250)
	validado	= models.BooleanField(default=False)

	# relaciones
	empresa 	= models.ForeignKey(Empresa)

	def __str__(self):
		return self.descripcion

	class Meta:
		verbose_name 		= 'Workflow'
		verbose_name_plural = 'Workflows'

class Proceso(models.Model):

	# atributos (generales)
	nombre 			= models.CharField(max_length=250)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	workflow		= models.ForeignKey(Workflow, null=True, blank=True)
	tipo_estado 	= models.ForeignKey(Tipo_Estado_Proceso)
	antecesor  		= models.ManyToManyField('self', symmetrical=False, blank=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Proceso'
		verbose_name_plural = 'Procesos'

class Proceso_Condicion(models.Model):

	# atributos (generales)
	valor 		= models.CharField(max_length=250)
	descripcion = models.CharField(max_length=250)

	# relaciones
	operacion 	= models.ForeignKey(Tipo_Operacion)
	proceso 	= models.ForeignKey(Proceso)
	entidad 	= models.ForeignKey(Entidad_Asociacion)

	def __str__(self):
		return self.descripcion

	class Meta:
		verbose_name 		= 'Proceso Condición'
		verbose_name_plural = 'Procesos Condiciones'
