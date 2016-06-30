# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from accounts.models import UserProfile
from administrador.models import Moneda, Moneda_Historial
from activos.models import Activo
from locales.models import Local

# Create your views here.
@login_required
def dashboard(request):

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

