# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.template import Context, loader
from django.template.loader import get_template 
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from administrador.models import Empresa, Cliente, Moneda, Moneda_Historial
from accounts.models import UserProfile
from locales.models import Local, Venta, Medidor_Electricidad, Medidor_Agua, Medidor_Gas
from activos.models import Activo, Gasto_Mensual
from conceptos.models import Concepto
from contrato.models import Contrato, Contrato_Tipo, Arriendo, Arriendo_Detalle, Arriendo_Variable, Gasto_Comun, Servicio_Basico
from procesos.models import Proceso, Detalle_Arriendo_Minimo, Detalle_Arriendo_Variable, Proceso_Detalle, Detalle_Gasto_Comun, Detalle_Electricidad, Detalle_Agua, Detalle_Gas
from operaciones.models import Lectura_Electricidad, Lectura_Agua, Lectura_Gas

from django.db.models import Sum
from datetime import datetime, timedelta
import os
import json
import pdfkit


from utilidades.views import primer_dia, ultimo_dia, meses_entre_fechas, sumar_meses

class ProcesoList(ListView):
	model = Proceso
	template_name = 'viewer/procesos/procesos_list.html'

	def get_context_data(self, **kwargs):		
		context = super(ProcesoList, self).get_context_data(**kwargs)
		context['title'] 		= 'Cálculo de Conceptos'
		context['subtitle'] 	= 'Procesos de Facturación'
		context['name'] 		= 'Lista'
		context['href'] 		= 'procesos'

		context['conceptos'] 	= Concepto.objects.all()
		context['activos'] 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		
		return context

class ProcesoDelete(DeleteView):
	model = Proceso
	success_url = reverse_lazy('/procesos/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.delete()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)



# API -----------------
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

			detalles = []

			if proceso.concepto.id == 1:
				pass
				# print ('arriendo minimo')
			elif proceso.concepto.id == 2:
				pass
				# print ('arriendo variable')
			elif proceso.concepto.id == 3:
				pass
				# print ('gasto comun')
			elif proceso.concepto.id == 4:
				
				detalles_luz 	= Detalle_Electricidad.objects.filter(proceso=proceso)
				detalles_agua 	= Detalle_Agua.objects.filter(proceso=proceso)
				detalles_gas 	= Detalle_Gas.objects.filter(proceso=proceso)

				for item in detalles_luz:
					detalles.append(item)

				for item in detalles_agua:
					detalles.append(item)

				for item in detalles_gas:
					detalles.append(item)
				
			else:
				print ('no existe')

			for detalle in detalles:
				pass
				# print (detalle.id)


			# usuario
			usuario = {
				'id'		:proceso.user.id,
				'first_name':proceso.user.first_name,
				'last_name'	:proceso.user.last_name,
				'email'		:proceso.user.email,
			}

			# concepto
			concepto = {
				'id'	:proceso.concepto.id,
				'nombre':proceso.concepto.nombre,
			}

			data.append({
				'id'			: proceso.id,
				'fecha_creacion': proceso.creado_en.strftime('%d/%m/%Y'),
				'fecha_inicio'	: proceso.fecha_inicio.strftime('%d/%m/%Y'),
				'fecha_termino'	: proceso.fecha_termino.strftime('%d/%m/%Y'),
				'estado'		: proceso.proceso_estado.nombre,
				'usuario'		: usuario,
				'concepto'		: concepto,
				})

		return JsonResponse(data, safe=False)



# Funciones ---------------------
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
			'fecha_inicio'			: contrato.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'			: contrato.fecha_termino.strftime('%d/%m/%Y'),
			'fecha_habilitacion'	: contrato.fecha_habilitacion.strftime('%d/%m/%Y'),
			'cliente'				: contrato.cliente.nombre,
			'locales'				: 'locales', # {falta: poner locales}
		})	

	return JsonResponse(data, safe=False)



