from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# from activos.models import Medidor

# Create your models here.
class Lectura_Medidor(models.Model):

	MESES = (
		('1', 'ENERO'),
		('2', 'FEBRERO'),
		('3', 'MARZO'),
		('4', 'ABRIL'),
		('5', 'MAYO'),
		('6', 'JUNIO'),
		('7', 'JULIO'),
		('8', 'AGOSTO'),
		('9', 'SEPTIEMBRE'),
		('10', 'OCTUBRE'),
		('11', 'NOVIEMBRE'),
		('12', 'DICIEMBRE'),
	)

	fecha 			= models.DateField()
	mes 			= models.CharField(max_length=2, choices=MESES)
	valor 			= models.FloatField()
	imagen_file 	= models.FileField(upload_to='lectura-medidor', blank=True)
	imagen_type 	= models.CharField(max_length=250, blank=True)
	imagen_size 	= models.CharField(max_length=250, blank=True)

	# atributos (por defecto)
	visible 		= models.BooleanField(default=True)
	creado_en 		= models.DateTimeField(auto_now=True)

	# relaciones
	# medidor = models.ForeignKey(Medidor)
	user 	= models.ForeignKey(User)
	

	def __str__(self):
		return self.user





	