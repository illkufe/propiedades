# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader
from django.template.loader import get_template 
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.db.models import Sum
from django.views.generic import View, ListView, FormView, CreateView, DeleteView, UpdateView

from administrador.models import Empresa, Cliente, Workflow
from locales.models import Local
from avatar.models import Avatar

from .forms import *
from .models import *

from utilidades.views import *
from utilidades.plugins.owncloud import *
from copy import deepcopy

from datetime import datetime

import base64
import pdfkit
import json
import os

# variables
modulo = 'Contrato'


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
		else:
			return self.render_to_response(self.get_context_data(form=form))


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

		queryset.fecha_contrato 	= queryset.fecha_contrato.strftime('%d/%m/%Y') if queryset.fecha_contrato is not None else ''
		queryset.fecha_inicio 		= queryset.fecha_inicio.strftime('%d/%m/%Y') if queryset.fecha_inicio is not None else ''
		queryset.fecha_termino 		= queryset.fecha_termino.strftime('%d/%m/%Y') if queryset.fecha_termino is not None else ''
		queryset.fecha_inicio_renta = queryset.fecha_inicio_renta.strftime('%d/%m/%Y') if queryset.fecha_inicio_renta is not None else ''
		queryset.fecha_entrega 		= queryset.fecha_entrega.strftime('%d/%m/%Y') if queryset.fecha_entrega is not None else ''
		queryset.fecha_renovacion 	= queryset.fecha_renovacion.strftime('%d/%m/%Y') if queryset.fecha_renovacion is not None else ''
		queryset.fecha_habilitacion = queryset.fecha_habilitacion.strftime('%d/%m/%Y') if queryset.fecha_habilitacion is not None else ''

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
		self.object.locales.clear()

		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class ContratoDocuments(ListView):

	model 			= Contrato
	template_name 	= 'documents.html'

	def get_context_data(self, **kwargs):

		context 			= super(ContratoDocuments, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'contrato'
		context['name'] 	= 'documentos'
		context['href'] 	= '/contrato/list'

		# contrato
		contrato 			= Contrato.objects.get(id=self.kwargs['pk'])

		# info for owncloud
		context['id'] 		= int(self.kwargs['pk'])
		context['url'] 		= 'Iproperty/Clientes/'+str(contrato.cliente.nombre)
		context['model'] 	= 'contrato'

		owncloud_create_path(self.request, ['Iproperty', 'Clientes', str(contrato.cliente.nombre), str(contrato.nombre_local)])

		return context


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
		context['workflow']	= self.get_workflow()

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

	def get_workflow(self):

		workflow = Workflow.objects.filter(empresa=self.request.user.userprofile.empresa, validado=True).exists()

		return workflow

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

		self.object = form.save(commit=False)
		context 	= self.get_context_data()
		accion 		= context['accion']

		form_garantia 		= context['form_garantia']
		# formularios conceptos
		form_minimo 		= context['form_minimo']
		form_minimo_detalle = context['form_minimo_detalle']
		form_variable 		= context['form_variable']
		form_bodega 		= context['form_bodega']
		form_cuota 			= context['form_cuota']
		form_promocion 		= context['form_promocion']
		form_comun 			= context['form_comun']

		if accion == 'create':

			propuesta 				= Propuesta_Contrato(numero=form.cleaned_data['numero'])
			# propuesta.user 			= self.request.user
			propuesta.empresa 		= self.request.user.userprofile.empresa
			propuesta.save()
			self.object.propuesta 	= propuesta
			self.object.user 		= self.request.user
			self.object.save()
			form.save_m2m()

			Propuesta_Proceso(
				estado 		= False,
				proceso 	= Proceso.objects.get(tipo_estado=1, workflow__empresa=self.request.user.userprofile.empresa),
				propuesta 	= propuesta,
				user 		= self.request.user,
				).save()


			# formulario garantia
			if form_garantia.is_valid():
				formularios = form_garantia.save(commit=False)
				for formulario in formularios:
					formulario.propuesta = self.object
					formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))
			
			# formulario arriendo minimo
			if self.object.arriendo_minimo is True:
				if form_minimo.is_valid():
					arriendo_minimo = form_minimo.save(commit=False)
					arriendo_minimo.propuesta = self.object
					arriendo_minimo.save()

					if form_minimo_detalle.is_valid():
						formularios = form_minimo_detalle.save(commit=False)
						for formulario in formularios:
							formulario.propuesta_arriendo_minimo = arriendo_minimo
							formulario.save()
					else:
						transaction.rollback()
						transaction.connections.close_all()
						return self.render_to_response(self.get_context_data(form=form))
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario arriendo variable
			if self.object.arriendo_variable is True:
				if form_variable.is_valid():
					formularios = form_variable.save(commit=False)
					for formulario in formularios:
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario arriendo bodega
			if self.object.arriendo_bodega is True:
				if form_bodega.is_valid():
					formularios = form_bodega.save(commit=False)
					for formulario in formularios:
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario cuota de incorporacion
			if self.object.cuota_incorporacion is True:
				if form_cuota.is_valid():
					formularios = form_cuota.save(commit=False)
					for formulario in formularios:
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario fondo de promocion
			if self.object.fondo_promocion is True:
				if form_promocion.is_valid():
					formularios = form_promocion.save(commit=False)
					for formulario in formularios:
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario gasto comun
			if self.object.gasto_comun is True:
				if form_comun.is_valid():
					formularios = form_comun.save(commit=False)
					for formulario in formularios:
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

		else:

			self.object.pk 		= None
			self.object.user 	= self.request.user
			self.object.save()
			form.save_m2m()

			# formulario garantia
			if form_garantia.is_valid():
				formularios = form_garantia.save(commit=False)
				for formulario in formularios:
					formulario.pk = None
					formulario.propuesta = self.object
					formulario.save()
			else:
				transaction.rollback()
				transaction.connections.close_all()
				return self.render_to_response(self.get_context_data(form=form))

			# formulario arriendo minimo
			if self.object.arriendo_minimo is True:
				if form_minimo.is_valid():
					arriendo_minimo = form_minimo.save(commit=False)
					arriendo_minimo.pk = None
					arriendo_minimo.propuesta = self.object
					arriendo_minimo.save()

					if form_minimo_detalle.is_valid():
						formularios = form_minimo_detalle.save(commit=False)
						for formulario in formularios:
							formulario.pk = None
							formulario.propuesta_arriendo_minimo = arriendo_minimo
							formulario.save()
					else:
						transaction.rollback()
						transaction.connections.close_all()
						return self.render_to_response(self.get_context_data(form=form))
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario arriendo variable
			if self.object.arriendo_variable is True:
				if form_variable.is_valid():
					formularios = form_variable.save(commit=False)
					for formulario in formularios:
						formulario.pk = None
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario arriendo bodega
			if self.object.arriendo_bodega is True:
				if form_bodega.is_valid():
					formularios = form_bodega.save(commit=False)
					for formulario in formularios:
						formulario.pk = None
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario cuota de incorporacion
			if self.object.cuota_incorporacion is True:
				if form_cuota.is_valid():
					formularios = form_cuota.save(commit=False)
					for formulario in formularios:
						formulario.pk = None
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario fondo de promocion
			if self.object.fondo_promocion is True:
				if form_promocion.is_valid():
					formularios = form_promocion.save(commit=False)
					for formulario in formularios:
						formulario.pk = None
						formulario.propuesta = self.object
						formulario.save()
				else:
					transaction.rollback()
					transaction.connections.close_all()
					return self.render_to_response(self.get_context_data(form=form))

			# formulario gasto comun
			if self.object.gasto_comun is True:
				if form_comun.is_valid():
					formularios = form_comun.save(commit=False)
					for formulario in formularios:
						formulario.pk = None
						formulario.propuesta = self.object
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

			context['form_garantia'] 		= InlineFormPropuestaGarantia(self.request.POST, prefix='garantia')
			context['form_minimo']			= FormPropuestaArriendo(self.request.POST, prefix='arriendo_minimo')
			context['form_minimo_detalle'] 	= InlineFormPropuestaMinimoDetalle(self.request.POST, prefix='arriendo_minimo_detalle')
			context['form_variable'] 		= InlineFormPropuestaVariable(self.request.POST, prefix='arriendo_variable')
			context['form_bodega'] 			= InlineFormPropuestaBodega(self.request.POST, prefix='arriendo_bodega')
			context['form_cuota'] 			= InlineFormPropuestaCuota(self.request.POST, prefix='cuota_incorporacion')
			context['form_promocion'] 		= InlineFormPropuestaPromocion(self.request.POST, prefix='fondo_promocion')
			context['form_comun'] 			= InlineFormPropuestaComun(self.request.POST, prefix='gasto_comun')

		else:
			context['form_garantia'] 		= InlineFormPropuestaGarantia(prefix='garantia')
			context['form_minimo']			= FormPropuestaArriendo(prefix='arriendo_minimo')
			context['form_minimo_detalle'] 	= InlineFormPropuestaMinimoDetalle(prefix='arriendo_minimo_detalle')
			context['form_variable'] 		= InlineFormPropuestaVariable(prefix='arriendo_variable')
			context['form_bodega'] 			= InlineFormPropuestaBodega(prefix='arriendo_bodega')
			context['form_cuota'] 			= InlineFormPropuestaCuota(prefix='cuota_incorporacion')
			context['form_promocion'] 		= InlineFormPropuestaPromocion(prefix='fondo_promocion')
			context['form_comun'] 			= InlineFormPropuestaComun(prefix='gasto_comun')

		return context

