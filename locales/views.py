# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from accounts.models import *
from administrador.models import *
from activos.models import *
from contrato.models import Contrato

from .forms import *
from .models import *

from datetime import datetime, timedelta
from xlrd import open_workbook

import json
import codecs
import csv
import xlrd

# variables
modulo 	= 'Locales'


# tipos de locales
class LocalTipoList(ListView):

	model 			= Local_Tipo
	template_name 	= 'local_tipo_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(LocalTipoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'tipo de local'
		context['name'] 	= 'lista'
		context['href'] 	= '/locales-tipo/list'
		
		return context

	def get_queryset(self):

		queryset 	= Local_Tipo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

class LocalTipMixin(object):

	template_name 	= 'local_tipo_new.html'
	form_class 		= LocalTipoForm
	success_url 	= '/locales-tipo/list'

	def form_invalid(self, form):

		response = super(LocalTipMixin, self).form_invalid(form)

		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa
		obj.save()

		response = super(LocalTipMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class LocalTipoNew(LocalTipMixin, FormView):

    def get_context_data(self, **kwargs):

        context 			= super(LocalTipoNew, self).get_context_data(**kwargs)
        context['title'] 	= modulo
        context['subtitle'] = 'tipo de local'
        context['name'] 	= 'nuevo'
        context['href'] 	= '/locales-tipo/list'
        context['accion'] 	= 'create'

        return context

class LocalTipoUpdate(UpdateView):

    model 			= Local_Tipo
    form_class 		= LocalTipoForm
    template_name 	= 'local_tipo_new.html'
    success_url 	= '/locales-tipo/list'

    def get_context_data(self, **kwargs):

        context 			= super(LocalTipoUpdate, self).get_context_data(**kwargs)
        context['title'] 	= modulo
        context['subtitle'] = 'tipo de local'
        context['name'] 	= 'editar'
        context['href'] 	= '/locales-tipo/list'
        context['accion'] 	= 'update'

        return context

class LocalTipoDelete(DeleteView):

	model 		= Local_Tipo
	success_url = reverse_lazy('/locales-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		data = {'estado': True}

		return JsonResponse(data, safe=False)


# locales
class LocalList(ListView):

	model 			= Local
	template_name 	= 'local_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(LocalList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'local'
		context['name'] 	= 'lista'
		context['href'] 	= '/locales/list'
		
		return context

	def get_queryset(self):

		activos 	= Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)
		queryset 	= Local.objects.filter(activo_id__in=activos, visible=True)
	
		return queryset

class LocalMixin(object):

    template_name 	= 'local_new.html'
    form_class 		= LocalForm
    success_url 	= '/locales/list'

    def get_form_kwargs(self):

        kwargs = super(LocalMixin, self).get_form_kwargs()

        kwargs['request'] 	= self.request
        kwargs['activo_id'] = self.kwargs['activo_id']

        return kwargs

    def form_invalid(self, form):
        response = super(LocalMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):

        context 		= self.get_context_data()
        obj 			= form.save(commit=False)
        obj.activo_id 	= self.kwargs['activo_id']
        obj.save()
        form.save_m2m()

        form_electricidad 	= context['form_electricidad']
        form_gas 			= context['form_gas']
        form_agua 			= context['form_agua']

        if form_electricidad.is_valid():
            self.object 				= form.save(commit=False)
            form_electricidad.instance 	= self.object
            form_electricidad.save()

        if form_gas.is_valid():
            self.object 		= form.save(commit=False)
            form_gas.instance 	= self.object
            form_gas.save()

        if form_agua.is_valid():
            self.object 		= form.save(commit=False)
            form_agua.instance 	= self.object
            form_agua.save()

        response = super(LocalMixin, self).form_valid(form)

        if self.request.is_ajax():
            data = {'estado': True,}
            return JsonResponse(data)
        else:
            return response

class LocalNew(LocalMixin, FormView):

    def get_context_data(self, **kwargs):

        context 			= super(LocalNew, self).get_context_data(**kwargs)
        context['title'] 	= modulo
        context['subtitle'] = 'local'
        context['name'] 	= 'nuevo'
        context['href'] 	= '/locales/list'
        context['accion'] 	= 'create'

        if self.request.POST:
            context['form_electricidad'] 	= ElectricidadFormSet(self.request.POST)
            context['form_agua'] 			= AguaFormSet(self.request.POST)
            context['form_gas']				= GasFormSet(self.request.POST)
        else:
            context['form_electricidad'] 	= ElectricidadFormSet()
            context['form_agua'] 			= AguaFormSet()
            context['form_gas'] 			= GasFormSet()


        local_id                    = self.kwargs.pop('pk', None)
        data                        = obtener_clasificacion(self, local_id)
        context['clasificaciones']  = data

        return context

class LocalUpdate(LocalMixin, UpdateView):

    model 			= Local
    form_class 		= LocalForm
    template_name 	= 'local_new.html'
    success_url 	= '/locales/list'


    def get_context_data(self, **kwargs):

        context 			= super(LocalUpdate, self).get_context_data(**kwargs)
        context['title'] 	= modulo
        context['subtitle'] = 'local'
        context['name'] 	= 'editar'
        context['href'] 	= '/locales/list'
        context['accion'] 	= 'update'

        if self.request.POST:
            context['form_electricidad'] 	= ElectricidadFormSet(self.request.POST, instance=self.object)
            context['form_agua'] 			= AguaFormSet(self.request.POST, instance=self.object)
            context['form_gas'] 			= GasFormSet(self.request.POST, instance=self.object)
        else:
            context['form_electricidad'] 	= ElectricidadFormSet(instance=self.object)
            context['form_agua'] 			= AguaFormSet(instance=self.object)
            context['form_gas'] 			= GasFormSet(instance=self.object)

        local_id                    = self.kwargs.pop('pk', None)
        data                        = obtener_clasificacion(self, local_id)
        context['clasificaciones']  = data

        return context

class LocalDelete(DeleteView):

	model 		= Local
	success_url = reverse_lazy('/locales/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)


def obtener_clasificacion(self, local_id):
    cabeceras   = self.request.user.userprofile.empresa.clasificacion_set.filter(visible=True, tipo_clasificacion=1)
    cabecera    = list()

    if local_id is None:

        for c in cabeceras:

            detalles    = Clasificacion_Detalle.objects.filter(clasificacion=c)
            detalle     = list()

            for d in detalles:
                detalle.append({
                    'id'        : d.id,
                    'nombre'    : d.nombre,
                    'select'    : False
                })

            cabecera.append({
                'id'        : c.id,
                'nombre'    : c.nombre,
                'detalle'   : detalle
            })
    else:
        for c in cabeceras:

            detalles    = Clasificacion_Detalle.objects.filter(clasificacion=c)
            detalle     = list()

            for d in detalles:
                detalle.append({
                    'id'        : d.id,
                    'nombre'    : d.nombre,
                    'select'    : False if not d.local_set.filter(id=local_id).exists() else True
                })

            cabecera.append({
                'id'        : c.id,
                'nombre'    : c.nombre,
                'detalle'   : detalle
            })

    return cabecera


# ventas
class VentaList(ListView):

	model 			= Venta
	template_name 	= 'ventas_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(VentaList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'ventas'
		context['name'] 	= 'lista'
		context['href'] 	= 'locales'

		if self.request.user.userprofile.tipo_id == 2:
			contrato	= Contrato.objects.filter(cliente_id=self.request.user.userprofile.cliente, visible=True).values_list('locales', flat=True)
			locales 	= Local.objects.filter(id__in=contrato, visible=True)
		else:
			activos 			= Activo.objects.filter(empresa_id=self.request.user.userprofile.empresa, visible=True).values_list('id', flat=True)
			locales 			= Local.objects.filter(activo_id__in=activos, visible=True)
		context['locales'] 	= locales

		return context



class VENTAS(View):
	http_method_names = ['get', 'post', 'put', 'delete']

	def get(self, request, id=None):

		if id == None:
			self.object_list = Venta.objects.all().\
				extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
				values('year', 'month', 'local_id').\
				annotate(Sum('valor'))
		else:
			self.object_list = Venta.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def post(self, request):
		var_post 	= request.POST.copy()
		local     	= var_post['local']

		tempfile = request.FILES.get('file')

		book = open_workbook(filename=None, file_contents=tempfile.read())
		sheet = book.sheet_by_index(0)
		keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
		dict_list = []
		for row_index in range(1, sheet.nrows):
			d = {keys[col_index]: sheet.cell(row_index, col_index).value for col_index in range(sheet.ncols)}
			dict_list.append(d)
		cont = 1
		errors = list()
		estado = 'ok'

		for i in dict_list:
			list_error = list()
			try:

				list_error = self.validate_data(i['Fecha Inicio'], i['Fecha Termino'], i['Total'])

				if not list_error:
					fecha_inicio 	= datetime(*xlrd.xldate_as_tuple(i['Fecha Inicio'], 0))
					fecha_termino 	= datetime(*xlrd.xldate_as_tuple(i['Fecha Termino'], 0))
					valor 			= i['Total']

					if Venta.objects.filter(fecha_inicio=fecha_inicio, fecha_termino=fecha_termino, local_id=local).exists():
						venta 		= Venta.objects.get(fecha_inicio=fecha_inicio, fecha_termino=fecha_termino, local_id=local)
						venta.valor = valor
						venta.save()
					else:
						venta = Venta(
							fecha_inicio		= fecha_inicio,
							fecha_termino		= fecha_termino,
							valor				= valor,
							local_id 			= local,
							periodicidad		= 3,
							)
						venta.save()
				else:
					estado = 'error'

					errors.append({
						'row'			: cont,
						'fecha_inicio'	: i['Fecha Inicio'],
						'fecha_termino'	: i['Fecha Termino'],
						'valor'			: i['Total'],
						'error'			: list_error
					})

			except ValueError:
				estado = 'error'

				errors.append({
					'row'			: cont,
					'fecha_inicio'	: i['Fecha Inicio'],
					'fecha_termino'	: i['Fecha Termino'],
					'valor'			: i['Total'],
					'error'			: list_error
				})
			cont +=1

		if self.request.is_ajax():
			data = {
				'estado': estado,
				'errors': errors,
			}
			return JsonResponse(data)
		else:
			return render(request, 'viewer/locales/venta_list.html')
	
	def validate_data(self, fecha_inicio, fecha_termino, valor):

		list_error = list()

		fechas =[
			fecha_inicio,
			fecha_termino
		]

		for a in fechas:
			try:
				datetime(*xlrd.xldate_as_tuple(a, 0))
			except Exception:
				error = "Formato fecha no válido."
				if not error in list_error:
					list_error.append(error)

		try:
			float(valor)
		except Exception:
			error = "Valor no válido."
			list_error.append(error)

		return list_error

	def delete(self, request, project_id, module_id, id):
		venta = Venta.objects.get(pk=id)
		venta.delete()
		return render({'error':0, 'message':'Venta: eliminada correctamente'})

	def json_to_response(self):

		meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

		data = list()

		for venta in self.object_list:

			local = Local.objects.get(id=int(venta['local_id']))
				
			data.append({
				'id'			: 1,
				'local_id'		: local.id,
				'local_nombre'	: local.nombre,
				'mes'			: meses[int(venta['month'])-1],
				'ano'			: venta['year'],
				'valor'			: venta['valor__sum'],
				})

		return JsonResponse(data, safe=False)

class LOCAL(View):
	http_method_names = ['get']
	
	def get(self, request, id=None):

		profile = UserProfile.objects.get(user=self.request.user)
		empresa = Empresa.objects.get(id=profile.empresa_id)
		activos = Activo.objects.filter(empresa=empresa).values_list('id', flat=True)

		if id == None:
			self.object_list = Local.objects.filter(activo__in=activos, visible=True)
		else:
			self.object_list = Local.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def json_to_response(self):

		data = list()

		for local in self.object_list:

			data.append({
				'id' 		: local.id,
				'nombre' 	: local.nombre,
				'codigo' 	: local.codigo,
				'tipo' 		: local.local_tipo.nombre,
				'activo' 	: local.activo.nombre,
				'sector' 	: local.sector.nombre,
				'nivel' 	: local.nivel.nombre,
				})

		return JsonResponse(data, safe=False)
