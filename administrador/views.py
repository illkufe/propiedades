# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from conceptos.models import Concepto
from procesos.models import Factura

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

        response = super(ClienteMixin, self).form_valid(form)

        if self.request.is_ajax():
            data = {'estado' : True,}
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
	template_name 	= 'cliente_portal_new.html'
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

		self.object_list = request.user.userprofile.empresa.conexion_set.all()

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

		for item in self.object_list:

			data.append({
				'id' 		: item.id,
				'nombre' 	: item.nombre,
				'codigo' 	: item.codigo,
				'eliminar' 	: item.eliminar,
				'codigo_1' 	: item.codigo_1,
				'codigo_2' 	: item.codigo_2,
				'codigo_3' 	: item.codigo_3,
				'codigo_4' 	: item.codigo_4,
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

	def get(self, request, id=None):

		self.object_list = request.user.userprofile.empresa.concepto_set.all()

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':

			return self.json_to_response()

		else:

			return render(request, 'conexion_concepto_list.html', {
				'title' 	: 'Conexión',
				'href' 		: 'conexion-concepto',
				'subtitle'	: 'Conceptos',
				'name' 		: 'Configuración',
				})
	
	def post(self, request):

		try:
			var_post 	= request.POST.copy()
			conceptos 	= json.loads(var_post['conceptos'])
			
			for item in conceptos:

				concepto = Concepto.objects.get(id=item['id'])

				concepto.codigo_documento 	= item['codigo_documento']
				concepto.codigo_producto 	= item['codigo_producto']
				concepto.codigo_1 			= item['codigo_1']
				concepto.codigo_2 			= item['codigo_2']
				concepto.codigo_3 			= item['codigo_3']
				concepto.save()

				estado = True
					
		except Exception:

			estado = False

		return JsonResponse({'estado': estado}, safe=False)

	def json_to_response(self):

		data = list()

		for item in self.object_list:
				
			tipo = {
				'nombre': item.concepto_tipo.nombre,
				'codigo': item.concepto_tipo.codigo,
				}

			data.append({
				'id' 				: item.id,
				'nombre' 			: item.nombre,
				'codigo' 			: item.codigo,
				'codigo_documento' 	: item.codigo_documento,
				'codigo_producto' 	: item.codigo_producto,
				'codigo_1' 			: item.codigo_1,
				'codigo_2' 			: item.codigo_2,
				'codigo_3' 			: item.codigo_3,
				'codigo_4' 			: item.codigo_4,
				'tipo' 				: tipo,
				})

		return JsonResponse(data, safe=False)


# clasificacion
class ClasificacionList(ListView):
    model = Clasificacion
    template_name = 'clasificacion_list.html'

    def get_context_data(self, **kwargs):
        context = super(ClasificacionList, self).get_context_data(**kwargs)
        context['title'] = modulo
        context['subtitle'] = 'clasificacion'
        context['name'] = 'lista'
        context['href'] = '/clasificacion/list'

        return context

    def get_queryset(self):
        queryset = Clasificacion.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

        return queryset


class ClasificacionMixin(object):
    template_name = 'clasificacion_new.html'
    form_class = ClasificacionForm
    success_url = '/clasificacion/list'

    def form_invalid(self, form):

        response = super(ClasificacionMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):

        context = self.get_context_data()
        form_clasificacion_detalle = context['clasificacion_detalle_form']

        obj = form.save(commit=False)
        obj.empresa = self.request.user.userprofile.empresa
        obj.save()

        if form_clasificacion_detalle.is_valid():
            self.object = form.save(commit=False)
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
        context['title'] = modulo
        context['subtitle'] = 'clasificacion'
        context['name'] = 'nuevo'
        context['href'] = '/clasificacion/list'
        context['accion'] = 'create'

        if self.request.POST:
            context['clasificacion_detalle_form'] = ClasificacionFormSet(self.request.POST)
        else:
            context['clasificacion_detalle_form'] = ClasificacionFormSet()

        return context


class ClasificacionUpdate(ClasificacionMixin, UpdateView):
    model = Clasificacion
    form_class = ClasificacionForm
    template_name = 'clasificacion_new.html'
    success_url = '/clasificacion/list'

    def get_context_data(self, **kwargs):

        context = super(ClasificacionUpdate, self).get_context_data(**kwargs)
        context['title'] = modulo
        context['subtitle'] = 'clasificacion'
        context['name'] = 'editar'
        context['href'] = '/clasificacion/list'
        context['accion'] = 'update'

        if self.request.POST:
            context['clasificacion_detalle_form'] = ClasificacionFormSet(self.request.POST, instance=self.object)
        else:
            context['clasificacion_detalle_form'] = ClasificacionFormSet(instance=self.object)

        return context


class ClasificacionDelete(DeleteView):
    model = Clasificacion
    success_url = reverse_lazy('/clasificacion/list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.visible = False
        self.object.save()
        payload = {'delete': 'ok'}
        return JsonResponse(payload, safe=False)


