from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from administrador.models import Empresa, Cliente, Proceso


# modelos
class UserType(models.Model):

	# atributos (generales)
	nombre = models.CharField(max_length=250, blank=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= 'Tipo de Usuario'
		verbose_name_plural = 'Tipos de Usuarios'

class UserProfile(models.Model):

	# atributos (generales)
	rut				= models.CharField(max_length=250)
	cargo			= models.CharField(max_length=250)
	direccion 		= models.CharField(max_length=250, blank=True)
	ciudad 			= models.CharField(max_length=250, blank=True)
	comuna 			= models.CharField(max_length=250, blank=True)
	descripcion 	= models.TextField(blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user 			= models.OneToOneField(User)
	empresa 		= models.ForeignKey(Empresa)
	tipo 			= models.ForeignKey(UserType)
	proceso 		= models.ManyToManyField(Proceso)
	cliente 		= models.ForeignKey(Cliente, blank=True, null=True)

	def __str__(self):
		return self.user.email

	class Meta:
		verbose_name 		= 'Perfil'
		verbose_name_plural = 'Perfil'

class ConfiguracionOwnCloud(models.Model):

	# atributos (generales)
	usuario		= models.CharField(max_length=250)
	password	= models.CharField(max_length=250)
	url 		= models.TextField()

	# atributos (por defecto)
	creado_en 		= models.DateTimeField(auto_now_add=True)
	modificado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user = models.OneToOneField(User)

	def __str__(self):
		return self.user.email

	class Meta:
		verbose_name 		= 'Configuración OwnCloud'
		verbose_name_plural = 'Configuraciones OwnCloud'
