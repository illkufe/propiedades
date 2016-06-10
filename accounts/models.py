from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, Group
from administrador.models import Empresa

# Create your models here.
class UserProfile(models.Model):
	TIPO = (
		('1', 'NORMAL'),
		('2', 'COMERCIAL'),
		('3', 'CLIENTE'),
		('4', 'ADMINISTRADOR'),
	)

	# atributos (generales)
	rut			= models.CharField(max_length=250, blank=True)
	cargo		= models.CharField(max_length=250, blank=True)
	tipo 		= models.CharField(max_length=2, choices=TIPO)
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

	def __str__(self):
		return self.user.username
