# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader
from django.template.loader import get_template 
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.db.models import Sum
from django.views.generic import View, ListView, FormView, CreateView, DeleteView, UpdateView

from administrador.models import Empresa, Cliente
from locales.models import Local

from .forms import *
from .models import *

from utilidades.views import *

import base64
import pdfkit
import json
import os


# variables
modulo 	= 'Contrato'


# tipo de contrato
class ContratoTipoList(ListView):

	model 			= Contrato_Tipo
	template_name 	= 'contrato_tipo_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ContratoTipoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'tipos de contratos'
		context['name'] 	= 'lista'
		context['href'] 	= '/contrato-tipo/list'
		
		return context

	def get_queryset(self):

		queryset = Contrato_Tipo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

class ContratoTipoMixin(object):

	template_name 	= 'contrato_tipo_new.html'
	form_class 		= ContratoTipoForm
	success_url 	= '/contrato-tipo/list'

	def form_invalid(self, form):

		response = super(ContratoTipoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa
		obj.save()

		response = super(ContratoTipoMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class ContratoTipoNew(ContratoTipoMixin, FormView):

	def get_context_data(self, **kwargs): 
		
		context 			= super(ContratoTipoNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'tipo de contrato'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/contrato-tipo/list'
		context['accion'] 	= 'create'

		return context

class ContratoTipoUpdate(UpdateView):

	model 			= Contrato_Tipo
	form_class 		= ContratoTipoForm
	template_name 	= 'contrato_tipo_new.html'
	success_url 	= '/contrato-tipo/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(ContratoTipoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'tipo de contrato'
		context['name'] 	= 'editar'
		context['href'] 	= '/contrato-tipo/list'
		context['accion'] 	= 'update'

		return context

class ContratoTipoDelete(DeleteView):

	model 		= Contrato_Tipo
	success_url = reverse_lazy('/contrato-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		data = {'delete': 'ok'}

		return JsonResponse(data, safe=False)


# contrato
class ContratoList(ListView):

	model 			= Contrato
	template_name 	= 'contrato_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ContratoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Contrato'
		context['name'] 	= 'Lista'
		context['href'] 	= '/contrato/list'

		return context

	def get_queryset(self):

		queryset 	= Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		for item in queryset:
			item.fecha_inicio  	= item.fecha_inicio.strftime('%d/%m/%Y')
			item.fecha_termino 	= item.fecha_termino.strftime('%d/%m/%Y')
			item.cantidad 		= len(item.conceptos.all()) # {cantidad de conceptos}

		return queryset

class ContratoMixin(object):

	template_name 	= 'contrato_new.html'
	form_class 		= ContratoForm
	success_url 	= '/contrato/list'

	def get_form_kwargs(self):

		kwargs 				= super(ContratoMixin, self).get_form_kwargs()
		kwargs['request'] 	= self.request

		return kwargs

	def form_invalid(self, form):

		response = super(ContratoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context 		= self.get_context_data()
		form_garantia 	= context['form_garantia']

		obj 			= form.save(commit=False)
		obj.empresa 	= self.request.user.userprofile.empresa

		# comprobar si tiene estado
		try:
			obj.estado
		except Exception:
			obj.estado = Contrato_Estado.objects.get(id=1)

		obj.save()
		form.save_m2m()

		if form_garantia.is_valid():
			self.object = form.save(commit=False)
			form_garantia.instance = self.object
			form_garantia.save()

		response = super(ContratoMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class ContratoNew(ContratoMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(ContratoNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Contrato'
		context['name'] 	= 'Nuevo'
		context['href'] 	= '/contrato/list'
		context['accion'] 	= 'create'

		if self.request.POST:
			context['form_garantia'] = GarantiaFormSet(self.request.POST)
		else:
			context['form_garantia'] = GarantiaFormSet()
		
		return context

class ContratoUpdate(ContratoMixin, UpdateView):

	model 			= Contrato
	form_class 		= ContratoForm
	template_name 	= 'contrato_new.html'
	success_url 	= '/contrato/list'

	def get_object(self, queryset=None):

		queryset = Contrato.objects.get(id=int(self.kwargs['pk']))

		queryset.fecha_contrato 	= queryset.fecha_contrato.strftime('%d/%m/%Y')
		queryset.fecha_inicio 		= queryset.fecha_inicio.strftime('%d/%m/%Y')
		queryset.fecha_termino 		= queryset.fecha_termino.strftime('%d/%m/%Y')
		queryset.fecha_habilitacion = queryset.fecha_habilitacion.strftime('%d/%m/%Y')
		queryset.fecha_renovacion 	= queryset.fecha_renovacion.strftime('%d/%m/%Y')
		queryset.fecha_remodelacion = queryset.fecha_remodelacion.strftime('%d/%m/%Y') if queryset.fecha_remodelacion is not None else ''
		queryset.fecha_plazo 		= queryset.fecha_plazo.strftime('%d/%m/%Y') if queryset.fecha_plazo is not None else ''
		queryset.fecha_aviso 		= queryset.fecha_aviso.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):
		
		context 			= super(ContratoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Contrato'
		context['name'] 	= 'Editar'
		context['href'] 	= '/contrato/list'
		context['accion'] 	= 'update'

		if self.request.POST:
			context['form_garantia'] = GarantiaFormSet(self.request.POST, instance=self.object)
		else:
			context['form_garantia'] = GarantiaFormSet(instance=self.object)

		return context

class ContratoDelete(DeleteView):

	model 		= Contrato
	success_url = reverse_lazy('/contrato/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)


# propuesta
class PropuestaList(ListView):

	model 			= Propuesta_Version
	template_name 	= 'propuesta_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(PropuestaList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'propuesta'
		context['name'] 	= 'lista'
		context['href'] 	= '/propuesta/list'

		return context

	def get_queryset(self):

		queryset 	= []
		propuestas 	= Propuesta_Contrato.objects.filter(visible=True)

		for propuesta in propuestas:

			ultima_version 					= propuesta.propuesta_version_set.all().order_by('-id').first()			
			ultima_version.fecha_inicio 	= ultima_version.fecha_inicio.strftime('%d/%m/%Y') if ultima_version.fecha_inicio is not None else '---'
			ultima_version.fecha_termino 	= ultima_version.fecha_termino.strftime('%d/%m/%Y') if ultima_version.fecha_termino is not None else '---'

			queryset.append(ultima_version)

		return queryset

class PropuestaMixin(object):

	template_name 	= 'propuesta_new.html'
	form_class 		= PropuestaForm
	success_url 	= '/propuesta/list'

	def get_form_kwargs(self):

		kwargs 				= super(PropuestaMixin, self).get_form_kwargs()
		kwargs['request'] 	= self.request

		return kwargs

	def form_invalid(self, form):

		response = super(PropuestaMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		transaction.set_autocommit(False)

		context = self.get_context_data()
		obj 	= form.save(commit=False)

		form_arriendo_minimo 		= context['form_arriendo_minimo']
		form_arriendo_variable 		= context['form_arriendo_variable']
		form_arriendo_bodega 		= context['form_arriendo_bodega']
		form_cuota_incorporacion 	= context['form_cuota_incorporacion']
		form_fondo_promocion 		= context['form_fondo_promocion']
		form_gasto_comun 			= context['form_gasto_comun']

		# propuesta new
		if self.kwargs.pop('pk', None) is None:

			propuesta 			= Propuesta_Contrato(numero=form.cleaned_data['numero'])
			propuesta.empresa 	= self.request.user.userprofile.empresa
			propuesta.save()
			obj.propuesta 		= propuesta
			obj.save()
			form.save_m2m()

		# propuesta update
		else:
			obj.pk = None
			obj.save()
			form.save_m2m()

		# conceptos
		if obj.arriendo_minimo is True:
			if form_arriendo_minimo.is_valid():
				formulario 				= form_arriendo_minimo.save(commit=False)
				formulario.propuesta 	= obj
				formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))

		if obj.arriendo_variable is True:
			if form_arriendo_variable.is_valid():
				formulario 				= form_arriendo_variable.save(commit=False)
				formulario.propuesta 	= obj
				formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))

		if obj.arriendo_bodega is True:
			if form_arriendo_bodega.is_valid():
				formulario 				= form_arriendo_bodega.save(commit=False)
				formulario.propuesta 	= obj
				formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))

		if obj.cuota_incorporacion is True:
			if form_cuota_incorporacion.is_valid():
				formulario 				= form_cuota_incorporacion.save(commit=False)
				formulario.propuesta 	= obj
				formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))

		if obj.fondo_promocion is True:
			if form_fondo_promocion.is_valid():
				formulario 				= form_fondo_promocion.save(commit=False)
				formulario.propuesta 	= obj
				formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))

		if obj.gasto_comun is True:
			if form_gasto_comun.is_valid():
				formulario 				= form_gasto_comun.save(commit=False)
				formulario.propuesta 	= obj
				formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))

		transaction.commit()
		transaction.connections.close_all()


		response = super(PropuestaMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class PropuestaNew(PropuestaMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(PropuestaNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'propuesta'
		context['name'] 	= 'nueva'
		context['href'] 	= '/propuesta/list'
		context['accion'] 	= 'create'

		if self.request.POST:
			context['form_arriendo_minimo'] 	= FormPropuestaArriendoMinimo(self.request.POST, prefix="arriendo_minimo")
			context['form_arriendo_variable'] 	= FormPropuestaArriendoVariable(self.request.POST, prefix="arriendo_variable")
			context['form_arriendo_bodega'] 	= FormPropuestaArriendoBodega(self.request.POST, prefix="arriendo_bodega")
			context['form_cuota_incorporacion'] = FormPropuestaCuotaIncorporacion(self.request.POST, prefix="cuota_incorporacion")
			context['form_fondo_promocion'] 	= FormPropuestaFondoPromocion(self.request.POST, prefix="fondo_promocion")
			context['form_gasto_comun'] 		= FormPropuestaGastoComun(self.request.POST, prefix="gasto_comun")
		else:
			context['form_arriendo_minimo'] 	= FormPropuestaArriendoMinimo(prefix="arriendo_minimo")
			context['form_arriendo_variable'] 	= FormPropuestaArriendoVariable(prefix="arriendo_variable")
			context['form_arriendo_bodega'] 	= FormPropuestaArriendoBodega(prefix="arriendo_bodega")
			context['form_cuota_incorporacion'] = FormPropuestaCuotaIncorporacion(prefix="cuota_incorporacion")			
			context['form_fondo_promocion'] 	= FormPropuestaFondoPromocion(prefix="fondo_promocion")
			context['form_gasto_comun'] 		= FormPropuestaGastoComun(prefix="gasto_comun")			

		return context

class PropuestaUpdate(PropuestaMixin, UpdateView):

	model 			= Propuesta_Version
	form_class 		= PropuestaForm
	template_name 	= 'propuesta_new.html'
	success_url 	= '/propuesta/list'

	def get_object(self, queryset=None):

		queryset = Propuesta_Version.objects.get(id=int(self.kwargs['pk']))
		
		queryset.fecha_inicio 		= queryset.fecha_inicio.strftime('%d/%m/%Y') if queryset.fecha_inicio is not None else ''
		queryset.fecha_termino 		= queryset.fecha_termino.strftime('%d/%m/%Y') if queryset.fecha_termino is not None else ''
		queryset.fecha_habilitacion = queryset.fecha_habilitacion.strftime('%d/%m/%Y') if queryset.fecha_habilitacion is not None else ''
		queryset.fecha_renovacion 	= queryset.fecha_renovacion.strftime('%d/%m/%Y') if queryset.fecha_renovacion is not None else ''
		queryset.fecha_remodelacion = queryset.fecha_remodelacion.strftime('%d/%m/%Y') if queryset.fecha_remodelacion is not None else ''
		queryset.fecha_plazo 		= queryset.fecha_plazo.strftime('%d/%m/%Y') if queryset.fecha_plazo is not None else ''
		queryset.fecha_aviso 		= queryset.fecha_aviso.strftime('%d/%m/%Y') if queryset.fecha_aviso is not None else ''

		return queryset

	def get_context_data(self, **kwargs):
		
		context 			= super(PropuestaUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'propuesta'
		context['name'] 	= 'editar'
		context['href'] 	= '/propuesta/list'
		context['accion'] 	= 'update'

		if self.request.POST:

			context['form_arriendo_minimo'] 	= FormPropuestaArriendoMinimo(self.request.POST, prefix="arriendo_minimo")
			context['form_arriendo_variable'] 	= FormPropuestaArriendoVariable(self.request.POST, prefix="arriendo_variable")
			context['form_arriendo_bodega'] 	= FormPropuestaArriendoBodega(self.request.POST, prefix="arriendo_bodega")
			context['form_cuota_incorporacion'] = FormPropuestaCuotaIncorporacion(self.request.POST, prefix="cuota_incorporacion")
			context['form_fondo_promocion'] 	= FormPropuestaFondoPromocion(self.request.POST, prefix="fondo_promocion")
			context['form_gasto_comun'] 		= FormPropuestaGastoComun(self.request.POST, prefix="gasto_comun")

		else:

			propuesta = Propuesta_Version.objects.get(id=int(self.kwargs['pk']))

			context['form_arriendo_minimo'] 	= FormPropuestaArriendoMinimo(instance=propuesta.propuesta_arriendo_minimo_set.first(), prefix="arriendo_minimo")
			context['form_arriendo_variable'] 	= FormPropuestaArriendoVariable(instance=propuesta.propuesta_arriendo_variable_set.first(), prefix="arriendo_variable")
			context['form_arriendo_bodega'] 	= FormPropuestaArriendoBodega(instance=propuesta.propuesta_arriendo_bodega_set.first(), prefix="arriendo_bodega")
			context['form_cuota_incorporacion'] = FormPropuestaCuotaIncorporacion(instance=propuesta.propuesta_cuota_incorporacion_set.first(), prefix="cuota_incorporacion")
			context['form_fondo_promocion'] 	= FormPropuestaFondoPromocion(instance=propuesta.propuesta_fondo_promocion_set.first(), prefix="fondo_promocion")
			context['form_gasto_comun'] 		= FormPropuestaGastoComun(instance=propuesta.propuesta_gasto_comun_set.first(), prefix="gasto_comun")

		return context

class PropuestaDelete(DeleteView):

	model 		= Propuesta_Contrato
	success_url = reverse_lazy('/propuesta/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)


# propuesta historial
class PropuestaHistorialList(ListView):

	model 			= Propuesta_Version
	template_name 	= 'propuesta_historial.html'

	def get_context_data(self, **kwargs):

		context 			= super(PropuestaHistorialList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'propuesta'
		context['name'] 	= 'historial'
		context['href'] 	= '/propuesta/list'

		return context

	def get_queryset(self):
		data 				= list()
		data_numero 		= list()
		data_fecha_inicio 	= list()
		data_fecha_termino 	= list()
		# queryset 	= list()
		propuesta 	= Propuesta_Contrato.objects.get(id=self.kwargs['pk'])
		versiones 	= propuesta.propuesta_version_set.all()
		queryset 	= versiones


		for version in versiones:
			data_numero.append(version.numero)
			data_fecha_inicio.append(version.fecha_inicio)
			data_fecha_termino.append(version.fecha_termino)

		data.append({'item': 'Número', 'data':data_numero})
		data.append({'item': 'Fecha Inicio', 'data':data_fecha_inicio})
		data.append({'item': 'Fecha Término', 'data':data_fecha_termino})
		return data
		# for propuesta in propuestas:

		# 	ultima_version 					= propuesta.propuesta_version_set.all().order_by('-id').first()
		# 	ultima_version.fecha_inicio  	= ultima_version.fecha_inicio.strftime('%d/%m/%Y')
		# 	ultima_version.fecha_termino 	= ultima_version.fecha_termino.strftime('%d/%m/%Y')

		# 	queryset.append(ultima_version)

		# return queryset


# tipo de multa
class MultaTipoList(ListView):

	model 			= Multa_Tipo
	template_name 	= 'multa_tipo_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(MultaTipoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'tipos de multa'
		context['name'] 	= 'lista'
		context['href'] 	= '/multa-tipo/list'
		
		return context

	def get_queryset(self):
		
		queryset = Multa_Tipo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

class MultaTipoMixin(object):

	template_name 	= 'multa_tipo_new.html'
	form_class 		= MultaTipoForm
	success_url 	= '/multa-tipo/list'

	def form_invalid(self, form):

		response = super(MultaTipoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa
		obj.save()

		response = super(MultaTipoMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class MultaTipoNew(MultaTipoMixin, FormView):

	def get_context_data(self, **kwargs):

		context 			= super(MultaTipoNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'tipos de multa'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/multa-tipo/list'
		context['accion'] 	= 'create'

		return context

class MultaTipoUpdate(MultaTipoMixin, UpdateView):

	model 			= Multa_Tipo
	form_class 		= MultaTipoForm
	template_name 	= 'multa_tipo_new.html'
	success_url		= '/multa-tipo/list'

	def get_context_data(self, **kwargs):

		context 			= super(MultaTipoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'tipos de multa'
		context['name'] 	= 'editar'
		context['href'] 	= '/multa-tipo/list'
		context['accion'] 	= 'update'

		return context

class MultaTipoDelete(DeleteView):

	model 		= Multa_Tipo
	success_url = reverse_lazy('/multa-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)


# multa
class MultaList(ListView):

	model 			= Multa
	template_name 	= 'multa_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(MultaList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'multas'
		context['name'] 	= 'lista'
		context['href'] 	= '/multa/list'

		return context

	def get_queryset(self):

		queryset = Multa.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		for item in queryset:
			item.valor = item.valor * item.moneda.moneda_historial_set.all().order_by('-id').first().valor

		return queryset

class MultaMixin(object):

	template_name 	= 'multa_new.html'
	form_class 		= MultaForm
	success_url 	= '/multa/list'

	def get_form_kwargs(self):

		kwargs 				= super(MultaMixin, self).get_form_kwargs()
		kwargs['request'] 	= self.request

		return kwargs

	def form_invalid(self, form):

		response = super(MultaMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa

		obj.save()

		response = super(MultaMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class MultaNew(MultaMixin, FormView):

	def get_context_data(self, **kwargs):

		context 			= super(MultaNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'multas'
		context['name'] 	= 'nueva'
		context['href'] 	= '/multa/list'
		context['accion'] 	= 'create'

		return context

class MultaUpdate(MultaMixin, UpdateView):

	model 			= Multa
	form_class 		= MultaForm
	template_name 	= 'multa_new.html'
	success_url 	= '/multa/list'

	def get_context_data(self, **kwargs):

		context 			= super(MultaUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'multas'
		context['name'] 	= 'editar'
		context['href'] 	= '/multa/list'
		context['accion'] 	= 'update'

		return context

class MultaDelete(DeleteView):

	model 		= Multa
	success_url = reverse_lazy('/contrato-multa/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)


# conceptos de contrato
class ContratoConceptoMixin(object):

	template_name 	= 'contrato_concepto_new.html'
	form_class 		= InformacionForm
	success_url 	= '/contrato/list'

	def form_invalid(self, form):

		response = super(ContratoConceptoMixin, self).form_invalid(form)

		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context 	= self.get_context_data()
		concepto 	= Concepto.objects.get(id=context['concepto_id'])
		formulario 	= context['formulario']

		if concepto.concepto_tipo.id == 1:
			
			if formulario.is_valid():
				formulario_detalle 	= context['formulario_detalle']

				newscore = formulario.save(commit=False)
				newscore.concepto_id = concepto.id
				newscore.save()

				if formulario_detalle.is_valid():
					formulario_detalle.save()
				else:
					print ('----')
					print (formulario_detalle.errors)
					print ('----')
					return JsonResponse(form.errors, status=400)

			else:
				print ('----')
				print (formulario.errors)
				print ('----')
				return JsonResponse(form.errors, status=400)

		elif concepto.concepto_tipo.id == 2:

			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(form.errors, status=400)

		# gasto común
		elif concepto.concepto_tipo.id == 3:
			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				print ('----')
				print (formulario.errors)
				print ('----')
				return JsonResponse(formulario.errors, safe=False, status=400)

		elif concepto.concepto_tipo.id == 4:

			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
				formulario.save_m2m()

			else:
				return JsonResponse(form.errors, status=400)
			
		elif concepto.concepto_tipo.id == 5:

			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(form.errors, status=400)

		elif concepto.concepto_tipo.id == 6:
			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(form.errors, status=400)

		elif concepto.concepto_tipo.id == 7:

			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(form.errors, status=400)
		else:
			pass

		response = super(ContratoConceptoMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class ContratoConceptoNew(ContratoConceptoMixin, FormView):

	def get_context_data(self, **kwargs):

		context 				= super(ContratoConceptoNew, self).get_context_data(**kwargs)
		context['title'] 		= 'Contratos'
		context['subtitle'] 	= 'Arriendo'
		context['name'] 		= 'Nuevo'
		context['href'] 		= 'contratos'
		context['accion'] 		= 'create'
		context['contrato_id']	= self.kwargs['contrato_id']
		
		
		formularios	= list()
		conceptos 	= Contrato.objects.get(id=self.kwargs['contrato_id']).conceptos.all()
		contrato 	= Contrato.objects.get(id=self.kwargs['contrato_id'])

		if self.request.POST:

			context['concepto_id'] 	= self.request.POST.get('concepto_id')
			concepto 				= Concepto.objects.get(id=context['concepto_id'])


			if concepto.concepto_tipo.id == 1:
				if Arriendo.objects.filter(contrato=contrato, concepto=concepto).exists():
					arriendo_minimo 				= Arriendo.objects.get(contrato=contrato, concepto=concepto)
					context['formulario'] 			= ArriendoForm(self.request.POST, instance=arriendo_minimo)
					context['formulario_detalle'] 	= ArriendoDetalleFormSet(self.request.POST, instance=arriendo_minimo)
				else:
					context['formulario'] 			= ArriendoForm(self.request.POST)
					context['formulario_detalle'] 	= ArriendoDetalleFormSet(self.request.POST)

				# try:
				# 	arriendo_minimo 			= Arriendo.objects.get(contrato_id=self.kwargs['contrato_id'])
				# 	context['formset_arriendo'] = ArriendoForm(self.request.POST, instance=arriendo_minimo)
				# 	context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST,  instance=arriendo_minimo)
				# except Exception:
				# 	context['formset_arriendo'] = ArriendoForm(self.request.POST)
				# 	context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST)


			elif concepto.concepto_tipo.id == 2:
				context['formulario'] 	= ArriendoVariableFormSet(self.request.POST, instance=contrato, form_kwargs={'contrato': contrato})
			elif concepto.concepto_tipo.id == 3:
				context['formulario'] 	= GastoComunFormSet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 4:
				context['formulario'] 	= ServicioBasicoFormSet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 5:
				context['formulario'] 	= CuotaIncorporacionFormet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 6:
				context['formulario'] 	= FondoPromocionFormSet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 7:
				context['formulario'] 	= ArriendoBodegaFormSet(self.request.POST, instance=contrato)
			else:
				pass

		# GET
		else:
			for concepto in conceptos:

				if concepto.concepto_tipo.id == 1:
					if Arriendo.objects.filter(contrato=contrato, concepto=concepto).exists():
						arriendo 				= Arriendo.objects.get(contrato=contrato, concepto=concepto)
						arriendo.fecha_inicio 	= arriendo.fecha_inicio.strftime('%d/%m/%Y')
						form 					= ArriendoForm(instance=arriendo, contrato=contrato)
						form_detalle 			= ArriendoDetalleFormSet(instance=arriendo)
					else:
						form 			= ArriendoForm(contrato=contrato)
						form_detalle 	= ArriendoDetalleFormSet()

					formularios.append({
						'fomulario' 		: form, 
						'fomulario_detalle' : form_detalle,
						'contrato' 			: contrato,
						'concepto' 			: concepto,
					})

				elif concepto.concepto_tipo.id == 2:
					if Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = ArriendoVariableFormSet(instance=contrato, queryset=Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto), form_kwargs={'contrato': contrato})
					else:
						form = ArriendoVariableFormSet(form_kwargs={'contrato': contrato})

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})
				elif concepto.concepto_tipo.id == 3:
					if Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = GastoComunFormSet(instance=contrato, queryset=Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto), form_kwargs={'contrato': contrato})
					else:
						form = GastoComunFormSet(form_kwargs={'contrato': contrato})

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})
				elif concepto.concepto_tipo.id == 4:

					if Servicio_Basico.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = ServicioBasicoFormSet(instance=contrato, queryset=Servicio_Basico.objects.filter(contrato=contrato, concepto=concepto), form_kwargs={'contrato': contrato})
					else:
						form = ServicioBasicoFormSet()

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})

				elif concepto.concepto_tipo.id == 5:
					if Cuota_Incorporacion.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = CuotaIncorporacionFormet(instance=contrato, queryset=Cuota_Incorporacion.objects.filter(contrato=contrato, concepto=concepto))
					else:
						form = CuotaIncorporacionFormet()

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})

				elif concepto.concepto_tipo.id == 6:
					if Fondo_Promocion.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = FondoPromocionFormSet(instance=contrato, queryset=Fondo_Promocion.objects.filter(contrato=contrato, concepto=concepto))
					else:
						form = FondoPromocionFormSet()

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})

				elif concepto.concepto_tipo.id == 7:
					if Arriendo_Bodega.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = ArriendoBodegaFormSet(instance=contrato, queryset=Arriendo_Bodega.objects.filter(contrato=contrato, concepto=concepto))
					else:
						form = ArriendoBodegaFormSet()

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})
				else:
					pass

				context['formularios'] = formularios



		
		# print (formularios)

		

		# if self.request.POST:

		# 	contrato = Contrato.objects.get(id=self.kwargs['contrato_id'])

		# 	# arriendo mínimo
		# 	try:
		# 		arriendo_minimo 			= Arriendo.objects.get(contrato_id=self.kwargs['contrato_id'])
		# 		context['formset_arriendo'] = ArriendoForm(self.request.POST, instance=arriendo_minimo)
		# 		context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST,  instance=arriendo_minimo)
		# 	except Exception:
		# 		context['formset_arriendo'] = ArriendoForm(self.request.POST)
		# 		context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST)

			
		# 	# try:
		# 	# 	arriendo_bodega 				= Arriendo_Bodega.objects.filter(contrato_id=self.kwargs['contrato_id'])
		# 	# 	context['form_arriendo_bodega'] = ArriendoBodegaFormSet(self.request.POST, instance=contrato)
		# 	# except Exception:
		# 	# 	context['form_arriendo_bodega'] = ArriendoBodegaFormSet(self.request.POST)

		# 	# arriendo variable
		# 	try:
		# 		arriendo_variable 					= Arriendo_Variable.objects.filter(contrato_id=self.kwargs['contrato_id'])
		# 		context['form_arriendo_variable'] 	= ArriendoVariableFormSet(self.request.POST, instance=contrato)
		# 	except Exception:
		# 		context['form_arriendo_variable'] 	= ArriendoVariableFormSet(self.request.POST)

		# 	# gasto común
		# 	try:
		# 		gasto_comun 				= Gasto_Comun.objects.filter(contrato_id=self.kwargs['contrato_id'])
		# 		context['form_gasto_comun'] = GastoComunFormSet(self.request.POST, instance=contrato)
		# 	except Exception:
		# 		context['form_gasto_comun'] = GastoComunFormSet(self.request.POST)

		# 	# servicios básicos
		# 	try:
		# 		servicio_basico 					= Servicio_Basico.objects.filter(contrato=contrato)
		# 		context['form_servicios_basicos'] 	= ServicioBasicoFormSet(self.request.POST, instance=contrato)
		# 	except Exception:
		# 		context['form_servicios_basicos'] 	= ServicioBasicoFormSet(self.request.POST)

		# 	# cuota incorporacion
		# 	try:
		# 		cuota_incorporacion 				= Cuota_Incorporacion.objects.filter(contrato_id=self.kwargs['contrato_id'])
		# 		context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(self.request.POST, instance=contrato)
		# 	except Exception:
		# 		context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(self.request.POST)

		# 	# fondo promoción
		# 	try:
		# 		fondo_promocion 				= Fondo_Promocion.objects.filter(contrato_id=self.kwargs['contrato_id'])
		# 		context['form_fondo_promocion'] = FondoPromocionFormSet(self.request.POST, instance=contrato)
		# 	except Exception:
		# 		context['form_fondo_promocion'] = FondoPromocionFormSet(self.request.POST)

		# else:

		# 	contrato_id = self.kwargs['contrato_id']
		# 	contrato 	= Contrato.objects.get(id=contrato_id)

		# 	# arriendo mínimo
		# 	# try:
		# 	# 	arriendo_minimo 				= Arriendo.objects.get(contrato_id=contrato_id)
		# 	# 	arriendo_minimo.fecha_inicio 	= arriendo_minimo.fecha_inicio.strftime('%d/%m/%Y')
		# 	# 	context['formset_arriendo'] 	= ArriendoForm(instance=arriendo_minimo, contrato=contrato)
		# 	# 	context['formset_detalle'] 		= ArriendoDetalleFormSet(instance=arriendo_minimo)
		# 	# except Exception:
		# 	# 	context['formset_arriendo'] 	= ArriendoForm(contrato=contrato)
		# 	# 	context['formset_detalle'] 		= ArriendoDetalleFormSet()

		# 	# arriendo bodega
		# 	# try:
		# 	# 	arriendo_bodega 				= Arriendo_Bodega.objects.filter(contrato_id=contrato_id)
		# 	# 	context['form_arriendo_bodega'] = ArriendoBodegaFormSet(instance=contrato)
		# 	# except Exception:
		# 	# 	context['form_arriendo_bodega'] = ArriendoBodegaFormSet()

		# 	# arriendo variable
		# 	try:
		# 		arriendo_variable 					= Arriendo_Variable.objects.filter(contrato_id=contrato_id)
		# 		context['form_arriendo_variable'] 	= ArriendoVariableFormSet(instance=contrato)
		# 	except Exception:
		# 		context['form_arriendo_variable'] 	= ArriendoVariableFormSet()

		# 	# gasto común
		# 	try:
		# 		gasto_comun 				= Gasto_Comun.objects.filter(contrato=contrato)
		# 		context['form_gasto_comun'] = GastoComunFormSet(instance=contrato, form_kwargs={'contrato': contrato})
		# 	except Exception:
		# 		context['form_gasto_comun'] = GastoComunFormSet(form_kwargs={'contrato': contrato})

		# 	# servicios básicos
		# 	try:
		# 		servicio_basico 					= Servicio_Basico.objects.filter(contrato=contrato)
		# 		context['form_servicios_basicos'] 	= ServicioBasicoFormSet(instance=contrato, form_kwargs={'contrato': contrato})
		# 	except Exception:
		# 		context['form_servicios_basicos'] 	= ServicioBasicoFormSet(form_kwargs={'contrato': contrato})

		# 	# cuota incorporación
		# 	try:
		# 		cuota_incorporacion 				= Cuota_Incorporacion.objects.filter(contrato_id=contrato_id)
		# 		context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(instance=contrato, form_kwargs={'contrato': contrato})
		# 	except Exception:
		# 		context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(form_kwargs={'contrato': contrato})

		# 	# fondo promoción
		# 	try:
		# 		fondo_promocion 				= Fondo_Promocion.objects.filter(contrato_id=contrato_id)
		# 		context['form_fondo_promocion'] = FondoPromocionFormSet(instance=contrato, form_kwargs={'contrato': contrato})
		# 	except Exception:
		# 		context['form_fondo_promocion'] = FondoPromocionFormSet(form_kwargs={'contrato': contrato})

		return context


# contratos inactivos
class ContratosInactivosList(ListView):

	model 			= Contrato
	template_name 	= 'viewer/contratos/contratos_inactivos_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ContratosInactivosList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Contrato Incativos'
		context['name'] 	= 'Lista'
		context['href'] 	= 'contratos/inactivos'

		return context

	def get_queryset(self):

		queryset 	= Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True, estado__in=[1])

		for item in queryset:
			item.fecha_inicio  	= item.fecha_inicio.strftime('%d/%m/%Y')
			item.fecha_termino 	= item.fecha_termino.strftime('%d/%m/%Y')

		return queryset


# get
class CONTRATO(View):
	http_method_names = ['get']
	
	def get(self, request, id=None):

		if id is None:
			self.object_list = Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True, estado__in=[1])
		else:
			self.object_list = Contrato.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def json_to_response(self):

		data = list()

		for contrato in self.object_list:

			data_locales 	= list()
			data_conceptos 	= list()

			locales 		= contrato.locales.all()
			conceptos 		= contrato.conceptos.all()

			for local in locales:
				data_locales.append({
					'id'	: local.id,
					'nombre': local.nombre,
					'tipo'	: local.local_tipo.nombre,
					})

			for concepto in conceptos:
				data_conceptos.append({
					'id'	: concepto.id,
					'nombre': concepto.nombre,
					})

			data.append({
				'id' 					: contrato.id,
				'numero' 				: contrato.numero,
				'fecha_contrato' 		: contrato.fecha_contrato,
				'nombre_local' 			: contrato.nombre_local,
				'fecha_inicio' 			: contrato.fecha_inicio.strftime('%d/%m/%Y'),
				'fecha_termino' 		: contrato.fecha_termino.strftime('%d/%m/%Y'),
				'fecha_habilitacion' 	: contrato.fecha_habilitacion.strftime('%d/%m/%Y'),
				'fecha_activacion' 		: contrato.fecha_activacion.strftime('%d/%m/%Y') if contrato.fecha_activacion is not None else None,
				'fecha_renovacion' 		: contrato.fecha_renovacion.strftime('%d/%m/%Y'),
				'fecha_remodelacion' 	: contrato.fecha_remodelacion.strftime('%d/%m/%Y') if contrato.fecha_remodelacion is not None else None,
				'fecha_aviso' 			: contrato.fecha_aviso.strftime('%d/%m/%Y'),
				'fecha_plazo' 			: contrato.fecha_plazo.strftime('%d/%m/%Y') if contrato.fecha_plazo is not None else None,
				'bodega' 				: contrato.bodega,
				'metros_bodega' 		: contrato.metros_bodega,
				'tipo' 					: {'id': contrato.tipo.id, 'nombre': contrato.tipo.nombre},
				'estado' 				: {'id': contrato.estado.id, 'nombre': contrato.estado.nombre},
				'cliente' 				: {'id': contrato.cliente.id, 'nombre': contrato.cliente.nombre},
				'locales' 				: data_locales,
				'conceptos' 			: data_conceptos,
				})

		return JsonResponse(data, safe=False)

class PROPUESTA_CONTRATO(View):

	http_method_names = ['get']
	
	def get(self, request, id=None):

		if id == None:
			self.object_list = Propuesta_Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		else:
			self.object_list = Propuesta_Contrato.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def json_to_response(self):

		data = list()

		for propuesta in self.object_list:

			versiones 		= propuesta.propuesta_version_set.all().order_by('-id')
			data_versiones 	= list()

			for version in versiones:

				data_versiones.append({
					'id' 					: version.id,
					'numero'				: version.numero,
					'nombre_local'			: version.nombre_local,
					'fecha_inicio'			: version.fecha_inicio if version.fecha_inicio is not None else None,
					'fecha_termino'			: version.fecha_termino if version.fecha_termino is not None else None,
					'meses'					: version.meses if version.meses is not None else None,
					'fecha_habilitacion'	: version.fecha_habilitacion if version.fecha_habilitacion is not None else None,
					'fecha_activacion'		: version.fecha_activacion if version.fecha_activacion is not None else None,
					'fecha_renovacion'		: version.fecha_renovacion if version.fecha_renovacion is not None else None,
					'fecha_remodelacion'	: version.fecha_remodelacion if version.fecha_remodelacion is not None else None,
					'fecha_aviso'			: version.fecha_aviso if version.fecha_aviso is not None else None,
					'fecha_plazo'			: version.fecha_plazo if version.fecha_plazo is not None else None,
					'dias_salida'			: version.dias_salida if version.dias_salida is not None else None,
					'destino_comercial'		: version.destino_comercial if version.destino_comercial is not None else None,
					'creado_en' 			: version.creado_en
					})

			data.append({
				'id' 		: propuesta.id,
				'versiones' : data_versiones,
				})

		return JsonResponse(data, safe=False)


# funciones - propuesta contrato
def propuesta_enviar_correo(request):

	var_post 		= request.POST.copy()
	contenido 		= var_post['contenido']
	propuesta_id 	= var_post['propuesta_id']

	configuracion = {
		'contenido' 		: contenido,
		'asunto' 			: 'Propuesta',
		'destinatarios' 	: ['juan.mieres.s@gmail.com', 'egomez@informat.cl'],
		'id'				: '1',
	}

	response = enviar_correo(configuracion)

	return JsonResponse(response, safe=False)


def propuesta_restaurar_version(request, id=None):

	response 	= list()
	version 	= Propuesta_Version.objects.get(id=id)
	locales 	= version.locales.all()

	# version.id 		= None
	# version.locales = locales
	# version.save()

	return JsonResponse(response, safe=False)

def contrato_activar(request, contrato_id):

	try:
		data 		= {'estado': 'ok'}
		contrato 	= Contrato.objects.get(id=contrato_id)
		contrato.fecha_activacion 	= fecha_actual()
		contrato.estado 	= Contrato_Estado.objects.get(id=4)
		contrato.save()
		
	except Exception:
		data = {'estado': 'error'}

	return JsonResponse(data, safe=False)

def contrato_pdf(request, contrato_id):

	contrato 		= Contrato.objects.get(id=contrato_id)
	locales 		= contrato.locales.all()
	cliente 		= Cliente.objects.get(id=contrato.cliente_id)
	representantes 	= cliente.representante_set.all()
	empresa 		= Empresa.objects.get(id=cliente.empresa_id)
	metros 			= contrato.locales.all().aggregate(Sum('metros_cuadrados'))
	meses 			= ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
	renovacion 		= meses_entre_fechas(contrato.fecha_renovacion, contrato.fecha_termino)

	# arriendo
	try:
		arriendo 			= Arriendo.objects.get(contrato=contrato)
		arriendo_detalle 	= Arriendo_Detalle.objects.filter(arriendo=arriendo)
	except Exception:
		arriendo 			= None
		arriendo_detalle 	= None

	# arriendo bodega
	try:
		arriendo_bodega = Arriendo_Bodega.objects.filter(contrato=contrato)	
		if len(arriendo_bodega) == 0:
			arriendo_bodega = None
	except Exception:
		arriendo_bodega = None

	# gasto comun
	try:
		gasto_comun = Gasto_Comun.objects.filter(contrato=contrato)
	except Exception:
		gasto_comun = None

	# cuota
	try:
		cuota = Cuota_Incorporacion.objects.filter(contrato=contrato)
		if len(cuota) == 0:
			cuota = None
	except Exception:
		cuota = None

	# arriendo variable
	try:
		arriendo_variable = Arriendo_Variable.objects.filter(contrato=contrato)
		if len(arriendo_variable) == 0:
			arriendo_variable = None
	except Exception:
		arriendo_variable = None

	# fondo
	try:
		fondo = Fondo_Promocion.objects.filter(contrato=contrato)
	except Exception:
		fondo = None

	# garantía
	garantias_total = 0
	garantias = Garantia.objects.filter(contrato=contrato)
	for garantia in garantias:
		garantias_total += garantia.valor * garantia.moneda.moneda_historial_set.all().order_by('-id').first().valor


	options = {
		'margin-top': '0.75in',
		'margin-right': '0.75in',
		'margin-bottom': '0.55in',
		'margin-left': '0.75in',
		'encoding': "UTF-8",
		'no-outline': None,
		}

	css = ['static/assets/css/bootstrap.min.css']

	try:
		template = get_template('pdf/contratos/contrato_'+str(contrato.contrato_tipo_id)+'.html')
	except Exception:
		template = get_template('pdf/contratos/contrato_default.html')

	context = Context({
		'meses'				: meses,
		'empresa'			: empresa,
		'contrato'			: contrato,
		'locales'			: locales,
		'metros'			: metros['metros_cuadrados__sum'],
		'cliente'			: cliente,
		'representantes' 	: representantes,
		'renovacion'		: renovacion,
		'garantias_total'   : garantias_total,
		'arriendo' 			: arriendo,
		'arriendo_detalle'  : arriendo_detalle,
		'gasto_comun' 		: gasto_comun,
		'cuota'				: cuota,
		'arriendo_variable' : arriendo_variable,
		'arriendo_bodega'	: arriendo_bodega,
		'fondo' 			: fondo,
	})

	html 		= template.render(context)
	pdfkit.from_string(html, 'public/media/contratos/contrato_'+str(contrato.id)+'.pdf', options=options, css=css)
	pdf 		= open('public/media/contratos/contrato_'+str(contrato.id)+'.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=contrato_'+str(contrato.id)+'.pdf'
	pdf.close()

	return response



