# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
from utilidades.models import Moneda, Moneda_Historial
from activos.models import Activo
from locales.models import Local, Local_Tipo
from contrato.models import Contrato

from datetime import datetime
from django.db.models import Sum, Q
from utilidades.views import *

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






