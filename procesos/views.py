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
from contrato.models import Contrato, Contrato_Tipo, Arriendo, Arriendo_Detalle, Arriendo_Variable, Gasto_Comun, Servicio_Basico, Cuota_Incorporacion, Fondo_Promocion
from procesos.models import Proceso, Detalle_Arriendo_Minimo, Detalle_Arriendo_Variable, Detalle_Gasto_Comun, Detalle_Electricidad, Detalle_Agua, Detalle_Gas, Detalle_Cuota_Incorporacion, Detalle_Fondo_Promocion
from operaciones.models import Lectura_Electricidad, Lectura_Agua, Lectura_Gas

from django.db.models import Sum, Q
from datetime import datetime, timedelta
import os
import json
import pdfkit

from utilidades.views import primer_dia, ultimo_dia, meses_entre_fechas, sumar_meses, formato_moneda


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
		conceptos 		= var_post.get('conceptos').split(",")

		user 			= User.objects.get(pk=request.user.pk)
		contratos 		= contratos
		f_inicio 		= primer_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y")).date()
		f_termino 		= ultimo_dia(datetime.strptime(fecha_termino, "%d/%m/%Y")).date()
		fecha 			= ultimo_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y")).date()
		meses			= meses_entre_fechas(f_inicio, f_termino)
		data 			= []

		proceso = Proceso(
			fecha_inicio		= f_inicio.strftime('%Y-%m-%d'),
			fecha_termino		= f_termino.strftime('%Y-%m-%d'),
			user				= user,
			proceso_estado_id 	= 1,
		)
		proceso.save()

		for item in conceptos:

			concepto = Concepto.objects.get(id=item)
			proceso.conceptos.add(concepto)
			
			if concepto.id == 1:
				detalle = calculo_arriendo_minimo(request, proceso, contratos, meses, fecha)
			elif concepto.id == 2:
				detalle = calculo_arriendo_variable(request, proceso, contratos, meses, fecha)
			elif concepto.id == 3:
				detalle = calculo_gasto_comun(request, proceso, contratos, meses, fecha)
			elif concepto.id == 4:
				detalle = calculo_servicios_basico(request, proceso, contratos, meses, fecha)
			elif concepto.id == 5:
				detalle = calculo_cuota_incorporacion(request, proceso, contratos, meses, fecha)
			elif concepto.id == 6:
				detalle = calculo_fondo_promocion(request, proceso, contratos, meses, fecha)
			else:
				detalle = []

		return JsonResponse({'id': proceso.id}, safe=False)

	def json_to_response(self):
		data = list()

		for proceso in self.object_list:

			# usuario
			usuario = {
				'id'		:proceso.user.id,
				'first_name':proceso.user.first_name,
				'last_name'	:proceso.user.last_name,
				'email'		:proceso.user.email,
			}

			# conceptos
			conceptos 		= []
			contratos_id 	= []

			for concepto in proceso.conceptos.all():

				conceptos.append({
					'id'		: concepto.id,
					'nombre' 	: concepto.nombre,
					})

				if concepto.id == 1:
					contratos_id += Detalle_Arriendo_Minimo.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 2:
					contratos_id += Detalle_Arriendo_Variable.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 3:
					contratos_id += Detalle_Gasto_Comun.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 4:
					contratos_id += Detalle_Electricidad.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
					contratos_id += Detalle_Agua.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
					contratos_id += Detalle_Gas.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 5:
					contratos_id += Detalle_Cuota_Incorporacion.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 6:
					contratos_id += Detalle_Fondo_Promocion.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				else:
					pass

			contratos = []
			for contrato_id in contratos_id:
				contrato = Contrato.objects.get(id=contrato_id)
				contratos.append({
					'id'		: contrato.id,
					'numero' 	: contrato.numero,
					})


			data.append({
				'id'			: proceso.id,
				'fecha_creacion': proceso.creado_en.strftime('%d/%m/%Y'),
				'fecha_inicio'	: proceso.fecha_inicio.strftime('%d/%m/%Y'),
				'fecha_termino'	: proceso.fecha_termino.strftime('%d/%m/%Y'),
				'estado'		: proceso.proceso_estado.nombre,
				'usuario'		: usuario,
				'conceptos'		: conceptos,
				'contratos'		: contratos,
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
	# concepto 	= var_post['concepto'] {falta: buscar los contratos con estos conceptos}

	fecha_inicio 	= ultimo_dia(datetime.strptime('01/'+mes_inicio+'/'+ano_inicio+'', "%d/%m/%Y"))
	fecha_termino 	= ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+ano_termino+'', "%d/%m/%Y"))
	activo 			= Activo.objects.get(id=activo_id)
	locales 		= activo.local_set.all().values_list('id', flat=True)
	contratos 		= Contrato.objects.filter(locales__in=locales, fecha_habilitacion__lte=fecha_inicio, fecha_termino__gte=fecha_termino, visible=True).distinct() # {falta: buscar por la fecha de activació del contrato}

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



