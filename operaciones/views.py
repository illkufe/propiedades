# -*- coding: utf-8 -*-a
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.views.generic import ListView, FormView, CreateView, DeleteView, UpdateView, View
from xlrd import open_workbook
from datetime import datetime

from activos.models import Activo
from locales.models import Local
from utilidades.views import sumar_meses, formato_moneda_local

from .forms import *
from .models import *


# variables
modulo 		= 'Operaciones'
meses 		= ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
tipos 		= ['Electicidad','Agua y Alcantarillado','Gas']
unidades 	= ['kWh', 'm3', 'kg']


# lecturas
class LecturaMedidorList(ListView):

	model 			= Lectura_Electricidad
	template_name 	= 'lectura_medidor_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(LecturaMedidorList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Lectura Medidores'
		context['name'] 	= 'Lista'
		context['href'] 	= 'lectura-medidores'

		return context

	def get_queryset(self):

		queryset 		= []
		meses 			= ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

		activos 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)
		locales 		= Local.objects.filter(activo_id__in=activos, visible=True).values_list('id', flat=True)
		medidores_luz	= Medidor_Electricidad.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)
		medidores_agua 	= Medidor_Agua.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)
		medidores_gas 	= Medidor_Gas.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)

		lectura_electricidad 	= Lectura_Electricidad.objects.filter(medidor_electricidad__in=medidores_luz, visible=True)
		lectura_agua 			= Lectura_Agua.objects.filter(medidor_agua__in=medidores_agua, visible=True)
		lectura_gas 			= Lectura_Gas.objects.filter(medidor_gas__in=medidores_gas, visible=True)

		for item in lectura_electricidad:
			item.nombre = item.medidor_electricidad.nombre
			item.local 	= item.medidor_electricidad.local.nombre
			item.activo = item.medidor_electricidad.local.activo
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= 'Electricidad'
			item.url 	= 'electricidad'
			queryset.append(item)

		for item in lectura_agua:
			item.nombre = item.medidor_agua.nombre
			item.local 	= item.medidor_agua.local.nombre
			item.activo = item.medidor_agua.local.activo
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= 'Agua'
			item.url 	= 'agua'
			queryset.append(item)

		for item in lectura_gas:
			item.nombre = item.medidor_gas.nombre
			item.local 	= item.medidor_gas.local.nombre
			item.activo = item.medidor_gas.local.activo
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= 'Gas'
			item.url 	= 'gas'
			queryset.append(item)

		return queryset

