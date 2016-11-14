
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from django.db.models import Sum
from accounts.models import UserProfile
from contrato.models import Contrato
from procesos.models import Factura
from reporteria.forms import *
from .models import *
from datetime import datetime
from utilidades.views import *

import io
import time
import xlsxwriter


class REPORTES(View):

	http_method_names =  ['get', 'post']

	def get(self, request, id=None):
		
		if id == None:
			self.object_list = Reporte_Tipo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)
		else:
			self.object_list = Reporte_Tipo.objects.filter(pk=id)

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			# tipos 		= request.user.userprofile.empresa.reporte_tipo_set.all()
			# reportes 	= Reporte_Tipo.objects.filter(empresa=request.user.userprofile.empresa)

			return render(request, 'reporte_list.html', {
				'title' 	: 'Reporteria',
				'href' 		: 'reportes',
				'subtitle'	: 'Reportes',
				'name' 		: 'Lista',
				'tipos' 	: '',
				'reportes' 	: '',
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

		# reporte = Reporte(
		# 	nombre 			= var_post['nombre'],
		# 	nombre_pdf 		= nombre,
		# 	user 			= request.user,
		# 	empresa 		= request.user.userprofile.empresa,
		# 	reporte_tipo_id	= int(var_post['tipo']),
		# )
        #
		# reporte.save()

		configuration = {
			'default' 		: default,
			'html'			: html,
			'destination'	: destination,
			# 'nombre_pdf'	: str(reporte.empresa.id)+'_'+str(reporte.id)+'_'+nombre,
			}

		generar_pdf(configuration, data)

		return True

	except Exception as asd:

		return False

def vacancia_por_centro_comercial(request):

	data 	= list()
	empresa = request.user.userprofile.empresa

	return data


class REPORTE_INGRESO_ACTIVO(View):
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			return render(request, 'reportes/reporte_ingreso_activo.html', {
				'title' 	: 'Reporteria',
				'href' 		: 'reportes',
				'subtitle'	: 'Reportes',
				'name' 		: 'Ingreso Activos',
				'form'		: FiltroIngresoActivo(request=self.request)
			})

	def post(self, request):

		var_post 		= request.POST.copy()

		nombre_meses 	= ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
							'Octubre', 'Noviembre', 'Diciembre']

		data_cabecera 	= {}
		data_concepto 	= list()
		count 			= 0
		count_2 		= 0
		ano_anterior 	= datetime.now().year - int(var_post['cantidad_periodos'])

		if int(var_post['periodos']) == 0:

			fecha_inicial = sumar_meses(datetime.now(), -int(var_post['cantidad_periodos']) )

			while fecha_inicial < datetime.now().date():
				dias 					= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
				fecha_inicial 			+= timedelta(days=dias)
				data_cabecera[count] 	= str(nombre_meses[fecha_inicial.month -1]) + ' '+str(fecha_inicial.year)
				count 					+=1


			if var_post['activo'] != '':
				activos = Activo.objects.filter(id=int(var_post['activo']), empresa=request.user.userprofile.empresa, visible=True)
			else:
				activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)


			for activo in activos:

				locales 	= Local.objects.filter(activo_id=activo.id, visible=True)

				if var_post['cliente'] !='':
					contratos 	= Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, cliente_id=int(var_post['cliente']), visible=True)
				else:
					contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, visible=True)

				for contrato in contratos:
					meses 			= {}
					aux   			= 0
					fecha_inicial 	= sumar_meses(datetime.now(), -int(var_post['cantidad_periodos']))
					dias 			= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
					fecha_inicial 	+= timedelta(days=dias)
					while fecha_inicial <= datetime.now().date():

						if var_post['conceptos'] != '':
							total_activo 	= Factura.objects.filter(contrato_id=contrato.id, visible=True, factura_detalle__concepto_id=int(var_post['conceptos']),
																	  fecha_inicio__month=fecha_inicial.month,
																	  fecha_inicio__year=fecha_inicial.year)\
											.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
						else:
							total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  fecha_inicio__month=fecha_inicial.month,
																  fecha_inicio__year=fecha_inicial.year) \
								.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

						total_activo 	= total_activo if total_activo is not None else 0
						meses[aux] 		= [str(nombre_meses[fecha_inicial.month -1]) + ' '+str(fecha_inicial.year), formato_moneda_local(request, total_activo)]

						dias 			= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
						fecha_inicial  += timedelta(days=dias)
						aux			   += 1

					data_concepto.append({
						'activo' 	: activo.nombre,
						'cliente'	: contrato.cliente.nombre,
						'contrato'  : contrato.numero,
						'valores'	: meses
					})

		#TREMESTRAL O SEMESTRAL
		elif int(var_post['periodos']) == 1 or int(var_post['periodos']) == 2:

			if int(var_post['periodos']) == 1:
				nombre_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct', 'Nov', 'Dic']
				semestral = [[1, 3], [4, 6], [7, 9], [10, 12]]
			else:
				semestral = [[1, 6], [7, 12]]

			for ano in range(ano_anterior, datetime.now().year + 1):
				for semestre in semestral:
					data_cabecera[count] = str(nombre_meses[semestre[0] - 1]) + '-' + str(ano) + '  ' + str(nombre_meses[semestre[1] - 1]) + '-' + str(ano)
					count 				+= 1

			if var_post['activo'] != '':
				activos = Activo.objects.filter(id=int(var_post['activo']),
												empresa=request.user.userprofile.empresa, visible=True)
			else:
				activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

			for activo in activos:

				locales = Local.objects.filter(activo_id=activo.id, visible=True)

				if var_post['cliente'] != '':
					contratos = Contrato.objects.filter(locales__in=locales,
														empresa=request.user.userprofile.empresa,
														cliente_id=int(var_post['cliente']), visible=True)
				else:
					contratos = Contrato.objects.filter(locales__in=locales,
														empresa=request.user.userprofile.empresa, visible=True)

				for contrato in contratos:
					meses 	= {}
					aux 	= 0
					for ano in range(ano_anterior, datetime.now().year + 1):
						for semestre in semestral:
							if var_post['conceptos'] != '':
								total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  	factura_detalle__concepto_id=int(var_post['conceptos']),
																	fecha_inicio__month__gte=semestre[0],
																	fecha_inicio__month__lte=semestre[1],
																  	fecha_inicio__year=ano)\
											.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
							else:
								total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																	  fecha_inicio__month__gte=semestre[0],
																	  fecha_inicio__month__lte=semestre[1],
																	  fecha_inicio__year=ano) \
									.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

							total_activo 	= total_activo if total_activo is not None else 0
							meses[aux] 		= [str(str(nombre_meses[semestre[0] - 1]) + '-' + str(ano) + '  ' + str(nombre_meses[semestre[1] - 1]) + '-' + str(ano)), formato_moneda_local(request, total_activo)]
							aux 			+= 1

					data_concepto.append({
						'activo' 	: activo.nombre,
						'cliente'	: contrato.cliente.nombre,
						'contrato'  : contrato.numero,
						'valores'	: meses
					})
		#ANUAL
		elif int(var_post['periodos']) == 3:


			for ano in range(ano_anterior, datetime.now().year + 1):
				data_cabecera[count] = 'Año ' + str(ano)
				count += 1

			if var_post['activo'] != '':
				activos = Activo.objects.filter(id=int(var_post['activo']),
												empresa=request.user.userprofile.empresa, visible=True)
			else:
				activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

			for activo in activos:

				locales = Local.objects.filter(activo_id=activo.id, visible=True)

				if var_post['cliente'] != '':
					contratos = Contrato.objects.filter(locales__in=locales,
														empresa=request.user.userprofile.empresa,
														cliente_id=int(var_post['cliente']), visible=True)
				else:
					contratos = Contrato.objects.filter(locales__in=locales,
														empresa=request.user.userprofile.empresa, visible=True)

				for contrato in contratos:
					meses 	= {}
					aux 	= 0
					for ano in range(ano_anterior, datetime.now().year + 1):
						if var_post['conceptos'] != '':
							total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  factura_detalle__concepto_id=int(
																	  var_post['conceptos']),
																  fecha_inicio__year=ano) \
								.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
						else:
							total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  fecha_inicio__year=ano) \
								.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

						total_activo 	= total_activo if total_activo is not None else 0
						meses[aux] 		= ['Año ' + str(ano), formato_moneda_local(request, total_activo)]
						aux            += 1

					data_concepto.append({
						'activo'	: activo.nombre,
						'cliente'	: contrato.cliente.nombre,
						'contrato'	: contrato.numero,
						'valores'	: meses
					})

		return JsonResponse({'cabecera': data_cabecera, 'data':data_concepto} , safe=False)

