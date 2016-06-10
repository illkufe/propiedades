from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from activos.models import Medidor

# Create your models here.
class Lectura_Medidor(models.Model):

	fecha 			= models.DateField()
	valor 			= models.FloatField()
	imagen_file 	= models.FileField(upload_to='lectura-medidor', blank=True)
	imagen_type 	= models.CharField(max_length=250, blank=True)
	imagen_size 	= models.CharField(max_length=250, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	medidor = models.ForeignKey(Medidor)
	user 	= models.ForeignKey(User)
	

	def __str__(self):
		return self.medidor.nombre





	