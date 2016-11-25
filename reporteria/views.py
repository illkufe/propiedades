
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from django.db.models import Sum
from accounts.models import UserProfile
from administrador.models import Clasificacion_Detalle
from contrato.models import Contrato
from locales.models import Local_Tipo, Local
from procesos.models import Factura
from reporteria.forms import *
from .models import *
from datetime import datetime
from utilidades.views import *

import io
import time
import xlsxwriter
import json


# variables
nombre_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

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

			# tipos         = request.user.userprofile.empresa.reporte_tipo_set.all()
			# reportes  = Reporte_Tipo.objects.filter(empresa=request.user.userprofile.empresa)

			return render(request, 'reporte_list.html', {
				'title'     : 'Reporteria',
				'href'      : 'reportes',
				'subtitle'  : 'Reportes',
				'name'      : 'Lista',
				'tipos'     : '',
				'reportes'  : '',
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
				'nombre'    : reporte.reporte_tipo.nombre,
				'icono'     : reporte.reporte_tipo.icono,
				'color'     : reporte.reporte_tipo.color,
				}

			usuario = {
				'id'            : reporte.user.id,
				'first_name'    : reporte.user.first_name,
				'last_name'     : reporte.user.last_name,
				}

			data.append({
				'id'            : reporte.id,
				'nombre'        : reporte.nombre,
				'nombre_pdf'    : reporte.nombre_pdf,
				'fecha'         : reporte.creado_en.strftime("%d/%m/%Y"),
				'tipo'          : tipo,
				'usuario'       : usuario,
				'empresa'       : empresa,
				})

		return JsonResponse(data, safe=False)

def datos_reporte(request, var_post):

	default     = 'reportes/default.html'
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
		#   nombre          = var_post['nombre'],
		#   nombre_pdf      = nombre,
		#   user            = request.user,
		#   empresa         = request.user.userprofile.empresa,
		#   reporte_tipo_id = int(var_post['tipo']),
		# )
		#
		# reporte.save()

		configuration = {
			'default'       : default,
			'html'          : html,
			'destination'   : destination,
			# 'nombre_pdf'  : str(reporte.empresa.id)+'_'+str(reporte.id)+'_'+nombre,
			}

		generar_pdf(configuration, data)

		return True

	except Exception as asd:

		return False

def vacancia_por_centro_comercial(request):

	data    = list()
	empresa = request.user.userprofile.empresa

	return data


#INGRESO POR ACTIVO
class REPORTE_INGRESO_ACTIVO(View):
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		return render(request, 'reportes/reporte_ingreso_activo.html', {
			'title' 	: 'Reporteria',
			'href' 		: 'reportes',
			'subtitle'	: 'Reportes',
			'name' 		: 'Ingreso Activos',
			'form'		: FiltroIngresoActivo(request=self.request)
		})

	def post(self, request):

		var_post 		= request.POST.copy()

		data_cabecera 	= {}
		data_concepto 	= list()
		count 			= 0

		tipo 		    = int(var_post['periodos'])
		periodos 	    = int(var_post['cantidad_periodos'])
		activo          = var_post.getlist('activo[]')
		cliente         = var_post.getlist('cliente[]')
		conceptos       = var_post.getlist('conceptos[]')

		#Calculo de periodos
		response        = calcular_periodos(tipo, periodos, 'restar')

		## Se obtiene el detalle de la tabla

		activos = Activo.objects.filter(id__in=activo , empresa=request.user.userprofile.empresa,
											visible=True).order_by('nombre')

		for activo in activos:

			locales 	= Local.objects.filter(activo_id=activo.id, visible=True)
			contratos 	= Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													cliente__in=cliente, visible=True).order_by('cliente', 'numero')

			for contrato in contratos:
				meses = {}
				aux = 0

				for data in response:

					total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  factura_detalle__concepto__in=conceptos,
															  fecha_inicio__gte=data['fecha_inicio'],
															  fecha_inicio__lte=data['fecha_termino']) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']


					total_activo = total_activo if total_activo is not None else 0

					if tipo == 1:
						meses[aux]  = [str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year),formato_moneda_local(request, total_activo)]
					elif tipo ==2 or tipo == 3:
						meses[aux] 	= [str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year)), formato_moneda_local(request, total_activo)]
					elif tipo == 4:
						meses[aux]  = ['Año ' + str(data['fecha_inicio'].year), formato_moneda_local(request, total_activo)]

					aux += 1

				data_concepto.append({
					'activo'    : activo.nombre,
					'cliente'	: contrato.cliente.nombre,
					'contrato'  : contrato.numero,
					'valores'	: meses
				})

		## Se obtiene Cabecera de las tablas
		for data in response:

			if tipo == 1:
				data_cabecera[count] = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
			elif tipo == 2 or tipo == 3:
				data_cabecera[count] = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
			elif tipo == 4:
				data_cabecera[count] = 'Año ' + str(data['fecha_inicio'].year)

			count += 1

		return JsonResponse({'cabecera': data_cabecera, 'data':data_concepto} , safe=False)

def ingreso_activo_xls(request):

	var_post 		= request.POST.copy()
	fecha          	= str(time.strftime('%d-%m-%Y'))
	hora           	= str(time.strftime("%X"))
	count 			= 2

	tipo 			= int(var_post['periodos'])
	periodos 		= int(var_post['cantidad_periodos'])
	activo 			= var_post.getlist('activo')
	cliente 		= var_post.getlist('cliente')
	conceptos 		= var_post.getlist('conceptos')

	response 		= calcular_periodos(tipo, periodos, 'restar')

	data_excel		= []
	output  		= io.BytesIO()

	workbook 		= xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet 		= workbook.add_worksheet()

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


	## Se obtiene Cabecera de las tablas
	for data in response:

		cabecera  = ''
		if tipo == 1:
			cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
		elif tipo == 2 or tipo == 3:
			cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
		elif tipo == 4:
			cabecera = 'Año ' + str(data['fecha_inicio'].year)

		colums.append({'header': cabecera,'header_format': format, 'format': format_cell_number})

		count += 1


	## Se obtiene el detalle de la tabla

	activos = Activo.objects.filter(id__in=activo, empresa=request.user.userprofile.empresa,
										visible=True).order_by('nombre')

	for activo in activos:

		locales 	= Local.objects.filter(activo_id=activo.id, visible=True)
		contratos 	= Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
												cliente__in=cliente, visible=True).order_by('cliente', 'numero')

		for contrato in contratos:
			x = []
			x.append(activo.nombre)
			x.append(contrato.cliente.nombre)
			x.append(contrato.numero)

			for data in response:

				total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
														  factura_detalle__concepto__in=conceptos,
														  fecha_inicio__gte=data['fecha_inicio'],
														  fecha_inicio__lte=data['fecha_termino']) \
						.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']


				total_activo = total_activo if total_activo is not None else 0

				x.append(total_activo)

			data_excel.append(x)

	worksheet.add_table(6, 0, data_excel.__len__()+6, count, {'data': data_excel, 'columns': colums, 'autofilter': False,})
	worksheet.set_column(0,count, 25)
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
	data_pdf 		= []
	data_cabecera 	= []


	tipo 			= int(var_post['periodos'])
	periodos 		= int(var_post['cantidad_periodos'])
	activo 			= var_post.getlist('activo')
	cliente 		= var_post.getlist('cliente')
	conceptos 		= var_post.getlist('conceptos')

	response 		= calcular_periodos(tipo, periodos, 'restar')


	## Se obtiene Cabecera de las tablas
	for data in response:

		cabecera  = ''
		if tipo == 1:
			cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
		elif tipo == 2 or tipo == 3:
			cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1])[:3] + '-' + str(data['fecha_termino'].year))
		elif tipo == 4:
			cabecera = 'Año ' + str(data['fecha_inicio'].year)

		data_cabecera.append(cabecera)


	## Se obtiene el detalle de la tabla

	activos = Activo.objects.filter(id__in=activo, empresa=request.user.userprofile.empresa,
										visible=True).order_by('nombre')

	for activo in activos:

		locales 	= Local.objects.filter(activo_id=activo.id, visible=True)
		contratos 	= Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
												cliente__in=cliente, visible=True).order_by('cliente', 'numero')

		for contrato in contratos:
			x = []
			x.append(activo.nombre)
			x.append(contrato.cliente.nombre)
			x.append(contrato.numero)

			for data in response:

				total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
														  factura_detalle__concepto__in=conceptos,
														  fecha_inicio__gte=data['fecha_inicio'],
														  fecha_inicio__lte=data['fecha_termino']) \
						.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']


				total_activo = total_activo if total_activo is not None else 0

				x.append(formato_moneda_local(request, total_activo))

			data_pdf.append(x)



	hora 	= str(time.strftime("%X"))
	context = {'empresa': request.user.userprofile.empresa.nombre.encode(encoding='UTF-8', errors='strict'),
			   'modulo': 'INGRESOS POR ACTIVOS', 'rut': request.user.userprofile.empresa.rut,
			   'direccion': request.user.userprofile.empresa.direccion, 'hora': hora}

	content = render_to_string('pdf/cabeceras/cabecera_default.html', context)

	with open('public/media/reportes/cabecera.html', 'w', encoding='UTF-8') as static_file:
		static_file.write(content)

	options = {
		'page-size'		: 'A4',
		'orientation'	: 'Landscape',
		'margin-top'	: '1.25in',
		'margin-right'	: '0.55in',
		'margin-bottom'	: '0.55in',
		'margin-left'	: '0.55in',
		'header-html'	: 'public/media/reportes/cabecera.html',
	}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/reportes/ingreso_activo_detalle.html')
	fecha 		= str(time.strftime('%d-%m-%Y'))
	hora 		= str(time.strftime("%X"))

	context = {
		'data'			: data_pdf,
		'data_cabecera'	: data_cabecera,
		'user'			: request.user.userprofile,
		'fecha'			: fecha,
		'hora'			: hora,
	}

	html = template.render(context)  # Renders the template with the context data.

	pdfkit.from_string(html, 'public/media/reportes/ingresos-activos.pdf', options=options, css=css)
	pdf = open('public/media/reportes/ingresos-activos.pdf', 'rb')

	dt 			= datetime.now()
	filename 	= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_'))+'-ingreso-activo-' + dt.strftime('%Y%m%d') + '.pdf'

	response 						= HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	pdf.close()
	return response  # returns the response.


