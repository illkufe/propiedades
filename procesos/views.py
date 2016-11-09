# -*- coding: utf-8 -*-
import urllib

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.db import transaction
from django.shortcuts import render
from django.views.generic import View
from django.template import Context, loader
from django.template.loader import get_template 
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from administrador.models import Configuracion
from facturacion.views.views import *
from locales.models import *
from activos.models import *
from conceptos.models import *
from contrato.models import *
from procesos.models import *
from operaciones.models import *
from utilidades.models import *

from utilidades.views import *
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from decimal import Decimal

import os
import json
import pdfkit


class PropuestaGenerarList(ListView):

	model 			= Factura
	template_name 	= 'propuesta_generar_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(PropuestaGenerarList, self).get_context_data(**kwargs)
		context['title'] 	= 'Gererar Propuestas'
		context['subtitle'] = 'propuestas de facturación'
		context['name'] 	= 'generar'
		context['href'] 	= 'propuesta/generar'

		context['conceptos'] 	= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		context['activos'] 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		
		return context

class PropuestaProcesarList(ListView):

	model 			= Factura
	template_name 	= 'propuesta_procesar_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(PropuestaProcesarList, self).get_context_data(**kwargs)
		context['title'] 	= 'Procesar Propuesta'
		context['subtitle'] = 'propuestas de facturación'
		context['name'] 	= 'enviar'
		context['href'] 	= 'propuesta/procesar'

		data_propuestas = list()
		data_procesadas = list()
		users 			= self.request.user.userprofile.empresa.userprofile_set.all().values_list('user_id', flat=True)

		for item in Factura.objects.filter(user__in=users, estado_id__in=[1,3], visible=True):
			data_propuestas.append({
				'id' 			: item.id,
				'nombre'		: item.nombre,
				'fecha_inicio'	: item.fecha_inicio,
				'fecha_termino' : item.fecha_termino,
				'contrato'		: item.contrato,
				'total'			: formato_moneda_local(self.request, item.total)
			})

		for item in Factura.objects.filter(user__in=users, estado_id__in=[2,4,5], visible=True):
			data_procesadas.append({
				'id'			: item.id,
				'numero_pedido'	: item.numero_pedido,
				'nombre'		: item.nombre,
				'fecha_inicio'	: item.fecha_inicio,
				'fecha_termino'	: item.fecha_termino,
				'contrato'		: item.contrato,
				'total'			: formato_moneda_local(self.request, item.total)
			})

		context['facturas_propuestas'] = data_propuestas
		context['facturas_procesadas'] = data_procesadas
		
		return context

class PROPUESTA_CONSULTAR(View):

	http_method_names = ['get', 'post']

	def get(self, request):

		return render(request, 'propuesta_consultar.html',{
			'title' 	: 'Proceso de Facturación',
			'subtitle' 	: 'conceptos facturados',
			'name' 		: 'consultar',
			'href' 		: '/propuesta/consultar',
			})

	def post(self, request):

		data 		= list()

		contratos 	= Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, estado__in=[4,6], visible=True)
		conceptos 	= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		var_post 	= request.POST.copy()
		var_mes 	= var_post['mes']
		var_anio 	= var_post['anio']

		for contrato in contratos:

			data_conceptos = list()

			for concepto in conceptos:

				if contrato.conceptos.filter(id=concepto.id).exists():

					asociado = True

					if contrato.factura_set.filter(estado__in=[2,4,5], fecha_inicio__month=var_mes, fecha_inicio__year=var_anio, fecha_termino__month=var_mes, fecha_termino__year=var_anio, visible=True).exists():
						valido = True
					else:
						valido = False

				else:
					asociado 	= False
					valido 		= None

				data_conceptos.append({
					'id'		: concepto.id,
					'nombre'	: concepto.nombre,
					'codigo'	: concepto.codigo,
					'asociado'	: asociado,
					'valido'	: valido,
				})

			data.append({
				'id'		: contrato.id,
				'numero'	: contrato.numero,
				'nombre'	: contrato.nombre_local,
				'cliente'	: contrato.cliente.nombre,
				'conceptos'	: data_conceptos,
			})

		return JsonResponse(data, safe=False)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def propuesta_filtrar(request):

	data 			= list()

	var_post 		= request.POST.copy()
	activo_id		= var_post['activo']
	conceptos_id 	= var_post.getlist('conceptos')

	fecha 			= ultimo_dia(datetime.strptime('01/'+var_post['mes']+'/'+var_post['anio']+'', "%d/%m/%Y"))
	activo 			= Activo.objects.get(id=activo_id)
	locales 		= activo.local_set.filter(visible=True).values_list('id', flat=True)
	contratos 		= Contrato.objects.filter(locales__in=locales, estado__in=[4,6], visible=True).distinct()

	for contrato in contratos:

		conceptos = list()

		for concepto_id in conceptos_id:

			concepto = Concepto.objects.get(id=concepto_id)

			if contrato.conceptos.filter(id=concepto_id).exists():
				asociado 	= True
				valido 		= validar_concepto(contrato, concepto, fecha)
			else:
				asociado 	= False 
				valido 		= {'estado': False, 'mensaje': 'no tiene este concepto asociado'}

			conceptos.append({
				'id'		: concepto.id,
				'nombre'	: concepto.nombre,
				'codigo'	: concepto.codigo,
				'asociado'	: asociado,
				'valido'	: valido,
			})

		data.append({
			'id'		: contrato.id,
			'numero'	: contrato.numero,
			'nombre'	: contrato.nombre_local,
			'cliente'	: contrato.cliente.nombre,
			'conceptos'	: conceptos,
		})

	return JsonResponse(data, safe=False)

