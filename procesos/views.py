# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.template import Context, loader
from django.template.loader import get_template 
from django.contrib.auth.models import User

from administrador.models import Empresa, Cliente, Moneda, Moneda_Historial
from accounts.models import UserProfile
from locales.models import Local, Venta
from activos.models import Activo
from conceptos.models import Concepto
from contrato.models import Contrato, Contrato_Tipo, Arriendo, Arriendo_Detalle, Arriendo_Variable, Gasto_Comun, Servicio_Basico
from procesos.models import Proceso, Proceso_Detalle
from operaciones.models import Lectura_Medidor

from django.db.models import Sum
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import calendar
import os
import json
import pdfkit


def procesos_list(request):

	data = [
	{'nombre':'Procesos', 'path':'@'},
	{'nombre':'Calculo de Concepto', 'path':'@'},
	]

	conceptos 		= Concepto.objects.all()
	activos 		= Activo.objects.all()
	contrato_tipos 	= Contrato_Tipo.objects.all()

	return render(request, 'viewer/procesos/procesos_list.html',{
		'title': 'Cálculo de Conceptos',
		'subtitle': 'Procesos de Facturación',
		'name': 'Lista',
		'href': 'contratos-tipo',
		'conceptos': conceptos,
		'activos': activos,
		'contrato_tipos': contrato_tipos, 
		})

class PROCESOS(View):

	http_method_names =  ['get', 'post']

	def get(self, request, id=None):
		if id == None:
			self.object_list = Proceso.objects.all()
		else:
			self.object_list = Proceso.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()
	
	def post(self, request):

		print ('crear proceso')

		var_post 		= request.POST.copy()
		contratos 		= var_post.get('contratos').split(",")
		fecha_inicio 	= var_post.get('fecha_inicio')
		fecha_termino 	= var_post.get('fecha_termino')
		concepto 		= var_post.get('concepto')

		if int(concepto) == 1:
			data = calculo_arriendo_minimo(request, fecha_inicio, fecha_termino, contratos)
		elif int(concepto) == 2:
			data = calculo_arriendo_variable(request, fecha_inicio, fecha_termino, contratos)
		elif int(concepto) == 3:
			data = calculo_gasto_comun(request, fecha_inicio, fecha_termino, contratos)
		elif int(concepto) == 4:
			data = calculo_servicios_basico(request, fecha_inicio, fecha_termino, contratos)
		else:
			data = []

		return JsonResponse(data, safe=False)


	def json_to_response(self):
		data = list()

		for proceso in self.object_list:
			total = 0

			for detalle in proceso.proceso_detalle_set.all():
				total += detalle.total

			data.append({
				'id':proceso.id,
				'fecha_inicio':proceso.fecha_inicio,
				'fecha_termino':proceso.fecha_termino,
				'total': total,
				'estado': proceso.proceso_estado.nombre,
				})

		return JsonResponse(data, safe=False)


def calculo_arriendo_variable(request, fecha_inicio, fecha_termino, contratos):

	user 		= User.objects.get(pk=request.user.pk)
	contratos 	= contratos
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%m/%d/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	meses		= meses_entre_fechas(f_inicio, f_termino)
	data 		= []


	proceso = Proceso(
		fecha_inicio		= f_inicio.strftime('%Y-%m-%d'),
		fecha_termino		= f_termino.strftime('%Y-%m-%d'),
		user				= user,
		concepto_id			= 2,
		proceso_estado_id 	= 1,
		)
	proceso.save()
	
	for x in range(meses):

		for item in contratos:

			total 		= 0
			contrato 	= Contrato.objects.get(id=item)

			try:
				detalles = Arriendo_Variable.objects.filter(contrato=contrato)

				for detalle in detalles:
					if fecha.month >= int(detalle.mes_inicio) and fecha.month <= int(detalle.mes_termino):

						venta_valor	= 0
						
						locales = contrato.locales.all()

						ventas 	= Venta.objects.filter(local_id__in=locales).\
						extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
						values('year', 'month', 'local_id').\
						annotate(Sum('valor'))

						for venta in ventas:
							if fecha.month == venta['month'] and fecha.year == venta['year']:
								venta_valor += venta['valor__sum']

						valor = (detalle.valor / 100) + 1

						reajuste_valor 	= 1
						reajuste_moneda = 1
						reajuste_factor = 1

						metros_valor 	= 1

					else:
						venta_valor	= 0
						valor 	= 0

						reajuste_valor 	= 0
						reajuste_moneda = 0
						reajuste_factor = 0
						metros_valor 	= 0

					total = venta_valor * valor

			except Arriendo_Variable.DoesNotExist:
				total 			= 0

			proceso_detalle = Proceso_Detalle(
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			)
			proceso_detalle.save()
			
			data.append({
				'id'				: proceso.id,
				'fecha_inicio'		: primer_dia(fecha),
				'fecha_termino'		: ultimo_dia(fecha),
				'concepto'			: 'Arriendo Variable',
				'contrato_numero'	: contrato.numero,
				'contrato_nombre'	: contrato.nombre_local,
				'valor'				: total,
			})

		fecha = sumar_meses(fecha, 1)

	return data