#INGRESO POR CLASIFICACION
class REPORTE_INGRESO_CLASIFICACION(View):
	#TODO realizar de nuevo esta función, ya que esta tomando un solo local de los contratos.
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		return render(request, 'reportes/reporte_ingreso_clasificacion.html', {
			'title' 	: 'Reporteria',
			'href' 		: 'reportes',
			'subtitle'	: 'Reportes',
			'name' 		: 'Ingreso Clasificación',
			'form'		: FiltroIngresoClasificacion(request=self.request)
		})

	def post(self, request):

		var_post 			= request.POST.copy()

		tipo_periodo 		= int(var_post['periodos'])
		cant_periodo 	    = int(var_post['cantidad_periodos'])
		clasificacion_id	= var_post.getlist('clasificacion[]')
		conceptos       	= var_post.getlist('conceptos[]')

		data 				= data_report_ingreso_clasificacion(request, tipo_periodo, cant_periodo, clasificacion_id, conceptos)

		return JsonResponse(data, safe=False)

def ingreso_clasificacion_xls(request):

	var_post 		= request.POST.copy()
	fecha          	= str(time.strftime('%d-%m-%Y'))
	hora           	= str(time.strftime("%X"))
	count 			= 1
	data_excel 		= []
	tipo_periodo 		= int(var_post['periodos'])
	cant_periodo 		= int(var_post['cantidad_periodos'])
	clasificacion_id 	= var_post.getlist('clasificacion')
	conceptos 			= var_post.getlist('conceptos')

	data 				= data_report_ingreso_clasificacion(request, tipo_periodo, cant_periodo, clasificacion_id, conceptos)

	output  		= io.BytesIO()

	workbook 		= xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet 		= workbook.add_worksheet()

	footer = '&CPage &P of &N'
	worksheet.set_footer(footer)

	format       		= workbook.add_format({'bold': True, 'align': 'center', 'font_size':10, 'border': True, 'bottom_color': '#286ca0'})
	format_cell  		= workbook.add_format({'font_size': 10})
	format_cell_number 	= workbook.add_format({'font_size': 10,'num_format': '#,##0'})
	format_merge 		= workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})

	worksheet.merge_range('D2:E2', 'INGRESOS POR CLASIFICACIÓN', format_merge)

	worksheet.write(1, 0, str(request.user.userprofile.empresa), format_cell)
	worksheet.write(2, 0, str(request.user.userprofile.empresa.rut), format_cell)
	worksheet.write(3, 0, str(request.user.userprofile.empresa.direccion), format_cell)

	worksheet.write(1, 7, str(fecha), format_cell)
	worksheet.write(2, 7, str(hora), format_cell)

	colums = list()
	colums.append({'header': 'Clasificación', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'Detalle', 'header_format': format, 'format': format_cell})

	len_cabecera = data[0]['cabecera'].__len__()

	for a in range(0, len_cabecera):
		colums.append({'header': data[0]['cabecera'][a] , 'header_format': format, 'format': format_cell_number})
		count +=1

	len_detalle = data[0]['data'].__len__()
	for b in range(0, len_detalle):

		len_valores = data[0]['data'][b]['detalles'].__len__()

		for c in range(0, len_valores):

			len_prueba = data[0]['data'][b]['detalles'][c]['valores'].__len__()

			data_detalle = []
			data_detalle.append(data[0]['data'][b]['clasificacion'])
			data_detalle.append(data[0]['data'][b]['detalles'][c]['detalle_clasificacion'])
			for d in range(0, len_prueba):
				data_detalle.append(data[0]['data'][b]['detalles'][c]['valores'][d][1])

			data_excel.append(data_detalle)


	worksheet.add_table(6, 0, data_excel.__len__()+6, count, {'data': data_excel, 'columns': colums, 'autofilter': False,})
	worksheet.set_column(0, count, 25)
	workbook.close()
	# Rewind the buffer.
	output.seek(0)

	fecha_documento = datetime.now()
	fecha 			= fecha_documento.strftime('%d/%m/%Y')
	filename 		= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_')) + '-' + 'ingresos-clasificacion' + '-' + fecha + '.xls'

	response 						= HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	response.write(output.read())
	return response

def ingreso_clasificacion_pdf(request):

	var_post 			= request.POST.copy()
	data_pdf 			= []
	data_cabecera 		= []
	tipo_periodo 		= int(var_post['periodos'])
	cant_periodo 		= int(var_post['cantidad_periodos'])
	clasificacion_id 	= var_post.getlist('clasificacion')
	conceptos 			= var_post.getlist('conceptos')

	data 				= data_report_ingreso_clasificacion(request, tipo_periodo, cant_periodo, clasificacion_id, conceptos)


	len_cabecera = data[0]['cabecera'].__len__()

	for a in range(0, len_cabecera):
		data_cabecera.append(data[0]['cabecera'][a])


	len_detalle = data[0]['data'].__len__()
	for b in range(0, len_detalle):

		len_valores = data[0]['data'][b]['detalles'].__len__()

		for c in range(0, len_valores):

			len_prueba = data[0]['data'][b]['detalles'][c]['valores'].__len__()

			data_detalle = []
			data_detalle.append(data[0]['data'][b]['clasificacion'])
			data_detalle.append(data[0]['data'][b]['detalles'][c]['detalle_clasificacion'])
			for d in range(0, len_prueba):
				data_detalle.append(data[0]['data'][b]['detalles'][c]['valores_formateado'][d][1])

			data_pdf.append(data_detalle)

	hora 	= str(time.strftime("%X"))
	context = {'empresa': request.user.userprofile.empresa.nombre.encode(encoding='UTF-8', errors='strict'),
			   'modulo': 'INGRESOS POR CLASIFICACIÓN', 'rut': request.user.userprofile.empresa.rut,
			   'direccion': request.user.userprofile.empresa.direccion, 'hora': hora}

	content = render_to_string('pdf/cabeceras/cabecera_default.html', context)

	with open('public/media/reportes/cabecera.html', 'w', encoding='UTF-8') as static_file:
		static_file.write(content)

	options = {
		'page-size'		: 'A4',
		'orientation'	: 'Landscape',
		'margin-top'	: '1.25in',
		'margin-right'	: '0.55in',
		'margin-bottom'	: '0.55in',
		'margin-left'	: '0.55in',
		'header-html'	: 'public/media/reportes/cabecera.html',
	}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/reportes/ingreso_clasificacion_detalle.html')
	fecha 		= str(time.strftime('%d-%m-%Y'))
	hora 		= str(time.strftime("%X"))

	context = {
		'data'			: data_pdf,
		'data_cabecera'	: data_cabecera,
		'user'			: request.user.userprofile,
		'fecha'			: fecha,
		'hora'			: hora,
	}

	html = template.render(context)  # Renders the template with the context data.

	pdfkit.from_string(html, 'public/media/reportes/ingresos-clasificacion.pdf', options=options, css=css)
	pdf = open('public/media/reportes/ingresos-clasificacion.pdf', 'rb')

	dt 			= datetime.now()
	filename 	= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_'))+'-ingresos-clasificacion-' + dt.strftime('%Y%m%d') + '.pdf'

	response 						= HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	pdf.close()
	return response  # returns the response.


