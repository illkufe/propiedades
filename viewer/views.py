# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
from administrador.models import Clasificacion, Clasificacion_Detalle
from conceptos.models import Concepto
from procesos.models import Factura
from utilidades.models import Moneda, Moneda_Historial
from activos.models import Activo
from locales.models import Local, Local_Tipo
from contrato.models import Contrato

from datetime import datetime
from django.db.models import Sum, Q
from utilidades.views import *


import json

nombre_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


@login_required
def dashboard(request):

	if request.user.userprofile.tipo_id == 2:
		return render(request, 'viewer/dashboard_cliente.html')
	else:
		return render(request, 'viewer/dashboard.html')

def flag_currencies(request):

	data 		= []
	currencies 	= []

	currencies.append({'id':1})
	currencies.append({'id':2})
	currencies.append({'id':3})
	currencies.append({'id':4})

	for currency in currencies:

		moneda 		= Moneda.objects.get(id=int(currency['id']))
		historial 	= Moneda_Historial.objects.filter(moneda=moneda).last()

		data.append({
			'id'		: moneda.id,
			'nombre'	: moneda.nombre,
			'abrev'		: moneda.abrev,
			'simbolo'	: moneda.simbolo,
			'value'		: historial.valor,
			})

	return JsonResponse(data, safe=False)

def flag_commercial(request):

	data 		= []
	profile 	= UserProfile.objects.get(user=request.user)
	activos 	= Activo.objects.filter(empresa_id=profile.empresa_id).values_list('id', flat=True)
	locales 	= Local.objects.filter(activo_id__in=activos, visible=True)

	for local in locales:

		data.append({
			'id'		: local.id,
			'nombre'	: local.nombre,
			'activo'	: local.activo.nombre,
			})

	return JsonResponse(data, safe=False)