class PropuestaUpdate(PropuestaMixin, UpdateView):

	model 			= Propuesta_Version
	form_class 		= PropuestaForm
	template_name 	= 'propuesta_new.html'
	success_url 	= '/propuesta/list'

	def get_object(self, queryset=None):

		queryset = Propuesta_Version.objects.get(id=int(self.kwargs['pk']))

		queryset.fecha_contrato 	= queryset.fecha_contrato.strftime('%d/%m/%Y') if queryset.fecha_contrato is not None else ''
		queryset.fecha_inicio 		= queryset.fecha_inicio.strftime('%d/%m/%Y') if queryset.fecha_inicio is not None else ''
		queryset.fecha_termino 		= queryset.fecha_termino.strftime('%d/%m/%Y') if queryset.fecha_termino is not None else ''
		queryset.fecha_inicio_renta = queryset.fecha_inicio_renta.strftime('%d/%m/%Y') if queryset.fecha_inicio_renta is not None else ''
		queryset.fecha_entrega 		= queryset.fecha_entrega.strftime('%d/%m/%Y') if queryset.fecha_entrega is not None else ''
		queryset.fecha_habilitacion = queryset.fecha_habilitacion.strftime('%d/%m/%Y') if queryset.fecha_habilitacion is not None else ''
		queryset.fecha_renovacion 	= queryset.fecha_renovacion.strftime('%d/%m/%Y') if queryset.fecha_renovacion is not None else ''

		return queryset

	def get_context_data(self, **kwargs):
		
		context 			= super(PropuestaUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'propuesta'
		context['name'] 	= 'editar'
		context['href'] 	= '/propuesta/list'
		context['accion'] 	= 'update'
		propuesta  			= Propuesta_Version.objects.get(id=int(self.kwargs['pk']))

		if self.request.POST:

			context['form_garantia'] 		= InlineFormPropuestaGarantia(self.request.POST, instance=propuesta, prefix='garantia')
			context['form_minimo']			= FormPropuestaArriendo(self.request.POST, instance=propuesta.propuesta_arriendo_minimo_set.first(), prefix="arriendo_minimo")
			context['form_minimo_detalle'] 	= InlineFormPropuestaMinimoDetalle(self.request.POST, instance=propuesta.propuesta_arriendo_minimo_set.first(), prefix="arriendo_minimo_detalle")
			context['form_variable'] 		= InlineFormPropuestaVariable(self.request.POST, instance=propuesta, prefix="arriendo_variable")
			context['form_bodega'] 			= InlineFormPropuestaBodega(self.request.POST, instance=propuesta, prefix="arriendo_bodega")
			context['form_cuota'] 			= InlineFormPropuestaCuota(self.request.POST, instance=propuesta, prefix="cuota_incorporacion")
			context['form_promocion'] 		= InlineFormPropuestaPromocion(self.request.POST, instance=propuesta, prefix="fondo_promocion")
			context['form_comun'] 			= InlineFormPropuestaComun(self.request.POST, instance=propuesta, prefix="gasto_comun")

		else:

			context['form_garantia'] 		= InlineFormPropuestaGarantia(instance=propuesta, prefix='garantia')
			context['form_minimo']			= FormPropuestaArriendo(instance=propuesta.propuesta_arriendo_minimo_set.first(), prefix="arriendo_minimo")
			context['form_minimo_detalle'] 	= InlineFormPropuestaMinimoDetalle(instance=propuesta.propuesta_arriendo_minimo_set.first(), prefix="arriendo_minimo_detalle")
			context['form_variable'] 		= InlineFormPropuestaVariable(instance=propuesta, prefix="arriendo_variable")
			context['form_bodega'] 			= InlineFormPropuestaBodega(instance=propuesta, prefix="arriendo_bodega")
			context['form_cuota'] 			= InlineFormPropuestaCuota(instance=propuesta, prefix="cuota_incorporacion")
			context['form_promocion'] 		= InlineFormPropuestaPromocion(instance=propuesta, prefix="fondo_promocion")
			context['form_comun'] 			= InlineFormPropuestaComun(instance=propuesta, prefix="gasto_comun")

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

		context 				= super(PropuestaHistorialList, self).get_context_data(**kwargs)
		context['title'] 		= modulo
		context['subtitle'] 	= 'propuesta'
		context['name'] 		= 'historial'
		context['href'] 		= '/propuesta/list'
		context['propuesta_id'] = self.kwargs['pk']

		return context


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
			item.valor = formato_moneda_local(self.request, item.valor * item.moneda.moneda_historial_set.all().order_by('-id').first().valor, None)

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
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(formulario.errors, status=400, safe=False)

		elif concepto.concepto_tipo.id == 2:

			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(formulario.errors, status=400, safe=False)

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
				return JsonResponse(formulario.errors, status=400, safe=False)

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
				return JsonResponse(formulario.errors, status=400, safe=False)
			
		elif concepto.concepto_tipo.id == 5:

			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(formulario.errors, status=400, safe=False)

		elif concepto.concepto_tipo.id == 6:
			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(formulario.errors, status=400, safe=False)

		elif concepto.concepto_tipo.id == 7:

			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(formulario.errors, status=400, safe=False)

		elif concepto.concepto_tipo.id == 10:
			if formulario.is_valid():
				newscores = formulario.save(commit=False)

				for obj in formulario.deleted_objects:
					obj.delete()

				for newscore in newscores:
					newscore.concepto_id = concepto.id
					newscore.save()
			else:
				return JsonResponse(formulario.errors, status=400, safe=False)

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
		context['subtitle'] 	= 'Contratos'
		context['name'] 		= 'Conceptos'
		context['href'] 		= '/contrato/list'
		context['contrato_id']	= self.kwargs['contrato_id']

		formularios	= list()
		conceptos 	= Contrato.objects.get(id=self.kwargs['contrato_id']).conceptos.all()
		contrato 	= Contrato.objects.get(id=self.kwargs['contrato_id'])

		if self.request.POST:

			context['concepto_id'] 	= self.request.POST.get('concepto_id')
			concepto 				= Concepto.objects.get(id=context['concepto_id'])

			if concepto.concepto_tipo.id == 1:
				context['formulario'] 	= ArriendoMinimoFormSet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 2:
				context['formulario'] 	= ArriendoVariableFormSet(self.request.POST, instance=contrato, form_kwargs={'contrato': contrato})
			elif concepto.concepto_tipo.id == 3:
				context['formulario'] 	= GastoComunFormSet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 4:
				context['formulario'] 	= ServicioBasicoFormSet(self.request.POST, instance=contrato, form_kwargs={'contrato': contrato})
			elif concepto.concepto_tipo.id == 5:
				context['formulario'] 	= CuotaIncorporacionFormet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 6:
				context['formulario'] 	= GastoAsociadoFormSet(self.request.POST, instance=contrato, form_kwargs={'contrato': contrato})
			elif concepto.concepto_tipo.id == 7:
				context['formulario'] 	= ArriendoBodegaFormSet(self.request.POST, instance=contrato)
			elif concepto.concepto_tipo.id == 10:
				context['formulario'] 	= ReajusteFormSet(self.request.POST, instance=contrato, form_kwargs={'contrato': contrato})
			else:
				pass

			context['accion'] = 'create'

		# GET
		else:
			for concepto in conceptos:

				if concepto.concepto_tipo.id == 1:

					if Arriendo_Minimo.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = ArriendoMinimoFormSet(instance=contrato, queryset=Arriendo_Minimo.objects.filter(contrato=contrato, concepto=concepto))
					else:
						form = ArriendoMinimoFormSet()

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})


					# pass
				# 	if Arriendo.objects.filter(contrato=contrato, concepto=concepto).exists():
				# 		arriendo 				= Arriendo.objects.get(contrato=contrato, concepto=concepto)
				# 		arriendo.fecha_inicio 	= arriendo.fecha_inicio.strftime('%d/%m/%Y')
				# 		form 					= ArriendoForm(instance=arriendo, contrato=contrato)
				# 		form_detalle 			= ArriendoDetalleFormSet(instance=arriendo)
				# 	else:
				# 		form 			= ArriendoForm(contrato=contrato)
				# 		form_detalle 	= ArriendoDetalleFormSet()

				# 	formularios.append({
				# 		'fomulario' 		: form, 
				# 		'fomulario_detalle' : form_detalle,
				# 		'contrato' 			: contrato,
				# 		'concepto' 			: concepto,
				# 	})

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
						form = ServicioBasicoFormSet(form_kwargs={'contrato': contrato})

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
					if Gasto_Asociado.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = GastoAsociadoFormSet(instance=contrato, queryset=Gasto_Asociado.objects.filter(contrato=contrato, concepto=concepto), form_kwargs={'contrato': contrato})
					else:
						form = GastoAsociadoFormSet(form_kwargs={'contrato': contrato})

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

				elif concepto.concepto_tipo.id == 10:
					if Reajuste.objects.filter(contrato=contrato, concepto=concepto).exists():
						form = ReajusteFormSet(instance=contrato, queryset=Reajuste.objects.filter(contrato=contrato, concepto=concepto), form_kwargs={'contrato': contrato})
					else:
						form = ReajusteFormSet(form_kwargs={'contrato': contrato})

					formularios.append({
						'fomulario' : form, 
						'contrato' 	: contrato,
						'concepto' 	: concepto,
					})

				else:
					pass

				context['formularios'] 	= formularios
				context['accion'] 		= 'update'

		return context