def ingreso_activo_xls(request):

	var_post 		= request.POST.copy()
	fecha          	= str(time.strftime('%d-%m-%Y'))
	hora           	= str(time.strftime("%X"))
	ano_anterior 	= datetime.now().year - int(var_post['cantidad_periodos'])
	count 			= 2
	nombre_meses 	= ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
						'Octubre', 'Noviembre', 'Diciembre']

	data    = []
	output  = io.BytesIO()

	workbook 	= xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet 	= workbook.add_worksheet()

	footer = '&CPage &P of &N'
	worksheet.set_footer(footer)

	format       		= workbook.add_format({'bold': True, 'align': 'center', 'font_size':10, 'border': True, 'bottom_color': '#286ca0'})
	format_cell  		= workbook.add_format({'font_size': 10})
	format_cell_number 	= workbook.add_format({'font_size': 10,'num_format': '#,##0'})
	format_merge 		= workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})

	worksheet.merge_range('D2:E2', 'INGRESOS POR ACTIVOS', format_merge)

	worksheet.write(1, 0, str(request.user.userprofile.empresa), format_cell)
	worksheet.write(2, 0, str(request.user.userprofile.empresa.rut), format_cell)
	worksheet.write(3, 0, str(request.user.userprofile.empresa.direccion), format_cell)

	worksheet.write(1, 7, str(fecha), format_cell)
	worksheet.write(2, 7, str(hora), format_cell)

	colums = list()
	colums.append({'header': 'Activo', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'Cliente', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'Contrato', 'header_format': format, 'format': format_cell})

	# MENSUAL
	if int(var_post['periodos']) == 0:

		fecha_inicial = sumar_meses(datetime.now(), -int(var_post['cantidad_periodos']))
		##Armar Cabecera dinamica de Excel
		while fecha_inicial < datetime.now().date():
			dias 			 = calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
			fecha_inicial 	+= timedelta(days=dias)
			count 			+= 1
			colums.append({'header': str(nombre_meses[fecha_inicial.month - 1]) + ' ' + str(fecha_inicial.year), 'header_format': format, 'format': format_cell_number})

		##Armar detalle de excel de acuerdo a los filtros
		if var_post['activo'] != '':
			activos = Activo.objects.filter(id=int(var_post['activo']), empresa=request.user.userprofile.empresa,
											visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if var_post['cliente'] != '':
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													cliente_id=int(var_post['cliente']), visible=True).order_by('cliente', 'numero')
			else:
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													visible=True).order_by('cliente', 'numero')

			for contrato in contratos:

				fecha_inicial 	= sumar_meses(datetime.now(), -int(var_post['cantidad_periodos']))
				dias 			= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
				fecha_inicial  += timedelta(days=dias)

				x = []
				x.append(activo.nombre)
				x.append(contrato.cliente.nombre)
				x.append(contrato.numero)
				while fecha_inicial <= datetime.now().date():

					if var_post['conceptos'] != '':
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  factura_detalle__concepto_id=int(var_post['conceptos']),
															  fecha_inicio__month=fecha_inicial.month,
															  fecha_inicio__year=fecha_inicial.year) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					else:
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  fecha_inicio__month=fecha_inicial.month,
															  fecha_inicio__year=fecha_inicial.year) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

					total_activo = total_activo if total_activo is not None else 0
					x.append(total_activo)
					dias 			= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
					fecha_inicial += timedelta(days=dias)

				data.append(x)

	# TREMESTRAL O SEMESTRAL
	elif int(var_post['periodos']) == 1 or int(var_post['periodos']) == 2:

		if int(var_post['periodos']) == 1:
			nombre_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct', 'Nov', 'Dic']
			semestral = [[1, 3], [4, 6], [7, 9], [10, 12]]
		else:
			semestral = [[1, 6], [7, 12]]

		for ano in range(ano_anterior, datetime.now().year + 1):
			for semestre in semestral:
				cabecera = str(nombre_meses[semestre[0] - 1]) + '-' + str(ano) + '  ' + str(nombre_meses[semestre[1] - 1]) + '-' + str(ano)
				colums.append({'header': cabecera, 'header_format': format, 'format': format_cell_number})
				count 	+= 1

		if var_post['activo'] != '':
			activos = Activo.objects.filter(id=int(var_post['activo']),
											empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if var_post['cliente'] != '':
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa,
													cliente_id=int(var_post['cliente']), visible=True).order_by('cliente', 'numero')
			else:
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa, visible=True).order_by('cliente', 'numero')

			for contrato in contratos:
				x = []
				x.append(activo.nombre)
				x.append(contrato.cliente.nombre)
				x.append(contrato.numero)
				for ano in range(ano_anterior, datetime.now().year + 1):
					for semestre in semestral:
						if var_post['conceptos'] != '':
							total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  factura_detalle__concepto_id=int
																	  (var_post['conceptos']),
																  fecha_inicio__month__gte=semestre[0],
																  fecha_inicio__month__lte=semestre[1],
																  fecha_inicio__year=ano) \
								.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
						else:
							total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  fecha_inicio__month__gte=semestre[0],
																  fecha_inicio__month__lte=semestre[1],
																  fecha_inicio__year=ano) \
								.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

						total_activo 	= total_activo if total_activo is not None else 0
						x.append(total_activo)
				data.append(x)

	# ANUAL
	elif int(var_post['periodos']) == 3:

		for ano in range(ano_anterior, datetime.now().year + 1):
			colums.append({'header': 'Año ' + str(ano), 'header_format': format, 'format': format_cell_number})
			count += 1

		if var_post['activo'] != '':
			activos = Activo.objects.filter(id=int(var_post['activo']),
											empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if var_post['cliente'] != '':
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa,
													cliente_id=int(var_post['cliente']), visible=True).order_by('cliente', 'numero')
			else:
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa, visible=True).order_by('cliente', 'numero')

			for contrato in contratos:
				x = []
				x.append(activo.nombre)
				x.append(contrato.cliente.nombre)
				x.append(contrato.numero)
				for ano in range(ano_anterior, datetime.now().year + 1):
					if var_post['conceptos'] != '':
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  factura_detalle__concepto_id=int(
																  var_post['conceptos']),
															  fecha_inicio__year=ano) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					else:
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  fecha_inicio__year=ano) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

					total_activo 	= total_activo if total_activo is not None else 0
					x.append(total_activo)
				data.append(x)

	worksheet.add_table(6, 0, data.__len__()+6, count, {'data': data, 'columns': colums, 'autofilter': False,})
	worksheet.set_column(0,count, 20)
	workbook.close()
	# Rewind the buffer.
	output.seek(0)

	fecha_documento = datetime.now()
	fecha 			= fecha_documento.strftime('%d/%m/%Y')
	filename 		= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_')) + '-' + 'ingresos-activos' + '-' + fecha + '.xls'

	response 						= HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	response.write(output.read())
	return response

