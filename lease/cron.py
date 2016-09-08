from urllib.request import urlopen
from datetime import datetime
from utilidades.models import Moneda, Moneda_Historial
from notificaciones.models import Alerta, Alerta_Miembro

import json
import pyrebase

def update_currency():

	# variables
	currencies = []

	# obtener monedas e indicadores
	url 	= "http://indicadoresdeldia.cl/webservice/indicadores.json"
	reponse = urlopen(url).read().decode("utf-8") 
	data 	= json.loads(reponse)

	# monedas e indicadores
	fecha = datetime.strptime(data['date'], "%Y-%m-%d %H:%M:%S")
	currencies.append({'id':1, 'value':format_currency(data['moneda']['dolar'])})
	currencies.append({'id':2, 'value':format_currency(data['moneda']['euro'])})
	currencies.append({'id':3, 'value':format_currency(data['indicador']['uf'])})
	currencies.append({'id':4, 'value':format_currency(data['indicador']['utm'])})

	# actualizar monedas
	for currency in currencies:

		try:
			historial 		= Moneda_Historial.objects.get(fecha__day=fecha.day, fecha__month=fecha.month, fecha__year=fecha.year,  moneda_id=currency['id'])
			historial.valor = currency['value']
			historial.fecha = fecha
			historial.save()

		except Moneda_Historial.DoesNotExist:
			Moneda_Historial(fecha=fecha, moneda_id=currency['id'], valor=currency['value']).save()

def update_alert():

	# configuración firebase
	config = {
		"apiKey": "AIzaSyAj7z483ospf7R-8vGshCjCWcanGJLkwDI",
		"authDomain": "lease-61711.firebaseapp.com",
		"databaseURL": "https://lease-61711.firebaseio.com",
		"storageBucket": "lease-61711.appspot.com",
		# "serviceAccount": "lease-5c67010de9d1.json",
	}

	# instanciar firebase
	firebase 	= pyrebase.initialize_app(config)
	db 			= firebase.database()

	alertas = Alerta.objects.all()
	date 	= datetime.now()

	for alerta in alertas:

		if date >= alerta.fecha:

			alerta_miembros = alerta.alerta_miembro_set.all()

			for alerta_miembro in alerta_miembros:
				if alerta_miembro.estado is False:
					
					# crear alerta firebase
					data = {
						"mensaje"		: alerta.nombre,
						"descripcion"	: alerta.descripcion,
						"emisor"		: alerta.creador.first_name
						}

					db.child("alertas/"+str(alerta_miembro.user.id)).push(data)

					# cambiar estado
					alerta_miembro.estado = True
					alerta_miembro.save()
				else:
					pass
		else:
			pass

def format_currency(value):

	value = value.replace("$", "")
	value = value.replace(".", "")
	value = value.replace(",", ".")
	value = float(value)

	return value