# contratos inactivos
class ContratosInactivosList(ListView):

	model 			= Contrato
	template_name 	= 'contrato_inactivo_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ContratosInactivosList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Contrato Inactivos'
		context['name'] 	= 'Lista'
		context['href'] 	= '/contratos/inactivos/list'

		return context

	def get_queryset(self):

		queryset = Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True, estado__in=[1])

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
				'nombre_local' 			: contrato.nombre_local,
				'fecha_contrato' 		: contrato.fecha_contrato,
				'fecha_inicio' 			: contrato.fecha_inicio.strftime('%d/%m/%Y'),
				'fecha_termino' 		: contrato.fecha_termino.strftime('%d/%m/%Y'),
				'fecha_inicio_renta' 	: contrato.fecha_inicio_renta.strftime('%d/%m/%Y') if contrato.fecha_inicio_renta is not None else None,
				'fecha_entrega' 		: contrato.fecha_entrega.strftime('%d/%m/%Y') if contrato.fecha_entrega is not None else None,
				'fecha_habilitacion' 	: contrato.fecha_habilitacion.strftime('%d/%m/%Y'),
				'fecha_renovacion' 		: contrato.fecha_renovacion.strftime('%d/%m/%Y'),
				'fecha_activacion' 		: contrato.fecha_activacion.strftime('%d/%m/%Y') if contrato.fecha_activacion is not None else None,
				'bodega' 				: contrato.bodega,
				'metros_bodega' 		: contrato.metros_bodega,
				'tipo' 					: {'id': contrato.tipo.id, 'nombre': contrato.tipo.nombre},
				'estado' 				: {'id': contrato.estado.id, 'nombre': contrato.estado.nombre},
				'cliente' 				: {'id': contrato.cliente.id, 'nombre': contrato.cliente.nombre},
				'locales' 				: data_locales,
				'conceptos' 			: data_conceptos,
				})

		return JsonResponse(data, safe=False)