#VACANCIA DE ACTIVOS
class REPORTE_VACANCIA(View):
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		return render(request, 'reportes/reporte_vacancia_activo.html', {
			'title' 	: 'Reporteria',
			'href' 		: 'reportes',
			'subtitle'	: 'Reportes',
			'name' 		: 'Vacancias',
			'form'		: FiltroVacancia(request=self.request)
		})

	def post(self, request):

		var_post 		= request.POST.copy()

		data_cabecera 	= {}
		data_response   = list()
		count 			= 0

		activo          = var_post['activo']
		agrupador       = var_post['agrupador'] if var_post['agrupador'] == '' else int(var_post['agrupador'])
		tipo_periodos   = int(var_post['periodos'])
		cant_periodos 	= int(var_post['cantidad_periodos'])

		#Calculo de periodos
		response        = calcular_periodos(tipo_periodos, cant_periodos, 'sumar')

		## Se obtiene el detalle de la tabla
		if activo  != '':
			activos = Activo.objects.filter(id=activo , empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			##Agrupador por Tipo de Local
			if agrupador == 1:

				tipos 	= Local_Tipo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

				for tipo in tipos:

					m_totales  	= Local.objects.filter(activo=activo, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
					aux 		= 0
					meses 		= {}
					meses[aux] 	= ['Tipos de Locales',tipo.nombre]
					aux 		+= 1

					for data in response:
						locales    		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
						m_ocupados 		= Local.objects.filter(id__in=locales, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

						m_totales  		= m_totales if m_totales is not None else 0
						m_ocupados 		= m_ocupados if m_ocupados is not None else 0

						m_disponibles 	= m_totales - m_ocupados

						# Mensual
						if tipo_periodos == 1:
							meses[aux] = [str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year), m_disponibles]
						# Trimestral o Semestral
						elif tipo_periodos == 2 or tipo_periodos == 3:
							meses[aux] = [str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year)), m_disponibles]
						# Anual
						elif tipo_periodos == 4:
							meses[aux] = ['Año ' + str(data['fecha_inicio'].year), m_disponibles]

						aux += 1

					data_response.append({
						'activo'	: activo.nombre,
						'tipo'      : tipo.nombre,
						'valores'	: meses,
					})

			## Agrupador por Niveles
			elif agrupador == 2:

				niveles = activo.nivel_set.all()

				for nivel in niveles:

					m_totales = Local.objects.filter(activo=activo, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
					aux 		= 0
					meses 		= {}
					meses[aux] 	= ['Niveles', nivel.nombre]
					aux 		+= 1

					for data in response:
						locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
						m_ocupados 		= Local.objects.filter(id__in=locales, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

						m_totales 		= m_totales if m_totales is not None else 0
						m_ocupados 		= m_ocupados if m_ocupados is not None else 0

						m_disponibles 	= m_totales - m_ocupados

						# Mensual
						if tipo_periodos == 1:
							meses[aux] = [str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year), m_disponibles]
						# Trimestral o Semestral
						elif tipo_periodos == 2 or tipo_periodos == 3:
							meses[aux] = [str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year)), m_disponibles]
						# Anual
						elif tipo_periodos == 4:
							meses[aux] = ['Año ' + str(data['fecha_inicio'].year), m_disponibles]

						aux += 1

					data_response.append({
						'activo'	: activo.nombre,
						'valores'	: meses,
					})

			##Agrupador por Sector
			elif agrupador == 3:

				sectores 	= activo.sector_set.all()

				for sector in sectores:
					m_totales 	= Local.objects.filter(activo=activo, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
					aux 		= 0
					meses 		= {}

					meses[aux] 	= ['Sectores', sector.nombre]
					aux 		+= 1

					for data in response:

						locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
						m_ocupados 		= Local.objects.filter(id__in=locales, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

						m_totales 		= m_totales if m_totales is not None else 0
						m_ocupados 		= m_ocupados if m_ocupados is not None else 0
						m_disponibles 	= m_totales - m_ocupados

						#Mensual
						if tipo_periodos == 1:
							meses[aux] = [str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year), m_disponibles]
						# Trimestral o Semestral
						elif tipo_periodos == 2 or tipo_periodos == 3:
							meses[aux] = [str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year)), m_disponibles]
						#Anual
						elif tipo_periodos == 4:
							meses[aux] = ['Año ' + str(data['fecha_inicio'].year), m_disponibles]

						aux += 1

					data_response.append({
						'activo'	: activo.nombre,
						'valores'	: meses,
					})

			##Todos los Activos (Sin Agrupador)
			else:
				m_totales 	= activo.local_set.all().filter(visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				aux 		= 0
				meses 		= {}

				for data in response:
					locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'] , visible=True)
					m_ocupados 		= Local.objects.filter(id__in=locales, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

					m_totales 		= m_totales if m_totales is not None else 0
					m_ocupados 		= m_ocupados if m_ocupados is not None else 0
					m_disponibles 	= m_totales - m_ocupados

					# Mensual
					if tipo_periodos == 1:
						meses[aux] = [str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year), m_disponibles]
					# Trimestral o Semestral
					elif tipo_periodos == 2 or tipo_periodos == 3:
						meses[aux] = [str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year)), m_disponibles]
					# Anual
					elif tipo_periodos == 4:
						meses[aux] = ['Año ' + str(data['fecha_inicio'].year), m_disponibles]

					aux += 1

				data_response.append({
					'activo'		: activo.nombre,
					'valores'	    : meses,
				})

		if agrupador == 1:
			data_cabecera[count] = 'Tipos de Locales'
			count +=1
		elif agrupador ==2:
			data_cabecera[count] = 'Niveles'
			count += 1
		elif agrupador == 3:
			data_cabecera[count] = 'Sectores'
			count += 1

		## Se obtiene Cabecera de las tablas
		for data in response:

			if tipo_periodos == 1:
				data_cabecera[count] = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
			elif tipo_periodos == 2 or tipo_periodos == 3:
				data_cabecera[count] = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
			elif tipo_periodos == 4:
				data_cabecera[count] = 'Año ' + str(data['fecha_inicio'].year)

			count += 1


		return JsonResponse({'cabecera': data_cabecera, 'data': data_response}, safe=False)

