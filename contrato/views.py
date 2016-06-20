# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import Context, loader
from django.template.loader import get_template 
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, CreateView, DeleteView, UpdateView

from .forms import ContratoTipoForm, ContratoForm, InformacionForm, ArriendoForm, ArriendoDetalleFormSet, ArriendoVariableForm, ArriendoVariableFormSet, GastoComunFormSet, ServicioBasicoFormSet
from .models import Contrato_Tipo, Contrato, Arriendo, Arriendo_Variable, Gasto_Comun, Servicio_Basico

from accounts.models import UserProfile
from administrador.models import Empresa, Cliente
from locales.models import Local
from procesos.models import Proceso, Proceso_Detalle

import pdfkit
import json
import os


class ContratoTipoMixin(object):

	template_name = 'viewer/contratos/contrato_tipo_new.html'
	form_class = ContratoTipoForm
	success_url = '/contratos-tipo/list'

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
				'pk': 'ok',
			}
			return JsonResponse(data)
		else:
			return response

class ContratoTipoNew(ContratoTipoMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(ContratoTipoNew, self).get_context_data(**kwargs)
		context['title'] = 'Contratos'
		context['subtitle'] = 'Tipo de Contrato'
		context['name'] = 'Nueva'
		context['href'] = 'contratos-tipo'
		context['accion'] = 'create'
		return context

class ContratoTipoList(ListView):

	model = Contrato_Tipo
	template_name = 'viewer/contratos/contrato_tipo_list.html'

	def get_context_data(self, **kwargs):
		context = super(ContratoTipoList, self).get_context_data(**kwargs)
		context['title'] = 'Contratos'
		context['subtitle'] = 'Tipo de Contrato'
		context['name'] = 'Lista'
		context['href'] = 'contratos-tipo'
		
		return context

	def get_queryset(self):

		profile 	= UserProfile.objects.get(user=self.request.user)
		queryset 	= Contrato_Tipo.objects.filter(empresa_id=profile.empresa_id, visible=True)

		return queryset

class ContratoTipoDelete(DeleteView):
	model = Contrato_Tipo
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class ContratoTipoUpdate(UpdateView):

	model = Contrato_Tipo
	form_class = ContratoTipoForm
	template_name = 'viewer/contratos/contrato_tipo_new.html'
	success_url = '/contratos-tipo/list'

	def get_context_data(self, **kwargs):
		
		context = super(ContratoTipoUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Contratos'
		context['subtitle'] = 'Tipo de Contrato'
		context['name'] = 'Editar'
		context['href'] = 'contratos-tipo'
		context['accion'] = 'update'
		return context



class ContratoMixin(object):

	template_name = 'viewer/contratos/contrato_new.html'
	form_class = ContratoForm
	success_url = '/contratos/list'

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
		# form.save_m2m()
		obj.save()
		form.save_m2m()

		# generar_contrato_pdf(obj)

		response = super(ContratoMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'ok',
			}
			return JsonResponse(data)
		else:
			return response

class ContratoNew(ContratoMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context = super(ContratoNew, self).get_context_data(**kwargs)
		context['title'] = 'Contratos'
		context['subtitle'] = 'Contrato'
		context['name'] = 'Nuevo'
		context['href'] = 'contratos'
		context['accion'] = 'create'
		return context

class ContratoList(ListView):
	model = Contrato
	template_name = 'viewer/contratos/contrato_list.html'

	def get_context_data(self, **kwargs):

		context = super(ContratoList, self).get_context_data(**kwargs)
		context['title'] = 'Contratos'
		context['subtitle'] = 'Contrato'
		context['name'] = 'Lista'
		context['href'] = 'contratos'

		return context

	def get_queryset(self):

		profile 	= UserProfile.objects.get(user=self.request.user)
		queryset 	= Contrato.objects.filter(empresa=profile.empresa, visible=True)

		return queryset

class ContratoDelete(DeleteView):
	model = Contrato
	success_url = reverse_lazy('/contratos/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class ContratoUpdate(ContratoMixin, UpdateView):

	model = Contrato
	form_class = ContratoForm
	template_name = 'viewer/contratos/contrato_new.html'
	success_url = '/contratos/list'

	def get_object(self, queryset=None):

		queryset = Contrato.objects.get(id=int(self.kwargs['pk']))

		if queryset.fecha_contrato:
			queryset.fecha_contrato = queryset.fecha_contrato.strftime('%d/%m/%Y')
		if queryset.fecha_inicio:
			queryset.fecha_inicio = queryset.fecha_inicio.strftime('%d/%m/%Y')
		if queryset.fecha_termino:
			queryset.fecha_termino = queryset.fecha_termino.strftime('%d/%m/%Y')
		if queryset.fecha_habilitacion:
			queryset.fecha_habilitacion = queryset.fecha_habilitacion.strftime('%d/%m/%Y')
		if queryset.fecha_activacion:
			queryset.fecha_activacion = queryset.fecha_activacion.strftime('%d/%m/%Y')
		if queryset.fecha_renovacion:
			queryset.fecha_renovacion = queryset.fecha_renovacion.strftime('%d/%m/%Y')
		if queryset.fecha_remodelacion:
			queryset.fecha_remodelacion = queryset.fecha_remodelacion.strftime('%d/%m/%Y')
		if queryset.fecha_aviso:
			queryset.fecha_aviso = queryset.fecha_aviso.strftime('%d/%m/%Y')
		if queryset.fecha_plazo:
			queryset.fecha_plazo = queryset.fecha_plazo.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):
		
		context = super(ContratoUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Contratos'
		context['subtitle'] = 'Contrato'
		context['name'] = 'Editar'
		context['href'] = 'contratos'
		context['accion'] = 'update'
		return context



class ArriendoPruebMixin(object):

	template_name = 'viewer/contratos/contrato_informacion.html'
	form_class = InformacionForm
	success_url = '/contratos/list'


	# def get_form_kwargs(self):
	# 	kwargs = super(ArriendoPruebMixin, self).get_form_kwargs()
	# 	kwargs['request'] = self.request
	# 	return kwargs



	def form_invalid(self, form):
		# print "invalido"

		response = super(ArriendoPruebMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		# user 	= User.objects.get(pk=self.request.user.pk)
		# profile = UserProfile.objects.get(user=user)

		context 			= self.get_context_data()
		formset_arriendo 	= context['formset_arriendo']
		formset_detalle 	= context['formset_detalle']

		form_arriendo_variable 	= context['form_arriendo_variable']

		formset_gasto_comun	= context['form_gasto_comun']

		formset_servicio_basico	= context['form_servicio_basico']

		
		if formset_gasto_comun.is_valid():
			formset_gasto_comun.save()

		if formset_servicio_basico.is_valid():
			formset_servicio_basico.save()

		if form_arriendo_variable.is_valid():
			form_arriendo_variable.save()

		# obj = form.save()

		if formset_arriendo.is_valid():
			formset_arriendo.save()

			if formset_detalle.is_valid():
				self.object = formset_arriendo.save(commit=False)
				formset_detalle.instance = self.object
				formset_detalle.save()

		response = super(ArriendoPruebMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class ArriendoPruebaNew(ArriendoPruebMixin, FormView):


	def get_context_data(self, **kwargs):

		context 				= super(ArriendoPruebaNew, self).get_context_data(**kwargs)
		context['title'] 		= 'Contratos'
		context['subtitle'] 	= 'Arriendo'
		context['name'] 		= 'Nuevo'
		context['href'] 		= 'contratos'
		context['accion'] 		= 'create'
		context['contrato_id']	= self.kwargs['contrato_id']

		if self.request.POST:

			contrato = Contrato.objects.get(id=self.kwargs['contrato_id'])

			try:
				arriendo_minimo 	= Arriendo.objects.get(contrato_id=self.kwargs['contrato_id'])
				context['formset_arriendo'] = ArriendoForm(self.request.POST, instance=arriendo_minimo)
				context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST,  instance=arriendo_minimo)
			except Exception:
				context['formset_arriendo'] = ArriendoForm(self.request.POST)
				context['formset_detalle'] 	= ArriendoDetalleFormSet(self.request.POST)

			try:
				arriendo_variable 	= Arriendo_Variable.objects.filter(contrato_id=self.kwargs['contrato_id'])
				context['form_arriendo_variable'] = ArriendoVariableFormSet(self.request.POST, instance=contrato)
				# print "try arriendo variable"
			except Exception:
				# print "exeception arriendo variable"
				context['form_arriendo_variable'] = ArriendoVariableFormSet(self.request.POST)


			try:
				gasto_comun = Gasto_Comun.objects.filter(contrato_id=self.kwargs['contrato_id'])
				context['form_gasto_comun'] = GastoComunFormSet(self.request.POST, instance=contrato)
				# print "try gasto comun"
			except Exception:
				# print "exeception gasto comun"
				context['form_gasto_comun'] = GastoComunFormSet(self.request.POST)

			try:
				servicio_basico = Servicio_Basico.objects.filter(contrato_id=self.kwargs['contrato_id'])
				context['form_servicio_basico'] = ServicioBasicoFormSet(self.request.POST, instance=contrato)
				# print "try gasto comun"
			except Exception:
				# print "exeception gasto comun"
				context['form_servicio_basico'] = ServicioBasicoFormSet(self.request.POST)

		else:

			contrato_id = self.kwargs['contrato_id']
			contrato 	= Contrato.objects.get(id=contrato_id)

			try:
				arriendo_minimo 	= Arriendo.objects.get(contrato_id=contrato_id)
				context['formset_arriendo'] = ArriendoForm(instance=arriendo_minimo)
				context['formset_detalle'] 	= ArriendoDetalleFormSet(instance=arriendo_minimo)
			except Exception:
				context['formset_arriendo'] = ArriendoForm()
				context['formset_detalle'] 	= ArriendoDetalleFormSet()



			try:
				arriendo_variable 	= Arriendo_Variable.objects.filter(contrato_id=contrato_id)
				context['form_arriendo_variable'] = ArriendoVariableFormSet(instance=contrato)
			except Exception:
				context['form_arriendo_variable'] = ArriendoVariableFormSet()

			try:
				gasto_comun = Gasto_Comun.objects.filter(contrato_id=contrato_id)
				context['form_gasto_comun'] = GastoComunFormSet(instance=contrato, form_kwargs={'contrato': contrato})
			except Exception:
				context['form_gasto_comun'] = GastoComunFormSet(form_kwargs={'contrato': contrato})

			try:
				servicio_basico = Servicio_Basico.objects.filter(contrato_id=contrato_id)
				context['form_servicio_basico'] = ServicioBasicoFormSet(instance=contrato, form_kwargs={'contrato': contrato})
			except Exception:
				context['form_servicio_basico'] = ServicioBasicoFormSet(form_kwargs={'contrato': contrato})

		return context






def generar_contrato_pdf(contrato, contrato_id=None):

	if contrato_id != None:
		contrato = Contrato.objects.get(id=contrato_id)

	cliente 		= Cliente.objects.get(id=contrato.cliente_id)
	empresa 		= Empresa.objects.get(id=cliente.empresa_id)
	representantes 	= cliente.representante_set.all()
	meses 			= ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

	options = {
		# 'page-size': 'Letter',
		# 'orientation': 'Landscape',
		'margin-top': '0.75in',
		'margin-right': '0.75in',
		'margin-bottom': '0.55in',
		'margin-left': '0.75in',
		'encoding': "UTF-8",
		'no-outline': None
		}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('contratos/contrato_'+str(empresa.id)+'_'+str(contrato.contrato_tipo_id)+'.html')

	context = Context({
		'meses'				: meses,
		'empresa'			: empresa,
		'contrato'			: contrato,
		'cliente'			: cliente,
		'representantes' 	: representantes,
	})

	html = template.render(context)  # Renders the template with the context data.
	pdfkit.from_string(html, 'public/media/contratos/'+str(contrato.id)+'.pdf', options=options, css=css)
	pdf = open('public/media/contratos/'+str(contrato.id)+'.pdf')
	response = HttpResponse(pdf.read(), content_type='application/pdf')  # Generates the response as pdf response.
	response['Content-Disposition'] = 'attachment; filename=output.pdf'
	pdf.close()
	# os.remove("out.pdf")  # remove the locally created pdf file.

	return response  # returns the response.






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

			data_local 	= list()
			locales 	= contrato.locales.all()

			for local in locales:

				data_local.append({
					'id'	: local.id,
					'nombre': local.nombre,
					'tipo'	: local.local_tipo.nombre,
					})

			data.append({
				'id'			: contrato.id,
				'numero'		: contrato.numero,
				'tipo'			: contrato.contrato_tipo.nombre,
				'nombre_local'	: contrato.nombre_local,
				'fecha_inicio'	: contrato.fecha_inicio,
				'fecha_termino'	: contrato.fecha_termino,
				'activo'		: 'cambiar',#local.activo.nombre, # {falta: cargar el activo del local, ojo que el contrato no puede tener locales de diferentes locales}
				'locales'		: data_local,
				'estado'		: contrato.contrato_estado.nombre,
				})

		return JsonResponse(data, safe=False)