class GET_CONTRATO_DOCUMENTS(View):

	http_method_names = ['get']

	def get(self, request, pk):

		contrato = Contrato.objects.get(id=pk)

		data = oc_list_directory(str(contrato.nombre_local), 'Iproperty/Clientes/'+str(contrato.cliente.nombre)+'/'+str(contrato.nombre_local))

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

				version

				cliente = {
					'id' 			: version.cliente.id, 
					'nombre' 		: version.cliente.nombre,
				}

				tipo = {
					'id' 			: version.tipo.id, 
					'nombre' 		: version.tipo.nombre, 
					'codigo' 		: version.tipo.codigo, 
					'descripcion' 	: version.tipo.descripcion, 
				}

				user = {
					'id' 			: version.user.id,
					'first_name' 	: version.user.first_name,
					'last_name' 	: version.user.last_name,
				}

				data_versiones.append({
					'id' 					: version.id,
					'numero'				: version.numero,
					'nombre_local'			: version.nombre_local,
					'destino_comercial'		: version.destino_comercial if version.destino_comercial is not None else None,
					'fecha_inicio'			: version.fecha_inicio if version.fecha_inicio is not None else None,
					'fecha_termino'			: version.fecha_termino if version.fecha_termino is not None else None,
					'fecha_inicio_renta'	: version.fecha_inicio_renta if version.fecha_inicio_renta is not None else None,
					'fecha_entrega'			: version.fecha_entrega if version.fecha_entrega is not None else None,
					'meses_contrato'		: version.meses_contrato if version.meses_contrato is not None else None,
					'meses_aviso_comercial'	: version.meses_aviso_comercial if version.meses_aviso_comercial is not None else None,
					'meses_remodelacion'	: version.meses_remodelacion if version.meses_remodelacion is not None else None,
					'fecha_habilitacion'	: version.fecha_habilitacion if version.fecha_habilitacion is not None else None,
					'fecha_renovacion'		: version.fecha_renovacion if version.fecha_renovacion is not None else None,
					'creado_en' 			: version.creado_en.strftime('%d/%m/%Y'),
					'cliente'				: cliente,
					'tipo'					: tipo,
					'user'					: user,
					})



			data.append({
				'id' 		: propuesta.id,
				'creado_en' : propuesta.creado_en.strftime('%d/%m/%Y'),
				'versiones' : data_versiones,
				})

		return JsonResponse(data, safe=False)