def chart_vacancia(request):

	response 	= list()
	var_post 	= request.POST.copy()
	fecha 		= datetime.strptime(str(var_post['fecha']), "%d/%m/%Y")
	activos 	= Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

	for activo in activos:

		m_totales 	= activo.local_set.all().filter(visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
		locales 	= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gt=fecha, visible=True)
		m_ocupados 	= Local.objects.filter(id__in=locales, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

		m_totales 	= m_totales if m_totales is not None else 0
		m_ocupados 	= m_ocupados if m_ocupados is not None else 0

		response.append({
			'id'			: activo.id,
			'codigo'		: activo.codigo,
			'nombre'		: activo.nombre,
			'm_totales'		: m_totales,
			'm_ocupados'	: m_ocupados,
			'm_disponibles'	: m_totales - m_ocupados,
			})

	return JsonResponse(response, safe=False)


def chart_vacancia(request):

	response 	= list()
	var_post 	= request.POST.copy()
	fecha 		= datetime.strptime(str(var_post['fecha']), "%d/%m/%Y")
	activos 	= Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

	for activo in activos:

		m_totales 	= activo.local_set.all().filter(visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
		locales 	= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gt=fecha, visible=True)
		m_ocupados 	= Local.objects.filter(id__in=locales, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

		m_totales 	= m_totales if m_totales is not None else 0
		m_ocupados 	= m_ocupados if m_ocupados is not None else 0

		response.append({
			'id'			: activo.id,
			'codigo'		: activo.codigo,
			'nombre'		: activo.nombre,
			'm_totales'		: m_totales,
			'm_ocupados'	: m_ocupados,
			'm_disponibles'	: m_totales - m_ocupados,
			})

	return JsonResponse(response, safe=False)

def chart_vacancia_tipo(request):

	response 	= list()

	var_post 	= request.POST.copy()
	fecha 		= datetime.strptime(str(var_post['fecha']), "%d/%m/%Y")
	activo 		= Activo.objects.get(id=int(var_post['id']))
	indice 		= int(var_post['tipo'])

	if indice == 1:

		tipos 	= Local_Tipo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
		locales = Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gt=fecha, visible=True)

		for tipo in tipos:

			m_totales 	= Local.objects.filter(activo=activo, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m_ocupados 	= Local.objects.filter(id__in=locales, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m_totales 	= m_totales if m_totales is not None else 0
			m_ocupados 	= m_ocupados if m_ocupados is not None else 0

			response.append({
				'id'			: tipo.id,
				'nombre'		: tipo.nombre,
				'm_totales'		: m_totales,
				'm_ocupados'	: m_ocupados,
				'm_disponibles'	: m_totales - m_ocupados,
				})

	elif indice == 2:

		niveles = activo.nivel_set.all()
		locales = Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gt=fecha, visible=True)

		for nivel in niveles:

			m_totales 	= Local.objects.filter(activo=activo, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m_ocupados 	= Local.objects.filter(id__in=locales, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m_totales 	= m_totales if m_totales is not None else 0
			m_ocupados 	= m_ocupados if m_ocupados is not None else 0

			response.append({
				'id'			: nivel.id,
				'nombre'		: nivel.nombre,
				'm_totales'		: m_totales,
				'm_ocupados'	: m_ocupados,
				'm_disponibles'	: m_totales - m_ocupados,
				})
	elif indice == 3:

		sectores 	= activo.sector_set.all()
		locales 	= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gt=fecha, visible=True)

		for sector in sectores:

			m_totales 	= Local.objects.filter(activo=activo, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m_ocupados 	= Local.objects.filter(id__in=locales, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m_totales 	= m_totales if m_totales is not None else 0
			m_ocupados 	= m_ocupados if m_ocupados is not None else 0

			response.append({
				'id'			: sector.id,
				'nombre'		: sector.nombre,
				'm_totales'		: m_totales,
				'm_ocupados'	: m_ocupados,
				'm_disponibles'	: m_totales - m_ocupados,
				})
	else:
		pass

	return JsonResponse(response, safe=False)

def chart_ingreso_centro(request):

	data_table	= {}
	var_post 	= request.POST.copy()
	conceptos 	= json.loads(var_post['conceptos'])

	if conceptos is '' or conceptos is None:
		conceptos = Concepto.objects.filter(empresa=request.user.userprofile.empresa, visible=True).values_list('id', flat=True)

	activos = Activo.objects.filter(empresa_id=request.user.userprofile.empresa, visible=True)

	data_table['table'] 		= {}
	data_table['table']['data'] = list()
	data_table['chart']			= list()
	data_table['fechas'] 		= list()

	## Data Grafico
	response = calcular_periodos(1, 6, 'restar')

	data_table['fechas'].append(response[0]['fecha_inicio'])
	data_table['fechas'].append(response[response.__len__() -1]['fecha_termino'])

	cabecera = []
	cabecera.append('x')
	for data in response:
		fecha = data['fecha_inicio']
		cabecera.append(fecha)

	data_table['chart'].append(cabecera)

	for activo in activos:
		cabecera = []
		cabecera.append(activo.nombre)
		for data in response:
			locales 		= Local.objects.filter(activo=activo, visible=True)
			contratos 		= Contrato.objects.filter(locales__in=locales)
			total_activo 	= Factura.objects.filter(contrato_id__in=contratos, visible=True,
													 fecha_inicio__gte=data['fecha_inicio'], fecha_inicio__lte=data['fecha_termino'],
													 factura_detalle__concepto__in=conceptos).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

			total_activo 	= total_activo if total_activo is not None else 0
			cabecera.append(total_activo)
		data_table['chart'].append(cabecera)

	## Data Tabla
	for item in activos:

		locales 		= Local.objects.filter(activo_id=item.id, visible=True)
		contratos 		= Contrato.objects.filter(locales__in=locales)
		total_activo	= Factura.objects.filter(contrato_id__in=contratos,fecha_inicio__gte=response[0]['fecha_inicio'], fecha_inicio__lte=response[response.__len__() -1]['fecha_termino'], visible=True, factura_detalle__concepto__in=conceptos).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

		total_activo 	= total_activo if total_activo is not None else 0

		data_table['table']['data'].append({'activo_id': item.id, 'activo': item.nombre, 'totales': formato_moneda_local(request, total_activo) })

	return JsonResponse(data_table, safe=False)

def get_conceptos_activo(request, id):

	var_post 			= request.POST.copy()
	tipo_periodo    	= json.loads(var_post['tipo_filtro'])


	locales 			= Local.objects.filter(activo_id=id, visible=True)
	contratos 			= Contrato.objects.filter(locales__in=locales)
	data_concepto 		= list()
	data_encabezado 	= {}
	data_valor_total 	= {}
	count				= 0

	data_conceptos 		= Concepto.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
	response 			= calcular_periodos(tipo_periodo, 6, 'restar')

	## Se obtiene Cabecera de las tablas
	for data in response:

		if tipo_periodo == 1:
			data_encabezado[count] = str(nombre_meses[data['fecha_inicio'].month - 1][:3]) + '-' + str(data['fecha_inicio'].year)
		elif tipo_periodo == 2 or tipo_periodo == 3:
			data_encabezado[count] = str(
				str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year) + '  ' + str(
					nombre_meses[data['fecha_termino'].month - 1])[:3] + '-' + str(data['fecha_termino'].year))
		elif tipo_periodo == 4:
			data_encabezado[count] = 'Año ' + str(data['fecha_inicio'].year)

		count += 1

	for item in data_conceptos:
		meses 	= {}
		aux     = 0

		for data in response:
			total_activo = Factura.objects.filter(contrato_id__in=contratos, visible=True, factura_detalle__concepto_id=item.id,
												  fecha_inicio__gte=data['fecha_inicio'],
												  fecha_inicio__lte=data['fecha_termino']).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

			total_activo 	= total_activo if total_activo is not None else 0
			if tipo_periodo == 1:

				nombre_cabecera = str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year)
				meses[aux] 		= [nombre_cabecera, formato_moneda_local(request, total_activo)]

			elif tipo_periodo == 2 or tipo_periodo == 3:

				nombre_cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1])[:3] + '-' + str(data['fecha_termino'].year))
				meses[aux] 		= [nombre_cabecera, formato_moneda_local(request, total_activo)]
			elif tipo_periodo == 4:

				nombre_cabecera ='Año ' + str(data['fecha_inicio'].year),
				meses[aux]		= [nombre_cabecera, formato_moneda_local(request, total_activo)]

			aux +=1

		data_concepto.append({
			'concepto': item.nombre,
			'valores': meses,
		})

	for data in response:
		total_mes = Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__gte=data['fecha_inicio'],fecha_inicio__lte=data['fecha_termino']).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

		total_mes = total_mes if total_mes is not None else 0

		if tipo_periodo == 1:

			nombre_cabecera 					= str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year)
			data_valor_total[nombre_cabecera] 	= formato_moneda_local(request, total_mes)

		elif tipo_periodo == 2 or tipo_periodo == 3:

			nombre_cabecera 					= str(str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1])[:3] + '-' + str(data['fecha_termino'].year))
			data_valor_total[nombre_cabecera] 	= formato_moneda_local(request, total_mes)

		elif tipo_periodo == 4:

			nombre_cabecera 					= 'Año ' + str(data['fecha_inicio'].year),
			data_valor_total[nombre_cabecera] 	= formato_moneda_local(request, total_mes)


	return JsonResponse({'meses': data_encabezado, 'conceptos': data_concepto, 'total_mes': data_valor_total}, safe=False)


