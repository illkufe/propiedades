# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from django.core import serializers
from conceptos.models import *
from procesos.models import *

from .models import *
from .forms import *

import json

# variables
modulo 	= 'Configuración'


# cliente
class ClienteList(ListView):

	model 			= Cliente
	template_name 	= 'cliente_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ClienteList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'clientes'
		context['name'] 	= 'lista'
		context['href'] 	= '/clientes/list'
		
		return context

	def get_queryset(self):

		queryset 	= Cliente.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

class ClienteMixin(object):

	template_name 	= 'cliente_new.html'
	form_class 		= ClienteForm
	success_url 	= '/clientes/list'

	def form_invalid(self, form):

		response = super(ClienteMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context 			= self.get_context_data()
		form_representante 	= context['representante_form']

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa
		obj.save()
		form.save_m2m()


		if form_representante.is_valid():
			self.object 				= form.save(commit=False)
			form_representante.instance = self.object
			form_representante.save()


		cliente  =  Cliente.objects.filter(id=obj.id)

		response = super(ClienteMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {
				'estado' 	: True,
				'id'		: obj.id,
				'nombre'	: obj.nombre,
				}
			return JsonResponse(data)
		else:
			return response

class ClienteNew(ClienteMixin, FormView):

	def get_context_data(self, **kwargs):

		context 					= super(ClienteNew, self).get_context_data(**kwargs)
		context['title'] 			= modulo
		context['subtitle'] 		= 'clientes'
		context['name'] 			= 'nuevo'
		context['href'] 			= '/clientes/list'
		context['accion'] 			= 'create'

		cliente_id  				= self.kwargs.pop('pk', None)
		data        				= obtener_clasificacion(self, cliente_id)
		context['clasificaciones'] 	= data

		if self.request.POST:
			context['representante_form'] = ClienteFormSet(self.request.POST)
		else:
			context['representante_form'] = ClienteFormSet()

		return context
	
class ClienteUpdate(ClienteMixin, UpdateView):

	model 			= Cliente
	form_class 		= ClienteForm
	template_name 	= 'cliente_new.html'
	success_url 	= '/clientes/list'

	def get_context_data(self, **kwargs):

		context 					= super(ClienteUpdate, self).get_context_data(**kwargs)
		context['title'] 			= modulo
		context['subtitle'] 		= 'cliente'
		context['name'] 			= 'editar'
		context['href'] 			= '/clientes/list'
		context['accion'] 			= 'update'

		cliente_id  				= self.kwargs.pop('pk', None)
		data        				= obtener_clasificacion(self, cliente_id)
		context['clasificaciones'] 	= data


		if self.request.POST:
			context['representante_form'] = ClienteFormSet(self.request.POST, instance=self.object)
		else:
			context['representante_form'] = ClienteFormSet(instance=self.object)

		return context

class ClienteUpdatePortal(ClienteMixin, UpdateView):

	model 			= Cliente
	form_class 		= ClienteForm
	template_name 	= 'portal_cliente/cliente_portal_new.html'
	success_url 	= '/'

	def get_context_data(self, **kwargs):

		context 					= super(ClienteUpdatePortal, self).get_context_data(**kwargs)
		context['title'] 			= 'Datos Generales'
		context['subtitle'] 		= 'cliente'
		context['name'] 			= 'editar'
		context['href'] 			= ''
		context['accion'] 			= 'update'

		cliente_id  				= self.kwargs.pop('pk', None)
		data        				= obtener_clasificacion(self, cliente_id)
		context['clasificaciones'] 	= data
		context['facturas']			= facturas_generadas(self)


		if self.request.POST:
			context['representante_form'] = ClienteFormSet(self.request.POST, instance=self.object)
		else:
			context['representante_form'] = ClienteFormSet(instance=self.object)

		return context

class ClienteDelete(DeleteView):
	model = Cliente
	success_url = reverse_lazy('/clientes/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)


# conexión conceptos
class ConexionConceptoList(ListView):

	model 			= Cliente
	template_name 	= 'conexion_concepto_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ConexionConceptoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'clientes'
		context['name'] 	= 'lista'
		context['href'] 	= '/clientes/list'
		
		return context

	def get_queryset(self):

		queryset = Cliente.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

def obtener_clasificacion(self, cliente_id):

	cabeceras = self.request.user.userprofile.empresa.clasificacion_set.filter(visible=True, tipo_clasificacion=2)
	cabecera = list()

	if cliente_id is None:

		for c in cabeceras:

			detalles = Clasificacion_Detalle.objects.filter(clasificacion=c)
			detalle = list()

			for d in detalles:
				detalle.append({
					'id': d.id,
					'nombre': d.nombre,
					'select': False
				})

			cabecera.append({
				'id': c.id,
				'nombre': c.nombre,
				'detalle': detalle
			})
	else:
		for c in cabeceras:

			detalles = Clasificacion_Detalle.objects.filter(clasificacion=c)
			detalle = list()

			for d in detalles:
				detalle.append({
					'id': d.id,
					'nombre': d.nombre,
					'select': False if not d.cliente_set.filter(id=cliente_id).exists() else True
				})

			cabecera.append({
				'id': c.id,
				'nombre': c.nombre,
				'detalle': detalle
			})

	return cabecera

def facturas_generadas(self):
	contratos_cliente = self.request.user.userprofile.cliente.contrato_set.values_list('id', flat=True)
	try:
		facturas = Factura.objects.filter(contrato_id__in=contratos_cliente, estado_id=2).__bool__()
	except Exception:
		facturas = False

	return facturas


# conexion parametro
class CONEXION_PARAMETRO(View):

	http_method_names =  ['get', 'post']

	def get(self, request, id=None):

		self.object_list = request.user.userprofile.empresa.conexion

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			return render(request, 'conexion_parametro_list.html', {
				'title' 	: 'Conexión',
				'href' 		: 'conexion-parametro',
				'subtitle'	: 'Parametros Generales',
				'name' 		: 'Configuración',
				})
	
	def post(self, request):

		try:
			var_post 	= request.POST.copy()
			parametros 	= json.loads(var_post['parametros'])
			
			for item in parametros:

				if item['id'] is not '':

					parametro = Conexion.objects.get(id=item['id'])

					if item['eliminar'] == 'true':
						parametro.delete()
					else:
						parametro.nombre 	= item['nombre']
						parametro.codigo 	= item['codigo']
						parametro.codigo_1 	= item['codigo_1']
						parametro.codigo_2 	= item['codigo_2']
						parametro.codigo_3 	= item['codigo_3']
						parametro.codigo_4 	= item['codigo_4']
						parametro.save()
				else:

					if item['eliminar'] == 'false':

						Conexion(
							nombre 		= item['nombre'],
							codigo 		= item['codigo'],
							codigo_1 	= item['codigo_1'],
							codigo_2 	= item['codigo_2'],
							codigo_3 	= item['codigo_3'],
							codigo_4 	= item['codigo_4'],
							empresa 	= request.user.userprofile.empresa,
						).save()
				
			estado = True
					
		except Exception as asd:
			print(asd)
			
			estado = False

		return JsonResponse({'estado': estado}, safe=False)

	def json_to_response(self):

		data = list()

		# for item in self.object_list:

		data.append({
			'id' 					: self.object_list.id,
			'cod_condicion_venta' 	: self.object_list.cod_condicion_venta,
			'cod_bodega_salida' 	: self.object_list.cod_bodega_salida,
			'cod_vendedor' 			: self.object_list.cod_vendedor,
			'cod_sucursal' 			: self.object_list.cod_sucursal,
			'cod_lista_precio' 		: self.object_list.cod_lista_precio,

			})

		return JsonResponse(data, safe=False)

# conexion cliente
class CONEXION_CLIENTE(View):

	http_method_names =  ['get', 'post']

	def get(self, request, id=None):

		self.object_list = request.user.userprofile.empresa.cliente_set.all()

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			return render(request, 'conexion_cliente_list.html', {
				'title' 	: 'Conexión',
				'href' 		: 'conexion-cliente',
				'subtitle'	: 'Clientes',
				'name' 		: 'Configuración',
				})
	
	def post(self, request):

		try:
			var_post 	= request.POST.copy()
			clientes 	= json.loads(var_post['clientes'])
			
			for item in clientes:

				cliente = Cliente.objects.get(id=item['id'])

				cliente.codigo_1 	= item['codigo_1']
				cliente.codigo_2 	= item['codigo_2']
				cliente.codigo_3 	= item['codigo_3']
				cliente.codigo_4 	= item['codigo_4']

				cliente.save()
				estado = True
					
		except Exception:

			estado = False

		return JsonResponse({'estado': estado}, safe=False)

	def json_to_response(self):

		data = list()

		for item in self.object_list:

			data.append({
				'id' 		: item.id,
				'nombre' 	: item.nombre,
				'rut' 		: item.rut,
				'codigo_1' 	: item.codigo_1,
				'codigo_2' 	: item.codigo_2,
				'codigo_3' 	: item.codigo_3,
				'codigo_4' 	: item.codigo_4,
				})

		return JsonResponse(data, safe=False)

# conexion concepto
class CONEXION_CONCEPTO(View):

	http_method_names =  ['get', 'post']

	def get(self, request, pk=None):

		if pk == None:
			self.object_list = Cliente.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		else:
			self.object_list = Cliente.objects.filter(pk=pk)

		return self.json_to_response()

	def json_to_response(self):

		data = list()

		for cliente in self.object_list:

			estado 			= True
			data_conceptos 	= list()
			conceptos 		= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

			for concepto in conceptos:

				configuracion = Configuracion_Concepto.objects.filter(cliente=cliente, concepto=concepto).exists()

				if configuracion:

					configuracion = Configuracion_Concepto.objects.get(cliente=cliente, concepto=concepto)

				data_conceptos.append({
					'id'				: concepto.id,
					'nombre'			: concepto.nombre,
					'codigo' 			: concepto.codigo,
					'codigo_documento' 	: '' if configuracion is False else configuracion.codigo_documento,
					'codigo_producto' 	: '' if configuracion is False else configuracion.codigo_producto,
					'codigo_1' 			: '' if configuracion is False else configuracion.codigo_1,
					'codigo_2' 			: '' if configuracion is False else configuracion.codigo_2,
					'codigo_3' 			: '' if configuracion is False else configuracion.codigo_3,
					'codigo_4' 			: '' if configuracion is False else configuracion.codigo_4,
					'estado' 			: False if configuracion is False or configuracion.estado is False else configuracion.estado,
					})

				estado = False if configuracion is False else estado

			data.append({
				'id' 		: cliente.id,
				'nombre' 	: cliente.nombre,
				'rut' 		: cliente.rut,
				'direccion' : cliente.direccion,
				'telefono' 	: cliente.telefono,
				'conceptos'	: data_conceptos,
				'estado' 	: estado,
				})

		return JsonResponse(data, safe=False)

	def post(self, request):

		status 	= True
		message = 'ok'

		try:

			var_post 	= request.POST.copy()
			conceptos 	= json.loads(var_post['conceptos'])
			clientes 	= json.loads(var_post['clientes'])

			for cliente in clientes:

				for concepto in conceptos:

					if Configuracion_Concepto.objects.filter(cliente_id=cliente, concepto=concepto['id']).exists():
						
						configuracion = Configuracion_Concepto.objects.get(cliente_id=cliente, concepto=concepto['id'])
					else:
						configuracion = Configuracion_Concepto()

						configuracion.cliente_id 	= int(cliente)
						configuracion.concepto_id 	= int(concepto['id'])

					configuracion.estado = True if concepto['codigo_documento'] is not '' and concepto['codigo_producto'] is not '' else False

					configuracion.codigo_documento 	= concepto['codigo_documento']
					configuracion.codigo_producto 	= concepto['codigo_producto']
					configuracion.codigo_1 			= concepto['codigo_1']
					configuracion.codigo_2 			= concepto['codigo_2']
					configuracion.codigo_3 			= concepto['codigo_3']
					configuracion.codigo_4 			= concepto['codigo_4']
						
					configuracion.save()
			
		except Exception as error:

			status 	= False
			message = error

		response = {
			'status'	:status,
			'message'	:message,
		}

		return JsonResponse(response, safe=False)

# clasificacion
class ClasificacionList(ListView):
	model           = Clasificacion
	template_name   = 'clasificacion_list.html'

	def get_context_data(self, **kwargs):
		context = super(ClasificacionList, self).get_context_data(**kwargs)
		context['title']    = modulo
		context['subtitle'] = 'clasificacion'
		context['name']     = 'lista'
		context['href']     = '/clasificacion/list'

		return context

	def get_queryset(self):
		queryset = Clasificacion.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

class ClasificacionMixin(object):
	template_name   = 'clasificacion_new.html'
	form_class      = ClasificacionForm
	success_url     = '/clasificacion/list'

	def form_invalid(self, form):

		response = super(ClasificacionMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context                     = self.get_context_data()
		form_clasificacion_detalle  = context['clasificacion_detalle_form']

		obj         = form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa
		obj.save()

		if form_clasificacion_detalle.is_valid():
			self.object                         = form.save(commit=False)
			form_clasificacion_detalle.instance = self.object
			form_clasificacion_detalle.save()

		response = super(ClasificacionMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class ClasificacionNew(ClasificacionMixin, FormView):
	def get_context_data(self, **kwargs):

		context = super(ClasificacionNew, self).get_context_data(**kwargs)
		context['title']    = modulo
		context['subtitle'] = 'clasificacion'
		context['name']     = 'nuevo'
		context['href']     = '/clasificacion/list'
		context['accion']   = 'create'

		if self.request.POST:
			context['clasificacion_detalle_form'] = ClasificacionFormSet(self.request.POST)
		else:
			context['clasificacion_detalle_form'] = ClasificacionFormSet()

		return context

class ClasificacionUpdate(ClasificacionMixin, UpdateView):
	model           = Clasificacion
	form_class      = ClasificacionForm
	template_name   = 'clasificacion_new.html'
	success_url     = '/clasificacion/list'

	def get_context_data(self, **kwargs):

		context = super(ClasificacionUpdate, self).get_context_data(**kwargs)
		context['title']    = modulo
		context['subtitle'] = 'clasificacion'
		context['name']     = 'editar'
		context['href']     = '/clasificacion/list'
		context['accion']   = 'update'

		if self.request.POST:
			context['clasificacion_detalle_form'] = ClasificacionFormSet(self.request.POST, instance=self.object)
		else:
			context['clasificacion_detalle_form'] = ClasificacionFormSet(instance=self.object)

		return context

class ClasificacionDelete(DeleteView):
	model = Clasificacion
	success_url = reverse_lazy('/clasificacion/list')

	def delete(self, request, *args, **kwargs):
		self.object         = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

# workflow
class WORKFLOW(View):

	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		self.object_list = request.user.userprofile.empresa.workflow_set.all()

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':
			return self.json_to_response()
		else:
			return render(request, 'workflow_new.html', {
				'title'                     : 'Configuración',
				'href' 		                : 'workflow',
				'subtitle'	                : 'WorkFlow',
				'name' 		                : 'Configuración',
				'procesos_form'             : ProcesosBorradorForm(request=self.request),
				'condiciones_form'          : ProcesoCondicionFormSet()
			})

	def get_queryset(self, tipo_estado):

		queryset = Proceso.objects.filter(workflow__empresa=self.request.user.userprofile.empresa, visible=True, tipo_estado_id=tipo_estado)

		return queryset

	def post(self, request):

		if self.request.POST.get('action') == 'create':
			try:

				form_proceso = ProcesosBorradorForm(self.request.POST, request=self.request)

				if form_proceso.is_valid():
					data_proceso 	= form_proceso.cleaned_data
					workflow        = Workflow.objects.filter(empresa=self.request.user.userprofile.empresa).first()


					nuevo_proceso  				= Proceso()
					nuevo_proceso.nombre 		= data_proceso.get('nombre')
					nuevo_proceso.workflow		= workflow
					nuevo_proceso.tipo_estado	= data_proceso.get('tipo_estado')
					nuevo_proceso.save()

					if data_proceso.get('antecesor') != None:
						for obj in data_proceso.get('antecesor'):
							nuevo_proceso.antecesor.add(obj.id)


					nuevo_proceso.userprofile_set.set(self.request.POST.getlist('responsable'))


					workflow            = Workflow.objects.get(empresa=self.request.user.userprofile.empresa)
					workflow.validado   = False
					workflow.save()
				else:
					return JsonResponse(form_proceso.errors, status=400)

				estado = True

			except Exception as a:
				error   = a
				estado  = False

			return JsonResponse({'estado': estado}, safe=False)
		elif self.request.POST.get('action') == 'update':

			try:

				proceso_update  = get_object_or_404(Proceso, pk=self.request.POST.get('id'))
				form_proceso    = ProcesosBorradorForm(self.request.POST, request=self.request)

				if form_proceso.is_valid():

					data_proceso 	= form_proceso.cleaned_data
					workflow 		= Workflow.objects.filter(empresa=self.request.user.userprofile.empresa).first()

					proceso_update.nombre 		= data_proceso.get('nombre')
					proceso_update.workflow 	= workflow
					proceso_update.tipo_estado 	= data_proceso.get('tipo_estado')
					proceso_update.save()

					#Delete responsables

					for user in proceso_update.userprofile_set.all():
						proceso_update.userprofile_set.remove(user)

					proceso_update.userprofile_set.set(self.request.POST.getlist('responsable'))



					proceso_update.antecesor.clear()

					#Insert antecesor
					if data_proceso.get('antecesor') != None:
						for obj in data_proceso.get('antecesor'):
							proceso_update.antecesor.add(obj.id)

					workflow            = Workflow.objects.get(empresa=self.request.user.userprofile.empresa)
					workflow.validado   = False
					workflow.save()

				else:
					return JsonResponse(form_proceso.errors, status=400)

				estado = True

			except Exception as b:
				error   = b
				estado  = False

			return JsonResponse({'estado': estado}, safe=False)
		elif self.request.POST.get('action') == 'delete':

			try:
				proceso_id = self.request.POST.get('proceso_id')

				proceso         = Proceso.objects.get(id=proceso_id, workflow__empresa=self.request.user.userprofile.empresa, visible=True)
				proceso.visible = False
				proceso.save()

				workflow            = Workflow.objects.get(empresa=self.request.user.userprofile.empresa)
				workflow.validado   = False
				workflow.save()


				estado = True

			except Exception as c:
				error   = c
				estado  = False

			return JsonResponse({'estado': estado}, safe=False)

	def json_to_response(self):

		data                = list()

		for item in Proceso.objects.filter(workflow=self.object_list, visible=True).order_by('id'):

			data_responsable    = list()
			data_antecesor      = list()

			for responsable in UserProfile.objects.filter(proceso=item, visible=True):

				# obtener avatar
				primary_avatar = responsable.user.avatar_set.all().order_by('-primary')[:1]
				if primary_avatar:
					avatar = str(primary_avatar[0].avatar)
				else:
					avatar = None

				data_responsable.append({
					'id'        : responsable.id,
					'nombre'    : responsable.user.username,
					'first_name': responsable.user.first_name,
					'last_name'	: responsable.user.last_name,
					'avatar' 	: avatar,
				})

			for antecesor in item.antecesor.filter(visible=True):
				data_antecesor.append({
					'id'        : antecesor.id,
					'nombre'    : antecesor.nombre
				})

			link_data_1 = [{'id': l.id, 'proceso': l.proceso_id, 'entidad_id': l.entidad_id,
							'entidad': l.entidad.nombre,'operacion_id': l.operacion_id,'operacion': l.operacion.simbolo,
							'valor': l.valor} for l in Proceso_Condicion.objects.filter(proceso_id=item.id)]

			data.append({
				'id' 	            : item.id,
				'id_tipo_estado'    : item.tipo_estado_id,
				'tipo_estado'       : item.tipo_estado.nombre,
				'background_estado' : item.tipo_estado.background,
				'nombre' 	        : item.nombre,
				'responsable' 	    : data_responsable,
				'antecesor' 	    : data_antecesor ,
				'existe_condicion' 	: False if not Proceso_Condicion.objects.filter(proceso_id=item.id).count() else Proceso_Condicion.objects.filter(proceso_id=item.id).__bool__(),
				'condicion'         : link_data_1
			})

		return JsonResponse(data, safe=False)

class WORKFLOW_CONDICION(View):

	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		self.object_list = Proceso_Condicion.objects.filter(proceso_id= self.request.GET.get('proceso_id'))

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			return render(request, 'conexion_parametro_list.html', {
				'title'     : 'Conexión',
				'href' 		: 'conexion-parametro',
				'subtitle'	: 'Parametros Generales',
				'name' 		: 'Configuración',
			})

	def post(self, request):

		try:
			form_condicion  = ProcesoCondicionFormSet(self.request.POST)
			if form_condicion.is_valid():

				for obj_condicion in form_condicion:
					data = obj_condicion.cleaned_data

					if data.get('id') is not None:

						condicion = Proceso_Condicion.objects.get(id=data.get('id').id)

						if data.get('DELETE') == True:
							condicion.delete()
						else:
							condicion.entidad   = data.get('entidad')
							condicion.operacion = data.get('operacion')
							condicion.valor     = data.get('valor')
							condicion.save()
					else:

						if data.get('DELETE') == False:
							new_condicion           = Proceso_Condicion()
							new_condicion.proceso   = data.get('proceso')
							new_condicion.entidad   = data.get('entidad')
							new_condicion.operacion = data.get('operacion')
							new_condicion.valor     = data.get('valor')
							new_condicion.save()

				workflow            = Workflow.objects.get(empresa=self.request.user.userprofile.empresa)
				workflow.validado   = False
				workflow.save()
			else:
				return JsonResponse(form_condicion.errors, status=400, safe=False)
			estado = True
		except Exception as d:
			error   = d
			estado  = False

		return JsonResponse({'estado': estado}, safe=False)

	def json_to_response(self):

		data            = list()
		data_entidad    = list()

		for obj in Entidad_Asociacion.objects.all():
			data_entidad.append({
				'id'        : obj.id,
				'nombre'    : obj.nombre
			})


		for item in self.object_list:


			data.append({
				'proceso_id'            : item.proceso_id,
				'id' 					: item.id,
				'entidad' 	            : item.entidad_id,
				'operacion' 	        : item.operacion_id,
				'valor' 			    : item.valor
			})

		return JsonResponse({'entidades': data_entidad, 'condiciones': data}, safe=False)

def validar_workflow(request):

	try:
		estado          = True
		error           = ''
		object_workflow = request.user.userprofile.empresa.workflow_set.all()
		object_list     = Proceso.objects.filter(workflow=object_workflow, visible=True).order_by('tipo_estado_id','id')

		if not object_list.filter(tipo_estado_id=1).exists() or not object_list.filter(tipo_estado_id=3).exists():
			estado = False
			error  = "Error, debe contar con un proceso borrador y una aprobación."
		else:
			lista_antecesor = list()


			##Obtengo la lista de antecesores del workflow
			for b in object_list:
				for j in b.antecesor.filter(visible=True).values_list('proceso__antecesor', flat=True).distinct():
					if j not in lista_antecesor:
						lista_antecesor.append(j)
			count = 1
			for a in object_list:

				##Valida que el proceso tenga antecesor y que sea distinto de tipo borrador
				if not a.antecesor.filter(visible=True).count() and a.tipo_estado_id != 1:
					estado = False
					error = "El proceso " + str(a.nombre) + " no cuenta con un antecesor."
					break
				##Valida que el proceso no sea antecesor de sí mismo
				elif a.antecesor.filter(visible=True, nombre=a.nombre).distinct().exists():
					estado = False
					error = "El proceso " + str(a.nombre) + " no puede ser antecesor de sí mismo."
					break
				##Valida que un proceso de tipo revisión no pueda tener un antecesor tipo aprobación
				elif a.tipo_estado_id == 2 and a.antecesor.filter(tipo_estado_id=3).exists():
					estado  = False
					error   = "El proceso " + str(a.nombre) + " no puede tener un antecesor Tipo Aprobación."
					break
				##Valida que un proceso tipo aprobación no tenga un antecesor tipo borrador si existen tipo revisión.
				elif a.tipo_estado_id == 3 and a.antecesor.filter(tipo_estado_id=1).exists() and Proceso.objects.filter(tipo_estado_id=2,visible=True).count():
					estado  = False
					error   = "El proceso " + str(a.nombre) + " no debe tener un antecesor Tipo Borrador."
					break
				else:

					# Si existe el proceso como antecesor lo elimino de la lista de antecesores.
					if a.id in lista_antecesor:
						lista_antecesor.remove(a.id)
					else:
						# El proceso no es de tipo aprobación.
						if not a.tipo_estado_id == 3:
							estado  = False
							error   = "El proceso " + str(a.nombre) + " no es antecesor de ningún proceso."
							break

					for j in a.antecesor.filter(visible=True):
						## Validar loop procesos
						try:

							proceso_recursivos  = list()
							aux                 = count
							proceso_recursivos.append(a.nombre)

							## Busca que el proceso antecesor se encuentra en los siguientes procesos
							while aux < object_list.count():
								sig_proceso = object_list[aux]
								proceso_recursivos.append(sig_proceso.nombre)

								if j == sig_proceso:
									estado  = False
									error   = "Existe recursividad entre " + tuple(proceso_recursivos).__str__()
									break

								aux += 1

							if estado == False:
								break
						except Exception as a:
							break
				if estado == False:
					break
				else:
					count += 1

	except Exception as a:
		estado = False
		error  = "Error al validar Workflow."

	if estado == True:
		workflow            = Workflow.objects.get(empresa=request.user.userprofile.empresa)
		workflow.validado   = True
		workflow.save()

	return JsonResponse({'estado': estado, 'error': error}, safe=False)


class CONFIGURACION_MONEDA(View):
	http_method_names = ['get', 'post']

	def get(self, request, id=None):

		self.object_list = request.user.userprofile.empresa.concepto_set.all()

		return render(request, 'configuracion_moneda_new.html', {
			'title'                 : 'Configuración',
			'href' 		            : 'configuracion-moneda',
			'subtitle'	            : 'Monedas',
			'name' 		            : 'Configuración',
			'configuracion_form'    : ConfiguracionMonedaFormSet(queryset=Configuracion_Monedas.objects.filter(empresa=request.user.userprofile.empresa))
		})

	def post(self, request):

		try:

			form_moneda = ConfiguracionMonedaFormSet(self.request.POST)

			if form_moneda.is_valid():
				form_moneda.save()
			else:
				return JsonResponse(form_moneda.errors, status=400, safe=False)

			estado = True

		except Exception as b:
			error   = b
			estado  = False

		return JsonResponse({'estado': estado}, safe=False)