def calculo_arriendo_minimo(request, fecha_inicio, fecha_termino, contratos):

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

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato)
				detalle 	= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)
					
				metro_cuadrado	= detalle[0].metro_cuadrado
				
				if metro_cuadrado is True:
					factor 			= detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
					metros 			= metros_total['metros_cuadrados__sum']
					metros_local 	= metros_total['metros_cuadrados__sum']
				else:
					factor 			= 1
					metros 			= 1
					metros_local 	=  None

				valor = detalle[0].valor * factor * metros

				if arriendo.reajuste is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):
					reajuste = True

					if arriendo.moneda.id == 6:
						reajuste_valor = (arriendo.valor/100)+1
					else:
						reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

					total = valor * reajuste_valor

				else:
					reajuste 		= False
					reajuste_valor 	= None
					total 			= valor

			except Arriendo.DoesNotExist:
				valor			= None
				metro_cuadrado	= False
				metros_local    = None
				reajuste		= False
				reajuste_valor	= None
				total 			= None


			proceso_detalle = Detalle_Arriendo_Minimo(
				valor			= valor,
				metro_cuadrado	= metro_cuadrado,
				metros_local	= metros_local,
				reajuste		= reajuste,
				reajuste_valor	= reajuste_valor,
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()
			
			data.append({'id':proceso.id})

		fecha = sumar_meses(fecha, 1)

	return data

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

			contrato 	= Contrato.objects.get(id=item)
			locales 	= contrato.locales.all()

			try:
				existe = Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()
				if existe is True:
					detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)	
					valor 			= detalle[0].valor
					ventas 			= 0
					ventas_local 	= Venta.objects.filter(local_id__in=locales).\
					extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
					values('year', 'month', 'local_id').\
					annotate(Sum('valor'))

					for venta in ventas_local:
						if fecha.month == venta['month'] and fecha.year == venta['year']:
							ventas += venta['valor__sum']

					arriendo_minimo = 0

					if arriendo_minimo >= ventas:
						total = 0
					else:
						total = ((ventas * valor) / 100)

				else:

					valor 			= None
					ventas 			= None
					arriendo_minimo = None
					total 			= None

			except Exception:

				valor 			= None
				ventas 			= None
				arriendo_minimo = None
				total 			= None


			proceso_detalle = Detalle_Arriendo_Variable(
				valor 			= valor,
				ventas 			= ventas,
				arriendo_minimo = arriendo_minimo,
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()
			
			data.append({'id':proceso.id})

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

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))
	
			for local in locales:
				
				try:
					gasto_comun = Gasto_Comun.objects.get(contrato=contrato, local=local)
					if gasto_comun.prorrateo == True:
						valor 		= None
						prorrateo 	= True
						try:
							gasto_mensual 	= Gasto_Mensual.objects.get(activo=local.activo, mes=fecha.month, anio=fecha.year).valor
							total 		 	= (local.metros_cuadrados * gasto_mensual) / metros_total['metros_cuadrados__sum']
						except Exception:						
							gasto_mensual	= None
							total 			= None
					else:
						factor 			= gasto_comun.moneda.moneda_historial_set.all().order_by('-id').first().valor

						valor 			= gasto_comun.valor
						gasto_mensual 	= None
						prorrateo 		= False
						total 			= valor * factor
					

				except Gasto_Comun.DoesNotExist:
					valor 			= None
					gasto_mensual 	= None
					prorrateo 		= False
					total 			= None


				Detalle_Gasto_Comun(
					valor 			= valor,
					prorrateo		= prorrateo,
					gasto_mensual 	= gasto_mensual,
					metros_total 	= metros_total['metros_cuadrados__sum'],
					total 			= total, 
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso 		= proceso,
					contrato 		= contrato,
					local 			= local,
				).save()
			
			data.append({'id':proceso.id})

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

			data.append({'id':proceso.id})

		fecha = sumar_meses(fecha, 1)

	return data



def data_arriendo_minimo(proceso):

	data 	= {}
	detalle = []
	total 	= 0
	
	detalles = Detalle_Arriendo_Minimo.objects.filter(proceso=proceso)

	for item in detalles:

		contrato = item.contrato
		locales = contrato.locales.all()

		detalle.append({
			'valor'				: item.valor if item.valor is not None else '---',
			'metro_cuadrado'	: 'SI' if item.metro_cuadrado == True else 'No',
			'metros_local'		: item.metros_local if item.metro_cuadrado is True and item.metros_local is not None else '---',
			'reajuste'			: 'SI' if item.reajuste == True else 'No',
			'reajuste_valor'	: item.reajuste_valor if item.reajuste_valor is not None else '---',
			'total'				: item.total if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_arriendo_variable(proceso):

	data 	= {}
	detalle = []
	total 	= 0

	detalles = Detalle_Arriendo_Variable.objects.filter(proceso=proceso)

	for item in detalles:

		contrato = item.contrato
		locales = contrato.locales.all()

		detalle.append({
			'valor' 			: item.valor if item.valor is not None else '---',
			'ventas' 			: item.ventas if item.ventas is not None else '---',
			'arriendo_minimo' 	: item.arriendo_minimo if item.arriendo_minimo is not None else '---',
			'total' 			: item.total if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_servicios_basicos(proceso):

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
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
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

def data_gastos_comunes(proceso):

	data 			= {}
	detalle 		= []
	total			= 0

	detalles = Detalle_Gasto_Comun.objects.filter(proceso=proceso)

	for item in detalles:
		detalle.append({
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'local'				: item.local.nombre,
			'proratea' 			: 'si' if item.prorrateo == True else 'no',
			'valor' 			: item.valor if item.valor is not None else 'N/A',
			'metros_local' 		: item.local.metros_cuadrados,
			'factor' 			: item.gasto_mensual if item.gasto_mensual is not None else 'N/A',
			'total' 			: item.total if item.total is not None else 'N/A',
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data



def propuesta_pdf(proceso, pk=None):


	if pk is not None:
		proceso = Proceso.objects.get(id=pk)

	options = {
		# 'orientation': 'Landscape',
		'margin-top': '0.5in',
		'margin-right': '0.2in',
		'margin-left': '0.2in',
		'margin-bottom': '0.5in',
		'encoding': "UTF-8",
		}

	css = 'static/assets/css/bootstrap.min.css'

	if proceso.concepto_id == 1:
		data    	= data_arriendo_minimo(proceso)
		template 	= get_template('pdf/procesos/propuesta_arriendo_minimo.html')

	elif proceso.concepto_id == 2:
		data    	= data_arriendo_variable(proceso)
		template 	= get_template('pdf/procesos/propuesta_arriendo_variable.html')

	elif proceso.concepto_id == 3:
		data 		= data_gastos_comunes(proceso)
		template 	= get_template('pdf/procesos/propuesta_gastos_comunes.html')

	elif proceso.concepto_id == 4:
		data 		= data_servicios_basicos(proceso)
		template 	= get_template('pdf/procesos/propuesta_servicios_basicos.html')	

	else:
		print ('error: concepto sin template ni data')

	context = Context({
		'proceso' 	: proceso,
		'detalle' 	: data['detalle'],
		'total'		: data['total'],
	})

	html 		= template.render(context)
	pdfkit.from_string(html, 'public/media/contratos/propuesta_facturacion.pdf', options=options, css=css)
	pdf 		= open('public/media/contratos/propuesta_facturacion.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=propuesta_facturacion.pdf'
	pdf.close()

	return response