def chart_ingreso_clasificacion(request):

	#variables
	data_table 					= {}
	data_table['table'] 		= {}
	data_table['table']['data'] = list()
	data_table['chart']			= list()
	data_table['fechas'] 		= list()

	data_locales 				= []

	activos 			= request.user.userprofile.empresa.activo_set.all().values_list('id', flat=True)
	periodos 			= calcular_periodos(1, 6, 'restar')
	contratos 			= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

	data_table['fechas'].append(periodos[0]['fecha_inicio'])
	data_table['fechas'].append(periodos[periodos.__len__() -1]['fecha_termino'])

	cabecera = []
	cabecera.append('x')
	## Se obtiene Cabecera de las tablas
	for periodo in periodos:
		cabecera.append(periodo['fecha_inicio'])

	data_table['chart'].append(cabecera)

	##Obtengo todos lo locales y el primero si es que existen mas de 2 en el contrato
	for item_contrato in contratos:
		if item_contrato.locales.all().first().id not in data_locales:
			data_locales.append(item_contrato.locales.all().first().id)

	## Se total de clasificaciones
	clasificaciones = Clasificacion.objects.filter(empresa=request.user.userprofile.empresa, visible=True, tipo_clasificacion_id=1).order_by('nombre')

	for clasificacion in clasificaciones:

		det_clasificaciones = Clasificacion_Detalle.objects.filter(clasificacion=clasificacion)
		locales 			= Local.objects.filter(visible=True, activo__in=activos, id__in=data_locales, clasificaciones__in=det_clasificaciones).values_list('id', flat=True)
		contratos 			= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True, locales__in=locales)

		cabecera 			= []
		cabecera.append(clasificacion.nombre)
		for periodo in periodos:

			total_clasificacion = Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__gte=periodo['fecha_inicio'], fecha_inicio__lte=periodo['fecha_termino']).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

			cabecera.append(format_number(request, 0, True) if total_clasificacion is None else format_number(request, total_clasificacion, True))
		data_table['chart'].append(cabecera)

	for clasificacion in clasificaciones:

		det_clasificaciones = Clasificacion_Detalle.objects.filter(clasificacion=clasificacion)
		locales 			= Local.objects.filter(visible=True, activo__in=activos, id__in=data_locales, clasificaciones__in=det_clasificaciones).values_list('id', flat=True)
		contratos 			= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True, locales__in=locales)
		total_clasificacion = Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__gte=periodos[0]['fecha_inicio'], fecha_inicio__lte=periodos[periodos.__len__() -1]['fecha_termino']).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

		data_table['table']['data'].append({'id': clasificacion.id, 'clasificacion': clasificacion.nombre, 'totales': format_number(request, 0, True) if total_clasificacion is None else format_number(request, total_clasificacion, True)})

	return JsonResponse(data_table, safe=False)