def vacancia_xls(request):

	var_post 		= request.POST.copy()
	fecha          	= str(time.strftime('%d-%m-%Y'))
	hora           	= str(time.strftime("%X"))
	count 			= 0

	activo 			= var_post['activo']
	agrupador 		= var_post['agrupador'] if var_post['agrupador'] == '' else int(var_post['agrupador'])
	tipo_periodos 	= int(var_post['periodos'])
	cant_periodos 	= int(var_post['cantidad_periodos'])

	# Calculo de periodos
	response 		= calcular_periodos(tipo_periodos, cant_periodos, 'sumar')

	data_excel		= []
	output  		= io.BytesIO()

	workbook 		= xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet 		= workbook.add_worksheet()

	footer = '&CPage &P of &N'
	worksheet.set_footer(footer)

	format       		= workbook.add_format({'bold': True, 'align': 'center', 'font_size':10, 'border': True, 'bottom_color': '#286ca0'})
	format_cell  		= workbook.add_format({'font_size': 10})
	format_cell_number 	= workbook.add_format({'font_size': 10,'num_format': '#,##0'})
	format_merge 		= workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})

	worksheet.merge_range('D2:E2', 'VACANCIA POR ACTIVOS', format_merge)

	worksheet.write(1, 0, str(request.user.userprofile.empresa), format_cell)
	worksheet.write(2, 0, str(request.user.userprofile.empresa.rut), format_cell)
	worksheet.write(3, 0, str(request.user.userprofile.empresa.direccion), format_cell)

	worksheet.write(1, 7, str(fecha), format_cell)
	worksheet.write(2, 7, str(hora), format_cell)

	colums = list()
	colums.append({'header': 'Activo', 'header_format': format, 'format': format_cell})

	#Agrega cabecera de Agrupador al excel
	cabecera_agrupador = None
	if agrupador == 1:
		cabecera_agrupador = 'Tipos de Locales'
		colums.append({'header': cabecera_agrupador, 'header_format': format, 'format': format_cell})
		count += 1
	elif agrupador == 2:
		cabecera_agrupador = 'Niveles'
		colums.append({'header': cabecera_agrupador, 'header_format': format, 'format': format_cell})
		count += 1
	elif agrupador == 3:
		cabecera_agrupador = 'Sectores'
		colums.append({'header': cabecera_agrupador, 'header_format': format, 'format': format_cell})
		count += 1

	## Se obtiene Cabecera de los Periodos seleccionados
	for data in response:

		cabecera  = ''
		if tipo_periodos == 1:
			cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
		elif tipo_periodos == 2 or tipo_periodos == 3:
			cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
		elif tipo_periodos == 4:
			cabecera = 'Año ' + str(data['fecha_inicio'].year)

		colums.append({'header': cabecera,'header_format': format, 'format': format_cell})

		count += 1


	## Se obtiene el detalle de la tabla
	if activo != '':
		activos = Activo.objects.filter(id=activo, empresa=request.user.userprofile.empresa,
										visible=True).order_by('nombre')
	else:
		activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

	for activo in activos:

		##Agrupador por Tipo de Locales
		if agrupador == 1:

			tipos = Local_Tipo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

			for tipo in tipos:
				m_totales = Local.objects.filter(activo=activo, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				x = []
				x.append(activo.nombre)
				x.append(tipo.nombre)

				for data in response:
					locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
					m_ocupados 		= Local.objects.filter(id__in=locales, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

					m_totales 		= m_totales if m_totales is not None else 0
					m_ocupados 		= m_ocupados if m_ocupados is not None else 0
					m_disponibles 	= m_totales - m_ocupados

					x.append(m_disponibles)

				data_excel.append(x)

		##Agrupador por Niveles
		elif agrupador == 2:

			niveles = activo.nivel_set.all().order_by('nombre')

			for nivel in niveles:
				m_totales = Local.objects.filter(activo=activo, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				x = []
				x.append(activo.nombre)
				x.append(nivel.nombre)

				for data in response:
					locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
					m_ocupados 		= Local.objects.filter(id__in=locales, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

					m_totales 		= m_totales if m_totales is not None else 0
					m_ocupados 		= m_ocupados if m_ocupados is not None else 0
					m_disponibles	= m_totales - m_ocupados

					x.append(m_disponibles)

				data_excel.append(x)

		##Agrupador por Sectores
		elif agrupador == 3:

			sectores = activo.sector_set.all().order_by('nombre')

			for sector in sectores:
				m_totales = Local.objects.filter(activo=activo, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				x = []
				x.append(activo.nombre)
				x.append(sector.nombre)

				for data in response:

					locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
					m_ocupados 		= Local.objects.filter(id__in=locales, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

					m_totales 		= m_totales if m_totales is not None else 0
					m_ocupados 		= m_ocupados if m_ocupados is not None else 0
					m_disponibles 	= m_totales - m_ocupados

					x.append(m_disponibles)

				data_excel.append(x)

		##Todos los Activos (Sin Agrupador)
		else:
			m_totales = activo.local_set.all().filter(visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

			x = []
			x.append(activo.nombre)

			for data in response:
				locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'], visible=True)
				m_ocupados 		= Local.objects.filter(id__in=locales, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				m_totales 		= m_totales if m_totales is not None else 0
				m_ocupados 		= m_ocupados if m_ocupados is not None else 0
				m_disponibles 	= m_totales - m_ocupados

				x.append(m_disponibles)

			data_excel.append(x)


	worksheet.add_table(6, 0, data_excel.__len__()+6, count, {'data': data_excel, 'columns': colums, 'autofilter': False,})
	worksheet.set_column(0,count, 25)
	workbook.close()
	# Rewind the buffer.
	output.seek(0)

	fecha_documento = datetime.now()
	fecha 			= fecha_documento.strftime('%d/%m/%Y')
	filename 		= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_')) + '-' + 'vacancias-activos' + '-' + fecha + '.xls'

	response 						= HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	response.write(output.read())
	return response

def vacancia_pdf(request):

	var_post 		= request.POST.copy()
	data_pdf 		= []
	data_cabecera 	= []

	activo 			= var_post['activo']
	agrupador 		= var_post['agrupador'] if var_post['agrupador'] == '' else int(var_post['agrupador'])
	tipo_periodos 	= int(var_post['periodos'])
	cant_periodos 	= int(var_post['cantidad_periodos'])

	# Calculo de periodos
	response 		= calcular_periodos(tipo_periodos, cant_periodos, 'sumar')

	# Agrega cabecera de Agrupador al pdf
	cabecera_agrupador = ''
	if agrupador == 1:
		cabecera_agrupador = 'Tipos de Locales'
		data_cabecera.append(cabecera_agrupador)

	elif agrupador == 2:
		cabecera_agrupador = 'Niveles'
		data_cabecera.append(cabecera_agrupador)

	elif agrupador == 3:
		cabecera_agrupador = 'Sectores'
		data_cabecera.append(cabecera_agrupador)


	## Se obtiene Cabecera de los Periodos seleccionados
	for data in response:

		cabecera  = ''
		if tipo_periodos == 1:
			cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
		elif tipo_periodos == 2 or tipo_periodos == 3:
			cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1])[:3] + '-' + str(data['fecha_termino'].year))
		elif tipo_periodos == 4:
			cabecera = 'Año ' + str(data['fecha_inicio'].year)

		data_cabecera.append(cabecera)


	## Se obtiene el detalle de la tabla
	if activo != '':
		activos = Activo.objects.filter(id=activo, empresa=request.user.userprofile.empresa,
										visible=True).order_by('nombre')
	else:
		activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

	for activo in activos:

		##Agrupador por Tipo de Locales
		if agrupador == 1:

			tipos = Local_Tipo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

			for tipo in tipos:
				m_totales = Local.objects.filter(activo=activo, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				x = []
				x.append(activo.nombre)
				x.append(tipo.nombre)

				for data in response:
					locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
					m_ocupados		= Local.objects.filter(id__in=locales, local_tipo=tipo, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

					m_totales 		= m_totales if m_totales is not None else 0
					m_ocupados 		= m_ocupados if m_ocupados is not None else 0
					m_disponibles 	= m_totales - m_ocupados

					x.append(m_disponibles)

				data_pdf.append(x)

		##Agrupador por Niveles
		elif agrupador == 2:

			niveles = activo.nivel_set.all().order_by('nombre')

			for nivel in niveles:
				m_totales = Local.objects.filter(activo=activo, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				x = []
				x.append(activo.nombre)
				x.append(nivel.nombre)

				for data in response:
					locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
					m_ocupados 		= Local.objects.filter(id__in=locales, nivel=nivel, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

					m_totales 		= m_totales if m_totales is not None else 0
					m_ocupados 		= m_ocupados if m_ocupados is not None else 0
					m_disponibles	= m_totales - m_ocupados

					x.append(m_disponibles)

				data_pdf.append(x)

		##Agrupador por Sectores
		elif agrupador == 3:

			sectores = activo.sector_set.all().order_by('nombre')

			for sector in sectores:
				m_totales = Local.objects.filter(activo=activo, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				x = []
				x.append(activo.nombre)
				x.append(sector.nombre)

				for data in response:

					locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), visible=True, fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'])
					m_ocupados 		= Local.objects.filter(id__in=locales, sector=sector, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

					m_totales 		= m_totales if m_totales is not None else 0
					m_ocupados 		= m_ocupados if m_ocupados is not None else 0
					m_disponibles	= m_totales - m_ocupados

					x.append(m_disponibles)

				data_pdf.append(x)

		##Todos los Activos (Sin Agrupador)
		else:
			m_totales = activo.local_set.all().filter(visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

			x = []
			x.append(activo.nombre)

			for data in response:
				locales 		= Contrato.objects.values_list('locales', flat=True).filter(locales__in=activo.local_set.all().filter(visible=True), fecha_termino__gte=data['fecha_termino'], fecha_termino__lte=data['fecha_termino'], visible=True)
				m_ocupados 		= Local.objects.filter(id__in=locales, visible=True).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				m_totales 		= m_totales if m_totales is not None else 0
				m_ocupados 		= m_ocupados if m_ocupados is not None else 0
				m_disponibles 	= m_totales - m_ocupados

				x.append(m_disponibles)

			data_pdf.append(x)

	hora 	= str(time.strftime("%X"))
	context = {'empresa': request.user.userprofile.empresa.nombre.encode(encoding='UTF-8', errors='strict'),
			   'modulo': 'VACANCIA POR ACTIVOS', 'rut': request.user.userprofile.empresa.rut,
			   'direccion': request.user.userprofile.empresa.direccion, 'hora': hora}

	content = render_to_string('pdf/cabeceras/cabecera_default.html', context)

	with open('public/media/reportes/cabecera.html', 'w', encoding='UTF-8') as static_file:
		static_file.write(content)

	options = {
		'page-size'		: 'A4',
		'orientation'	: 'Landscape',
		'margin-top'	: '1.25in',
		'margin-right'	: '0.55in',
		'margin-bottom'	: '0.55in',
		'margin-left'	: '0.55in',
		'header-html'	: 'public/media/reportes/cabecera.html',
	}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/reportes/vacancia_detalle.html')
	fecha 		= str(time.strftime('%d-%m-%Y'))
	hora 		= str(time.strftime("%X"))

	context = {
		'data'			: data_pdf,
		'data_cabecera'	: data_cabecera,
		'user'			: request.user.userprofile,
		'fecha'			: fecha,
		'hora'			: hora,
	}

	html = template.render(context)  # Renders the template with the context data.

	pdfkit.from_string(html, 'public/media/reportes/vacancia.pdf', options=options, css=css)
	pdf = open('public/media/reportes/vacancia.pdf', 'rb')

	dt 			= datetime.now()
	filename 	= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_'))+'-vacancias-activos-' + dt.strftime('%Y%m%d') + '.pdf'

	response 						= HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	pdf.close()
	return response  # returns the response.


#VENCIMIENTO DE CONTRATOS
class REPORTE_VENCIMIENTO_CONTRATOS(View):
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		return render(request, 'reportes/reporte_vencimiento_contrato.html', {
			'title' 	: 'Reporteria',
			'href' 		: 'reportes',
			'subtitle'	: 'Reportes',
			'name' 		: 'Vencimiento Contratos',
			'form'		: FiltroVencimientoContrato(request=self.request)
		})

	def post(self, request):

		var_post 		= request.POST.copy()

		data_cabecera 	= {}
		data_concepto 	= list()
		count 			= 0

		activo          = var_post['activo'] if var_post['activo'] == '' else int(var_post['activo'])
		cliente         = var_post['cliente'] if var_post['cliente'] == '' else int(var_post['cliente'])
		tipo_local      = var_post['tipo_local'] if var_post['tipo_local'] == '' else int(var_post['tipo_local'])
		tipo_periodo    = int(var_post['periodos'])
		cant_periodos   = int(var_post['cantidad_periodos'])

		#Calculo de periodos
		response        = calcular_periodos(tipo_periodo, cant_periodos, 'sumar')

		## Se obtiene el detalle de la tabla
		if activo  != '':
			activos = Activo.objects.filter(id=activo , empresa=request.user.userprofile.empresa, visible=True)
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

		for activo in activos:

			if tipo_local != '':
				locales = Local.objects.filter(activo_id=activo.id, visible=True, local_tipo=tipo_local)
			else:
				locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if cliente  != '':
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													cliente_id=cliente, visible=True)
			else:
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													visible=True)

			for contrato in contratos:

				meses 	= {}
				aux 	= 0

				for data in response:

					fecha_contrato 	= contrato.fecha_termino
					fecha_desde 	= data['fecha_inicio']
					fecha_hasta 	= data['fecha_termino']

					if tipo_periodo == 1:
						cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
					elif tipo_periodo == 2 or tipo_periodo == 3:
						cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
					elif tipo_periodo == 4:
						cabecera 		= 'Año ' + str(data['fecha_inicio'].year)

						fecha_contrato 	= contrato.fecha_termino.year
						fecha_desde    	= data['fecha_inicio'].year
						fecha_hasta    	= data['fecha_termino'].year


					if fecha_contrato >= fecha_desde and fecha_contrato <= fecha_hasta:
						valor = 'si'
					else:
						valor = 'no'

					meses[aux] = [cabecera, valor]
					aux +=1

				data_concepto.append({
					'activo'	: activo.nombre,
					'cliente'	: contrato.cliente.nombre,
					'contrato'	: contrato.numero,
					'valores'	: meses
				})

		## Se obtiene Cabecera de las tablas
		for data in response:

			if tipo_periodo == 1:
				cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
			elif tipo_periodo == 2 or tipo_periodo == 3:
				cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
			elif tipo_periodo == 4:
				cabecera = 'Año ' + str(data['fecha_inicio'].year)

			data_cabecera[count] = cabecera
			count += 1

		return JsonResponse({'cabecera': data_cabecera, 'data': data_concepto}, safe=False)

	def calcular_rango(self, rango_periodos):
		response 		= list()
		fecha_actual 	= datetime.now().date()

		for periodo in rango_periodos:

			fecha_termino 	= sumar_meses(fecha_actual, periodo)
			response.insert(len(response), {
				'fecha_inicio'	: fecha_actual,
				'fecha_termino'	: fecha_termino,
			})

			fecha_actual    = fecha_termino

		return response

def vencimiento_contrato_xls(request):

	var_post 		= request.POST.copy()
	fecha          	= str(time.strftime('%d-%m-%Y'))
	hora           	= str(time.strftime("%X"))
	count 			= 2

	activo 			= var_post['activo'] if var_post['activo'] == '' else int(var_post['activo'])
	cliente 		= var_post['cliente'] if var_post['cliente'] == '' else int(var_post['cliente'])
	tipo_local 		= var_post['tipo_local'] if var_post['tipo_local'] == '' else int(var_post['tipo_local'])
	tipo_periodo 	= int(var_post['periodos'])
	cant_periodos 	= int(var_post['cantidad_periodos'])

	response 		= calcular_periodos(tipo_periodo, cant_periodos, 'sumar')

	data_excel		= []
	output  		= io.BytesIO()

	workbook 		= xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet 		= workbook.add_worksheet()

	footer = '&CPage &P of &N'
	worksheet.set_footer(footer)

	format       		= workbook.add_format({'bold': True, 'align': 'center', 'font_size':10, 'border': True, 'bottom_color': '#286ca0'})
	format_cell  		= workbook.add_format({'font_size': 10})
	format_cell_text 	= workbook.add_format({'font_size': 10, 'align': 'center'})
	format_merge 		= workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})

	worksheet.merge_range('D2:E2', 'VENCIMIENTO DE CONTRATOS', format_merge)

	worksheet.write(1, 0, str(request.user.userprofile.empresa), format_cell)
	worksheet.write(2, 0, str(request.user.userprofile.empresa.rut), format_cell)
	worksheet.write(3, 0, str(request.user.userprofile.empresa.direccion), format_cell)

	worksheet.write(1, 7, str(fecha), format_cell)
	worksheet.write(2, 7, str(hora), format_cell)

	colums = list()
	colums.append({'header': 'Activo', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'Cliente', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'Contrato', 'header_format': format, 'format': format_cell})


	## Se obtiene Cabecera de las tablas
	for data in response:

		cabecera  = ''
		if tipo_periodo == 1:
			cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
		elif tipo_periodo == 2 or tipo_periodo == 3:
			cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
		elif tipo_periodo == 4:
			cabecera = 'Año ' + str(data['fecha_inicio'].year)

		colums.append({'header': cabecera,'header_format': format, 'format': format_cell_text})

		count += 1


	## Se obtiene el detalle de la tabla
	if activo != '':
		activos = Activo.objects.filter(id=activo, empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')
	else:
		activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

	for activo in activos:

		if tipo_local != '':
			locales = Local.objects.filter(activo_id=activo.id, visible=True, local_tipo=tipo_local)
		else:
			locales = Local.objects.filter(activo_id=activo.id, visible=True)

		if cliente != '':
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, cliente_id=cliente, visible=True).order_by('-cliente', '-numero')
		else:
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, visible=True).order_by('-cliente', '-numero')

		for contrato in contratos:

			x = []
			x.append(activo.nombre)
			x.append(contrato.cliente.nombre)
			x.append(contrato.numero)
			for data in response:

				fecha_contrato 	= contrato.fecha_termino
				fecha_desde 	= data['fecha_inicio']
				fecha_hasta 	= data['fecha_termino']

				if tipo_periodo == 4:
					fecha_contrato 	= contrato.fecha_termino.year
					fecha_desde 	= data['fecha_inicio'].year
					fecha_hasta 	= data['fecha_termino'].year

				if fecha_contrato >= fecha_desde and fecha_contrato <= fecha_hasta:
					valor = 'Caducidad Contrato'
				else:
					valor = '-----------------'

				x.append(valor)

			data_excel.append(x)

	worksheet.add_table(6, 0, data_excel.__len__()+6, count, {'data': data_excel, 'columns': colums, 'autofilter': False,})
	worksheet.set_column(0,count, 25)
	workbook.close()
	# Rewind the buffer.
	output.seek(0)

	fecha_documento = datetime.now()
	fecha 			= fecha_documento.strftime('%d/%m/%Y')
	filename 		= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_')) + '-' + 'vencimientos-contratos' + '-' + fecha + '.xls'

	response 						= HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	response.write(output.read())
	return response

def vencimiento_contrato_pdf(request):

	var_post 		= request.POST.copy()
	data_pdf 		= []
	data_cabecera 	= []

	activo 			= var_post['activo'] if var_post['activo'] == '' else int(var_post['activo'])
	cliente 		= var_post['cliente'] if var_post['cliente'] == '' else int(var_post['cliente'])
	tipo_local 		= var_post['tipo_local'] if var_post['tipo_local'] == '' else int(var_post['tipo_local'])
	tipo_periodo 	= int(var_post['periodos'])
	cant_periodos 	= int(var_post['cantidad_periodos'])

	response 		= calcular_periodos(tipo_periodo, cant_periodos, 'sumar')


	## Se obtiene Cabecera de las tablas
	for data in response:

		cabecera  = ''
		if tipo_periodo == 1:
			cabecera = str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + ' ' + str(data['fecha_inicio'].year)
		elif tipo_periodo == 2 or tipo_periodo == 3:
			cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1])[:3] + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1])[:3] + '-' + str(data['fecha_termino'].year))
		elif tipo_periodo == 4:
			cabecera = 'Año ' + str(data['fecha_inicio'].year)

		data_cabecera.append(cabecera)


	## Se obtiene el detalle de la tabla
	if activo != '':
		activos = Activo.objects.filter(id=activo, empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')
	else:
		activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

	for activo in activos:

		if tipo_local != '':
			locales = Local.objects.filter(activo_id=activo.id, visible=True, local_tipo=tipo_local)
		else:
			locales = Local.objects.filter(activo_id=activo.id, visible=True)

		if cliente != '':
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, cliente_id=cliente, visible=True).order_by('-cliente', '-numero')
		else:
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, visible=True).order_by('-cliente', '-numero')

		for contrato in contratos:

			x = []
			x.append(activo.nombre)
			x.append(contrato.cliente.nombre)
			x.append(contrato.numero)
			for data in response:

				fecha_contrato 	= contrato.fecha_termino
				fecha_desde 	= data['fecha_inicio']
				fecha_hasta 	= data['fecha_termino']

				if tipo_periodo == 4:
					fecha_contrato 	= contrato.fecha_termino.year
					fecha_desde 	= data['fecha_inicio'].year
					fecha_hasta 	= data['fecha_termino'].year

				if fecha_contrato >= fecha_desde and fecha_contrato <= fecha_hasta:
					valor = 'Caducidad Contrato'
				else:
					valor = '--------------------'

				x.append(valor)

			data_pdf.append(x)



	hora 	= str(time.strftime("%X"))
	context = {'empresa': request.user.userprofile.empresa.nombre.encode(encoding='UTF-8', errors='strict'),
			   'modulo': 'VENCIMIENTOS DE CONTRATOS', 'rut': request.user.userprofile.empresa.rut,
			   'direccion': request.user.userprofile.empresa.direccion, 'hora': hora}

	content = render_to_string('pdf/cabeceras/cabecera_default.html', context)

	with open('public/media/reportes/cabecera.html', 'w', encoding='UTF-8') as static_file:
		static_file.write(content)

	options = {
		'page-size'		: 'A4',
		'orientation'	: 'Landscape',
		'margin-top'	: '1.25in',
		'margin-right'	: '0.55in',
		'margin-bottom'	: '0.55in',
		'margin-left'	: '0.55in',
		'header-html'	: 'public/media/reportes/cabecera.html',
	}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/reportes/ingreso_activo_detalle.html')
	fecha 		= str(time.strftime('%d-%m-%Y'))
	hora 		= str(time.strftime("%X"))

	context = {
		'data'			: data_pdf,
		'data_cabecera'	: data_cabecera,
		'user'			: request.user.userprofile,
		'fecha'			: fecha,
		'hora'			: hora,
	}

	html = template.render(context)  # Renders the template with the context data.

	pdfkit.from_string(html, 'public/media/reportes/vencimientos-contratos.pdf', options=options, css=css)
	pdf = open('public/media/reportes/vencimientos-contratos.pdf', 'rb')

	dt 			= datetime.now()
	filename 	= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_'))+'-vencimientos-contratos-' + dt.strftime('%Y%m%d') + '.pdf'

	response 						= HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	pdf.close()
	return response  # returns the response.


