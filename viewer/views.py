# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
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




















	data 		= {}
	var_post 	= request.POST.copy()

	fecha 		= datetime.strptime(var_post['dia']+'/'+var_post['mes']+'/'+var_post['anio'], "%d/%m/%Y")
	activos 	= Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
	locales 	= Contrato.objects.values_list('locales', flat=True).filter(empresa=request.user.userprofile.empresa, fecha_termino__gt=fecha, visible=True).distinct()

	# chart	
	metros_total 		= Local.objects.filter(activo_id__in=activos, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
	metros_ocupados 	= Local.objects.filter(id__in=locales, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

	metros_total	 	= metros_total if metros_total is not None else 0
	metros_ocupados 	= metros_ocupados if metros_ocupados is not None else 0
	metros_disponibles 	= metros_total - metros_ocupados

	if metros_total == 0:
		ocupado 	= 0
		disponible 	= 0
	else:
		ocupado 	= (metros_ocupados * 100)/metros_total
		disponible 	= (metros_disponibles * 100)/metros_total

	data['chart'] = {'data': [['ocupado', ocupado], ['disponible', disponible]]}

	# table
	tipos 					= Local_Tipo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
	data['table'] 			= {}
	data['table']['data'] 	= list()

	for tipo in tipos:
		metros_total 		= Local.objects.filter(activo_id__in=activos, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
		metros_ocupados 	= Local.objects.filter(id__in=locales, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

		metros_total	 	= metros_total if metros_total is not None else 0
		metros_ocupados 	= metros_ocupados if metros_ocupados is not None else 0
		metros_disponibles 	= metros_total - metros_ocupados

		data['table']['data'].append({'nombre':tipo.nombre, 'metros_totales':metros_total, 'metros_ocupados':metros_ocupados, 'metros_disponibles':metros_disponibles})

	return JsonResponse(data, safe=False)

def chart_ingreso_centro(request):

	data		= {}
	var_post 	= request.POST.copy()

	conceptos = json.loads(var_post['conceptos'])

	if conceptos is '' or conceptos is None:
		conceptos = Concepto.objects.filter(empresa=request.user.userprofile.empresa, visible=True).values_list('id', flat=True)

	activos = Activo.objects.filter(empresa_id=request.user.userprofile.empresa, visible=True)

	data['table'] 			= {}
	data['table']['data'] 	= list()
	data['chart']			= []


	for item in activos:

		locales 		= Local.objects.filter(activo_id=item.id, visible=True)
		contratos 		= Contrato.objects.filter(locales__in=locales)
		total_activo	= Factura.objects.filter(contrato_id__in=contratos, visible=True, factura_detalle__concepto__in=conceptos).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

		total_activo 	= total_activo if total_activo is not None else 0


		data['table']['data'].append({'activo_id': item.id, 'activo': item.nombre, 'totales': formato_moneda_local(request, total_activo) })

		grafico = [item.nombre, total_activo]

		data['chart'].append(grafico)

	return JsonResponse(data, safe=False)


def get_conceptos_activo(request, id):

	var_post 			= request.POST.copy()
	filtro 				= json.loads(var_post['tipo_filtro'])

	nombre_meses 		= ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre',
			 				'Noviembre', 'Diciembre']

	locales 			= Local.objects.filter(activo_id=id, visible=True)
	contratos 			= Contrato.objects.filter(locales__in=locales)
	data_concepto 		= list()
	data_encabezado 	= {}
	data_valor_total 	= {}
	count				= 0
	count_2             = 0
	ano_anterior 		= datetime.now().year - 1
	data_conceptos 		= Concepto.objects.filter(empresa=request.user.userprofile.empresa, visible=True)


	## FILTRO MENSUAL
	if filtro == 0:


		for a in range(1, datetime.now().month + 1):
			data_encabezado[a] = nombre_meses[a - 1]


		for item in data_conceptos:
			meses = {}

			for a in range(1, datetime.now().month + 1):
				total_activo = Factura.objects.filter(contrato_id__in=contratos, visible=True, factura_detalle__concepto_id=item.id,
									   fecha_inicio__month=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

				total_activo 		= total_activo if total_activo is not None else 0
				meses[a] 			= formato_moneda_local(request, total_activo)

			data_concepto.append({
				'concepto': item.nombre,
				'valores': meses,
			})


		for a in range(1, datetime.now().month + 1):

			total_mes 			= Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__month=a)\
										.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

			total_mes 			= total_mes if total_mes is not None else 0
			data_valor_total[a] = formato_moneda_local(request, total_mes)


		## FILTRO TRIMESTRAL
	elif filtro == 1 or filtro ==2:

		if filtro == 1:
			meses 			= ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct','Nov', 'Dic']
			semestral 		= [[1, 3], [4, 6], [7, 9], [10, 12]]
		else:
			semestral 		= [[1, 6], [7, 12]]

		for b in range(ano_anterior, datetime.now().year + 1):
			for a in semestral:
				data_encabezado[count] = str(meses[a[0] - 1]) + '-' + str(b) + '  ' + str(meses[a[1] - 1]) + '-' + str(b)
				count += 1

		for item in data_conceptos:
			aux 	= 0
			anos 	= {}
			for a in range(ano_anterior, datetime.now().year + 1):

				for b in semestral:
					total_activo 	= Factura.objects.filter(contrato_id__in=contratos, visible=True,
														  factura_detalle__concepto_id=item.id, fecha_inicio__year=a,
														  fecha_inicio__month__gte=b[0],
														  fecha_inicio__month__lte=b[1]).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

					total_activo 	= total_activo if total_activo is not None else 0
					anos[aux] 		= formato_moneda_local(request, total_activo)
					aux += 1

			data_concepto.append({
				'concepto' : item.nombre,
				'valores'	: anos,
			})

		for a in range(ano_anterior, datetime.now().year + 1):
			for b in semestral:
				total_mes 					= Factura.objects.filter(contrato_id__in=contratos, visible=True,
																	  fecha_inicio__year=a, fecha_inicio__month__gte=b[0],
																	  fecha_inicio__month__lte=b[1]).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

				total_mes 					= total_mes if total_mes is not None else 0
				data_valor_total[count_2] 	= formato_moneda_local(request ,total_mes)
				count_2 += 1

	## FILTRO ANUAL
	elif filtro == 3:

		while (ano_anterior <= datetime.now().year):
			data_encabezado[count] = ano_anterior

			for item in data_conceptos:
				aux 	= 0
				anos 	= {}
				for a in range(datetime.now().year - 1, datetime.now().year + 1):
					total_activo = Factura.objects.filter(contrato_id__in=contratos, visible=True,
														  factura_detalle__concepto_id=item.id,
														  fecha_inicio__year=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

					total_activo 	= total_activo if total_activo is not None else 0
					anos[aux] 		= formato_moneda_local(request, total_activo)
					aux += 1

				data_concepto.append({
					'concepto': item.nombre,
					'valores': anos,
				})


			for a in range(datetime.now().year - 1, datetime.now().year + 1):
				total_mes 					= Factura.objects.filter(contrato_id__in=contratos, visible=True, fecha_inicio__year=a).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
				total_mes 					= total_mes if total_mes is not None else 0
				data_valor_total[count_2] 	= formato_moneda_local(request, total_mes)
				count_2 += 1

	return JsonResponse({'meses': data_encabezado, 'conceptos': data_concepto, 'total_mes': data_valor_total}, safe=False)


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