def get_detalle_clasificacion(request, id):
	#variables

	count 				= 0
	data_clasificacion 	= list()
	data_cabecera 		= {}
	data_locales 		= []

	activos 			= request.user.userprofile.empresa.activo_set.all().values_list('id', flat=True)
	periodos 			= calcular_periodos(1, 6, 'restar')
	contratos 			= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True)


	## Se obtiene Cabecera de las tablas
	for periodo in periodos:
		data_cabecera[count] = str(nombre_meses[periodo['fecha_inicio'].month - 1]) + ' ' + str(periodo['fecha_inicio'].year)
		count += 1

	##Obtengo todos lo locales y el primero si es que existen mas de 2 en el contrato
	for item_contrato in contratos:
		if item_contrato.locales.all().first().id not in data_locales:
			data_locales.append(item_contrato.locales.all().first().id)

	## Se total de clasificaciones
	clasificaciones 	= Clasificacion.objects.filter(id=id, empresa=request.user.userprofile.empresa, visible=True, tipo_clasificacion_id=1).order_by('nombre')
	det_clasificaciones = Clasificacion_Detalle.objects.filter(clasificacion__in=clasificaciones)
	for detalle in det_clasificaciones:

		locales 	= Local.objects.filter(visible=True, activo__in=activos, id__in=data_locales, clasificaciones=detalle).values_list('id', flat=True)
		contratos 	= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True, locales__in=locales)
		meses 		= {}
		aux 		= 0

		for periodo in periodos:

			total_clasificacion = Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__gte=periodo['fecha_inicio'], fecha_inicio__lte=periodo['fecha_termino']).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
			nom_cabecera 		= str(nombre_meses[periodo['fecha_inicio'].month - 1]) + ' ' + str(periodo['fecha_inicio'].year)

			meses[aux] 			= [nom_cabecera, format_number(request, 0, True) if total_clasificacion is None else format_number(request, total_clasificacion, True)]
			aux += 1

		data_clasificacion.append({
			'detalles'	: detalle.nombre,
			'valores'	: meses,
		})

	return JsonResponse({'meses': data_cabecera, 'conceptos': data_clasificacion}, safe=False)