#METROS CUADRADOS CLASIFICACION
class REPORTE_METROS_CUADRADOS_CLASIFICACION(View):
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		return render(request, 'reportes/reporte_metros_cuadrados_clasificacion.html', {
			'title' 	: 'Reporteria',
			'href' 		: 'reportes',
			'subtitle'	: 'Reportes',
			'name' 		: 'M² Clasificación',
			'form'		: FiltroMCuadradosClasificacion(request=self.request)
		})

	def post(self, request):

		var_post 		= request.POST.copy()

		data 			= list()

		activo          = var_post.getlist('activo')
		clasificacion   = var_post.getlist('clasificacion')

		activos = Activo.objects.filter(id__in=activo ,empresa=request.user.userprofile.empresa, visible=True)

		for activo in activos:

			clasificaciones = Clasificacion.objects.filter(id__in=clasificacion, empresa=request.user.userprofile.empresa, visible=True,
															   tipo_clasificacion_id=1)

			m_clasificacion = 0
			for items in clasificaciones:

				det_clasificaciones = Clasificacion_Detalle.objects.filter(clasificacion=items)
				items_detalle 		= list()

				m2_detalle_sin_clas	= Local.objects.filter(visible=True, activo=activo).exclude(clasificaciones__isnull=False).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
				m2_detalle_sin_clas = m2_detalle_sin_clas if m2_detalle_sin_clas is not None else 0

				m_clasificacion 	+= m2_detalle_sin_clas

				for obj in det_clasificaciones:
					m2_detalle		= Local.objects.filter(visible=True, activo=activo, clasificaciones__id=obj.id).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
					m2_detalle 		= m2_detalle if m2_detalle is not None else 0

					m_clasificacion += m2_detalle

					items_detalle.append({
						'detalle'       		: obj.nombre,
						'm_cuadrados_detalle'	: m2_detalle,
					})

				items_detalle.append({
					'detalle'       	    : 'Sin Clasificación',
					'm_cuadrados_detalle'	: m2_detalle_sin_clas,
				})
			data.append({
				'activo'				: activo.nombre,
				'clasificacion' 		: items.nombre,
				'm_cuadrado_total' 		: m_clasificacion,
				'detalles'				: items_detalle
			})


		return JsonResponse({'data': data}, safe=False)

