# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.template import Context, loader
from django.template.loader import get_template 
from django.contrib.auth.models import User

from administrador.models import Empresa, Cliente, Moneda, Moneda_Historial
from accounts.models import UserProfile
from locales.models import Local, Venta, Medidor_Electricidad, Medidor_Agua, Medidor_Gas
from activos.models import Activo
from conceptos.models import Concepto
from contrato.models import Contrato, Contrato_Tipo, Arriendo, Arriendo_Detalle, Arriendo_Variable, Gasto_Comun, Servicio_Basico
from procesos.models import Proceso, Proceso_Detalle, Detalle_Electricidad, Detalle_Agua, Detalle_Gas
from operaciones.models import Lectura_Electricidad, Lectura_Agua, Lectura_Gas

from django.db.models import Sum
from datetime import datetime, timedelta
import calendar
import os
import json
import pdfkit


def procesos_list(request):

	conceptos 	= Concepto.objects.all()
	activos 	= Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

	return render(request, 'viewer/procesos/procesos_list.html',{
		'title': 'Cálculo de Conceptos',
		'subtitle': 'Procesos de Facturación',
		'name': 'Lista',
		'href': 'contratos-tipo',
		'conceptos': conceptos,
		'activos': activos,
		})

class PROCESOS(View):

	http_method_names =  ['get', 'post']

	def get(self, request, id=None):

		profile 	= UserProfile.objects.get(user=self.request.user)
		profiles 	= profile.empresa.userprofile_set.all().values_list('id', flat=True)
		users 		= User.objects.filter(userprofile__in=profiles).values_list('id', flat=True)

		if id == None:
			self.object_list = Proceso.objects.filter(visible=True, user__in=users)
		else:
			self.object_list = Proceso.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()
	
	def post(self, request):

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
			val_luz 	= var_post.get('valor_luz')
			val_agua 	= var_post.get('valor_agua')
			val_gas 	= var_post.get('valor_gas')
			data = calculo_servicios_basico(request, fecha_inicio, fecha_termino, contratos, val_luz, val_agua, val_gas)
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




def filtrar_contratos(request):

	data 		= list()
	var_post 	= request.POST.copy()

	mes_inicio	= var_post['mes_inicio']
	ano_inicio	= var_post['ano_inicio']
	mes_termino	= var_post['mes_termino']
	ano_termino	= var_post['ano_termino']
	activo_id	= var_post['activo']
	concepto 	= var_post['concepto']

	fecha_inicio 	= primer_dia(datetime.strptime('01/'+mes_inicio+'/'+ano_inicio+'', "%d/%m/%Y"))
	fecha_termino 	= ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+ano_termino+'', "%d/%m/%Y"))
	activo 			= Activo.objects.get(id=activo_id)
	locales 		= activo.local_set.all().values_list('id', flat=True)
	contratos 		= Contrato.objects.filter(locales__in=locales, fecha_habilitacion__lt=fecha_inicio, fecha_termino__gt=fecha_termino, visible=True).distinct()

	for contrato in contratos:
		data.append({
			'id'					: contrato.id,
			'numero'				: contrato.numero,
			'fecha_inicio'			: contrato.fecha_inicio,
			'fecha_termino'			: contrato.fecha_termino,
			'fecha_habilitacion'	: contrato.fecha_habilitacion,
			'cliente'				: contrato.cliente.nombre,
			'locales'				: 'locales', # {falta: poner locales}
		})	

	return JsonResponse(data, safe=False)



def calculo_arriendo_variable(request, fecha_inicio, fecha_termino, contratos):

	user 		= User.objects.get(pk=request.user.pk)
	contratos 	= contratos
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%d/%m/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
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

	print ('arriendo minimo')
	user 		= User.objects.get(pk=request.user.pk)
	contratos 	= contratos
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%d/%m/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
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
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%d/%m/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
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