def data_ingreso_metros(request, id=None):

	data 		= list()
	activos 	= Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
	periodos 	= calcular_periodos(1, 6, 'restar')

	for activo in activos:

		locales 	= Local.objects.filter(activo=activo, visible=True)
		metros 		= locales.all().aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
		contratos 	= Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, visible=True)

		data_periodos = list()

		for periodo in periodos:

			total = Factura.objects.filter(contrato__in=contratos, visible=True,fecha_inicio__gte=periodo['fecha_inicio'],fecha_inicio__lte=periodo['fecha_termino']).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

			data_periodos.append({
				'fecha_inicio'		: periodo['fecha_inicio'],
				'fecha_termino'		: periodo['fecha_termino'],
				# 'ingreso' 			: formato_moneda_local(request, 0) if total is None else formato_moneda_local(request, total),
				# 'ingreso_metros' 	: formato_moneda_local(request, 0) if total is None else formato_moneda_local(request, (total / metros)),

				'ingreso' 			: format_number(request, 0, True) if total is None else format_number(request, total, True),
				'ingreso_metros' 	: format_number(request, 0, True) if total is None else format_number(request, (total / metros), True),
				})

		data.append({
			'id'		: activo.id,
			'nombre'	: activo.nombre,
			'metros'	: metros,
			'periodos'	: data_periodos,
			})

	return JsonResponse(data, safe=False)