class LECTURASMEDIDOR(View):
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		activos 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)
		locales 		= Local.objects.filter(activo_id__in=activos, visible=True).values_list('id', flat=True)

		medidores_luz 	= Medidor_Electricidad.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)
		medidores_agua 	= Medidor_Agua.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)
		medidores_gas 	= Medidor_Gas.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)

		if id == None:
			self.lectura_electricidad 	= Lectura_Electricidad.objects.filter(medidor_electricidad__in=medidores_luz, visible=True)
			self.lectura_agua 			= Lectura_Agua.objects.filter(medidor_agua__in=medidores_agua, visible=True)
			self.lectura_gas 			= Lectura_Gas.objects.filter(medidor_gas__in=medidores_gas, visible=True)
		else:

			self.lectura_electricidad 	= Lectura_Electricidad.objects.filter(pk=id, medidor_electricidad__in=medidores_luz, visible=True)
			self.lectura_agua	 		= Lectura_Agua.objects.filter(pk=id, medidor_agua__in=medidores_agua, visible=True)
			self.lectura_gas 			= Lectura_Gas.objects.filter(pk=id, medidor_gas__in=medidores_gas, visible=True)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def post(self, request):

		tempfile 	= request.FILES.get('file')

		book 		= open_workbook(filename=None, file_contents=tempfile.read())
		sheet 		= book.sheet_by_index(0)
		keys 		= [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
		title_excel = ['N° Rotulo', 'Tipo Medidor', 'Lectura Medidor', 'Mes', 'Ano']

		errors 	= list()
		estado 	= 'ok'
		tipo 	= ''

		if len(set(title_excel) & set(keys)) == 5:

			dict_list = []
			for row_index in range(1, sheet.nrows):
				d = {keys[col_index]: sheet.cell(row_index, col_index).value for col_index in
					 range(sheet.ncols)}
				dict_list.append(d)
			cont = 1

			for i in dict_list:
				list_error = list()

				try:
					list_error = self.validate_data(i['N° Rotulo'], i['Tipo Medidor'], i['Lectura Medidor'],
													i['Mes'], i['Ano'])
					if list_error:
						estado 	= 'error'
						tipo 	= 'data'

						errors.append({
							'row'			: cont,
							'rotulo'		: i['N° Rotulo'],
							'medidor'		: i['Tipo Medidor'],
							'lectura'		: i['Lectura Medidor'],
							'mes'			: i['Mes'],
							'ano'			: i['Ano'],
							'error'			: list_error
						})

				except ValueError as a:
					estado 	= 'error'
					tipo 	= 'data'
					list_error.append(a)

					errors.append({
						'row'		: cont,
						'rotulo'		: i['N° Rotulo'],
						'medidor'		: i['Tipo Medidor'],
						'lectura'		: i['Lectura Medidor'],
						'mes'			: i['Mes'],
						'ano'			: i['Ano'],
						'error'			: list_error
					})
				cont += 1
		else:
			estado = 'error'
			tipo = 'formato'

			errors.append({
				'error'		: 'Formato de Excel subido es incorrecto.'
			})


		if not errors:

			for i in dict_list:

				rotulo 			= i['N° Rotulo']
				tipo_medidor	= i['Tipo Medidor']
				lectura			= i['Lectura Medidor']
				mes				= int(i['Mes'])
				ano				= int(i['Ano'])

				if str(tipo_medidor).upper() == 'ELECTRICIDAD':

					medidores_luz = Medidor_Electricidad.objects.filter(numero_rotulo=rotulo, visible=True)

					if Lectura_Electricidad.objects.filter(medidor_electricidad__in=medidores_luz, visible=True, mes=mes, anio=ano).exists():

						electricidad_update 		= Lectura_Electricidad.objects.get(mes=mes, anio=ano, medidor_electricidad__numero_rotulo=rotulo)
						electricidad_update.valor 	= lectura
						electricidad_update.save()

					else:

						electricidad_new 						= Lectura_Electricidad()
						electricidad_new.mes 					= mes
						electricidad_new.anio 					= ano
						electricidad_new.valor 					= lectura
						electricidad_new.user   				= self.request.user
						electricidad_new.medidor_electricidad 	= medidores_luz.first()
						electricidad_new.save()


				elif str(tipo_medidor).upper() == 'AGUA':

					medidores_agua = Medidor_Agua.objects.filter(numero_rotulo=rotulo, visible=True)

					if Lectura_Agua.objects.filter(medidor_agua__in=medidores_agua, visible=True, mes=mes, anio=ano).exists():

						agua_update 		= Lectura_Agua.objects.get(mes=mes, anio=ano, medidor_agua__numero_rotulo=rotulo)
						agua_update.valor 	= lectura
						agua_update.save()

					else:
						agua_new 				= Lectura_Agua()
						agua_new.mes 			= mes
						agua_new.anio 			= ano
						agua_new.valor 			= lectura
						agua_new.user   		= self.request.user
						agua_new.medidor_agua	= medidores_agua.first()
						agua_new.save()

				elif str(tipo_medidor).upper() == 'GAS':

					medidores_gas = Medidor_Gas.objects.filter(numero_rotulo=rotulo, visible=True)

					if Lectura_Gas.objects.filter(medidor_gas__in=medidores_gas, visible=True, mes=mes, anio=ano).exists():

						gas_update 			= Lectura_Gas.objects.get(mes=mes, anio=ano, medidor_gas__numero_rotulo=rotulo)
						gas_update.valor 	= lectura
						gas_update.save()

					else:

						gas_new 			= Lectura_Gas()
						gas_new.mes 		= mes
						gas_new.anio 		= ano
						gas_new.valor 		= lectura
						gas_new.user   		= self.request.user
						gas_new.medidor_gas	= medidores_gas.first()
						gas_new.save()


		if self.request.is_ajax():
			data = {
				'estado': estado,
				'tipo'	: tipo,
				'errors': errors,
			}
			return JsonResponse(data)
		else:
			return render(request, 'lectura_medidor_list.html')

	def validate_data(self, rotulo, tipo_medidor, lectura, mes, ano):

		list_error = list()

		activos 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)
		locales 		= Local.objects.filter(activo_id__in=activos, visible=True).values_list('id', flat=True)

		estado_mes_ano 		= True
		fecha_mes_anterior 	= ''

		## Validación de mes.
		try:
			int(mes)

			if mes > 12 or mes <= 0:
				error = "Número de mes erroneo."
				list_error.append(error)

		except Exception:
			error = "Mes ingresado invalido."
			list_error.append(error)
			estado_mes_ano = False

		## Validación del año.
		try:
			int(ano)

			today = datetime.now()

			if ano > today.year:
				error = "Año no puede ser mayor al año actual."
				list_error.append(error)

		except Exception:
			error = "Año ingresado invalido."
			list_error.append(error)
			estado_mes_ano = False


		##Validación de lectura de medidor.
		try:
			int(lectura)
			if int(lectura) <=0:
				error = "Lectura de Medidor invalido."
				list_error.append(error)
		except Exception:
			error = "Lectura de Medidor invalido."
			list_error.append(error)

		## Validación de Nro Rotulo de Medidor
		if str(tipo_medidor).upper() == 'ELECTRICIDAD':
			medidores_luz 	= Medidor_Electricidad.objects.filter(local__in=locales, visible=True, numero_rotulo=rotulo).exists()

			if not medidores_luz:
				error = "Medidor de Electricidad no existe."
				list_error.append(error)

		elif str(tipo_medidor).upper() == 'GAS':
			medidores_gas 	= Medidor_Gas.objects.filter(local__in=locales, visible=True, numero_rotulo=rotulo).exists()

			if not medidores_gas:
				error = "Medidor de Gas no existe."
				list_error.append(error)


		elif str(tipo_medidor).upper() == 'AGUA':
			medidores_agua 	= Medidor_Agua.objects.filter(local__in=locales, visible=True, numero_rotulo=rotulo).exists()

			if not medidores_agua:
				error = "Medidor de Agua no existe."
				list_error.append(error)

		else:
			error = "Tipo de medidor erroneo."
			list_error.append(error)


		## Validación de lectura de medidor mayor a mes anterior
		if estado_mes_ano:

			fecha_mes_anterior  = self.calculo_mes_anterior(mes, ano)

			##Validación de existencia de fecha del mes anterior
			if fecha_mes_anterior:
				try:
					lectura_luz = Lectura_Electricidad.objects.get(medidor_electricidad__numero_rotulo=rotulo,
																   visible=True, mes=fecha_mes_anterior.month,
																   anio=fecha_mes_anterior.year)
					if lectura < lectura_luz.valor:
						error = "Nueva Lectura es menor a la anterior."
						list_error.append(error)
				except Exception:
					pass

				try:
					lectura_gas = Lectura_Gas.objects.get(medidor_gas__numero_rotulo=rotulo,
														  visible=True, mes=fecha_mes_anterior.month,
														  anio=fecha_mes_anterior.year)
					if lectura < lectura_gas.valor:
						error = "Nueva Lectura es menor a la anterior."
						list_error.append(error)
				except Exception:
					pass

				try:

					lectura_agua = Lectura_Agua.objects.get(medidor_agua__numero_rotulo=rotulo,
															visible=True, mes=fecha_mes_anterior.month,
															anio=fecha_mes_anterior.year)
					if lectura < lectura_agua.valor:
						error = "Nueva Lectura es menor a la anterior."
						list_error.append(error)
				except Exception:
					pass


		return list_error

	def calculo_mes_anterior(self, mes,ano):

		try:
			fecha_string 	= '01' + '/' + str(int(mes)) + '/' + str(int(ano))
			fecha_calcular  = datetime.strptime(fecha_string, "%d/%m/%Y")
			fecha_anterior  = sumar_meses(fecha_calcular, -1)
		except Exception as a:
			asd = a
			fecha_anterior = ''

		return fecha_anterior

	def json_to_response(self):

		meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
				 "Noviembre", "Diciembre"]

		data 				= list()
		data_electricidad 	= list()
		data_agua			= list()
		data_gas			= list()

		for item_e in self.lectura_electricidad:
			data_electricidad.append({
				'id'		: item_e.id,
				'nombre' 	: item_e.medidor_electricidad.nombre,
				'local'		: item_e.medidor_electricidad.local.nombre,
				'activo' 	: item_e.medidor_electricidad.local.activo.nombre,
				'mes' 		: meses[int(item_e.mes)-1],
				'anio'		: item_e.anio,
				'lectura'	: item_e.valor,
				'creado'	: item_e.creado_en,
				'image'		: '' if not item_e.imagen_file else str(item_e.imagen_file),
				'tipo' 		: 'Electricidad',
				'url' 		: 'electricidad',
			})

		for item_a in self.lectura_agua:
			data_agua.append({
				'id'		: item_a.id,
				'nombre' 	: item_a.medidor_agua.nombre,
				'local'		: item_a.medidor_agua.local.nombre,
				'activo' 	: item_a.medidor_agua.local.activo.nombre,
				'mes' 		: meses[int(item_a.mes)-1],
				'anio'		: item_a.anio,
				'lectura'	: item_a.valor,
				'creado'	: item_a.creado_en,
				'image'		: '' if not item_a.imagen_file else str(item_a.imagen_file),
				'tipo' 		: 'Agua',
				'url' 		: 'agua',
			})

		for item_g in self.lectura_gas:

			data_gas.append({
				'id'		: item_g.id,
				'nombre'	: item_g.medidor_gas.nombre,
				'local'		: item_g.medidor_gas.local.nombre,
				'activo' 	: item_g.medidor_gas.local.activo.nombre,
				'mes' 		: meses[int(item_g.mes ) -1],
				'anio'		: item_g.anio,
				'lectura'	: item_g.valor,
				'creado'	: item_g.creado_en,
				'image'		: '' if not item_g.imagen_file else str(item_g.imagen_file),
				'tipo' 		: 'Gas',
				'url' 		: 'gas',
			})

		data.append({
			'luz'		: data_electricidad,
			'agua'		: data_agua,
			'gas'		: data_gas,
		})

		return JsonResponse(data, safe=False)