def calculo_arriendo_minimo(request, fecha_inicio, fecha_termino, contratos):

	user 		= User.objects.get(pk=request.user.pk)
	contratos 	= contratos
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%m/%d/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	meses		= meses_entre_fechas(f_inicio, f_termino)
	data 		= []

	proceso = Proceso(
		fecha_inicio		= f_inicio.strftime('%Y-%m-%d'),
		fecha_termino		= f_termino.strftime('%Y-%m-%d'),
		user				= user,
		concepto_id			= 1,
		proceso_estado_id 	= 1,
		)
	proceso.save()
	
	for x in range(meses):

		for item in contratos:

			total 		= 0
			contrato 	= Contrato.objects.get(id=item)

			try:
				arriendo = Arriendo.objects.get(contrato=contrato)
				detalles = Arriendo_Detalle.objects.filter(arriendo=arriendo)

				for detalle in detalles:
					if fecha.month >= int(detalle.mes_inicio) and fecha.month <= int(detalle.mes_termino):
						valor 	= detalle.valor
						moneda 	= detalle.moneda.id
						factor  = detalle.moneda.moneda_historial_set.all().order_by('-id').first().valor

						reajuste_valor 	= 1
						reajuste_moneda = 1
						reajuste_factor = 1
						reajuste 		= arriendo.reajuste
						metros 			= detalle.metro_cuadrado
						metros_valor 	= 1

						if arriendo.reajuste == True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

							reajuste_valor 	= arriendo.valor
							reajuste_moneda = arriendo.moneda.id
							reajuste_factor = arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

							if arriendo.moneda.id == 6:
								reajuste_valor = (reajuste_valor/100)+1
						
						if detalle.metro_cuadrado == True:
							locales =  contrato.locales.all()
							metros_valor = 0
							for local in locales:
								metros_valor += local.metros_cuadrados

					total = valor * factor * metros_valor * (reajuste_valor * reajuste_factor)

			except Arriendo.DoesNotExist:
				total = 0

			proceso_detalle = Proceso_Detalle(
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			)
			proceso_detalle.save()
			
			data.append({
				'id'				: proceso.id,
				'fecha_inicio'		: primer_dia(fecha),
				'fecha_termino'		: ultimo_dia(fecha),
				'concepto'			: 'Arriendo Minimo',
				'contrato_numero'	: contrato.numero,
				'contrato_nombre'	: contrato.nombre_local,
				'valor'				: total,
			})

		fecha = sumar_meses(fecha, 1)

	return data

def calculo_gasto_comun(request, fecha_inicio, fecha_termino, contratos):

	user 		= User.objects.get(pk=request.user.pk)
	contratos 	= contratos
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%m/%d/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	meses		= meses_entre_fechas(f_inicio, f_termino)
	data 		= []


	proceso = Proceso(
		fecha_inicio		= f_inicio.strftime('%Y-%m-%d'),
		fecha_termino		= f_termino.strftime('%Y-%m-%d'),
		user				= user,
		concepto_id			= 3,
		proceso_estado_id 	= 1,
		)
	proceso.save()
	
	for x in range(meses):
		for item in contratos:
			contrato 	= Contrato.objects.get(id=item)
			total 		= 0

			try:
				detalles = Gasto_Comun.objects.filter(contrato=contrato)
				for detalle in detalles:
					if fecha.month >= int(detalle.mes_inicio) and fecha.month <= int(detalle.mes_termino):

						valor 	= detalle.valor
						factor 	= detalle.moneda.moneda_historial_set.all().order_by('-id').first().valor
						total 	= valor * factor

						if detalle.prorrateo == True:
							pass

			except Arriendo_Variable.DoesNotExist:
				total = 0


			proceso_detalle = Proceso_Detalle(
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,			
			)
			proceso_detalle.save()
			
			data.append({
				'id'				: proceso.id,
				'fecha_inicio'		: primer_dia(fecha),
				'fecha_termino'		: ultimo_dia(fecha),
				'concepto'			: 'Gasto Comun',
				'contrato_numero'	: contrato.numero,
				'contrato_nombre'	: contrato.nombre_local,
				'valor'				: total,
			})

		fecha = sumar_meses(fecha, 1)

	return data