class PROPUESTA_CONTRATO_WORKFLOW(View):

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

			for proceso in propuesta.procesos.all():

				acciones				= False
				workflow_responsables 	= list()
				workflow_estados 		= list()
				version 				= propuesta.propuesta_version_set.all().order_by('-id').first()

				version = {
					'id' 			: version.id,
					'nombre_local' 	: version.nombre_local,
					'creado_en' 	: version.creado_en.strftime('%d/%m/%Y %H:%M'),
				}

				# responsables
				for responsable in proceso.responsable.all():

					if responsable.user == self.request.user:
						acciones = True

					# obtener avatar
					primary_avatar = responsable.user.avatar_set.all().order_by('-primary')[:1]
					if primary_avatar:
						avatar = str(primary_avatar[0].avatar)
					else:
						avatar = None

					workflow_responsables.append({
						'id'			: responsable.user.id,
						'first_name'	: responsable.user.first_name,
						'last_name'		: responsable.user.last_name,
						'username'		: responsable.user.username,
						'avatar' 		: avatar,
					})

				# proceso
				workflow_proceso = {
					'id'			: proceso.id,
					'nombre' 		: proceso.nombre,
					'background' 	: proceso.tipo_estado.background,
					'acciones'		: acciones,
					'estado'		: Propuesta_Proceso.objects.get(propuesta=propuesta, proceso=proceso).estado,
					'tipo'			: {'id':proceso.tipo_estado.id, 'nombre':proceso.tipo_estado.nombre}
				}

				workflow = {
					'responsables'	: workflow_responsables,
					'proceso'		: workflow_proceso,
				}

				data.append({
					'id' 			: propuesta.id,
					'creado_en' 	: propuesta.creado_en.strftime('%d/%m/%Y %H:%M'),
					'version' 		: version,
					'workflow' 		: workflow,
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
	
	try:

		version 	= Propuesta_Version.objects.get(id=id)

		clone 		= deepcopy(version)
		clone.id 	= None
		clone.save()

		# relaciones
		clone.locales = version.locales.all()
		clone.save()

		if version.arriendo_minimo is True:
			concepto 	= deepcopy(version.propuesta_arriendo_minimo_set.first())
			concepto.id = None
			concepto.propuesta = clone
			concepto.save()

		if version.arriendo_variable is True:
			concepto 	= deepcopy(version.propuesta_arriendo_variable_set.first())
			concepto.id = None
			concepto.propuesta = clone
			concepto.save()

		if version.arriendo_bodega is True:
			concepto 	= deepcopy(version.propuesta_arriendo_bodega_set.first())
			concepto.id = None
			concepto.propuesta = clone
			concepto.save()

		if version.cuota_incorporacion is True:
			concepto 	= deepcopy(version.propuesta_cuota_incorporacion_set.first())
			concepto.id = None
			concepto.propuesta = clone
			concepto.save()

		if version.fondo_promocion is True:
			concepto 	= deepcopy(version.propuesta_fondo_promocion_set.first())
			concepto.id = None
			concepto.propuesta = clone
			concepto.save()

		if version.gasto_comun	 is True:
			concepto 	= deepcopy(version.propuesta_gasto_comun_set.first())
			concepto.id = None
			concepto.propuesta = clone
			concepto.save()

		estado 	= True
		mensaje = 'restauración correcta'

	except Exception as error:
		estado 	= False
		mensaje = error

	response = {
		'estado'	: estado,
		'mensaje'	: mensaje,
	}

	return JsonResponse(response, safe=False)

def propuesta_historial_tabla(request, id=None):

	head = list()
	body = list()

	propuesta = Propuesta_Contrato.objects.get(id=id)
	versiones = propuesta.propuesta_version_set.all()

	# datos informacion
	usuario					= list()
	numero 					= list()
	# datos periodo
	fecha_contrato 			= list()
	fecha_inicio 			= list()
	fecha_termino 			= list()
	fecha_inicio_renta 		= list()
	fecha_entrega 			= list()
	fecha_habilitacion 		= list()
	fecha_renovacion 		= list()
	meses_contrato 			= list()
	meses_aviso_comercial 	= list()
	meses_remodelacion 		= list()
	# datos conceptos
	garantia 		 		= list()
	arriendo_minimo 		= list()
	arriendo_variable 		= list()
	arriendo_bodega 		= list()
	cuota_incorporacion 	= list()
	fondo_promocion 		= list()
	gasto_comun 			= list()


	# datos informacion
	numero.append({'data':'item', 'value': 'Número Contrato'})
	usuario.append({'data':'item', 'value': 'Usuario Creador'})
	# datos periodo
	fecha_contrato.append({'data':'item', 'value': 'Fecha de Contrato'})
	fecha_inicio.append({'data':'item', 'value': 'Fecha de Inicio'})
	fecha_termino.append({'data':'item', 'value': 'Fecha de Término'})
	fecha_inicio_renta.append({'data':'item', 'value': 'Fecha de Inicio de Renta'})
	fecha_entrega.append({'data':'item', 'value': 'Fecha de Entrega'})
	fecha_habilitacion.append({'data':'item', 'value': 'Fecha de Habilitación'})
	fecha_renovacion.append({'data':'item', 'value': 'Fecha de Remodelación'})
	meses_contrato.append({'data':'item', 'value': 'Meses de Arriendo'})
	meses_aviso_comercial.append({'data':'item', 'value': 'Meses Aviso Comercial'})
	meses_remodelacion.append({'data':'item', 'value': 'Meses de Remodelacion'})
	# datos conceptos
	garantia.append({'data':'item', 'value': 'Garantía'})
	arriendo_minimo.append({'data':'item', 'value': 'Arriendo Mínimo'})
	arriendo_variable.append({'data':'item', 'value': 'Arriendo Variable'})
	arriendo_bodega.append({'data':'item', 'value': 'Arriendo de Bodega'})
	cuota_incorporacion.append({'data':'item', 'value': 'Cuota de Incorporación'})
	fondo_promocion.append({'data':'item', 'value': 'Fondo de Promoción'})
	gasto_comun.append({'data':'item', 'value': 'Gasto Común'})

	for version in versiones:

		value_garantia 				= '<span class="badge">no aplica</span>'
		value_arriendo_minimo 		= '<span class="badge">no aplica</span>'
		value_arriendo_variable 	= '<span class="badge">no aplica</span>'
		value_arriendo_bodega 		= '<span class="badge">no aplica</span>'
		value_cuota_incorporacion 	= '<span class="badge">no aplica</span>'
		value_fondo_promocion 		= '<span class="badge">no aplica</span>'
		value_gasto_comun 			= '<span class="badge">no aplica</span>'

		# conceptos
		if version.arriendo_minimo is True:
			value_arriendo_minimo = str(version.propuesta_arriendo_minimo_set.first().valor)+' '+str(version.propuesta_arriendo_minimo_set.first().moneda)
		if version.arriendo_variable is True:
			value_arriendo_variable = str(version.propuesta_arriendo_variable_set.first().valor)+' '+str(version.propuesta_arriendo_variable_set.first().moneda)
		if version.arriendo_bodega is True:
			value_arriendo_bodega = str(version.propuesta_arriendo_bodega_set.first().valor)+' '+str(version.propuesta_arriendo_bodega_set.first().moneda)
		if version.cuota_incorporacion is True:
			value_cuota_incorporacion = str(version.propuesta_cuota_incorporacion_set.first().valor)+' '+str(version.propuesta_cuota_incorporacion_set.first().moneda)
		if version.fondo_promocion is True:
			value_fondo_promocion = str(version.propuesta_fondo_promocion_set.first().valor)+' '+str(version.propuesta_fondo_promocion_set.first().moneda)
		if version.gasto_comun is True:
			value_gasto_comun = str(version.propuesta_gasto_comun_set.first().valor)+' '+str(version.propuesta_gasto_comun_set.first().moneda)

		head.append({'data':version.id, 'title': version.creado_en.strftime('%d/%m/%Y %H:%M')})
		# datos informacion
		numero.append({'data':version.id, 'value': version.numero, 'type': 'informacion'})
		usuario.append({'data':version.id, 'value': avatar_usuario(version.user), 'type': 'informacion'})
		# datos periodo
		fecha_contrato.append({'data':version.id, 'value': version.fecha_contrato.strftime('%d/%m/%Y') if version.fecha_contrato is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		fecha_inicio.append({'data':version.id, 'value': version.fecha_inicio.strftime('%d/%m/%Y') if version.fecha_inicio is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		fecha_termino.append({'data':version.id, 'value': version.fecha_termino.strftime('%d/%m/%Y') if version.fecha_termino is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		fecha_inicio_renta.append({'data':version.id, 'value': version.fecha_inicio_renta.strftime('%d/%m/%Y') if version.fecha_inicio_renta is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		fecha_entrega.append({'data':version.id, 'value': version.fecha_entrega.strftime('%d/%m/%Y') if version.fecha_entrega is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		fecha_habilitacion.append({'data':version.id, 'value': version.fecha_habilitacion.strftime('%d/%m/%Y') if version.fecha_habilitacion is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		fecha_renovacion.append({'data':version.id, 'value': version.fecha_renovacion.strftime('%d/%m/%Y') if version.fecha_renovacion is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		meses_contrato.append({'data':version.id, 'value': str(version.meses_contrato)+' mes(s)' if version.meses_contrato is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		meses_aviso_comercial.append({'data':version.id, 'value': str(version.meses_aviso_comercial)+' mes(s)' if version.meses_aviso_comercial is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		meses_remodelacion.append({'data':version.id, 'value': str(version.meses_remodelacion)+' mes(s)' if version.meses_remodelacion is not None else '<span class="badge">sin dato</span>', 'type': 'periodo'})
		# datos conceptos
		garantia.append({'data':version.id, 'value': value_garantia, 'type': 'concepto'})
		arriendo_minimo.append({'data':version.id, 'value': value_arriendo_minimo, 'type': 'concepto'})
		arriendo_variable.append({'data':version.id, 'value': value_arriendo_variable, 'type': 'concepto'})
		arriendo_bodega.append({'data':version.id, 'value': value_arriendo_bodega, 'type': 'concepto'})
		cuota_incorporacion.append({'data':version.id, 'value': value_cuota_incorporacion, 'type': 'concepto'})
		fondo_promocion.append({'data':version.id, 'value': value_fondo_promocion, 'type': 'concepto'})
		gasto_comun.append({'data':version.id, 'value': value_gasto_comun, 'type': 'concepto'})

	# datos informacion
	body.append(numero)
	body.append(usuario)
	# datos periodo
	body.append(fecha_contrato)
	body.append(fecha_inicio)
	body.append(fecha_termino)
	body.append(fecha_inicio_renta)
	body.append(fecha_entrega)
	body.append(fecha_habilitacion)
	body.append(fecha_renovacion)
	body.append(meses_contrato)
	body.append(meses_aviso_comercial)
	body.append(meses_remodelacion)
	# datos conceptos
	body.append(garantia)
	body.append(arriendo_minimo)
	body.append(arriendo_variable)
	body.append(arriendo_bodega)
	body.append(cuota_incorporacion)
	body.append(fondo_promocion)
	body.append(gasto_comun)

	return JsonResponse({'head':head, 'body':body}, safe=False)

def propuesta_generar_pdf(request, id=None):

	version 			= Propuesta_Version.objects.get(id=id)
	representantes 		= list()
	locales 			= list()
	arriendo_minimo 	= 'No Aplica'
	arriendo_variable 	= 'No Aplica'
	arriendo_bodega 	= 'No Aplica'
	cuota_incorporacion = 'No Aplica'
	fondo_promocion 	= 'No Aplica'
	gasto_comun 		= 'No Aplica'

	for local in version.locales.all():
		locales.append({
			'id' 		: local.id,
			'nombre' 	: local.nombre,
			'activo' 	: {'id':local.activo.id, 'nombre':local.activo.nombre},
			})

	for representante in version.cliente.representante_set.all():
		representantes.append({
			'id' 			: representante.id,
			'nombre' 		: representante.nombre,
			'rut' 			: representante.rut,
			'nacionalidad' 	: representante.nacionalidad,
			'profesion' 	: representante.profesion,
			'domicilio' 	: representante.domicilio,
			'estado_civil' 	: {'id':representante.estado_civil.id, 'nombre':representante.estado_civil.nombre} ,
			})

	empresa = {
		'id' 		: version.propuesta.empresa.id,
		'nombre'	: version.propuesta.empresa.nombre,
	}

	cliente = {
		'id' 				: version.cliente.id,
		'nombre'			: version.cliente.nombre,
		'rut'				: version.cliente.rut,
		'email'				: version.cliente.email,
		'razon_social'		: version.cliente.razon_social,
		'region'			: version.cliente.region,
		'comuna'			: version.cliente.comuna,
		'ciudad'			: version.cliente.ciudad,
		'direccion'			: version.cliente.direccion,
		'telefono'			: version.cliente.telefono,
		'representantes'	: representantes,
		'giro'				: {'id':version.cliente.giro.id, 'descripcion':version.cliente.giro.descripcion},
	}

	if version.arriendo_minimo is True:
		arriendo_minimo = str(version.propuesta_arriendo_minimo_set.first().valor)+' '+str(version.propuesta_arriendo_minimo_set.first().moneda)
	if version.arriendo_variable is True:
		arriendo_variable = str(version.propuesta_arriendo_variable_set.first().valor)+' '+str(version.propuesta_arriendo_variable_set.first().moneda)
	if version.arriendo_bodega is True:
		arriendo_bodega = str(version.propuesta_arriendo_bodega_set.first().valor)+' '+str(version.propuesta_arriendo_bodega_set.first().moneda)
	if version.cuota_incorporacion is True:
		cuota_incorporacion = str(version.propuesta_cuota_incorporacion_set.first().valor)+' '+str(version.propuesta_cuota_incorporacion_set.first().moneda)
	if version.fondo_promocion is True:
		fondo_promocion = str(version.propuesta_fondo_promocion_set.first().valor)+' '+str(version.propuesta_fondo_promocion_set.first().moneda)
	if version.gasto_comun is True:
		gasto_comun = str(version.propuesta_gasto_comun_set.first().valor)+' '+str(version.propuesta_gasto_comun_set.first().moneda)

	data = {
		'id'					: version.id,
		# 'fecha_contrato'		: version.fecha_contrato,
		'fecha_inicio'			: version.fecha_inicio,
		'fecha_termino'			: version.fecha_termino,
		'arriendo_minimo' 		: arriendo_minimo,
		'arriendo_variable' 	: arriendo_variable,
		'arriendo_bodega' 		: arriendo_bodega,
		'cuota_incorporacion' 	: cuota_incorporacion,
		'fondo_promocion' 		: fondo_promocion,
		'gasto_comun' 			: gasto_comun,
		'empresa'				: empresa,
		'cliente'				: cliente,
		'locales'				: locales,
		}

	# configuracion pdf
	css 		= ['static/assets/css/bootstrap.min.css']
	template 	= 'pdf/template_propuesta.html'
	options  	= {
		'margin-top': '0.75in',
		'margin-right': '0.75in',
		'margin-bottom': '0.55in',
		'margin-left': '0.75in',
		'encoding': "UTF-8",
		'no-outline': None,
	}
	archive 	= {
		'directory' :'public/media/propuestas',
		'name' 		:'propuesta_'+str(version.id),
	} 

	configuracion = {
		'options'	: options,
		'template' 	: template,
		'css'       : css,
		'archive' 	: archive,
	}

	# return JsonResponse(data, safe=False)
	return generar_pdf(configuracion, data)

def propuesta_workflow(request):
	estado 	= True 
	mensaje = 'accción realizada correctamente'

	try:
		var_post 		= request.POST.copy()

		propuesta_id 	= var_post['propuesta']
		proceso_id 		= var_post['proceso']
		estado_accion	= var_post['estado']

		propuesta 			= Propuesta_Contrato.objects.get(id=propuesta_id)
		proceso 			= propuesta.procesos.get(id=proceso_id)
		propuesta_proceso 	= Propuesta_Proceso.objects.get(propuesta=propuesta, proceso=proceso)

		if estado_accion == 'true':
			propuesta_proceso.estado = True
			propuesta_proceso.save()

			if Propuesta_Proceso.objects.filter(propuesta=propuesta, estado=False).exists() is not True:
				#{falta: revisar ultimo proceso}
				data_sucesores 		= list()
				propuesta_procesos 	= Propuesta_Proceso.objects.filter(propuesta=propuesta).values_list('proceso_id', flat=True)
				
				for item in Proceso.objects.filter(antecesor__in=propuesta_procesos).distinct():
					data_sucesores.append(item.id)

				Propuesta_Proceso.objects.filter(propuesta=propuesta).delete()

				for sucesor in data_sucesores:
					Propuesta_Proceso(propuesta=propuesta, proceso_id=sucesor).save()

		elif estado_accion == 'false':
			Propuesta_Proceso.objects.filter(propuesta=propuesta).delete()
			for antecesor in proceso.antecesor.all():
				Propuesta_Proceso(propuesta=propuesta, proceso=antecesor).save()
		else:
			estado 	= False 
			mensaje = 'error'

	except Exception as error:
		estado 	= False 
		mensaje = error

	response = {
		'estado'	: estado,
		'mensaje'	: mensaje,
	}

	return JsonResponse(response, safe=False)

# funciones - contrato
def contrato_activar(request, contrato_id):

	try:
		data 						= {'estado': 'ok'}
		contrato 					= Contrato.objects.get(id=contrato_id)
		contrato.fecha_activacion 	= datetime.now()
		contrato.estado 			= Contrato_Estado.objects.get(id=4)
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
		template = get_template('pdf/default.html')

	context = Context({
		'meses'				: meses,
		'empresa'			: empresa,
		'contrato'			: contrato,
		'locales'			: locales,
		'metros'			: metros['metros_cuadrados__sum'],
		'cliente'			: cliente,
		'representantes' 	: representantes,
		'renovacion'		: renovacion,
		'garantias_total' 	: garantias_total,
		'arriendo' 			: arriendo,
		'arriendo_detalle' 	: arriendo_detalle,
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