def calculo_servicios_basico(request, fecha_inicio, fecha_termino, contratos, valor_luz, valor_agua, valor_gas):

	user 		= User.objects.get(pk=request.user.pk)
	contratos 	= contratos
	f_inicio 	= primer_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
	f_termino 	= ultimo_dia(datetime.strptime(fecha_termino, "%d/%m/%Y"))
	fecha 		= ultimo_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y"))
	meses		= meses_entre_fechas(f_inicio, f_termino)
	data 		= []

	proceso = Proceso(
		fecha_inicio		= f_inicio.strftime('%Y-%m-%d'),
		fecha_termino		= f_termino.strftime('%Y-%m-%d'),
		user				= user,
		concepto_id			= 4,
		proceso_estado_id 	= 1,
		)
	proceso.save()
	
	for x in range(meses):

		for item in contratos:
			
			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.values_list('id', flat=True).all()	
			medidores_luz  	= Medidor_Electricidad.objects.filter(local__in=locales)
			medidores_agua  = Medidor_Agua.objects.filter(local__in=locales)
			medidores_gas  	= Medidor_Gas.objects.filter(local__in=locales)


			for medidor in medidores_luz:
				try:
					valor_anterior 	= Lectura_Electricidad.objects.get(medidor_electricidad=medidor, mes=(fecha.month-1), anio=fecha.year).valor
				except Exception:
					valor_anterior	= None
				try:
					valor_actual 	= Lectura_Electricidad.objects.get(medidor_electricidad=medidor, mes=fecha.month, anio=fecha.year).valor
				except Exception:
					valor_actual	= None

				Detalle_Electricidad(
					valor			= valor_luz,
					valor_anterior	= valor_anterior,
					valor_actual	= valor_actual,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso			= proceso,
					contrato		= contrato,
					medidor			= medidor,
				).save()

			for medidor in medidores_agua:
				try:
					lectura_anterior 	= Lectura_Agua.objects.get(medidor_electricidad=medidor, mes=(fecha.month-1), anio=fecha.year)
				except Exception as error:
					lectura_anterior	= None
				try:
					lectura_actual 		= Lectura_Agua.objects.get(medidor_electricidad=medidor, mes=fecha.month, anio=fecha.year)
				except Exception as error:
					lectura_actual		= None

				Detalle_Agua(
					valor			= valor_agua,
					valor_anterior	= None,
					valor_actual	= None,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso			= proceso,
					contrato		= contrato,
					medidor			= medidor,
				).save()

			for medidor in medidores_gas:
				try:
					lectura_anterior 	= Lectura_Gas.objects.get(medidor_electricidad=medidor, mes=(fecha.month-1), anio=fecha.year)
				except Exception as error:
					lectura_anterior	= None
				try:
					lectura_actual 		= Lectura_Gas.objects.get(medidor_electricidad=medidor, mes=fecha.month, anio=fecha.year)
				except Exception as error:
					lectura_actual		= None

				Detalle_Gas(
					valor			= valor_gas,
					valor_anterior	= None,
					valor_actual	= None,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso			= proceso,
					contrato		= contrato,
					medidor			= medidor,
				).save()

			data.append({
				'id'				: proceso.id,
				'fecha_inicio'		: primer_dia(fecha),
				'fecha_termino'		: ultimo_dia(fecha),
				'concepto'			: 'Servicio Basico',
				'contrato_numero'	: contrato.numero,
				'contrato_nombre'	: contrato.nombre_local,
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


	if pk is not None:
		proceso = Proceso.objects.get(id=pk)
		print (proceso.id)

	options = {
		'orientation': 'Landscape',
		'margin-top': '0.75in',
		'margin-right': '0.75in',
		'margin-bottom': '0.55in',
		'margin-left': '0.75in',
		'encoding': "UTF-8",
		'no-outline': None
		}

	css = 'static/assets/css/bootstrap.min.css'

	if proceso.concepto_id == 4:
		data 		= data_detalle_electricidad(proceso)
		template 	= get_template('pdf/procesos/propuesta_servicios_basicos.html')
	else:
		data 	= {}
		detalle = []
		total 	= 0
		template = get_template('pdf/procesos/propuesta_facturacion.html')

		detalles = Proceso_Detalle.objects.filter(proceso=proceso)

		for item in detalles:

			contrato = item.contrato
			locales = contrato.locales.all()

			detalle.append({
				'fecha_inicio'		: item.fecha_inicio,
				'fecha_termino'		: item.fecha_termino,
				'concepto'			: proceso.concepto.nombre,
				'contrato_numero'	: contrato.numero,
				'contrato_nombre'	: contrato.nombre_local,
				'cliente'			: contrato.cliente.nombre,
				'locales'			: locales,
				'valor'				: item.total,
			})

			total += item.total

		data['detalle'] = detalle
		data['total'] 	= total

	context = Context({
		'proceso' 	: proceso,
		'detalle' 	: data['detalle'],
		'total'		: data['total'],
	})

	html = template.render(context)  # Renders the template with the context data.
	pdfkit.from_string(html, 'public/media/contratos/propuesta_facturacion.pdf', options=options, css=css)
	pdf = open('public/media/contratos/propuesta_facturacion.pdf', 'rb')
	response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=propuesta_facturacion.pdf'
	pdf.close()
	# os.remove("propuesta_facturacion.pdf")  # remove the locally created pdf file.

	return response  # returns the response.



def data_detalle_electricidad(proceso):

	data 			= {}
	detalles 		= []
	detalle 		= []
	total			= 0

	detalles_luz 	= Detalle_Electricidad.objects.filter(proceso=proceso)
	detalles_agua 	= Detalle_Agua.objects.filter(proceso=proceso)
	detalles_gas 	= Detalle_Gas.objects.filter(proceso=proceso)

	for item in detalles_luz:
		detalles.append(item)

	for item in detalles_agua:
		detalles.append(item)

	for item in detalles_gas:
		detalles.append(item)


	for item in detalles:
		detalle.append({
			'fecha_inicio'		: item.fecha_inicio,
			'fecha_termino'		: item.fecha_termino,
			'contrato'			: item.contrato.numero,
			'local'				: item.medidor.local.nombre,
			'medidor'			: item.medidor.nombre,
			'lectura_anterior' 	: item.valor_anterior if item.valor_anterior is not None else 'Sin Datos',
			'lectura_actual' 	: item.valor_actual if item.valor_actual is not None else 'Sin Datos',
			'valor' 			: item.valor,
			'diferencia'		: (item.valor_actual - item.valor_anterior) if item.valor_anterior is not None and item.valor_actual is not None else 'N/A',
			'total'				: (item.valor_actual - item.valor_anterior) * item.valor if item.valor_anterior is not None and item.valor_actual is not None else 'N/A',
		})

		total += (item.valor_actual - item.valor_anterior) * item.valor if item.valor_anterior is not None and item.valor_actual is not None else 0

	
	data['detalle'] = detalle
	data['total'] 	= total

	return data