def calculo_arriendo_minimo(request, proceso, contratos, meses, fecha):

	for x in range(meses):

		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle = Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)

					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor 			= detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros 			= metros_total['metros_cuadrados__sum']
						metros_local 	= metros_total['metros_cuadrados__sum']
					else:
						factor 			= detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros 			= 1
						metros_local 	=  None

					valor = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and arriendo.por_meses is False and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):
						reajuste = True

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						total = valor * reajuste_valor

					elif arriendo.reajuste is True and arriendo.por_meses is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						reajuste_factor = int((meses_entre_fechas(arriendo.fecha_inicio, fecha) -1)/arriendo.meses)

						if arriendo.moneda.id == 6:
							reajuste_valor = ((arriendo.valor * reajuste_factor)/100)+1
						else:
							reajuste_valor = (arriendo.valor * reajuste_factor) * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						total = valor * reajuste_valor
						reajuste = True

					else:
						reajuste 		= False
						reajuste_valor 	= None
						total 			= valor

				else:
					valor			= None
					metro_cuadrado	= False
					metros_local    = None
					reajuste		= False
					reajuste_valor	= None
					total 			= None

			except Arriendo.DoesNotExist:
				valor			= None
				metro_cuadrado	= False
				metros_local 	= None
				reajuste		= False
				reajuste_valor	= None
				total 			= None


			Detalle_Arriendo_Minimo(
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

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_arriendo_variable(request, proceso, contratos, meses, fecha):

	for x in range(meses):

		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()

			# cálculo arriendo mínimo {falta: ver que el valor sea del mes anterior}
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)
					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = metros_total['metros_cuadrados__sum']
					else:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = 1

					valor = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and arriendo.por_meses is False and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):
						reajuste = True

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					elif arriendo.reajuste is True and arriendo.por_meses is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						reajuste_factor = int((meses_entre_fechas(arriendo.fecha_inicio, fecha) -1)/arriendo.meses)

						if arriendo.moneda.id == 6:
							reajuste_valor = ((arriendo.valor * reajuste_factor)/100)+1
						else:
							reajuste_valor = (arriendo.valor * reajuste_factor) * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					else:
						arriendo_minimo = valor

				else:
					arriendo_minimo = None

			except Arriendo.DoesNotExist:
				arriendo_minimo = None






			# try:

			# 	arriendos = Arriendo_Variable.objects.filter(contrato=contrato)

			# 	for arriendo_variable in arriendos:

			# 		mes_inicio 		= arriendo_variable.mes_inicio if arriendo_variable.mes_inicio > 9 else '0'+str(arriendo_variable.mes_inicio)
			# 		mes_termino 	= arriendo_variable.mes_termino if arriendo_variable.mes_termino > 9 else '0'+str(arriendo_variable.mes_termino)
			# 		anio_inicio 	= arriendo_variable.anio_inicio
			# 		anio_termino 	= arriendo_variable.anio_termino

			# 		fecha_inicio 	= primer_dia(datetime.strptime('01/'+str(mes_inicio)+'/'+str(anio_inicio), "%d/%m/%Y")).date()
			# 		fecha_termino 	= ultimo_dia(datetime.strptime('01/'+str(mes_termino)+'/'+str(anio_termino), "%d/%m/%Y")).date()
				
			# 		if fecha >= fecha_inicio and fecha <= fecha_termino

				

			# except Exception:
			# 	print ('exception')
			# 	pass
			# 	# valor 	= None
			# 	# ventas 	= None
			# 	# total 	= None


			


			try:

				# print (fecha.month)
				# print (fecha.year)
				existe = Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()


				existe = Arriendo_Variable.objects.filter(contrato=contrato, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()

				# print (existe)

				if existe is True:
					# detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					valor 			= detalle[0].valor
					ventas 			= 0
					ventas_local 	= Venta.objects.filter(local_id__in=locales).\
					extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
					values('year', 'month', 'local_id').\
					annotate(Sum('valor'))

					for venta in ventas_local:
						if fecha.month == venta['month'] and fecha.year == venta['year']:
							ventas += venta['valor__sum']

					if ((ventas * valor) / 100) >= arriendo_minimo and arriendo_minimo is not None:
						total = ((ventas * valor) / 100) - arriendo_minimo
					else:
						total = 0

				else:
					valor 	= None
					ventas 	= None
					total 	= None

			except Exception:
				valor 	= None
				ventas 	= None
				total 	= None

			Detalle_Arriendo_Variable(
				valor 			= valor,
				ventas 			= ventas,
				arriendo_minimo = arriendo_minimo,
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_gasto_comun(request, proceso, contratos, meses, fecha):

	for x in range(meses):
		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
						
			activos 		= contrato.locales.all().values_list('activo_id', flat=True)
			metros_total   	= Local.objects.filter(activo__in=activos, prorrateo=True).aggregate(Sum('metros_cuadrados'))

			for local in locales:

				if Gasto_Comun.objects.filter(contrato=contrato, local=local).exists():
					gasto_comun = Gasto_Comun.objects.filter(contrato=contrato, local=local)
					if gasto_comun[0].prorrateo == True:
						valor 		= gasto_comun[0].valor
						prorrateo 	= True
						try:
							gasto_mensual 	= Gasto_Mensual.objects.get(activo=local.activo, mes=fecha.month, anio=fecha.year).valor
							total 		 	= ((local.metros_cuadrados * gasto_mensual) / metros_total['metros_cuadrados__sum'])*((100+valor))/100

						except Exception:
							gasto_mensual	= None
							total 			= None
					else:
						factor 			= gasto_comun[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						valor 			= gasto_comun[0].valor
						gasto_mensual 	= None
						prorrateo 		= False
						total 			= valor * factor
				else:
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

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_servicios_basico(request, proceso, contratos, meses, fecha):

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
				try:
					if medidor.local.servicio_basico_set.all().exists():
						servicios_basicos = medidor.local.servicio_basico_set.all()
						valor_luz = servicios_basicos[0].valor_electricidad
					else:
						valor_luz	= None
				except Exception:
					valor_luz	= None

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
				try:
					if medidor.local.servicio_basico_set.all().exists():
						servicios_basicos = medidor.local.servicio_basico_set.all()
						valor_agua = servicios_basicos[0].valor_agua
					else:
						valor_agua	= None
				except Exception:
					valor_agua	= None

				Detalle_Agua(
					valor			= valor_agua,
					valor_anterior	= lectura_anterior,
					valor_actual	= lectura_actual,
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
				try:
					if medidor.local.servicio_basico_set.all().exists():
						servicios_basicos = medidor.local.servicio_basico_set.all()
						valor_gas = servicios_basicos[0].valor_gas
					else:
						valor_gas	= None
				except Exception:
					valor_gas	= None

				Detalle_Gas(
					valor			= valor_gas,
					valor_anterior	= lectura_actual,
					valor_actual	= lectura_actual,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso			= proceso,
					contrato		= contrato,
					medidor			= medidor,
				).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_cuota_incorporacion(request, proceso, contratos, meses, fecha):

	for x in range(meses):
		for item in contratos:

			contrato = Contrato.objects.get(id=item)
			
			try:
				existe = Cuota_Incorporacion.objects.filter(contrato=contrato, fecha__year=fecha.year, fecha__month=fecha.month).exists()

				if existe is True:
					cuota_incorporacion = Cuota_Incorporacion.objects.filter(contrato=contrato, fecha__year=fecha.year, fecha__month=fecha.month)

					if cuota_incorporacion[0].metro_cuadrado == True:
						metros_cuadrados = cuota_incorporacion[0].contrato.locales.all().aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
					else:
						metros_cuadrados = 1

					valor 				= cuota_incorporacion[0].valor
					factor 				= cuota_incorporacion[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
					total 				= valor * factor * metros_cuadrados
				else:
					valor 	= None
					factor 	= None
					total 	= None

			except Cuota_Incorporacion.DoesNotExist:
				valor 			= None
				factor 			= None
				total 			= None

			Detalle_Cuota_Incorporacion(
				valor 			= valor,
				factor 			= factor,
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_fondo_promocion(request, proceso, contratos, meses, fecha):

	for x in range(meses):
		for item in contratos:

			contrato = Contrato.objects.get(id=item)

			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)
					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = metros_total['metros_cuadrados__sum']
					else:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = 1

					valor = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and arriendo.por_meses is False and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):
						reajuste = True

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					elif arriendo.reajuste is True and arriendo.por_meses is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						reajuste_factor = int((meses_entre_fechas(arriendo.fecha_inicio, fecha) -1)/arriendo.meses)

						if arriendo.moneda.id == 6:
							reajuste_valor = ((arriendo.valor * reajuste_factor)/100)+1
						else:
							reajuste_valor = (arriendo.valor * reajuste_factor) * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					else:
						arriendo_minimo = valor

				else:
					arriendo_minimo = None

			except Arriendo.DoesNotExist:
				arriendo_minimo = None

			try:
				# existe = Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()
				existe = Arriendo_Variable.objects.filter(contrato=contrato, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()
				if existe is True:
					# detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					valor 			= detalle[0].valor
					ventas 			= 0
					ventas_local 	= Venta.objects.filter(local_id__in=locales).\
					extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
					values('year', 'month', 'local_id').\
					annotate(Sum('valor'))

					for venta in ventas_local:
						if fecha.month == venta['month'] and fecha.year == venta['year']:
							ventas += venta['valor__sum']

					if ((ventas * valor) / 100) >= arriendo_minimo and arriendo_minimo is not None:
						arriendo_reajustable = ((ventas * valor) / 100)
					elif arriendo_minimo is not None:
						arriendo_reajustable = arriendo_minimo
					else:
						arriendo_reajustable = 0

				else:
					arriendo_reajustable 	= None

			except Exception:
				arriendo_reajustable = None

			try:
				fondos_promocion = Fondo_Promocion.objects.filter(contrato=contrato)

				for fondo_promocion in fondos_promocion:
					
					if fondo_promocion.periodicidad == 0:

						mes_1 = sumar_meses(fondo_promocion.fecha, 11)

						try:
							if fecha.month == mes_1.month:
								valor 	= fondo_promocion.valor
								factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
								total 	= valor * factor
							else:
								valor 	= None
								factor 	= None
								total 	= None
							
						except Exception:
							valor 	= None
							factor 	= None
							total 	= None

					elif fondo_promocion.periodicidad == 1:

						mes_1 = sumar_meses(fondo_promocion.fecha, 5)
						mes_2 = sumar_meses(fondo_promocion.fecha, 11)

						try:
							if fecha.month == mes_1.month or fecha.month==mes_2.month:
								valor 	= fondo_promocion.valor
								factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
								total 	= valor * factor
							else:
								valor 	= None
								factor 	= None
								total 	= None
							
						except Exception:
							valor 	= None
							factor 	= None
							total 	= None

					elif fondo_promocion.periodicidad == 2:

						mes_1 = sumar_meses(fondo_promocion.fecha, 3)
						mes_2 = sumar_meses(fondo_promocion.fecha, 7)
						mes_3 = sumar_meses(fondo_promocion.fecha, 11)

						try:
							if fecha.month == mes_1.month or fecha.month==mes_2.month or fecha.month==mes_3.month:
								valor 	= fondo_promocion.valor
								factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
								total 	= valor * factor
							else:
								valor 	= None
								factor 	= None
								total 	= None
						except Exception:
							valor 	= None
							factor 	= None
							total 	= None

					elif fondo_promocion.periodicidad == 3:

						valor 	= fondo_promocion.valor
						factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
						total 	= valor * factor

					else:
						valor 			= None
						factor 			= None
						total 			= None


					if arriendo_reajustable is not None and valor is not None:
						total = (arriendo_reajustable * valor) / 100
					else:
						total = None

					Detalle_Fondo_Promocion(
						valor 			= valor,
						factor 			= factor,
						total 			= total,
						fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
						fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
						proceso 		= proceso,
						contrato 		= contrato,
					).save()

			except Fondo_Promocion.DoesNotExist:

				Detalle_Fondo_Promocion(
					valor 			= None,
					factor 			= None,
					total 			= None,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso 		= proceso,
					contrato 		= contrato,
				).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'



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
			'total'				: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
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
			'total' 			: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
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
			'medidor'			: item.medidor.nombre,
			'lectura_anterior' 	: item.valor_anterior if item.valor_anterior is not None else '---',
			'lectura_actual' 	: item.valor_actual if item.valor_actual is not None else '---',
			'valor' 			: item.valor if item.valor is not None else '---',
			'diferencia'		: (item.valor_actual - item.valor_anterior) if item.valor_anterior is not None and item.valor_actual is not None else '---',
			'total'				: formato_moneda((item.valor_actual - item.valor_anterior) * item.valor) if item.valor_anterior is not None and item.valor_actual is not None and item.valor is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'cliente'			: item.contrato.cliente.nombre,
			'nombre_local'		: item.contrato.nombre_local,
			'local'				: item.medidor.local.nombre,
		})

		total += (item.valor_actual - item.valor_anterior) * item.valor if item.valor_anterior is not None and item.valor_actual is not None and item.valor is not None else 0

	
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
			'proratea' 			: 'si' if item.prorrateo == True else '---',
			'valor' 			: item.valor if item.valor is not None else '---',
			'metros_local' 		: item.local.metros_cuadrados,
			'factor' 			: item.gasto_mensual if item.gasto_mensual is not None else '---',
			'total' 			: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'cliente'			: item.contrato.cliente.nombre,
			'nombre_local'		: item.contrato.nombre_local,
			'local'				: item.local.nombre,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_cuota_incorporacion(proceso):

	data 	= {}
	detalle = []
	total 	= 0
	
	detalles = Detalle_Cuota_Incorporacion.objects.filter(proceso=proceso)

	for item in detalles:

		contrato 	= item.contrato
		locales 	= contrato.locales.all()

		detalle.append({
			'valor'				: item.valor if item.valor is not None else '---',
			'factor'			: item.factor if item.factor is not None else '---',
			'total'				: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
			'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_fondo_promocion(proceso):

	data 	= {}
	detalle = []
	total 	= 0
	
	detalles = Detalle_Fondo_Promocion.objects.filter(proceso=proceso)

	for item in detalles:

		contrato 	= item.contrato
		locales 	= contrato.locales.all()

		detalle.append({
			'valor'				: item.valor if item.valor is not None else '---',
			'factor'			: item.factor if item.factor is not None else '---',
			'total'				: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
			'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data


# funciones globales

def arriendo_minimo_reajustable(contratos, meses, fecha):

	data = list()

	for x in range(meses):

		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle = Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)

					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = metros_total['metros_cuadrados__sum']
					else:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = 1

					valor_arriendo_minimo = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor_arriendo_minimo * reajuste_valor

					else:
						arriendo_minimo = valor_arriendo_minimo

				else:
					arriendo_minimo = 0

			except Arriendo.DoesNotExist:
				arriendo_minimo = 0

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

					arriendo_variable = ((ventas * valor) / 100)

					if arriendo_variable >= arriendo_minimo:
						total = arriendo_variable
					else:
						total = arriendo_minimo

				else:
					valor 			= None
					ventas 			= None
					total 			= None

			except Exception:

				valor 			= None
				ventas 			= None
				total 			= None

			data.append({
				'arriendo_minimo' 	: arriendo_minimo,
				'arriendo_variable' : arriendo_variable,
				'total' 			: total,
				'fecha_inicio'		: primer_dia(fecha).strftime('%Y-%m-%d'),
				'fecha_termino'		: ultimo_dia(fecha).strftime('%Y-%m-%d'),
				'contrato' 			: contrato,
				})

		fecha = sumar_meses(fecha, 1)

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

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/procesos/propuesta_facturacion.html')

	total 		= 0
	detalle 	= []

	for concepto in proceso.conceptos.all():

		if concepto.id == 1:
			data = data_arriendo_minimo(proceso)
			item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.id == 2:
			data = data_arriendo_variable(proceso)
			item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.id == 3:
			data = data_gastos_comunes(proceso)
			item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.id == 4:
			data = data_servicios_basicos(proceso)
			item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.id == 5:
			data = data_cuota_incorporacion(proceso)
			item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.id == 6:
			data = data_fondo_promocion(proceso)
			item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		else:
			print ('error: concepto no definido')

		detalle.append(item)
		total += data['total']

	context = Context({
		'proceso' 	: proceso,
		'detalle' 	: detalle,
		'total'		: formato_moneda(total),
	})

	html 		= template.render(context)
	pdfkit.from_string(html, 'public/media/contratos/propuesta_facturacion.pdf', options=options, css=css)
	pdf 		= open('public/media/contratos/propuesta_facturacion.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=propuesta_facturacion.pdf'
	pdf.close()

	return response






