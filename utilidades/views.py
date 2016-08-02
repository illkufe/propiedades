from django.shortcuts import render
from django import forms
from datetime import date, datetime, timedelta

import calendar

def variables_globales(request):

	try:
		user 			= request.user
		empresa 		= user.userprofile.empresa
		configuracion 	= empresa.configuracion

		return {
		'lease_user_id' 	: user.id,
		'lease_symbol' 		: configuracion.moneda.simbolo,
		'lease_format_dec' 	: ',' if configuracion.formato_decimales == 1 else '.', 
		'lease_format_mil' 	: '.' if configuracion.formato_decimales == 1 else ',',
		'lease_decimales' 	: configuracion.cantidad_decimales,
		}
	except Exception:
		return {'estado':'error'}

def fecha_actual():

	return datetime.now()

def primer_dia(fecha):

	dia 	= '01'
	mes 	= fecha.strftime('%m')
	anio 	= fecha.strftime('%Y')
	fecha 	= dia+'/'+mes+'/'+anio
	fecha 	= datetime.strptime(fecha, "%d/%m/%Y")

	return fecha

def ultimo_dia(fecha):

	dia 	= str(calendar.monthrange(fecha.year, fecha.month)[1])
	mes 	= fecha.strftime('%m')
	anio 	= fecha.strftime('%Y')
	fecha 	= dia+'/'+mes+'/'+anio
	fecha 	= datetime.strptime(fecha, "%d/%m/%Y")

	return fecha

def meses_entre_fechas(f_inicio, f_termino):

	delta = 0
	while True:

		dias = calendar.monthrange(f_inicio.year, f_inicio.month)[1]
		f_inicio += timedelta(days=dias)
		if f_inicio <= f_termino:
			delta += 1
		else:
			break

	return delta + 1

def sumar_meses(fecha, meses):

	month 	= fecha.month - 1 + meses
	year 	= int(fecha.year + month / 12 )
	month 	= month % 12 + 1
	day 	= min(fecha.day,calendar.monthrange(year,month)[1])
	fecha 	= str(day)+'/'+str(month)+'/'+str(year)

	return datetime.strptime(fecha, "%d/%m/%Y").date()

def formato_moneda(valor):

	moneda = '${:,.2f}'.format(valor)
	
	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda

def formato_numero(valor):

	moneda = '{:,.2f}'.format(valor)
	
	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda


# CLASES

class NumberField(forms.Field):
	def to_python(self, value):
		print ('--------')
		print (value)
		print ('--------')
		if value is not '' and value is not None:
			return value.replace(".", "").replace(",", ".")