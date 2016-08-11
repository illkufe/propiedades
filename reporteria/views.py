from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from accounts.models import UserProfile
from procesos.models import Proceso
from .models import *

from utilidades.views import *


class REPORTES(View):

	http_method_names =  ['get', 'post']

	def get(self, request, id=None):
		
		if id == None:
			self.object_list = Reporte.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
		else:
			self.object_list = Reporte.objects.filter(pk=id)

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			tipos 		= request.user.userprofile.empresa.reporte_tipo_set.all()
			reportes 	= Reporte.objects.filter(empresa=request.user.userprofile.empresa)

			return render(request, 'reporte_list.html', {
				'title' 	: 'Reporteria',
				'href' 		: 'reportes',
				'subtitle'	: 'Reportes',
				'name' 		: 'Lista',
				'tipos' 	: tipos,
				'reportes' 	: reportes,
				})
	
	def post(self, request):

		var_post 	= request.POST.copy()
		estado 		= datos_reporte(request, var_post)

		return JsonResponse({'estado': estado}, safe=False)

	def json_to_response(self):

		data = list()

		for reporte in self.object_list:

			empresa = {
				'id' : reporte.user.userprofile.empresa.id,
			}

			tipo = {
				'nombre' 	: reporte.reporte_tipo.nombre,
				'icono' 	: reporte.reporte_tipo.icono,
				'color' 	: reporte.reporte_tipo.color,
				}

			usuario = {
				'id'			: reporte.user.id,
				'first_name'	: reporte.user.first_name,
				'last_name'		: reporte.user.last_name,
				}

			data.append({
				'id' 			: reporte.id,
				'nombre' 		: reporte.nombre,
				'nombre_pdf' 	: reporte.nombre_pdf,
				'fecha' 		: reporte.creado_en.strftime("%d/%m/%Y"),
				'tipo' 			: tipo,
				'usuario' 		: usuario,
				'empresa' 		: empresa,
				})

		return JsonResponse(data, safe=False)



def datos_reporte(request, var_post):

	default 	= 'reportes/default.html'
	destination = 'public/media/reportes/'

	if int(var_post['tipo']) == 1:
		data = 1
		html = 'reportes/reporte_vacancia_comercial.html'
	elif int(var_post['tipo']) == 2:
		data = 2
		html = 'reportes/reporte_vacancia_comercial.html'
	else:
		return False

	nombre = var_post['nombre'].replace(" ", "_")

	try:

		reporte = Reporte(
			nombre 			= var_post['nombre'],
			nombre_pdf 		= nombre,
			user 			= request.user,
			empresa 		= request.user.userprofile.empresa,
			reporte_tipo_id	= int(var_post['tipo']),
		)

		reporte.save()

		configuration = {
			'default' 		: default,
			'html'			: html,
			'destination'	: destination,
			'nombre_pdf'	: str(reporte.empresa.id)+'_'+str(reporte.id)+'_'+nombre,
			}

		generar_pdf(configuration, data)

		return True

	except Exception as asd:

		return False




def vacancia_por_centro_comercial(request):

	data 	= list()
	empresa = request.user.userprofile.empresa

	return data