def propuesta_generar(request):

	response 		= list()
	var_post 		= request.POST.copy()

	contratos_id 	= var_post.get('contratos').split(",")
	conceptos_id 	= var_post.get('conceptos').split(",")
	fecha 			= ultimo_dia(datetime.strptime('01/'+var_post['mes']+'/'+var_post['anio']+'', "%d/%m/%Y").date())

	configuracion = {
		'uf' : Decimal(var_post.get('uf_valor').replace(".", "").replace(",", "."))
	}

	for contrato_id in contratos_id:

		contrato 	= Contrato.objects.get(id=contrato_id)
		conceptos 	= list()

		for concepto_id in conceptos_id:

			concepto = Concepto.objects.get(id=concepto_id)

			if validar_concepto(contrato, concepto, fecha)['estado'] == True:

				total = calcular_concepto(contrato, concepto, fecha, configuracion)

				if total is not 0:
					conceptos.append({
						'id'		: concepto.id,
						'nombre'	: concepto.nombre,
						'total'		: total,
						})

		cliente = {
			'id' 		: contrato.cliente.id,
			'nombre' 	: contrato.cliente.nombre,
			'rut' 		: contrato.cliente.rut,
		}

		response.append({
			'id'		: contrato.id,
			'numero'	: contrato.numero,
			'nombre'	: contrato.nombre_local,
			'cliente'	: cliente,
			'conceptos' : conceptos,
			})

	return JsonResponse(response, safe=False)

@transaction.atomic
def propuesta_guardar(request):

	response 	= list()
	var_post 	= request.POST.copy()
	data 		= json.loads(var_post['contratos'])

	try:
		with transaction.atomic():

			nombre 			= var_post['nombre']
			fecha_inicio	= primer_dia(datetime.strptime('01/'+var_post['mes']+'/'+var_post['anio']+'', "%d/%m/%Y"))
			fecha_termino	= ultimo_dia(datetime.strptime('01/'+var_post['mes']+'/'+var_post['anio']+'', "%d/%m/%Y"))

			for item in data:

				total 		= 0 
				contrato 	= Contrato.objects.get(id=int(item['id']))
				estado 		= Factura_Estado.objects.get(id=int(1))			
				conceptos 	= item['conceptos']

				factura = Factura(
					nombre 			= nombre,
					fecha_inicio	= fecha_inicio,
					fecha_termino	= fecha_termino,
					uf_valor		= Decimal(var_post.get('uf_valor').replace(".", "").replace(",", ".")),
					uf_modificada	= True if var_post.get('uf_modificada') == 'true' else False,
					contrato 		= contrato,
					estado 			= estado,
					total 			= total,
					user 			= request.user,
					motor_emision 	= request.user.userprofile.empresa.configuracion.motor_factura,
				)
				factura.save()
				
				for concepto in conceptos:
					if Factura_Detalle.objects.filter(factura__contrato=contrato, concepto_id=concepto['id'], factura__fecha_inicio=fecha_inicio, factura__fecha_termino=fecha_termino).exists():
						factura_detalle 		= Factura_Detalle.objects.get(factura__contrato=contrato, concepto_id=concepto['id'], factura__fecha_inicio=fecha_inicio, factura__fecha_termino=fecha_termino)
						factura_anterior 		= factura_detalle.factura
						factura_anterior.total 	= factura_anterior.total - factura_detalle.total
						factura_anterior.save()
						factura_detalle.delete()

						if factura_anterior.factura_detalle_set.all().count() == 0:
							factura_anterior.delete()
							

					concepto_id 		= concepto['id']
					concepto_nombre 	= concepto['nombre']
					concepto_total 		= Decimal(concepto['total'].replace(".", "").replace(",", "."))
					concepto_modificado = concepto['modified']

					Factura_Detalle(
						nombre 			= concepto_nombre,
						total 			= concepto_total,
						factura 		= factura,
						concepto_id 	= int(concepto_id),
					).save()

					total += concepto_total

				factura.total = total
				factura.save()

			id 		= factura.id
			estado 	= True
			mensaje = 'ok'

	except Exception as error:
		id 		= None
		estado 	= False
		mensaje = str(error)

	return JsonResponse({'estado':estado, 'mensaje':mensaje, 'id':id}, safe=False)

