
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


        tipo 		    = int(var_post['periodos'])
        periodos 	    = int(var_post['cantidad_periodos'])
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
	nombre_meses 	= ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
						'Octubre', 'Noviembre', 'Diciembre']

	tipo 			= int(var_post['periodos'])
	periodos 		= int(var_post['cantidad_periodos'])
	activo 			= var_post['activo']
	cliente 		= var_post['cliente']
	conceptos 		= var_post['conceptos']

	response 		= calcular_periodos(tipo, periodos)

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
	if activo != '':
		activos = Activo.objects.filter(id=activo, empresa=request.user.userprofile.empresa,
										visible=True).order_by('nombre')
	else:
		activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

	for activo in activos:

		locales = Local.objects.filter(activo_id=activo.id, visible=True)

		if cliente != '':
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
												cliente_id=cliente, visible=True).order_by('cliente', 'numero')
		else:
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
												visible=True).order_by('cliente', 'numero')

		for contrato in contratos:
			x = []
			x.append(activo.nombre)
			x.append(contrato.cliente.nombre)
			x.append(contrato.numero)

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
	nombre_meses 	= ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
						'Octubre', 'Noviembre', 'Diciembre']

	tipo 			= int(var_post['periodos'])
	periodos 		= int(var_post['cantidad_periodos'])
	activo 			= var_post['activo']
	cliente 		= var_post['cliente']
	conceptos 		= var_post['conceptos']

	response 		= calcular_periodos(tipo, periodos)


	## Se obtiene Cabecera de las tablas
	for data in response:

		cabecera  = ''
		if tipo == 1:
			cabecera = str(nombre_meses[data['fecha_inicio'].month - 1]) + ' ' + str(data['fecha_inicio'].year)
		elif tipo == 2 or tipo == 3:
			cabecera = str(str(nombre_meses[data['fecha_inicio'].month - 1]) + '-' + str(data['fecha_inicio'].year) + '  ' + str(nombre_meses[data['fecha_termino'].month - 1]) + '-' + str(data['fecha_termino'].year))
		elif tipo == 4:
			cabecera = 'Año ' + str(data['fecha_inicio'].year)

		data_cabecera.append(cabecera)


	## Se obtiene el detalle de la tabla
	if activo != '':
		activos = Activo.objects.filter(id=activo, empresa=request.user.userprofile.empresa,
										visible=True).order_by('nombre')
	else:
		activos = Activo.objects.filter(empresa=request.user.userprofile.empresa, visible=True).order_by('nombre')

	for activo in activos:

		locales = Local.objects.filter(activo_id=activo.id, visible=True)

		if cliente != '':
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
												cliente_id=cliente, visible=True).order_by('cliente', 'numero')
		else:
			contratos = Contrato.objects.filter(locales__in=locales, empresa=request.user.userprofile.empresa,
												visible=True).order_by('cliente', 'numero')

		for contrato in contratos:
			x = []
			x.append(activo.nombre)
			x.append(contrato.cliente.nombre)
			x.append(contrato.numero)

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