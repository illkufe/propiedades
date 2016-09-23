from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from administrador.models import Empresa, Cliente


# modelos

class UserType(models.Model):

	nombre = models.CharField(max_length=250, blank=True)

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name = "Tipo Usuario"
		verbose_name_plural = "Tipos de Usuarios"

class UserProfile(models.Model):

	# atributos (generales)
	rut			= models.CharField(max_length=250, blank=True)
	cargo		= models.CharField(max_length=250, blank=True)
	direccion 	= models.CharField(max_length=250, blank=True)
	ciudad 		= models.CharField(max_length=250, blank=True)
	comuna 		= models.CharField(max_length=250, blank=True)
	descripcion = models.TextField(blank=True)

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	user 	= models.OneToOneField(User)
	empresa = models.ForeignKey(Empresa)
	tipo 	= models.ForeignKey(UserType)
	cliente = models.ForeignKey(Cliente, blank=True, null=True)

	def __str__(self):
		return self.user.username

	class Meta:
		verbose_name 		= "Perfil"
		verbose_name_plural = "Perfil"