def metros_cuadrados_clasificacion_xls(request):

	var_post 		= request.POST.copy()
	fecha          	= str(time.strftime('%d-%m-%Y'))
	hora           	= str(time.strftime("%X"))

	activo 			= var_post.getlist('activo')
	clasificacion 	= var_post.getlist('clasificacion')

	data_excel		= []
	output  		= io.BytesIO()

	workbook 		= xlsxwriter.Workbook(output, {'in_memory': True})
	worksheet 		= workbook.add_worksheet()

	footer = '&CPage &P of &N'
	worksheet.set_footer(footer)

	format       		= workbook.add_format({'bold': True, 'align': 'center', 'font_size':10, 'border': True, 'bottom_color': '#286ca0'})
	format_cell  		= workbook.add_format({'font_size': 10})
	format_cell_text 	= workbook.add_format({'font_size': 10, 'align': 'center'})
	format_merge 		= workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})

	worksheet.merge_range('B2:C2', 'M² por Clasificación', format_merge)

	worksheet.write(1, 0, str(request.user.userprofile.empresa), format_cell)
	worksheet.write(2, 0, str(request.user.userprofile.empresa.rut), format_cell)
	worksheet.write(3, 0, str(request.user.userprofile.empresa.direccion), format_cell)

	worksheet.write(1, 3, str(fecha), format_cell)
	worksheet.write(2, 3, str(hora), format_cell)

	colums = list()
	colums.append({'header': 'Activo', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'Clasificación', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'Detalle Clasificación', 'header_format': format, 'format': format_cell})
	colums.append({'header': 'M² Detalle', 'header_format': format, 'format': format_cell})

	## Se obtiene el detalle de la tabla

	activos = Activo.objects.filter(id__in=activo, empresa=request.user.userprofile.empresa, visible=True)

	for activo in activos:

		clasificaciones = Clasificacion.objects.filter(id__in=clasificacion, empresa=request.user.userprofile.empresa,
														   visible=True,
														   tipo_clasificacion_id=1)

		m_clasificacion = 0
		for items in clasificaciones:

			det_clasificaciones = Clasificacion_Detalle.objects.filter(clasificacion=items)
			m2_detalle_sin_clas = Local.objects.filter(visible=True, activo=activo).exclude(clasificaciones__isnull=False).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m2_detalle_sin_clas = m2_detalle_sin_clas if m2_detalle_sin_clas is not None else 0

			m_clasificacion    += m2_detalle_sin_clas

			for obj in det_clasificaciones:
				m2_detalle = Local.objects.filter(visible=True, activo=activo, clasificaciones__id=obj.id).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
				m2_detalle = m2_detalle if m2_detalle is not None else 0

				m_clasificacion += m2_detalle

				data = []
				data.append(activo.nombre)
				data.append(items.nombre)
				data.append(obj.nombre)
				data.append(m2_detalle)
				data_excel.append(data)

			data = []
			data.append(activo.nombre)
			data.append(items.nombre)
			data.append('Sin Clasificación')
			data.append(m2_detalle_sin_clas)
			data_excel.append(data)

			data_excel.append(['','','',''])
			data_excel.append(['','','M² Total',m_clasificacion])
			data_excel.append(['','','',''])

	worksheet.add_table(6, 0, data_excel.__len__()+6, 3, {'data': data_excel, 'columns': colums, 'autofilter': False,})
	worksheet.set_column(0,3, 25)
	workbook.close()
	# Rewind the buffer.
	output.seek(0)

	fecha_documento = datetime.now()
	fecha 			= fecha_documento.strftime('%d/%m/%Y')
	filename 		= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_')) + '-' + 'metros-cuadrados-clasificacion' + '-' + fecha + '.xls'

	response 						= HttpResponse(content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	response.write(output.read())
	return response

def metros_cuadrados_clasificacion_pdf(request):

	var_post 		= request.POST.copy()
	pdf_data 	    = list()
	activo 			= var_post.getlist('activo')
	clasificacion 	= var_post.getlist('clasificacion')

	## Se obtiene el detalle de la tabla

	activos = Activo.objects.filter(id__in=activo, empresa=request.user.userprofile.empresa, visible=True)

	for activo in activos:

		data_pdf_detalle 	= []
		data_pdf_totales	= []

		clasificaciones = Clasificacion.objects.filter(id__in=clasificacion, empresa=request.user.userprofile.empresa,
														   visible=True,
														   tipo_clasificacion_id=1)

		for items in clasificaciones:

			det_clasificaciones = Clasificacion_Detalle.objects.filter(clasificacion=items)
			m2_detalle_sin_clas = Local.objects.filter(visible=True, activo=activo).exclude(clasificaciones__isnull=False).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
			m2_detalle_sin_clas = m2_detalle_sin_clas if m2_detalle_sin_clas is not None else 0

			m_clasificacion 	= 0
			m_clasificacion    += m2_detalle_sin_clas

			for obj in det_clasificaciones:
				m2_detalle = Local.objects.filter(visible=True, activo=activo, clasificaciones__id=obj.id).aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
				m2_detalle = m2_detalle if m2_detalle is not None else 0

				m_clasificacion += m2_detalle

				data = []
				data.append(activo.nombre)
				data.append(items.nombre)
				data.append(obj.nombre)
				data.append(m2_detalle)
				data_pdf_detalle.append(data)

			data = []
			data.append(activo.nombre)
			data.append(items.nombre)
			data.append('Sin Clasificación')
			data.append(m2_detalle_sin_clas)
			data_pdf_detalle.append(data)

			data_pdf_totales.append(['M² Total','','',m_clasificacion])

		pdf_data.append({
			'detalles'	: data_pdf_detalle,
			'totales'   : data_pdf_totales
		})

	hora 	= str(time.strftime("%X"))
	context = {'empresa': request.user.userprofile.empresa.nombre.encode(encoding='UTF-8', errors='strict'),
			   'modulo': 'M² por Clasificación', 'rut': request.user.userprofile.empresa.rut,
			   'direccion': request.user.userprofile.empresa.direccion, 'hora': hora}

	content = render_to_string('pdf/cabeceras/cabecera_default.html', context)

	with open('public/media/reportes/cabecera.html', 'w', encoding='UTF-8') as static_file:
		static_file.write(content)

	options = {
		'page-size'		: 'A4',
		'orientation'	: 'Landscape',
		'margin-top'	: '1.25in',
		'margin-right'	: '0.55in',
		'margin-bottom'	: '0.55in',
		'margin-left'	: '0.55in',
		'header-html'	: 'public/media/reportes/cabecera.html',
	}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/reportes/m_cuadrado_clasificacion.html')
	fecha 		= str(time.strftime('%d-%m-%Y'))
	hora 		= str(time.strftime("%X"))

	context = {
		'data'			: pdf_data,
		'user'			: request.user.userprofile,
		'fecha'			: fecha,
		'hora'			: hora,
	}

	html = template.render(context)  # Renders the template with the context data.

	pdfkit.from_string(html, 'public/media/reportes/metros-cuadrados-clasificacion.pdf', options=options, css=css)
	pdf = open('public/media/reportes/metros-cuadrados-clasificacion.pdf', 'rb')

	dt 			= datetime.now()
	filename 	= "".join(str(request.user.userprofile.empresa.nombre).strip().replace(' ','_'))+'-metros-cuadrados-clasificacion-' + dt.strftime('%Y%m%d') + '.pdf'

	response 						= HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=' + filename + ''
	pdf.close()
	return response  # returns the response.



class REPORTE_GARANTIA_LOCAL(View):

	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			return render(request, 'reporte_garantia_local.html', {
				'title'     : 'Reporteria',
				'href'      : 'reportes',
				'subtitle'  : 'Reportes',
				'name'      : 'Garantía por Local',
				'form'      : FiltroIngresoActivo(request=self.request)
			})

	def post(self, request):

		var_post        = request.POST.copy()

		nombre_meses    = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
							'Octubre', 'Noviembre', 'Diciembre']

		data_cabecera   = {}
		data_concepto   = list()
		count           = 0


		tipo            = int(var_post['periodos'])
		periodos        = int(var_post['cantidad_periodos'])
		activo          = var_post['activo']
		cliente         = var_post['cliente']
		conceptos       = var_post['conceptos']

		response        = calcular_periodos(tipo, periodos)

		## Se obtiene el detalle de la tabla
		if activo  != '':
			activos = Activo.objects.filter(id=activo , empresa=request.user.userprofile.empresa,
											visible=True).order_by('nombre')
		else:
			activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

		for activo in activos:

			locales = Local.objects.filter(activo_id=activo.id, visible=True)

			if cliente  != '':
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													cliente_id=cliente, visible=True).order_by('cliente', 'numero')
			else:
				contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
													visible=True).order_by('cliente', 'numero')

			for contrato in contratos:
				meses = {}
				aux = 0

				for data in response:

					if var_post['conceptos'] != '':
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  factura_detalle__concepto_id=conceptos,
															  fecha_inicio__gte=data['fecha_inicio'],
															  fecha_inicio__lte=data['fecha_termino']) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
					else:
						total_activo = Factura.objects.filter(contrato_id=contrato.id, visible=True,
															  fecha_inicio__gte=data['fecha_inicio'],
															  fecha_inicio__lte=data['fecha_termino']) \
							.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

					total_activo = total_activo if total_activo is not None else 0

					if tipo == 1:
						meses[aux]  = [str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year),formato_moneda_local(request, total_activo)]
					elif tipo ==2 or tipo == 3:
						meses[aux]  = [str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year)), formato_moneda_local(request, total_activo)]
					elif tipo == 4:
						meses[aux]  = ['Año ' + str(data['fecha_inicio'].year), formato_moneda_local(request, total_activo)]

					aux += 1

				data_concepto.append({
					'activo'    : activo.nombre,
					'cliente'   : contrato.cliente.nombre,
					'contrato'  : contrato.numero,
					'valores'   : meses
				})

		## Se obtiene Cabecera de las tablas
		for data in response:

			if tipo == 1:
				data_cabecera[count] = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
			elif tipo == 2 or tipo == 3:
				data_cabecera[count] = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
			elif tipo == 4:
				data_cabecera[count] = 'Año ' + str(data['fecha_inicio'].year)

			count += 1

		return JsonResponse({'cabecera': data_cabecera, 'data':data_concepto} , safe=False)

	def json_to_response(self):

		data = list()

		contratos = Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		for contrato in contratos:

			locales = list()
			total  	= 0

			for local in contrato.locales.all():

				garantias = list()

				for garantia in local.garantia_set.all():

					valor = garantia.valor * garantia.moneda.moneda_historial_set.all().order_by('-id').first().valor

					garantias.append({
						'id' 		: garantia.id,
						'nombre' 	: garantia.nombre,
						'total' 	: valor,
					})

					total += valor

				locales.append({
					'id'  		: local.id,
					'nombre' 	: local.nombre,
					'garantias' : garantias,
					})

			data.append({
				'id'  		: contrato.id,
				'nombre' 	: contrato.nombre_local,
				'locales' 	: locales,
				'total' 	: total,
				})

		return JsonResponse(data, safe=False)


