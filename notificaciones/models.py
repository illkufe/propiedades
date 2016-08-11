from django.db import models
from django.contrib.auth.models import User

# Modelos
class Alerta(models.Model):

	# atributos (generales)
	nombre  	= models.CharField(max_length=250)
	descripcion = models.TextField()
	fecha 		= models.DateTimeField()

	# atributos (por defecto)
	visible 	= models.BooleanField(default=True)
	creado_en 	= models.DateTimeField(auto_now=True)

	# relaciones
	miembros 	= models.ManyToManyField(User, through='Alerta_Miembro')
	creador 	= models.ForeignKey(User, related_name='creador')

	def __str__(self):
		return self.nombre

	class Meta:
		verbose_name 		= "Alerta"
		verbose_name_plural = "Alertas"

class Alerta_Miembro(models.Model):

	# atributos (generales)
	estado 	= models.BooleanField(default=False)

	# relaciones
	user 	= models.ForeignKey(User)
	alerta 	= models.ForeignKey(Alerta)

	def __str__(self):
		return self.alerta.nombre+' - '+user.firt_name

	class Meta:
		verbose_name 		= "Miembro de Alerta "
		verbose_name_plural = "Miembros de Alertas"
