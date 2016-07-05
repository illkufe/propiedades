# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import Context, loader
from django.template.loader import get_template 
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.db.models import Sum
from django.views.generic import View, ListView, FormView, CreateView, DeleteView, UpdateView

from .forms import ContratoTipoForm, ContratoForm, InformacionForm, ArriendoForm, ArriendoDetalleFormSet, ArriendoVariableForm, ArriendoVariableFormSet, GastoComunFormSet, CuotaIncorporacionFormet, FondoPromocionForm
from .models import Contrato_Tipo, Contrato, Arriendo, Arriendo_Variable, Gasto_Comun, Cuota_Incorporacion, Fondo_Promocion

from accounts.models import UserProfile
from administrador.models import Empresa, Cliente
from locales.models import Local
from procesos.models import Proceso, Proceso_Detalle

from utilidades.views import meses_entre_fechas

import base64
import pdfkit
import json
import os


class ContratoTipoMixin(object):

	template_name 	= 'viewer/contratos/contrato_tipo_new.html'
	form_class 		= ContratoTipoForm
	success_url 	= '/contratos-tipo/list'

	def form_invalid(self, form):
		response = super(ContratoTipoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		profile 		= UserProfile.objects.get(user=self.request.user)
		obj 			= form.save(commit=False)
		obj.empresa_id 	= profile.empresa_id

		obj.save()

		response = super(ContratoTipoMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {
				'estado': 'ok',
			}
			return JsonResponse(data)
		else:
			return response

class ContratoTipoNew(ContratoTipoMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(ContratoTipoNew, self).get_context_data(**kwargs)
		context['title'] 	= 'Contratos'
		context['subtitle'] = 'Tipo de Contrato'
		context['name'] 	= 'Nueva'
		context['href'] 	= 'contratos-tipo'
		context['accion'] 	= 'create'

		return context

class ContratoTipoList(ListView):

	model 			= Contrato_Tipo
	template_name 	= 'viewer/contratos/contrato_tipo_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ContratoTipoList, self).get_context_data(**kwargs)
		context['title'] 	= 'Contratos'
		context['subtitle'] = 'Tipo de Contrato'
		context['name'] 	= 'Lista'
		context['href'] 	= 'contratos-tipo'
		
		return context

	def get_queryset(self):

		queryset = Contrato_Tipo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

class ContratoTipoDelete(DeleteView):

	model 		= Contrato_Tipo
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class ContratoTipoUpdate(UpdateView):

	model 			= Contrato_Tipo
	form_class 		= ContratoTipoForm
	template_name 	= 'viewer/contratos/contrato_tipo_new.html'
	success_url 	= '/contratos-tipo/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(ContratoTipoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Contratos'
		context['subtitle'] = 'Tipo de Contrato'
		context['name'] 	= 'Editar'
		context['href'] 	= 'contratos-tipo'
		context['accion'] 	= 'update'

		return context



class ContratoMixin(object):

	template_name 	= 'viewer/contratos/contrato_new.html'
	form_class 		= ContratoForm
	success_url 	= '/contratos/list'

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

		profile 		= UserProfile.objects.get(user=self.request.user)
		obj 			= form.save(commit=False)
		obj.empresa_id 	= profile.empresa_id
		obj.save()
		form.save_m2m()

		response = super(ContratoMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {
				'estado': 'ok',
			}
			return JsonResponse(data)
		else:
			return response

class ContratoNew(ContratoMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(ContratoNew, self).get_context_data(**kwargs)
		context['title'] 	= 'Contratos'
		context['subtitle'] = 'Contrato'
		context['name'] 	= 'Nuevo'
		context['href'] 	= 'contratos'
		context['accion'] 	= 'create'
		
		return context

class ContratoList(ListView):

	model 			= Contrato
	template_name 	= 'viewer/contratos/contrato_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ContratoList, self).get_context_data(**kwargs)
		context['title'] 	= 'Contratos'
		context['subtitle'] = 'Contrato'
		context['name'] 	= 'Lista'
		context['href'] 	= 'contratos'

		return context

	def get_queryset(self):

		queryset 	= Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		for item in queryset:
			item.fecha_inicio  	= item.fecha_inicio.strftime('%d/%m/%Y')
			item.fecha_termino 	= item.fecha_termino.strftime('%d/%m/%Y')
			item.cantidad 		= len(item.conceptos.all()) # cantidad de conceptos

		return queryset

class ContratoDelete(DeleteView):

	model 		= Contrato
	success_url = reverse_lazy('/contratos/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class ContratoUpdate(ContratoMixin, UpdateView):

	model 			= Contrato
	form_class 		= ContratoForm
	template_name 	= 'viewer/contratos/contrato_new.html'
	success_url 	= '/contratos/list'

	def get_object(self, queryset=None):

		queryset = Contrato.objects.get(id=int(self.kwargs['pk']))

		queryset.fecha_contrato 	= queryset.fecha_contrato.strftime('%d/%m/%Y')
		queryset.fecha_inicio 		= queryset.fecha_inicio.strftime('%d/%m/%Y')
		queryset.fecha_termino 		= queryset.fecha_termino.strftime('%d/%m/%Y')
		queryset.fecha_habilitacion = queryset.fecha_habilitacion.strftime('%d/%m/%Y')
		queryset.fecha_activacion 	= queryset.fecha_activacion.strftime('%d/%m/%Y')
		queryset.fecha_renovacion 	= queryset.fecha_renovacion.strftime('%d/%m/%Y')
		queryset.fecha_remodelacion = queryset.fecha_remodelacion.strftime('%d/%m/%Y')
		queryset.fecha_aviso 		= queryset.fecha_aviso.strftime('%d/%m/%Y')
		queryset.fecha_plazo 		= queryset.fecha_plazo.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):
		
		context 			= super(ContratoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Contratos'
		context['subtitle'] = 'Contrato'
		context['name'] 	= 'Editar'
		context['href'] 	= 'contratos'
		context['accion'] 	= 'update'

		return context



class ContratoConceptoMixin(object):

	template_name 	= 'viewer/contratos/contrato_conceptos_new.html'
	form_class 		= InformacionForm
	success_url 	= '/contratos/list'

	def form_invalid(self, form):

		response = super(ContratoConceptoMixin, self).form_invalid(form)

		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context 					= self.get_context_data()

		formset_arriendo 			= context['formset_arriendo']
		formset_detalle 			= context['formset_detalle']
		form_arriendo_variable 		= context['form_arriendo_variable']
		formset_gasto_comun			= context['form_gasto_comun']
		formset_cuota_incorporacion	= context['form_cuota_incorporacion']
		formset_fondo_promocion		= context['form_fondo_promocion']
		conceptos 					= Contrato.objects.get(id=self.kwargs['contrato_id']).conceptos.all()

		for concepto in conceptos:
			if concepto.id == 1:
				if formset_arriendo.is_valid():
					formset_arriendo.save()
					if formset_detalle.is_valid():
						self.object = formset_arriendo.save(commit=False)
						formset_detalle.instance = self.object
						formset_detalle.save()

			elif concepto.id == 2:
				if form_arriendo_variable.is_valid():
					form_arriendo_variable.save()

			elif concepto.id == 3:
				if formset_gasto_comun.is_valid():
					formset_gasto_comun.save()

			elif concepto.id == 5:
				if formset_cuota_incorporacion.is_valid():
					formset_cuota_incorporacion.save()

			elif concepto.id == 6:
				if formset_fondo_promocion.is_valid():
					formset_fondo_promocion.save()

			else:
				pass

		response = super(ContratoConceptoMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'estado': 'ok',
			}
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
		context['conceptos']	= Contrato.objects.get(id=self.kwargs['contrato_id']).conceptos.all()
		
		if self.request.POST:

			contrato = Contrato.objects.get(id=self.kwargs['contrato_id'])

			# arriendo mínimo
			try:
				arriendo_minimo 			= Arriendo.objects.get(contrato_id=self.kwargs['contrato_id'])
				context['formset_arriendo'] = ArriendoForm(self.request.POST, instance=arriendo_minimo)
				context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST,  instance=arriendo_minimo)
			except Exception:
				context['formset_arriendo'] = ArriendoForm(self.request.POST)
				context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST)

			# arriendo variable
			try:
				arriendo_variable 					= Arriendo_Variable.objects.filter(contrato_id=self.kwargs['contrato_id'])
				context['form_arriendo_variable'] 	= ArriendoVariableFormSet(self.request.POST, instance=contrato)
			except Exception:
				
				context['form_arriendo_variable'] 	= ArriendoVariableFormSet(self.request.POST)

			# gasto comun
			try:
				gasto_comun 				= Gasto_Comun.objects.filter(contrato_id=self.kwargs['contrato_id'])
				context['form_gasto_comun'] = GastoComunFormSet(self.request.POST, instance=contrato)
			except Exception:
				context['form_gasto_comun'] = GastoComunFormSet(self.request.POST)

			# cuota incorporacion
			try:
				cuota_incorporacion 				= Cuota_Incorporacion.objects.filter(contrato_id=self.kwargs['contrato_id'])
				context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(self.request.POST, instance=contrato)
			except Exception:
				context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(self.request.POST)

			# fondo promocion
			try:
				fondo_promocion 				= Fondo_Promocion.objects.get(contrato_id=self.kwargs['contrato_id'])
				context['form_fondo_promocion'] = FondoPromocionForm(self.request.POST, instance=fondo_promocion)
			except Exception:
				context['form_fondo_promocion'] = FondoPromocionForm(self.request.POST)

		else:

			contrato_id = self.kwargs['contrato_id']
			contrato 	= Contrato.objects.get(id=contrato_id)

			# arriendo mínimo
			try:
				arriendo_minimo 				= Arriendo.objects.get(contrato_id=contrato_id)
				arriendo_minimo.fecha_inicio 	= arriendo_minimo.fecha_inicio.strftime('%d/%m/%Y')
				context['formset_arriendo'] 	= ArriendoForm(instance=arriendo_minimo, contrato=contrato)
				context['formset_detalle'] 		= ArriendoDetalleFormSet(instance=arriendo_minimo)
			except Exception:
				context['formset_arriendo'] 	= ArriendoForm(contrato=contrato)
				context['formset_detalle'] 		= ArriendoDetalleFormSet()

			# arriendo variable
			try:
				arriendo_variable 					= Arriendo_Variable.objects.filter(contrato_id=contrato_id)
				context['form_arriendo_variable'] 	= ArriendoVariableFormSet(instance=contrato)
			except Exception:
				context['form_arriendo_variable'] 	= ArriendoVariableFormSet()

			# gasto comun
			try:
				gasto_comun 				= Gasto_Comun.objects.filter(contrato_id=contrato_id)
				context['form_gasto_comun'] = GastoComunFormSet(instance=contrato, form_kwargs={'contrato': contrato})
			except Exception:
				context['form_gasto_comun'] = GastoComunFormSet(form_kwargs={'contrato': contrato})

			# cuota incorporación
			try:
				cuota_incorporacion 				= Cuota_Incorporacion.objects.filter(contrato_id=contrato_id)
				context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(instance=contrato, form_kwargs={'contrato': contrato})

			except Exception as asd:
				print (asd)
				context['form_cuota_incorporacion'] = CuotaIncorporacionFormet(form_kwargs={'contrato': contrato})

			# fondo promoción
			try:
				fondo_promocion 				= Fondo_Promocion.objects.get(contrato=contrato)
				fondo_promocion.fecha 			= fondo_promocion.fecha.strftime('%d/%m/%Y')
				context['form_fondo_promocion'] = FondoPromocionForm(instance=fondo_promocion, contrato=contrato)
			except Exception:
				context['form_fondo_promocion'] = FondoPromocionForm(contrato=contrato)

		return context



# API -----------------
class CONTRATO(View):
	http_method_names = ['get']
	
	def get(self, request, id=None):

		profile = UserProfile.objects.get(user=self.request.user)
		empresa = Empresa.objects.get(id=profile.empresa_id)

		if id == None:
			self.object_list = Contrato.objects.filter(empresa=empresa, visible=True)
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
				'fecha_inicio' 			: contrato.fecha_inicio,
				'fecha_termino' 		: contrato.fecha_termino,
				'fecha_habilitacion' 	: contrato.fecha_habilitacion,
				'fecha_activacion' 		: contrato.fecha_activacion,
				'fecha_renovacion' 		: contrato.fecha_renovacion,
				'fecha_remodelacion' 	: contrato.fecha_remodelacion,
				'fecha_aviso' 			: contrato.fecha_aviso,
				'fecha_plazo' 			: contrato.fecha_plazo,
				'bodega' 				: contrato.bodega,
				'metros_bodega' 		: contrato.metros_bodega,
				'comentario' 			: contrato.comentario,
				'tipo' 					: {'id': contrato.contrato_tipo.id, 'nombre': contrato.contrato_tipo.nombre},
				'estado' 				: {'id': contrato.contrato_estado.id, 'nombre': contrato.contrato_estado.nombre},
				'cliente' 				: {'id': contrato.cliente.id, 'nombre': contrato.cliente.nombre},
				'locales' 				: data_locales,
				'conceptos' 			: data_conceptos,
				})

		return JsonResponse(data, safe=False)


# Funciones -----------------------------
def contrato_pdf(request, contrato_id):

	contrato 		= Contrato.objects.get(id=contrato_id)
	locales 		= contrato.locales.all()
	cliente 		= Cliente.objects.get(id=contrato.cliente_id)
	representantes 	= cliente.representante_set.all()
	empresa 		= Empresa.objects.get(id=cliente.empresa_id)
	metros 			= contrato.locales.all().aggregate(Sum('metros_cuadrados'))
	plazo 			= meses_entre_fechas(contrato.fecha_inicio, contrato.fecha_termino)
	meses 			= ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

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
		'plazo'				: plazo,
		'cliente'			: cliente,
		'representantes' 	: representantes,
	})

	html 		= template.render(context)
	pdfkit.from_string(html, 'public/media/contratos/contrato_'+str(contrato.id)+'.pdf', options=options, css=css)
	pdf 		= open('public/media/contratos/contrato_'+str(contrato.id)+'.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=contrato_'+str(contrato.id)+'.pdf'
	pdf.close()

	return response