class CONCEPTOS_ACTIVOS(View):

	http_method_names = ['get', 'post']

	def get(self, request, id=None):
		if id == None:
			self.object_list = Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		else:
			self.object_list = Activo.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def post(self, request, id=None):

		var_post 	= request.POST.copy()
		filtro 		= json.loads(var_post['tipo_filtro'])

		meses 		= ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
				 		'Noviembre', 'Diciembre']

		# 0	> Mensual
		if filtro == 0:

			data_meses = {}
			for a in range(1, datetime.now().month + 1):
				data_meses[a] = meses[a - 1]

			locales 	= Local.objects.filter(activo_id=id, visible=True)
			contratos 	= Contrato.objects.filter(locales__in=locales)
			concepto 	= list()

			data_conceptos = Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

			for item in data_conceptos:
				mes = {}
				for a in range(1, datetime.now().month + 1):
					total_activo 	= Factura.objects.filter(contrato_id__in=contratos, visible=True, factura_detalle__concepto_id=item.id, fecha_inicio__month=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					total_activo 	= total_activo if total_activo is not None else 0
					mes[a] 			= formato_moneda_local(self.request, total_activo)

				concepto.append({
					'concepto' : item.nombre,
					'valores'	: mes,
				})

			data_total_meses = {}
			for a in range(1, datetime.now().month + 1):
				total_mes 			= Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__month=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
				total_mes 			= total_mes if total_mes is not None else 0
				data_total_meses[a] = formato_moneda_local(self.request ,total_mes)

			return JsonResponse({'meses': data_meses ,'conceptos' : concepto, 'total_mes': data_total_meses}, safe=False)

		# 1	> Trimestral
		elif filtro == 1:
			ano_anterior 	= datetime.now().year -1
			data_encabezado = {}
			count 			= 0
			meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct',
					 'Nov', 'Dic']

			semestral = [[1, 3], [4, 6], [7, 9], [10, 12]]

			for b in range(datetime.now().year - 1, datetime.now().year + 1):
				for a in semestral:
					data_encabezado[count] = str(meses[a[0] -1]) +'-'+ str(b) +'  ' +str(meses[a[1] -1]) +'-'+ str(b)
					count += 1


			locales 		= Local.objects.filter(activo_id=id, visible=True)
			contratos 		= Contrato.objects.filter(locales__in=locales)
			concepto 		= list()
			data_conceptos 	= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

			for item in data_conceptos:
				aux = 0
				anos = {}
				for a in range(datetime.now().year - 1, datetime.now().year + 1):

					for b in semestral:
						total_activo 	= Factura.objects.filter(contrato_id__in=contratos, visible=True, factura_detalle__concepto_id=item.id, fecha_inicio__year=a, fecha_inicio__month__gte=b[0], fecha_inicio__month__lte=b[1]).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
						total_activo 	= total_activo if total_activo is not None else 0
						anos[aux] 		= formato_moneda_local(self.request, total_activo)
						aux += 1
				concepto.append({
					'concepto' 	: item.nombre,
					'valores'	: anos,
				})
			aux2 			= 0
			data_total_ano 	= {}
			for a in range(datetime.now().year - 1, datetime.now().year + 1):
				for b in semestral:
					total_mes 				= Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__year=a, fecha_inicio__month__gte=b[0], fecha_inicio__month__lte=b[1]).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					total_mes 				= total_mes if total_mes is not None else 0
					data_total_ano[aux2] 	= formato_moneda_local(self.request ,total_mes)
					aux2 +=1
			count +=1
			ano_anterior +=1

			return JsonResponse({'meses': data_encabezado ,'conceptos' : concepto, 'total_mes': data_total_ano}, safe=False)
		# 2	> Semestral
		elif filtro == 2:
			ano_anterior 	= datetime.now().year -1
			data_encabezado = {}
			count 			= 0

			semestral = [[1, 6], [7, 12]]

			for b in range(datetime.now().year - 1, datetime.now().year + 1):
				for a in semestral:
					data_encabezado[count] = str(meses[a[0] -1]) +'-'+ str(b) +'  ' +str(meses[a[1] -1]) +'-'+ str(b)
					count += 1


			locales 		= Local.objects.filter(activo_id=id, visible=True)
			contratos 		= Contrato.objects.filter(locales__in=locales)
			concepto 		= list()
			data_conceptos 	= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

			for item in data_conceptos:
				aux = 0
				anos = {}
				for a in range(datetime.now().year - 1, datetime.now().year + 1):

					for b in semestral:
						total_activo 	= Factura.objects.filter(contrato_id__in=contratos, visible=True, factura_detalle__concepto_id=item.id, fecha_inicio__year=a, fecha_inicio__month__gte=b[0], fecha_inicio__month__lte=b[1]).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
						total_activo 	= total_activo if total_activo is not None else 0
						anos[aux] 		= formato_moneda_local(self.request, total_activo)
						aux += 1
				concepto.append({
					'concepto' 	: item.nombre,
					'valores'	: anos,
				})
			aux2 			= 0
			data_total_ano 	= {}
			for a in range(datetime.now().year - 1, datetime.now().year + 1):
				for b in semestral:
					total_mes 				= Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__year=a, fecha_inicio__month__gte=b[0], fecha_inicio__month__lte=b[1]).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					total_mes 				= total_mes if total_mes is not None else 0
					data_total_ano[aux2] 	= formato_moneda_local(self.request ,total_mes)
					aux2 +=1
			count +=1
			ano_anterior +=1

			return JsonResponse({'meses': data_encabezado ,'conceptos' : concepto, 'total_mes': data_total_ano}, safe=False)
		# 3	> Anual
		elif filtro == 3:
			ano_anterior = datetime.now().year -1

			data_encabezado = {}
			count = 0
			while(ano_anterior <= datetime.now().year):
				data_encabezado[count] = ano_anterior

				locales 		= Local.objects.filter(activo_id=id, visible=True)
				contratos 		= Contrato.objects.filter(locales__in=locales)
				concepto 		= list()
				data_conceptos 	= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

				for item in data_conceptos:
					aux 	= 0
					anos 	= {}
					for a in range(datetime.now().year - 1, datetime.now().year + 1):
						total_activo 	= Factura.objects.filter(contrato_id__in=contratos, visible=True, factura_detalle__concepto_id=item.id, fecha_inicio__year=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
						total_activo 	= total_activo if total_activo is not None else 0
						anos[aux] 		= formato_moneda_local(self.request, total_activo)
						aux += 1

					concepto.append({
						'concepto' : item.nombre,
						'valores'	: anos,
					})
				aux2 			= 0
				data_total_ano 	= {}
				for a in range(datetime.now().year - 1, datetime.now().year + 1):
					total_mes 				= Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__year=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					total_mes 				= total_mes if total_mes is not None else 0
					data_total_ano[aux2] 	= formato_moneda_local(self.request ,total_mes)
					aux2 +=1
				count +=1
				ano_anterior +=1

			return JsonResponse({'meses': data_encabezado ,'conceptos' : concepto, 'total_mes': data_total_ano}, safe=False)


	def json_to_response(self):
		data = {}
		data['table'] = list()

		meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
				 'Noviembre', 'Diciembre']

		data_meses = {}
		for a in range(1, datetime.now().month + 1):
			data_meses [a] = meses[a - 1]

		for activo in self.object_list:

			locales 	= Local.objects.filter(activo_id=activo.id, visible=True)
			contratos 	= Contrato.objects.filter(locales__in=locales)
			concepto    = list()

			data_conceptos = Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

			for item in data_conceptos:
				mes 			= {}
				for a in range(1, datetime.now().month + 1):

					total_activo 	= Factura.objects.filter(contrato_id__in=contratos, visible=True,factura_detalle__concepto_id=item.id, fecha_inicio__month=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					total_activo 	= total_activo if total_activo is not None else 0
					mes[a] 			= formato_moneda_local(self.request, total_activo)

				concepto.append({
					'concepto' 	: item.nombre,
					'valores'	: mes,
				})

		data_total_meses = {}
		for a in range(1, datetime.now().month + 1):
			total_mes = Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__month=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
			total_mes = total_mes if total_mes is not None else 0
			data_total_meses[a] = formato_moneda_local(self.request,total_mes)

		return JsonResponse({'meses': data_meses,'conceptos' : concepto, 'total_mes': data_total_meses}, safe=False)












def activos_garantias(request, id=None):

	response = list()

	if id == None:
		activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
	else:
		activos = Activo.objects.filter(id=id)


	for activo in activos:

		total_activo 	= 0
		locales 		= list()

		for local in activo.local_set.filter(visible=True):

			total_local = 0
			garantias 	= list()

			for garantia in local.garantia_set.filter(visible=True):

				valor = (garantia.valor * garantia.moneda.moneda_historial_set.all().order_by('-id').first().valor)

				total_local 	+= valor
				total_activo 	+= valor

				garantias.append({
					'id' 		: garantia.id,
					'nombre' 	: garantia.nombre,
					'total'		: format_number(request, valor, True)
				})

			locales.append({
				'id'  		: local.id,
				'nombre' 	: local.nombre,
				'garantias' : garantias,
				'total'		: format_number(request, total_local, True)
				})

		response.append({
			'id'		: activo.id,
			'nombre'	: activo.nombre,			
			'locales' 	: locales,
			'total'		: format_number(request, total_activo, True)
			})

	return JsonResponse(response, safe=False)