class REPORTE_INGRESO_ACTIVO_METROS(View):

	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		return render(request, 'reporte_ingreso_metros.html', {
			'title' 	: 'Reporteria',
			'href' 		: '/reportes/ingreso-activo/metros/',
			'subtitle' 	: 'Reportes',
			'name' 		: 'Ingreso por m²',
			'form' 		: FormIngresoMetrosCuadrados(request=self.request)
		})

	def post(self, request):

		var_post 	= request.POST.copy()
		periodos  	= calcular_periodos(1, int(var_post['cantidad']), 'restar')
		activos 	= Activo.objects.filter(id__in=var_post.getlist('activos')) # self.request.user.userprofile.empresa.activo_set.all()
		conceptos 	= Concepto.objects.filter(id__in=var_post.getlist('conceptos')) # self.request.user.userprofile.empresa.concepto_set.all()
		data 		= data_report_ingreso_activo_metros(request, periodos, activos, conceptos)

		return JsonResponse(data, safe=False)

def data_report_ingreso_activo_metros(request, periodos, activos, conceptos):

	data = list()

	for activo in activos:

		locales 	= Local.objects.filter(activo=activo, visible=True)
		contratos_f = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa, visible=True)

		data_conceptos = list()

		for concepto in conceptos:

			data_ingresos = list()

			for periodo in periodos:

				total 			= Factura.objects.filter(contrato__in=contratos_f, visible=True, factura_detalle__concepto=concepto,fecha_inicio__gte=periodo['fecha_inicio'],fecha_inicio__lte=periodo['fecha_termino']).aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']
				contratos_id 	= Factura.objects.filter(visible=True, factura_detalle__concepto=concepto,fecha_inicio__gte=periodo['fecha_inicio'],fecha_inicio__lte=periodo['fecha_termino']).values_list('contrato', flat=True)
				contratos 		= Contrato.objects.filter(id__in=contratos_id)
				metros 			= 0

				for contrato in contratos:

					metros = contrato.locales.all().aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']

				ingreso 		= 0 if total is None else total
				ingreso_metros 	= 0 if metros is 0 else ingreso / metros

				data_ingresos.append({
					'fecha_inicio'		: periodo['fecha_inicio'],
					'fecha_termino'		: periodo['fecha_termino'],
					'metros' 			: metros,
					'ingreso' 			: ingreso,
					'ingreso_metros' 	: ingreso_metros,
					})

			data_conceptos.append({
				'id'		: concepto.id,
				'nombre'	: concepto.nombre,
				'ingresos'	: data_ingresos,
				})

		data.append({
			'id'		: activo.id,
			'nombre'	: activo.nombre,
			'conceptos'	: data_conceptos,
			})

	return data

