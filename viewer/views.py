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

from datetime import datetime
from notificaciones.models import Alerta, Alerta_Miembro
import pyrebase

@login_required
def dashboard(request):


	# configuración firebase
	# config = {
	# 	"apiKey": "AIzaSyAj7z483ospf7R-8vGshCjCWcanGJLkwDI",
	# 	"authDomain": "lease-61711.firebaseapp.com",
	# 	"databaseURL": "https://lease-61711.firebaseio.com",
	# 	"storageBucket": "lease-61711.appspot.com",
	# 	"serviceAccount": "lease-5c67010de9d1.json",
	# }

	# # instanciar firebase
	# firebase 	= pyrebase.initialize_app(config)
	# db 			= firebase.database()

	# alertas = Alerta.objects.all()
	# date 	= datetime.now()

	# for alerta in alertas:

	# 	if date >= alerta.fecha:

	# 		alerta_miembros = alerta.alerta_miembro_set.all()

	# 		for alerta_miembro in alerta_miembros:
	# 			if alerta_miembro.estado is False:
					
	# 				# crear alerta firebase
	# 				data = {
	# 					"mensaje"		: alerta.nombre,
	# 					"descripcion"	: alerta.descripcion,
	# 					"emisor"		: alerta.creador.first_name
	# 					}

	# 				db.child("alertas/"+str(alerta_miembro.user.id)).push(data)

	# 				# cambiar estado
	# 				alerta_miembro.estado = True
	# 				alerta_miembro.save()
	# 			else:
	# 				pass
	# 	else:
	# 		pass

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

