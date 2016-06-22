# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
# from utils.functions import renderjson as render
from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from django.core.urlresolvers import reverse_lazy

from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from administrador.models import Empresa
from activos.models import Activo

from .forms import LocalForm, LocalTipoForm
from .models import Local, Local_Tipo, Venta

import json
from datetime import datetime, timedelta

import codecs
import csv
import xlrd

from xlrd import open_workbook


class AjaxableResponseMixin(object):

	template_name = 'viewer/locales/local_tipo_new.html'
	form_class = LocalTipoForm
	success_url = '/locales-tipo/list'

	def form_invalid(self, form):
		response = super(AjaxableResponseMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		obj = form.save(commit=False)
		obj.empresa_id = profile.empresa_id
		obj.save()

		response = super(AjaxableResponseMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class LocalTipoNew(AjaxableResponseMixin, FormView):

	def get_context_data(self, **kwargs):

		context = super(LocalTipoNew, self).get_context_data(**kwargs)
		context['title'] 	= 'Locales'
		context['subtitle'] = 'Tipo de Local'
		context['name'] 	= 'Nuevo'
		context['href'] 	= 'locales-tipo'
		context['accion'] 	= 'create'

		return context

class LocalTipoList(ListView):
	model = Local_Tipo
	template_name = 'viewer/locales/local_tipo_list.html'

	def get_context_data(self, **kwargs):
		context = super(LocalTipoList, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Tipo de Local'
		context['name'] = 'Lista'
		context['href'] = 'locales-tipo'
		
		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		queryset 	= Local_Tipo.objects.filter(empresa_id=profile.empresa_id, visible=True)

		return queryset

class LocalTipoDelete(DeleteView):
	model = Local_Tipo
	success_url = reverse_lazy('/locales-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class LocalTipoUpdate(UpdateView):

	model = Local_Tipo
	form_class = LocalTipoForm
	template_name = 'viewer/locales/local_tipo_new.html'
	success_url = '/locales-tipo/list'

	def get_context_data(self, **kwargs):
		
		context = super(LocalTipoUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Tipo de Local'
		context['name'] = 'Editar'
		context['href'] = 'locales-tipo'
		context['accion'] = 'update'
		return context




class AjaxableResponseMixinLocal(object):

	template_name = 'viewer/locales/local_new.html'
	form_class = LocalForm
	success_url = '/locales/list'

	def get_form_kwargs(self):
		kwargs = super(AjaxableResponseMixinLocal, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_invalid(self, form):
		response = super(AjaxableResponseMixinLocal, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj = form.save(commit=False)
		obj.save()
		
		form.save_m2m()
		for medidor in form.cleaned_data['medidores']:
			medidor.estado = True
			medidor.save()

		response = super(AjaxableResponseMixinLocal, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class LocalNew(AjaxableResponseMixinLocal, FormView):

	def get_context_data(self, **kwargs):
		
		context = super(LocalNew, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Local'
		context['name'] = 'Nuevo'
		context['href'] = 'locales'
		context['accion'] = 'create'

		return context
	
class LocalList(ListView):
	model = Local
	template_name = 'viewer/locales/local_list.html'

	def get_context_data(self, **kwargs):
		context = super(LocalList, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Local'
		context['name'] = 'Lista'
		context['href'] = 'locales'
		
		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		activos 	= Activo.objects.filter(empresa_id=profile.empresa_id).values_list('id', flat=True)
		queryset 	= Local.objects.filter(activo_id__in=activos, visible=True)
	
		return queryset

class LocalDelete(DeleteView):
	model = Local
	success_url = reverse_lazy('/locales/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class LocalUpdate(UpdateView):

	model = Local
	form_class = LocalForm
	template_name = 'viewer/locales/local_new.html'
	success_url = '/locales/list'

	def get_form_kwargs(self):
		kwargs = super(LocalUpdate, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def get_context_data(self, **kwargs):
		
		context = super(LocalUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Local'
		context['name'] = 'Editar'
		context['href'] = 'locales'
		context['accion'] = 'update'

		return context




class VentaList(ListView):
	model = Venta
	template_name = 'viewer/locales/venta_list.html'

	def get_context_data(self, **kwargs):
		context = super(VentaList, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Ventas'
		context['name'] = 'Lista'
		context['href'] = 'locales'
		
		return context



class VENTAS(View):
	http_method_names = ['get', 'post', 'put', 'delete']

	def get(self, request, id=None):

		# user 	= User.objects.get(pk=request.user.pk)
		# profile = UserProfile.objects.get(user=user)

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
		# var_post 	= request.POST.copy()
		# local     = var_post['local']
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

			try:
				fecha_inicio 	= datetime(*xlrd.xldate_as_tuple(i['Fecha Inicio'], 0))
				fecha_termino 	= datetime(*xlrd.xldate_as_tuple(i['Fecha Termino'], 0))
				valor = i['Total']
				venta = Venta(
					fecha_inicio		= fecha_inicio,
					fecha_termino		= fecha_termino,
					valor				= valor,
					local_id 			= 1,
					periodicidad		= 3,
					)
				venta.save()
			except ValueError:
				estado = 'error'

				errors.append({
					'row'			: cont,
					'fecha_inicio'	: i['Fecha Inicio'],
					'fecha_termino'	: i['Fecha Termino'],
					'valor'			: i['Total'],
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