def data_report_ingreso_clasificacion(request, tipo_periodo, cant_periodo, clasificacion_id, conceptos):

	#variables
	data_detalle 		= list()
	count 				= 0
	data_clasificacion 	= list()
	data_cabecera 		= {}
	data 				= list()
	data_locales 		= []

	activos 			= request.user.userprofile.empresa.activo_set.all().values_list('id', flat=True)
	periodos 			= calcular_periodos(tipo_periodo, cant_periodo, 'restar')
	contratos 			= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True)

	## Se obtiene Cabecera de las tablas
	for cab_periodo in periodos:

		if tipo_periodo == 1:
			data_cabecera[count] = str(nombre_meses[cab_periodo['fecha_inicio'].month - 1]) + ' ' + str(cab_periodo['fecha_inicio'].year)
		elif tipo_periodo == 2 or tipo_periodo == 3:
			data_cabecera[count] = str(str(nombre_meses[cab_periodo['fecha_inicio'].month - 1]) + '-' + str(cab_periodo['fecha_inicio'].year) + '  ' + str(nombre_meses[cab_periodo['fecha_termino'].month - 1]) + '-' + str(cab_periodo['fecha_termino'].year))
		elif tipo_periodo == 4:
			data_cabecera[count] = 'Año ' + str(cab_periodo['fecha_inicio'].year)
		count += 1

	##Obtengo todos lo locales y el primero si es que existen mas de 2 en el contrato
	for item_contrato in contratos:
		if item_contrato.locales.all().first().id not in data_locales:
			data_locales.append(item_contrato.locales.all().first().id)

	## Se total de clasificaciones
	clasificaciones = Clasificacion.objects.filter(id__in=clasificacion_id, empresa=request.user.userprofile.empresa, visible=True, tipo_clasificacion_id=1).order_by('nombre')

	for clasificacion in clasificaciones:

		det_clasificaciones = Clasificacion_Detalle.objects.filter(clasificacion=clasificacion)
		locales_sin_clas 	= Local.objects.filter(visible=True, activo__in=activos, id__in=data_locales).exclude(clasificaciones__isnull=False).values_list('id', flat=True)
		#Locales con clasificacion
		for items in det_clasificaciones:

			locales 	= Local.objects.filter(visible=True, activo__in=activos, id__in=data_locales, clasificaciones=items).exclude(clasificaciones__isnull=True).values_list('id', flat=True)
			contratos 	= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True, locales__in=locales)
			meses 		= {}
			meses_format= {}
			aux 		= 0

			for periodo in periodos:

				total_clasificacion = Factura.objects.filter(contrato_id__in=contratos, visible=True,
															 factura_detalle__concepto__in=conceptos,
															 fecha_inicio__gte=periodo['fecha_inicio'],
															 fecha_inicio__lte=periodo['fecha_termino']) \
					.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

				total_clasificacion = total_clasificacion if total_clasificacion is not None else 0
				if tipo_periodo == 1:

					nom_cabecera = str(nombre_meses[periodo['fecha_inicio'].month - 1]) + ' ' + str(periodo['fecha_inicio'].year)

				elif tipo_periodo == 2 or tipo_periodo == 3:

					nom_cabecera = str(str(nombre_meses[periodo['fecha_inicio'].month - 1]) + '-' + str(periodo['fecha_inicio'].year) + '  ' + str(nombre_meses[periodo['fecha_termino'].month - 1]) + '-' + str(periodo['fecha_termino'].year))

				elif tipo_periodo == 4:
					nom_cabecera = 'Año ' + str(periodo['fecha_inicio'].year)

				meses[aux] 			= [nom_cabecera, total_clasificacion]
				meses_format[aux] 	= [nom_cabecera, formato_moneda_local(request, total_clasificacion)]
				aux += 1

			data_detalle.append({
				'detalle_clasificacion'	: items.nombre,
				'valores'				: meses,
				'valores_formateado'    : meses_format
			})

		## Se total de locales sin clasificacion
		contratos 	= Contrato.objects.filter(empresa=request.user.userprofile.empresa, visible=True, locales__in=locales_sin_clas)
		meses 		= {}
		meses_format= {}
		aux 		= 0
		for periodo in periodos:

			total_clasificacion = Factura.objects.filter(contrato_id__in=contratos, visible=True,
														 factura_detalle__concepto__in=conceptos,
														 fecha_inicio__gte=periodo['fecha_inicio'],
														 fecha_inicio__lte=periodo['fecha_termino']) \
				.aggregate(Sum('factura_detalle__total'))['factura_detalle__total__sum']

			total_clasificacion = total_clasificacion if total_clasificacion is not None else 0

			if tipo_periodo == 1:

				nom_cabecera = str(nombre_meses[periodo['fecha_inicio'].month - 1]) + ' ' + str(periodo['fecha_inicio'].year)

			elif tipo_periodo == 2 or tipo_periodo == 3:

				nom_cabecera = str(str(nombre_meses[periodo['fecha_inicio'].month - 1]) + '-' + str(periodo['fecha_inicio'].year) + '  ' + str(nombre_meses[periodo['fecha_termino'].month - 1]) + '-' + str(periodo['fecha_termino'].year))

			elif tipo_periodo == 4:

				nom_cabecera = 'Año ' + str(periodo['fecha_inicio'].year)

			meses[aux] 			= [nom_cabecera, total_clasificacion]
			meses_format[aux] 	= [nom_cabecera, formato_moneda_local(request, total_clasificacion)]

			aux += 1

		data_detalle.append({
			'detalle_clasificacion'	: 'Sin Clasificación',
			'valores'				: meses,
			'valores_formateado'	: meses_format
		})
		data_clasificacion.append({
			'clasificacion' : clasificacion.nombre,
			'detalles'      : data_detalle
		})

	data.append({
		'cabecera'	: data_cabecera,
		'data'		: data_clasificacion
	})

	return data