def calculo_servicios_basico(request, fecha_inicio, fecha_termino, contratos):

	user 		= User.objects.get(pk=request.user.pk)
	contratos 	= contratos
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%m/%d/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%m/%d/%Y"))
	meses		= meses_entre_fechas(f_inicio, f_termino)
	data 		= []

	proceso = Proceso(
		fecha_inicio		= f_inicio.strftime('%Y-%m-%d'),
		fecha_termino		= f_termino.strftime('%Y-%m-%d'),
		user				= user,
		concepto_id			= 4, # {falta: buscar de otra manera}
		proceso_estado_id 	= 1,
		)
	proceso.save()
	
	for x in range(meses):
		for item in contratos:

			contrato 	= Contrato.objects.get(id=item)
			total 		= 0

			locales 	= contrato.locales.values_list('id', flat=True).all()
			medidores  	= Medidor.objects.filter(local__in=locales)
			print ("contrato")
			print (item)
			print ("medidor")
			print (medidores)

			# asd = Servicio_Basico.objects.filter(contrato=contrato)
			

			try:
				detalles = Servicio_Basico.objects.filter(contrato=contrato)

				print (detalles)

				for detalle in detalles:
					print (detalle)
					if fecha.month >= int(detalle.mes_inicio) and fecha.month <= int(detalle.mes_termino):

						for medidor in medidores:
							# print ("-----------")
							# print (medidor)
							# print (medidor.id)
							# lectura = Lectura_Medidor.objects.get(medidor=medidor)
							lecturas = Lectura_Medidor.objects.filter(medidor=medidor).order_by('-id')[:2]
							index =  0
							for lectura in lecturas:
								print (lectura.valor)
								if index == 0:
									val = lectura.valor
								else:
									val = val - lectura.valor

								index += 1	
							print ("VALOR")
							print (val)
								# {falta: lectura del mes anterior}

						valor = detalle.valor
						# total = valor # {falta: traer la diferencia entre este mes y el mes anterior} 
						total = val

			except Arriendo_Variable.DoesNotExist:
				total = 0

			proceso_detalle = Proceso_Detalle(
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				contrato 		= contrato,
				proceso 		= proceso,
			)
			proceso_detalle.save()
			
			data.append({
				'id'				: proceso.id,
				'fecha_inicio'		: primer_dia(fecha),
				'fecha_termino'		: ultimo_dia(fecha),
				'concepto'			: 'Servicio Basico',
				'contrato_numero'	: contrato.numero,
				'contrato_nombre'	: contrato.nombre_local,
				'valor'				: total,
			})

		fecha = sumar_meses(fecha, 1)

	return data


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

	return datetime.strptime(fecha, "%d/%m/%Y")



def propuesta_pdf(proceso, pk=None):

	data = []
	total = 0

	if pk != None:
		proceso = Proceso.objects.get(id=pk)

	detalles = Proceso_Detalle.objects.filter(proceso=proceso)

	for detalle in detalles:

		contrato = detalle.contrato
		locales = contrato.locales.all()

		data.append({
			'fecha_inicio'		: detalle.fecha_inicio,
			'fecha_termino'		: detalle.fecha_termino,
			'concepto'			: proceso.concepto.nombre,
			'contrato_numero'	: contrato.numero,
			'contrato_nombre'	: contrato.nombre_local,
			'cliente'			: contrato.cliente.nombre,
			'locales'			: locales,
			'valor'				: detalle.total,
		})

		total += detalle.total
		
	options = {
		# 'page-size': 'Letter',
		# 'orientation': 'Landscape',
		'margin-top': '0.75in',
		'margin-right': '0.75in',
		'margin-bottom': '0.55in',
		'margin-left': '0.75in',
		'encoding': "UTF-8",
		'no-outline': None
		}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/procesos/propuesta_facturacion.html')

	context = Context({
		'data' : data,
		'proceso': proceso,
		'total': total,
	})

	html = template.render(context)  # Renders the template with the context data.
	pdfkit.from_string(html, 'public/media/contratos/propuesta_facturacion.pdf', options=options, css=css)
	pdf = open('public/media/contratos/propuesta_facturacion.pdf', 'rb')
	response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=propuesta_facturacion.pdf'
	pdf.close()
	# os.remove("propuesta_facturacion.pdf")  # remove the locally created pdf file.

	return response  # returns the response.
