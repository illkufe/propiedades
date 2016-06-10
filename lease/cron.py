from urllib.request import urlopen
from datetime import datetime
from administrador.models import Moneda, Moneda_Historial

import json

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



def format_currency(value):

	value = value.replace("$", "")
	value = value.replace(".", "")
	value = value.replace(",", ".")
	value = float(value)

	return value