def propuesta_pdf(request, pk=None):

	data 		= list()
	total 		= 0
	propuesta 	= Propuesta.objects.get(id=pk)

	for factura in propuesta.factura_set.all():

		conceptos 	= list()
		subtotal	= 0

		for detalle in factura.factura_detalle_set.all():

			subtotal 	+= detalle.total
			total 		+= detalle.total

			conceptos.append({
				'nombre'	: detalle.nombre,
				'total'		: formato_moneda(detalle.total),
				})

		item = {'contrato': factura.contrato, 'conceptos':conceptos, 'subtotal': formato_moneda(subtotal)}

		data.append(item)

	options = {
		'margin-top'	: '0.5in',
		'margin-right'	: '0.2in',
		'margin-left'	: '0.2in',
		'margin-bottom'	: '0.5in',
		'encoding'		: 'UTF-8',
		}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/procesos/propuesta_facturacion.html')
	

	context = Context({
		'propuesta' 	: propuesta,
		'propuestas' 	: data,
		'total'			: formato_moneda(total),
	})

	html 		= template.render(context)
	pdfkit.from_string(html, 'public/media/contratos/propuesta_facturacion.pdf', options=options, css=css)
	pdf 		= open('public/media/contratos/propuesta_facturacion.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=propuesta_facturacion.pdf'
	pdf.close()

	return response

def propuesta_enviar(request):

	var_post 	= request.POST.copy()
	factura 	= Factura.objects.get(id=var_post['id'])
	profile 	= UserProfile.objects.get(user=request.user)
	empresa 	= Empresa.objects.get(id=profile.empresa_id)
	estado 		= None
	data 		= list()
	response 	= list()

	parametro_de_facturacion = empresa.configuracion.motor_factura_id

	if parametro_de_facturacion == 1:
		response_ws = envio_factura_inet(request)

		if response_ws['success'] == True:
			respuesta = response_ws['respuesta']

			if len(respuesta.SDT_ERRORES_ERROR) == 1:
				for error in respuesta.SDT_ERRORES_ERROR:
					if int(error.NUMERROR) == 0:
						estado = True
						root = etree.fromstring(error.DESCERROR)
						response.append({
							'codigo': root.find('{http://www.informat.cl/ws}ATENUMREA').text,
							'estado': root.find('{http://www.informat.cl/ws}COD_ESTADO').text,
						})
						factura.estado_id 			= 2
						factura.motor_emision_id	= 1
						factura.numero_pedido		= int(root.find('{http://www.informat.cl/ws}ATENUMREA').text)
					else:
						estado = False
						response.append({
							'descripcion' 	: str(error.NUMERROR) + ': '+ error.DESCERROR,
						})
						factura.estado_id = 3
			else:
				estado = False
				factura.estado_id = 3
				for error in respuesta.SDT_ERRORES_ERROR:
					response.append({
						'descripcion'  : str(error.NUMERROR) + ': '+ error.DESCERROR,
					})

			factura.save()
			data.append({'estado'	: estado,
						 'response' :response,
						 })
			return JsonResponse(data, safe=False)

		else:
			estado = False
			factura.estado_id = 3

			response.append({
				'numero' 		: 9,
				'descripcion' 	: response_ws['error'],
			})

			factura.save()
			data.append({'estado'	: estado,'response' : response,
					 })
			return JsonResponse(data, safe=False)

	elif parametro_de_facturacion == 2:

		resultado 	= armar_dict_documento(request)

		if not resultado['error']:

			response_ws = envio_documento_tributario_electronico(**resultado)

			if response_ws['success'] == True:
				estado = True
				response.append({
					'folio'			: response_ws['folio'],
					'archivo_pdf'	: response_ws['ruta_archivo'],
				})

				factura.numero_pedido 		= int(response_ws['folio'])
				factura.url_documento		= response_ws['ruta_archivo']
				factura.estado_id 			= 2
				factura.motor_emision_id	= 2

			else:
				estado = False
				factura.estado_id = 3

				response.append({
					'descripcion' 	: response_ws['error'],
				})

			factura.save()
			data.append({'estado'	: estado,
						 'response' :response,
						 })

			return JsonResponse(data, safe=False)
		else:
			estado = False
			factura.estado_id = 3

			response.append({
				'descripcion' : resultado['error'],
			})

			factura.save()
			data.append({'estado'	: estado,
						 'response' :response,
						 })

			return JsonResponse(data, safe=False)

	else:
		estado 	= False
		error 	= "No se ha configurado proveedor de facturación."
		response.append({
			'descripcion': error,
		})

		factura.save()
		data.append({'estado': estado,
					 'response': response,
					 })

		return JsonResponse(data, safe=False)

def factura_pdf(request, pk=None):

	data = list()
	total = 0
	propuesta = Propuesta.objects.get(id=pk)

	for factura in propuesta.factura_set.all():

		conceptos = list()
		subtotal = 0

		for detalle in factura.factura_detalle_set.all():
			subtotal += detalle.total
			total += detalle.total

			conceptos.append({
				'nombre': detalle.nombre,
				'total'	: formato_moneda(detalle.total),
			})

		item = {'contrato': factura.contrato, 'conceptos' :conceptos, 'subtotal': formato_moneda(subtotal)}

		data.append(item)

	options = {
		'margin-top'	: '0.5in',
		'margin-right'	: '0.2in',
		'margin-left'	: '0.2in',
		'margin-bottom'	: '0.5in',
		'encoding'		: 'UTF-8',
	}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/procesos/propuesta_facturacion.html')


	context = Context({
		'propuesta' 	: propuesta,
		'propuestas' 	: data,
		'total'			: formato_moneda(total),
	})

	html 		= template.render(context)
	pdfkit.from_string(html, 'public/media/contratos/propuesta_facturacion.pdf', options=options, css=css)
	pdf 		= open('public/media/contratos/propuesta_facturacion.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=propuesta_facturacion.pdf'
	pdf.close()

	return response




# validar conceptos - - - - - - - - - - - - - - - - - - - - - - - - - -

def validar_concepto(contrato, concepto, fecha):

	if concepto.concepto_tipo.id == 1:
		return validar_arriendo_minimo(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 2:
		return validar_arriendo_variable(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 3:
		return validar_gasto_comun(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 4:
		return validar_servicios_basicos(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 5:
		return validar_cuota_de_incorporacion(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 6:
		return validar_gasto_asociado(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 7:
		return validar_arriendo_bodega(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 8:
		return validar_servicios_varios(contrato, concepto, fecha)

	elif concepto.concepto_tipo.id == 9:
		return validar_multas(contrato, concepto, fecha)

	else:
		return True

def validar_arriendo_minimo(contrato, concepto, periodo):

	mensajes = [
		'arriendo mínimo: tiene',
		'arriendo mínimo: no tiene',
		'arriendo mínimo: no tiene para este periodo',
		'arriendo mínimo: tiene más de uno para este período',
		'arriendo mínimo: tiene más de uno para este período para el reajuste',
	]

	# arriendo minimo
	if Arriendo_Minimo.objects.filter(contrato=contrato, concepto=concepto).exists():

		if Arriendo_Minimo.objects.filter(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() < 1:

			estado 	= False
			mensaje = 2

		elif Arriendo_Minimo.objects.filter(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() == 1:

			estado 	= True
			mensaje = 0

		else:

			estado 	= False
			mensaje = 3

	else:
		estado 	= False
		mensaje = 1

	# reajuste
	if estado is True:

		reajuste = validar_reajuste(contrato, concepto, periodo)

		if reajuste is False:

			estado 	= False
			mensaje = 4

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_arriendo_variable(contrato, concepto, periodo):

	mensajes = [
		'arriendo variable : correcto',
		'arriendo variable : incorrecto, existen varios detalles para este período',
		'arriendo variable : incorrecto, no tiene ventas para este período',
		'arriendo variable : incorrecto, no tiene uf del día especificado',
		'arriendo variable : incorrecto, no tiene arriendo mínimo facturado',
		'arriendo variable : incorrecto, no existe para este período',
	]

	if Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).exists():

		if Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() == 1:

			arriendo 	= Arriendo_Variable.objects.get(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo)
			locales 	= contrato.locales.all()

			if Venta.objects.filter(local_id__in=locales, fecha_inicio__month=periodo.month, fecha_termino__month=periodo.month, fecha_inicio__year=periodo.year, fecha_termino__year=periodo.year).exists():

				if Moneda_Historial.objects.filter(fecha__day=arriendo.dia_reajuste, fecha__month=periodo.month, fecha__year=periodo.year).exists():

					if arriendo.relacion is True:

						if Factura_Detalle.objects.filter(concepto=arriendo.arriendo_minimo, factura__contrato=contrato, factura__fecha_inicio__month=periodo.month, factura__fecha_inicio__year=periodo.year, factura__fecha_termino__month=periodo.month, factura__fecha_termino__year=periodo.year).exists():
							estado 	= True
							mensaje = 0
						else:
							estado 	= False
							mensaje = 4
					else:
						estado 	= True
						mensaje = 0

				else:
					estado 	= False
					mensaje = 3

			else:
				estado 	= False
				mensaje = 2

		else:
			estado 	= False
			mensaje = 1

	else:
		estado 	= False
		mensaje = 5

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_gasto_comun(contrato, concepto, periodo):

	mensajes = [
		'gasto común: correcto',
		'gasto común: incorrecto',
		'gasto comun: no existe',
		'gasto común: no existe gasto mensual ingresado para este período',
	]

	estado 	= False
	mensaje = 2

	if Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto).exists():

		estado 	= True
		mensaje = 0

		gastos_comunes = Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto)

		for gasto_comun in gastos_comunes:

			if gasto_comun.tipo == 2:

				if Gasto_Mensual.objects.filter(mes=periodo.month, anio=periodo.year, visible=True).exists() is False:

					estado 	= False
					mensaje = 3

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_servicios_basicos(contrato, concepto, periodo):

	mensajes = [
		'Correcto',
		'No tiene ingresado el consumo para este periodo',
		'No tiene servicos basicos',
	]

	estado 	= False
	mensaje = 2

	if Servicio_Basico.objects.filter(contrato=contrato, concepto=concepto).exists():

		estado 	= True
		mensaje = 0

		servicios_basicos = Servicio_Basico.objects.filter(contrato=contrato, concepto=concepto)

		for servicio_basico in servicios_basicos:

			for local in servicio_basico.locales.all():

				medidores_luz  	= Medidor_Electricidad.objects.filter(local=local)
				medidores_agua  = Medidor_Agua.objects.filter(local=local)
				medidores_gas  	= Medidor_Gas.objects.filter(local=local)

				for medidor_luz in medidores_luz:
					if Lectura_Electricidad.objects.filter(medidor_electricidad=medidor_luz, mes=(periodo.month-1), anio=periodo.year).exists():
						if Lectura_Electricidad.objects.filter(medidor_electricidad=medidor_luz, mes=(periodo.month), anio=periodo.year).exists() is False:
							return {
								'estado'	: False,
								'mensaje'	: 'falta lectura electricidad de este periodo',
							}
						else:
							lectura_anterior 	= Lectura_Electricidad.objects.get(medidor_electricidad=medidor_luz, mes=(periodo.month-1), anio=periodo.year).valor
							lectura_actual 		= Lectura_Electricidad.objects.get(medidor_electricidad=medidor_luz, mes=(periodo.month), anio=periodo.year).valor

							if lectura_anterior > lectura_actual:
								return {
									'estado'	: False,
									'mensaje'	: 'lectura electricidad mes actual mayor que el mes anterior',
								}								

					else:
						return {
							'estado'	: False,
							'mensaje'	: 'falta lectura electricidad mes anterior',
						}

				for medidor_agua in medidores_agua:
					if Lectura_Agua.objects.filter(medidor_agua=medidor_agua, mes=(periodo.month-1), anio=periodo.year).exists():
						if Lectura_Agua.objects.filter(medidor_agua=medidor_agua, mes=(periodo.month), anio=periodo.year).exists() is False:
							return {
								'estado'	: False,
								'mensaje'	: 'falta lectura agua de este periodo',
							}
						else:
							lectura_anterior 	= Lectura_Agua.objects.get(medidor_agua=medidor_agua, mes=(periodo.month-1), anio=periodo.year).valor
							lectura_actual 		= Lectura_Agua.objects.get(medidor_agua=medidor_agua, mes=(periodo.month), anio=periodo.year).valor

							if lectura_anterior > lectura_actual:
								return {
									'estado'	: False,
									'mensaje'	: 'lectura agua mes actual mayor que el mes anterior',
								}
					else:
						return {
							'estado'	: False,
							'mensaje'	: 'falta lectura agua mes anterior',
						}

				for medidor_gas in medidores_gas:
					if Lectura_Gas.objects.filter(medidor_gas=medidor_gas, mes=(periodo.month-1), anio=periodo.year).exists():
						if Lectura_Gas.objects.filter(medidor_gas=medidor_gas, mes=(periodo.month), anio=periodo.year).exists() is False:
							return {
								'estado'	: False,
								'mensaje'	: 'falta lectura gas de este periodo',
							}
						else:
							lectura_anterior 	= Lectura_Gas.objects.get(medidor_gas=medidor_gas, mes=(periodo.month-1), anio=periodo.year).valor
							lectura_actual 		= Lectura_Gas.objects.get(medidor_gas=medidor_gas, mes=(periodo.month), anio=periodo.year).valor

							if lectura_anterior > lectura_actual:
								return {
									'estado'	: False,
									'mensaje'	: 'lectura gas mes actual mayor que el mes anterior',
								}
					else:
						return {
							'estado'	: False,
							'mensaje'	: 'falta lectura gas mes anterior',
						}

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_cuota_de_incorporacion(contrato, concepto, periodo):

	mensajes = [
		'cuota de incorporación : correcto',
		'cuota de incorporación : incorrecto',
		'cuota de incorporación : no existe',
		'cuota de incorporación : no existe para este período',
	]

	estado 	= False
	mensaje = 2

	if Cuota_Incorporacion.objects.filter(contrato=contrato, concepto=concepto).exists():

		if Cuota_Incorporacion.objects.filter(contrato=contrato, concepto=concepto, fecha__year=periodo.year, fecha__month=periodo.month, visible=True).exists():
			estado 	= True
			mensaje = 0
		else:
			estado = False
			mensaje = 1

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_gasto_asociado(contrato, concepto, periodo):

	mensajes = [
		'gasto asociado : correcto',
		'gasto asociado : incorrecto',
		'gasto asociado : no existe',
		'gasto asociado : no existe para este período',
		'gasto asociado : el concepto asociado no fue facturado',
	]

	estado 	= False
	mensaje = 2
	
	if Gasto_Asociado.objects.filter(contrato=contrato, concepto=concepto).exists():

		estado 	= False
		mensaje = 3

		gastos_asociados = Gasto_Asociado.objects.filter(contrato=contrato, concepto=concepto)

		for gasto_asociado in gastos_asociados:

			# validar periodicidad del concepto alternativa
			if gasto_asociado.periodicidad == 1:

				if periodo >= gasto_asociado.fecha:

					estado 	= True
					mensaje = 0

			elif gasto_asociado.periodicidad == 2:

				fecha_1 = sumar_meses(gasto_asociado.fecha, 3)
				fecha_2 = sumar_meses(gasto_asociado.fecha, 6)
				fecha_3 = sumar_meses(gasto_asociado.fecha, 9)
				fecha_4 = sumar_meses(gasto_asociado.fecha, 12)

				if periodo >= gasto_asociado.fecha and (periodo.month == fecha_1.month or periodo.month == fecha_2.month or periodo.month == fecha_3.month or periodo.month == fecha_4.month):

					estado 	= True
					mensaje = 0

			elif gasto_asociado.periodicidad == 3:

				fecha_1 = sumar_meses(gasto_asociado.fecha, 6)
				fecha_2 = sumar_meses(gasto_asociado.fecha, 12)

				if periodo >= gasto_asociado.fecha and (periodo.month == fecha_1.month or periodo.month == fecha_2.month):

					estado 	= True
					mensaje = 0

			elif gasto_asociado.periodicidad == 4:

				if periodo >= gasto_asociado.fecha and gasto_asociado.fecha.month == periodo.month:

					estado 	= True
					mensaje = 0

			else:
				pass

			# validar vinculo del concepto
			if estado is True and gasto_asociado.valor_fijo is False:

				if Factura_Detalle.objects.filter(concepto=gasto_asociado.vinculo, factura__contrato=contrato, factura__fecha_inicio__month=sumar_meses(periodo, -1).month, factura__fecha_inicio__year=periodo.year, factura__fecha_termino__month=sumar_meses(periodo, -1).month, factura__fecha_termino__year=periodo.year).exists():
					estado 	= True
					mensaje = 0
				else:
					estado 	= False
					mensaje = 4


	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_arriendo_bodega(contrato, concepto, periodo):

	mensajes = [
		'arriendo bodega : correcto',
		'arriendo bodega : incorrecto, no tiene metros cuadrados',
		'arriendo bodega : no existe',
		'arriendo bodega : no existe para este período',
	]

	estado 	= False
	mensaje = 2
	
	if Arriendo_Bodega.objects.filter(contrato=contrato, concepto=concepto).exists():

		estado 	= False
		mensaje = 3

		arriendo_bodegas = Arriendo_Bodega.objects.filter(contrato=contrato, concepto=concepto)

		for arriendo_bodega in arriendo_bodegas:

			# validar periodicidad del concepto alternativa
			if arriendo_bodega.periodicidad == 1:

				if periodo >= arriendo_bodega.fecha_inicio:

					estado 	= True
					mensaje = 0

			elif arriendo_bodega.periodicidad == 2:

				fecha_1 = sumar_meses(arriendo_bodega.fecha_inicio, 3)
				fecha_2 = sumar_meses(arriendo_bodega.fecha_inicio, 6)
				fecha_3 = sumar_meses(arriendo_bodega.fecha_inicio, 9)
				fecha_4 = sumar_meses(arriendo_bodega.fecha_inicio, 12)

				if periodo >= arriendo_bodega.fecha_inicio and (periodo.month == fecha_1.month or periodo.month == fecha_2.month or periodo.month == fecha_3.month or periodo.month == fecha_4.month):

					estado 	= True
					mensaje = 0

			elif arriendo_bodega.periodicidad == 3:

				fecha_1 = sumar_meses(arriendo_bodega.fecha_inicio, 6)
				fecha_2 = sumar_meses(arriendo_bodega.fecha_inicio, 12)

				if periodo >= arriendo_bodega.fecha_inicio and (periodo.month == fecha_1.month or periodo.month == fecha_2.month):

					estado 	= True
					mensaje = 0

			elif arriendo_bodega.periodicidad == 4:

				if periodo >= arriendo_bodega.fecha_inicio and arriendo_bodega.fecha_inicio.month == periodo.month:

					estado 	= True
					mensaje = 0

			else:
				pass

			# verificar si tiene la cantidad de metros cuadrados
			if estado is True:

				if arriendo_bodega.metro_cuadrado is True and contrato.bodega is False:

					return {
						'estado'	: False,
						'mensaje'	: mensajes[1],
					}

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_servicios_varios(contrato, concepto, periodo):

	mensajes = [	
		'servicios varios: correcto',
		'servicios varios: incorrecto',
		'servicios varios: no existe',
		'servicios varios: no existe para este período',
	]

	estado 	= False
	mensaje = 2
	
	locales_id = contrato.locales.all().values_list('id', flat=True)

	if Gasto_Servicio.objects.filter(locales__in=locales_id).exists():

		if Gasto_Servicio.objects.filter(locales__in=locales_id, mes=periodo.month, anio=periodo.year).exists():

			estado 	= True
			mensaje = 0

		else:

			estado 	= False
			mensaje = 3

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_multas(contrato, concepto, periodo):

	mensajes = [
		'multas : correcto',
		'multas : incorrecto',
		'multas : no existe',
		'multas : no existe para este período',
	]

	estado 	= False
	mensaje = 2

	if Multa.objects.filter(contrato=contrato).exists():

		if Multa.objects.filter(contrato=contrato, mes=periodo.month, anio=periodo.year, visible=True).exists():
			estado 	= True
			mensaje = 0
		else:
			estado = False
			mensaje = 3

	return {
		'estado'	: estado,
		'mensaje'	: mensajes[mensaje],
	}

def validar_reajuste(contrato, concepto, periodo):

	if Reajuste.objects.filter(contrato=contrato, vinculo=concepto).exists():

		if Reajuste.objects.filter(contrato=contrato, vinculo=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() < 1:

			estado 	= True

		elif Reajuste.objects.filter(contrato=contrato, vinculo=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() == 1:

			estado 	= True

		else:

			estado 	= False

	else:
		estado = True

	return estado


# calcular conceptos - - - - - - - - - - - - - - - - - - - - - - - - -

def calcular_concepto(contrato, concepto, periodo, configuracion):

	if concepto.concepto_tipo.id == 1:
		return calcular_arriendo_minimo(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 2:
		return calcular_arriendo_variable(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 3:
		return calcular_gasto_comun(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 4:
		return calcular_servicios_basicos(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 5:
		return calcular_cuota_de_incorporacion(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 6:
		return calcular_gasto_asociado(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 7:
		return calcular_arriendo_bodega(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 8:
		return calcular_servicios_varios(contrato, concepto, periodo, configuracion)

	elif concepto.concepto_tipo.id == 9:
		return calcular_multas(contrato, concepto, periodo, configuracion)

	else:
		return True

def calcular_arriendo_minimo(contrato, concepto, periodo, configuracion):

	total = 0

	if Arriendo_Minimo.objects.filter(contrato=contrato, concepto=concepto).exists():

		if Arriendo_Minimo.objects.filter(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() == 1:

			arriendo 	= Arriendo_Minimo.objects.get(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo)
			valor 		= arriendo.valor

			# moneda
			if arriendo.moneda.id == 3:
				moneda = configuracion['uf']
			else:
				moneda = arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

			# metros cuadrados
			if arriendo.metro_cuadrado is True:
				metros = contrato.locales.all().aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			else:
				metros = 1

			total = valor * moneda * metros
	

	if validar_reajuste(contrato, concepto, periodo) is True:

		total = calcular_reajuste(contrato, concepto, periodo, total)


	return total

def calcular_arriendo_variable(contrato, concepto, periodo, configuracion):

	total = 0

	if Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).exists():

		if Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() == 1:

			arriendo 	= Arriendo_Variable.objects.get(contrato=contrato, concepto=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo)
			locales 	= contrato.locales.all()

			if Venta.objects.filter(local_id__in=locales, fecha_inicio__month=periodo.month, fecha_termino__month=periodo.month, fecha_inicio__year=periodo.year, fecha_termino__year=periodo.year).exists():

				if Moneda_Historial.objects.filter(fecha__day=arriendo.dia_reajuste, fecha__month=periodo.month, fecha__year=periodo.year).exists():

					ventas_valor 		= Venta.objects.filter(local_id__in=locales, fecha_inicio__month=periodo.month, fecha_termino__month=periodo.month, fecha_inicio__year=periodo.year, fecha_termino__year=periodo.year).aggregate(Sum('valor'))['valor__sum']
					ventas_uf			= Moneda_Historial.objects.get(fecha__day=arriendo.dia_reajuste, fecha__month=periodo.month, fecha__year=periodo.year, moneda_id=3).valor
					ventas_total   		= ventas_valor / ventas_uf
					ventas_correccion 	= ventas_total * configuracion['uf']
					valor 				= (ventas_correccion * arriendo.valor) / 100

					if arriendo.relacion is True:

						if Factura_Detalle.objects.filter(concepto=arriendo.arriendo_minimo, factura__contrato=contrato, factura__fecha_inicio__month=periodo.month, factura__fecha_inicio__year=periodo.year, factura__fecha_termino__month=periodo.month, factura__fecha_termino__year=periodo.year).exists():
							
							arriendo_minimo = Factura_Detalle.objects.filter(concepto=arriendo.arriendo_minimo, factura__contrato=contrato, factura__fecha_inicio__month=periodo.month, factura__fecha_inicio__year=periodo.year, factura__fecha_termino__month=periodo.month, factura__fecha_termino__year=periodo.year).last()
							arriendo_minimo = arriendo_minimo.total

							if valor > arriendo_minimo:
								total = valor - arriendo_minimo
							else:
								total = 0

					else:
						total = valor
	
	return total

def calcular_gasto_comun(contrato, concepto, periodo, configuracion):

	total = 0

	if Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto).exists():

		gastos_comunes = Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto)

		for gasto_comun in gastos_comunes:

			# valor por m2 del local
			if gasto_comun.metros_cuadrado is True:
				metros_cuadrados = gasto_comun.contrato.locales.all().aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']			
			else:
				metros_cuadrados = 1

			# verificar si es fijo o prorrateable
			if gasto_comun.tipo == 1:

				valor 	= gasto_comun.valor

				if gasto_comun.moneda.id == 3:
					factor 	= configuracion['uf']
				else:
					factor 	= gasto_comun.moneda.moneda_historial_set.all().order_by('-id').first().valor

			else:

				locales 		= contrato.locales.all()
				activos_id 		= contrato.locales.all().values_list('activo_id', flat=True)

				metros_total 	= Local.objects.filter(activo__in=activos_id, visible=True).aggregate(Sum('metros_cuadrados'))
				metros_local 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

				valor 	= Gasto_Mensual.objects.get(activo=contrato.locales.first().activo, mes=periodo.month, anio=periodo.year).valor
				factor 	= ((metros_local['metros_cuadrados__sum'] * 100) / (metros_total['metros_cuadrados__sum'])) / 100

			total += valor * factor * metros_cuadrados

	return total

def calcular_servicios_basicos(contrato, concepto, periodo, configuracion):

	total = 0

	servicios_basicos = Servicio_Basico.objects.filter(contrato=contrato, concepto=concepto)

	for servicio_basico in servicios_basicos:

		for local in servicio_basico.locales.all():

			medidores_luz  	= Medidor_Electricidad.objects.filter(local=local)
			medidores_agua  = Medidor_Agua.objects.filter(local=local)
			medidores_gas  	= Medidor_Gas.objects.filter(local=local)

			for medidor_luz in medidores_luz:

				lectura_anterior 	= Lectura_Electricidad.objects.get(medidor_electricidad=medidor_luz, mes=(periodo.month-1), anio=periodo.year).valor
				lectura_actual 		= Lectura_Electricidad.objects.get(medidor_electricidad=medidor_luz, mes=(periodo.month), anio=periodo.year).valor

				total += (lectura_actual - lectura_anterior) * servicio_basico.valor_electricidad

			for medidor_agua in medidores_agua:

				lectura_anterior 	= Lectura_Agua.objects.get(medidor_agua=medidor_agua, mes=(periodo.month-1), anio=periodo.year).valor
				lectura_actual 		= Lectura_Agua.objects.get(medidor_agua=medidor_agua, mes=(periodo.month), anio=periodo.year).valor

				total += (lectura_actual - lectura_anterior) * servicio_basico.valor_agua

			for medidor_gas in medidores_gas:
				lectura_anterior 	= Lectura_Gas.objects.get(medidor_gas=medidor_gas, mes=(periodo.month-1), anio=periodo.year).valor
				lectura_actual 		= Lectura_Gas.objects.get(medidor_gas=medidor_gas, mes=(periodo.month), anio=periodo.year).valor

				total += (lectura_actual - lectura_anterior) * servicio_basico.valor_gas

	return total

def calcular_cuota_de_incorporacion(contrato, concepto, periodo, configuracion):

	total 	= 0
	cuotas 	= Cuota_Incorporacion.objects.filter(contrato=contrato, concepto=concepto, fecha__year=periodo.year, fecha__month=periodo.month, visible=True)

	for cuota in cuotas:

		valor = cuota.valor

		if cuota.metro_cuadrado is True:
			metros_cuadrados = cuota.contrato.locales.all().aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']			
		else:
			metros_cuadrados = 1

		if cuota.moneda.id == 3:
			factor = configuracion['uf']
		else:
			factor = cuota.moneda.moneda_historial_set.all().order_by('-id').first().valor

		total += (valor * factor * metros_cuadrados)
	
	return total

def calcular_gasto_asociado(contrato, concepto, periodo, configuracion):

	total = 0

	if Gasto_Asociado.objects.filter(contrato=contrato, concepto=concepto).exists():

		gastos_asociados = Gasto_Asociado.objects.filter(contrato=contrato, concepto=concepto)

		for gasto_asociado in gastos_asociados:

			factor = False

			# calcular valor del gasto
			if gasto_asociado.periodicidad == 1:

				if periodo >= gasto_asociado.fecha:

					factor = (gasto_asociado.valor * gasto_asociado.moneda.moneda_historial_set.all().order_by('-id').first().valor)

			elif gasto_asociado.periodicidad == 2:

				fecha_1 = sumar_meses(gasto_asociado.fecha, 3)
				fecha_2 = sumar_meses(gasto_asociado.fecha, 6)
				fecha_3 = sumar_meses(gasto_asociado.fecha, 9)
				fecha_4 = sumar_meses(gasto_asociado.fecha, 12)

				if periodo >= gasto_asociado.fecha and (periodo.month == fecha_1.month or periodo.month == fecha_2.month or periodo.month == fecha_3.month or periodo.month == fecha_4.month):

					factor = (gasto_asociado.valor * gasto_asociado.moneda.moneda_historial_set.all().order_by('-id').first().valor)

			elif gasto_asociado.periodicidad == 3:

				fecha_1 = sumar_meses(gasto_asociado.fecha, 6)
				fecha_2 = sumar_meses(gasto_asociado.fecha, 12)

				if periodo >= gasto_asociado.fecha and (periodo.month == fecha_1.month or periodo.month == fecha_2.month):

					factor = (gasto_asociado.valor * gasto_asociado.moneda.moneda_historial_set.all().order_by('-id').first().valor)

			elif gasto_asociado.periodicidad == 4:

				if periodo >= gasto_asociado.fecha and gasto_asociado.fecha.month == periodo.month:

					factor = (gasto_asociado.valor * gasto_asociado.moneda.moneda_historial_set.all().order_by('-id').first().valor)

			else:
				factor = False

			# calcular valor del vinculo
			if factor is not False :

				if  gasto_asociado.valor_fijo is True:
					total += factor
				else:
					if Factura_Detalle.objects.filter(concepto=gasto_asociado.vinculo, factura__contrato=contrato, factura__fecha_inicio__month=sumar_meses(periodo, -1).month, factura__fecha_inicio__year=periodo.year, factura__fecha_termino__month=sumar_meses(periodo, -1).month, factura__fecha_termino__year=periodo.year).exists():
						concepto_facturado = Factura_Detalle.objects.get(concepto=gasto_asociado.vinculo, factura__contrato=contrato, factura__fecha_inicio__month=sumar_meses(periodo, -1).month, factura__fecha_inicio__year=periodo.year, factura__fecha_termino__month=sumar_meses(periodo, -1).month, factura__fecha_termino__year=periodo.year)
						total += concepto_facturado.total * (factor/100)

	return total

def calcular_arriendo_bodega(contrato, concepto, periodo, configuracion):

	total = 0

	if Arriendo_Bodega.objects.filter(contrato=contrato, concepto=concepto).exists():

		arriendo_bodegas = Arriendo_Bodega.objects.filter(contrato=contrato, concepto=concepto)

		for arriendo_bodega in arriendo_bodegas:

			factor = False

			# calcular valor del arriendo de bodega
			if arriendo_bodega.periodicidad == 1:

				if periodo >= arriendo_bodega.fecha_inicio:

					factor = arriendo_bodega.valor

			elif arriendo_bodega.periodicidad == 2:

				fecha_1 = sumar_meses(arriendo_bodega.fecha_inicio, 3)
				fecha_2 = sumar_meses(arriendo_bodega.fecha_inicio, 6)
				fecha_3 = sumar_meses(arriendo_bodega.fecha_inicio, 9)
				fecha_4 = sumar_meses(arriendo_bodega.fecha_inicio, 12)

				if periodo >= arriendo_bodega.fecha_inicio and (periodo.month == fecha_1.month or periodo.month == fecha_2.month or periodo.month == fecha_3.month or periodo.month == fecha_4.month):

					factor = arriendo_bodega.valor

			elif arriendo_bodega.periodicidad == 3:

				fecha_1 = sumar_meses(arriendo_bodega.fecha_inicio, 6)
				fecha_2 = sumar_meses(arriendo_bodega.fecha_inicio, 12)

				if periodo >= arriendo_bodega.fecha_inicio and (periodo.month == fecha_1.month or periodo.month == fecha_2.month):

					factor = arriendo_bodega.valor

			elif arriendo_bodega.periodicidad == 4:

				if periodo >= arriendo_bodega.fecha_inicio and arriendo_bodega.fecha_inicio.month == periodo.month:

					factor = arriendo_bodega.valor

			else:
				factor = False

			# calcular valor del vinculo
			if factor is not False:

				if arriendo_bodega.moneda.id == 3:
					valor = configuracion['uf']
				else:
					valor = arriendo_bodega.moneda.moneda_historial_set.all().order_by('-id').first().valor

				if arriendo_bodega.metro_cuadrado is False:
					total += factor * valor
					
				elif arriendo_bodega.metro_cuadrado is True and contrato.bodega is True:
					total += factor * valor * contrato.metros_bodega
				else:
					pass

	return total

def calcular_servicios_varios(contrato, concepto, periodo, configuracion):

	total 		= 0	
	locales 	= contrato.locales.all()

	for local in locales:
		
		if local.gasto_servicio_set.all().filter(mes=periodo.month, anio=periodo.year).exists():
			
			servicios = local.gasto_servicio_set.all().filter(mes=periodo.month, anio=periodo.year)

			for servicio in servicios:

				cantidad_locales = servicio.locales.all().count()
				total 			+= servicio.valor / cantidad_locales

	return total

def calcular_multas(contrato, concepto, periodo, configuracion):

	total 	= 0

	multas 	= Multa.objects.filter(contrato=contrato, mes=periodo.month, anio=periodo.year, visible=True)

	for multa in multas:

		if multa.moneda.id == 3:
			factor = configuracion['uf']
		else:			
			factor = multa.moneda.moneda_historial_set.all().order_by('-id').first().valor

		total += multa.valor * factor

	return total

def calcular_reajuste(contrato, concepto, periodo, total):

	if Reajuste.objects.filter(contrato=contrato, vinculo=concepto).exists():

		if Reajuste.objects.filter(contrato=contrato, vinculo=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo).count() == 1:

			reajuste = Reajuste.objects.get(contrato=contrato, vinculo=concepto, fecha_inicio__lte=periodo, fecha_termino__gte=periodo)
			total = total * (( reajuste.valor /100 ) + 1)

	return total

# API - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class FACTURA(View):

	http_method_names =  ['get', 'delete']

	def get(self, request, id=None):
		if id == None:
			self.object_list = Factura.objects.all()
		else:
			self.object_list = Factura.objects.filter(id=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def delete(self, request, id):

		try:
			factura 		= Factura.objects.get(pk=id)
			factura.visible = False
			factura.save()
			estado 			= True
			mensaje 		= 'eliminado correctamente'
		except Exception as error:
			estado 	= False
			mensaje = str(error)

		return JsonResponse({'estado':estado, 'mensaje':mensaje}, safe=False)
		

	def json_to_response(self):

		data = list()

		for factura in self.object_list:

			estado = {
				'id' 			: factura.estado.id,
				'nombre'		: factura.estado.nombre,
				'color'			: factura.estado.color,
			}

			cliente = {
				'id' 			: factura.contrato.cliente.id,
				'nombre'		: factura.contrato.cliente.nombre,
				'rut'			: factura.contrato.cliente.rut,
				'direccion'		: factura.contrato.cliente.direccion,
				'telefono'		: factura.contrato.cliente.telefono,
			}

			contrato = {
				'id' 			: factura.contrato.id,
				'numero'		: factura.contrato.numero,
				'nombre_local'	: factura.contrato.nombre_local,
				'cliente'		: cliente,
			}

			detalles = list()

			for detalle in factura.factura_detalle_set.filter(visible=True):

				detalles.append({
					'id'		: detalle.id,
					'nombre' 	: detalle.nombre,
					'total'		: formato_moneda_local(self.request, detalle.total),
					})

			# Calculo Neto e IVA.
			valores = calculo_iva_total_documento(factura.total, 19)

			data.append({
				'id'			: factura.id,
				'fecha' 		: factura.creado_en,
				'fecha_inicio'	: factura.fecha_inicio,
				'fecha_termino'	: factura.fecha_termino,
				'neto'			: formato_moneda_local(self.request, valores[0]),
				'iva'			: formato_moneda_local(self.request, valores[1]),
				'total'			: formato_moneda_local(self.request, valores[2]),
				'estado' 		: estado,
				'url_documento' : factura.url_documento,
				'contrato' 		: contrato,
				'detalles' 		: detalles,
				})

		return JsonResponse(data, safe=False)