def ingreso_activo_pdf(request):

	var_post 		= request.POST.copy()
	data 			= []
	data_cabecera 	= []
	ano_anterior 	= datetime.now().year - int(var_post['cantidad_periodos'])
	count 			= 2
	nombre_meses 	= ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
						'Octubre', 'Noviembre', 'Diciembre']


	# MENSUAL
	if int(var_post['periodos']) == 0:

		fecha_inicial = sumar_meses(datetime.now(), -int(var_post['cantidad_periodos']))
		##Armar Cabecera dinamica de Excel
		while fecha_inicial < datetime.now().date():
			dias 			= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
			fecha_inicial  += timedelta(days=dias)
			data_cabecera.append(str(nombre_meses[fecha_inicial.month - 1]) + ' ' + str(fecha_inicial.year))



		##Armar detalle de excel de acuerdo a los filtros
		if var_post['activo'] != '':
			activos = Activo.objects.filter(id=int(var_post['activo']), empresa=request.user.userprofile.empresa,
											visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if var_post['cliente'] != '':
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													cliente_id=int(var_post['cliente']), visible=True).order_by(
					'cliente', 'numero')
			else:
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													visible=True).order_by('cliente', 'numero')

			for contrato in contratos:

				fecha_inicial 	= sumar_meses(datetime.now(), -int(var_post['cantidad_periodos']))
				dias 			= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
				fecha_inicial  += timedelta(days=dias)
				x = []
				x.append(activo.nombre)
				x.append(contrato.cliente.nombre)
				x.append(contrato.numero)
				while fecha_inicial <= datetime.now().date():

					if var_post['conceptos'] != '':
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  factura_detalle__concepto_id=int(var_post['conceptos']),
															  fecha_inicio__month=fecha_inicial.month,
															  fecha_inicio__year=fecha_inicial.year) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					else:
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  fecha_inicio__month=fecha_inicial.month,
															  fecha_inicio__year=fecha_inicial.year) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

					total_activo 	= total_activo if total_activo is not None else 0
					dias 			= calendar.monthrange(fecha_inicial.year, fecha_inicial.month)[1]
					fecha_inicial  += timedelta(days=dias)

					x.append(formato_moneda_local(request, total_activo))

				data.append(x)

	# TREMESTRAL O SEMESTRAL
	elif int(var_post['periodos']) == 1 or int(var_post['periodos']) == 2:

		if int(var_post['periodos']) == 1:
			nombre_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sept', 'Oct', 'Nov', 'Dic']
			semestral = [[1, 3], [4, 6], [7, 9], [10, 12]]
		else:
			semestral = [[1, 6], [7, 12]]

		for ano in range(ano_anterior, datetime.now().year + 1):
			for semestre in semestral:
				cabecera = str(nombre_meses[semestre[0] - 1]) + '-' + str(ano) + '  ' + str(nombre_meses[semestre[1] - 1]) + '-' + str(ano)
				data_cabecera.append(cabecera)

		if var_post['activo'] != '':
			activos = Activo.objects.filter(id=int(var_post['activo']),
											empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if var_post['cliente'] != '':
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa,
													cliente_id=int(var_post['cliente']), visible=True).order_by(
					'cliente', 'numero')
			else:
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa, visible=True).order_by(
					'cliente', 'numero')

			for contrato in contratos:
				x = []
				x.append(activo.nombre)
				x.append(contrato.cliente.nombre)
				x.append(contrato.numero)
				for ano in range(ano_anterior, datetime.now().year + 1):
					for semestre in semestral:
						if var_post['conceptos'] != '':
							total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  factura_detalle__concepto_id=int
																  (var_post['conceptos']),
																  fecha_inicio__month__gte=semestre[0],
																  fecha_inicio__month__lte=semestre[1],
																  fecha_inicio__year=ano) \
								.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
						else:
							total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
																  fecha_inicio__month__gte=semestre[0],
																  fecha_inicio__month__lte=semestre[1],
																  fecha_inicio__year=ano) \
								.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

						total_activo = total_activo if total_activo is not None else 0
						x.append(formato_moneda_local(request, total_activo))
				data.append(x)

	# ANUAL
	elif int(var_post['periodos']) == 3:

		for ano in range(ano_anterior, datetime.now().year + 1):
			data_cabecera.append('Año ' + str(ano))

		if var_post['activo'] != '':
			activos = Activo.objects.filter(id=int(var_post['activo']),
											empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if var_post['cliente'] != '':
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa,
													cliente_id=int(var_post['cliente']), visible=True).order_by(
					'cliente', 'numero')
			else:
				contratos = Contrato.objects.filter(locales__in=locales,
													empresa=request.user.userprofile.empresa, visible=True).order_by(
					'cliente', 'numero')

			for contrato in contratos:
				x = []
				x.append(activo.nombre)
				x.append(contrato.cliente.nombre)
				x.append(contrato.numero)
				for ano in range(ano_anterior, datetime.now().year + 1):
					if var_post['conceptos'] != '':
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  factura_detalle__concepto_id=int(
																  var_post['conceptos']),
															  fecha_inicio__year=ano) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					else:
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  fecha_inicio__year=ano) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

					total_activo = total_activo if total_activo is not None else 0
					x.append(formato_moneda_local(request, total_activo))
				data.append(x)

	hora = str(time.strftime("%X"))
	context = {'empresa': request.user.userprofile.empresa.nombre.encode(encoding='UTF-8', errors='strict'),
			   'modulo': 'INGRESOS POR ACTIVOS', 'rut': request.user.userprofile.empresa.rut,
			   'direccion': request.user.userprofile.empresa.direccion, 'hora': hora}

	content = render_to_string('reportes/ingreso_activo_pdf.html', context)

	with open('reporteria/templates/reportes/cabecera_table.html', 'w', encoding='UTF-8') as static_file:
		static_file.write(content)

	options = {
		'page-size'		: 'A4',
		'orientation'	: 'Landscape',
		'margin-top'	: '1.25in',
		'margin-right'	: '0.55in',
		'margin-bottom'	: '0.55in',
		'margin-left'	: '0.55in',
		'header-html'	: 'reporteria/templates/reportes/cabecera_table.html',
	}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('reportes/ingreso_activo_pdf_detalle.html')
	fecha 		= str(time.strftime('%d-%m-%Y'))
	hora 		= str(time.strftime("%X"))

	context = {
		'data'			: data,
		'data_cabecera'	: data_cabecera,
		'user'			: request.user.userprofile,
		'fecha'			: fecha,
		'hora'			: hora,
	}

	html = template.render(context)  # Renders the template with the context data.

	pdfkit.from_string(html, 'public/media/reportes/prueba.pdf', options=options, css=css)
	pdf = open('public/media/reportes/prueba.pdf', 'rb')

	dt 			= datetime.now()
	filename 	= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_'))+'-ingreso-activo-' + dt.strftime('%Y%m%d') + '.pdf'

	response 						= HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	pdf.close()
	return response  # returns the response.



