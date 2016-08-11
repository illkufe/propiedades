from django.shortcuts import render
from django.template import Context, loader
from django.template.loader import get_template 
from django import forms
from datetime import date, datetime, timedelta

import pdfkit
import calendar


# variables globales
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


# funciones globales (fechas)
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

def meses_entre_fechas(fecha_inicio, fecha_termino):

	delta = 0
	while True:

		dias = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
		fecha_inicio += timedelta(days=dias)
		if fecha_inicio <= fecha_termino:
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


# funciones globales (numeros)
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


# funciones globales (pdf)
def generar_pdf(configuration, data):

	options = {
		'margin-top': '0.75in',
		'margin-right': '0.75in',
		'margin-bottom': '0.55in',
		'margin-left': '0.75in',
		'encoding': "UTF-8",
		'no-outline': None,
		}

	css = ['static/assets/css/bootstrap.min.css']

	try:
		template = get_template(configuration['html'])
	except Exception as asd:
		template = get_template(configuration['default'])

	context = Context({
		'data' : data,
	})

	html = template.render(context)
	pdfkit.from_string(html, configuration['destination']+''+configuration['nombre_pdf']+'.pdf', options=options, css=css)

	return True


# CLASES
class NumberField(forms.Field):
	def to_python(self, value):
		if value is not '' and value is not None:
			return value.replace(".", "").replace(",", ".")