# lecturas electricidad
class LecturaElectricidadMixin(object):

	template_name 	= 'lectura_electricidad_new.html'
	form_class 		= LecturaElectricidadForm
	success_url 	= '/lectura-medidores/list'

	def form_invalid(self, form):

		response = super(LecturaElectricidadMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			lectura 		= Lectura_Electricidad.objects.get(medidor_electricidad_id= obj.medidor_electricidad.id, mes=obj.mes, anio=obj.anio)
			lectura.valor 	= obj.valor
			lectura.user 	= obj.user
			lectura.visible = True
			lectura.save()
		except Exception:
			obj.save()

		response = super(LecturaElectricidadMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class LecturaElectricidadNew(LecturaElectricidadMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaElectricidadNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de electricidad'
		context['name'] 	= 'nueva'
		context['href'] 	= '/lectura-medidores/list'
		context['accion']	 = 'create'

		return context

class LecturaElectricidadDelete(DeleteView):

	model 		= Lectura_Electricidad
	success_url = reverse_lazy('/lectura-medidores/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class LecturaElectricidadUpdate(LecturaElectricidadMixin, UpdateView):

	model 			= Lectura_Electricidad
	form_class 		= LecturaElectricidadForm
	template_name 	= 'lectura_electricidad_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaElectricidadUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor electricidad'
		context['name'] 	= 'editar'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'update'

		return context


# lecturas agua
class LecturaAguaMixin(object):

	template_name 	= 'lectura_agua_new.html'
	form_class 		= LecturaAguaForm
	success_url 	= '/lectura-medidores/list'

	def form_invalid(self, form):

		response = super(LecturaAguaMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			lectura 		= Lectura_Agua.objects.get(medidor_agua_id= obj.medidor_agua.id, mes=obj.mes, anio=obj.anio)
			lectura.valor 	= obj.valor
			lectura.user 	= obj.user
			lectura.visible = True
			lectura.save()
		except Exception:
			obj.save()

		response = super(LecturaAguaMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class LecturaAguaNew(LecturaAguaMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaAguaNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de Agua'
		context['name'] 	= 'nueva'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'create'

		return context

class LecturaAguaDelete(DeleteView):

	model 		= Lectura_Agua
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class LecturaAguaUpdate(LecturaAguaMixin, UpdateView):

	model 			= Lectura_Agua
	form_class 		= LecturaAguaForm
	template_name 	= 'lectura_agua_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaAguaUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de agua'
		context['name'] 	= 'editar'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'update'

		return context


# lecturas gas
class LecturaGasMixin(object):

	template_name 	= 'lectura_gas_new.html'
	form_class 		= LecturaGasForm
	success_url 	= '/lectura-medidores/list'

	def form_invalid(self, form):

		response = super(LecturaGasMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			lectura 		= Lectura_Gas.objects.get(medidor_gas_id= obj.medidor_gas.id, mes=obj.mes, anio=obj.anio)
			lectura.valor 	= obj.valor
			lectura.user 	= obj.user
			lectura.visible = True
			lectura.save()
		except Exception:
			obj.save()

		response = super(LecturaGasMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class LecturaGasNew(LecturaGasMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaGasNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de gas'
		context['name'] 	= 'nueva'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'create'
		return context

class LecturaGasDelete(DeleteView):

	model 		= Lectura_Gas
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class LecturaGasUpdate(LecturaGasMixin, UpdateView):

	model 			= Lectura_Gas
	form_class 		= LecturaGasForm
	template_name 	= 'lectura_gas_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaGasUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de gas'
		context['name'] 	= 'editar'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'update'
		return context


# gasto servicios basicos
class GastoServicioBasicoList(ListView):

	model 			= Gasto_Servicio_Basico
	template_name 	= 'gasto_servicio_basico_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(GastoServicioBasicoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Gasto Servicios Básicos'
		context['name'] 	= 'Lista'
		context['href'] 	= 'list'

		return context

	def get_queryset(self):

		queryset = Gasto_Servicio_Basico.objects.filter(activo__empresa=self.request.user.userprofile.empresa, visible=True)

		for item in queryset:

			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= tipos[int(item.tipo)-1]
			item.valor  = formato_moneda_local(self.request, item.valor, item.moneda.id)


		return queryset

class GastoServicioBasicoMixin(object):

	template_name 	= 'gasto_servicio_basico_new.html'
	form_class 		= GastoServicioBasicoForm
	success_url 	= '/gasto-servicios-basicos/list'

	def get_form_kwargs(self):

		kwargs 				= super(GastoServicioBasicoMixin, self).get_form_kwargs()
		kwargs['request'] 	= self.request

		return kwargs

	def form_invalid(self, form):

		response = super(GastoServicioBasicoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa

		if Gasto_Servicio_Basico.objects.filter(tipo= obj.tipo, mes=obj.mes, anio=obj.anio).exists():

			Gasto_Servicio_Basico.objects.get(tipo= obj.tipo, mes=obj.mes, anio=obj.anio).delete()

		obj.save()

		response = super(GastoServicioBasicoMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class GastoServicioBasicoNew(GastoServicioBasicoMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(GastoServicioBasicoNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Gasto Servicios Básicos'
		context['name'] 	= 'nueva'
		context['href'] 	= 'list'
		context['accion'] 	= 'create'
		return context

class GastoServicioBasicoDelete(DeleteView):

	model 		= Gasto_Servicio_Basico
	success_url = reverse_lazy('/gasto-servicios-basicos/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class GastoServicioBasicoUpdate(GastoServicioBasicoMixin, UpdateView):

	model 			= Gasto_Servicio_Basico
	form_class 		= GastoServicioBasicoForm
	template_name 	= 'gasto_servicio_basico_new.html'
	success_url 	= '/gasto-servicios-basicos/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(GastoServicioBasicoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Gasto Servicios Básicos'
		context['name'] 	= 'editar'
		context['href'] 	= 'list'
		context['accion'] 	= 'update'
		return context

# gasto servicios basicos
class TarifaServicioBasicoList(ListView):

	model 			= Tarifa_Servicio_Basico
	template_name 	= 'tarifa_servicio_basico_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(TarifaServicioBasicoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Tarifa Servicios Básicos'
		context['name'] 	= 'Lista'
		context['href'] 	= 'list'

		return context

	def get_queryset(self):

		queryset = Tarifa_Servicio_Basico.objects.filter(activo__empresa=self.request.user.userprofile.empresa, visible=True)

		for item in queryset:

			item.unidad = unidades[int(item.tipo)-1]
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= tipos[int(item.tipo)-1]

		return queryset

class TarifaServicioBasicoMixin(object):

	template_name 	= 'tarifa_servicio_basico_new.html'
	form_class 		= TarifaServicioBasicoForm
	success_url 	= '/tarifa-servicios-basicos/list'

	def get_form_kwargs(self):

		kwargs 				= super(TarifaServicioBasicoMixin, self).get_form_kwargs()
		kwargs['request'] 	= self.request

		return kwargs

	def form_invalid(self, form):

		response = super(TarifaServicioBasicoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa

		if Tarifa_Servicio_Basico.objects.filter(tipo= obj.tipo, mes=obj.mes, anio=obj.anio).exists():

			Tarifa_Servicio_Basico.objects.get(tipo= obj.tipo, mes=obj.mes, anio=obj.anio).delete()

		obj.save()

		response = super(TarifaServicioBasicoMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class TarifaServicioBasicoNew(TarifaServicioBasicoMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(TarifaServicioBasicoNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Tarifa Servicios Básicos'
		context['name'] 	= 'nueva'
		context['href'] 	= 'list'
		context['accion'] 	= 'create'
		return context

class TarifaServicioBasicoDelete(DeleteView):

	model 		= Tarifa_Servicio_Basico
	success_url = reverse_lazy('/tarifa-servicios-basicos/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class TarifaServicioBasicoUpdate(TarifaServicioBasicoMixin, UpdateView):

	model 			= Tarifa_Servicio_Basico
	form_class 		= TarifaServicioBasicoForm
	template_name 	= 'tarifa_servicio_basico_new.html'
	success_url 	= '/tarifa-servicios-basicos/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(TarifaServicioBasicoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Tarifa Servicios Básicos'
		context['name'] 	= 'editar'
		context['href'] 	= 'list'
		context['accion'] 	= 'update'

		return context

