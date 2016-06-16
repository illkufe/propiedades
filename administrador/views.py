# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from accounts.models import UserProfile

from .models import Moneda, Empresa, Cliente, Representante
from .forms import MonedaForm, ClienteForm, ClienteFormSet

class MonedaMixin(object):

	template_name = 'viewer/configuracion/moneda_new.html'
	form_class = MonedaForm
	success_url = '/monedas/list'

	def form_invalid(self, form):
		response = super(MonedaMixin, self).form_invalid(form)
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

		response = super(MonedaMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class MonedaNew(MonedaMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(MonedaNew, self).get_context_data(**kwargs)
		context['title'] = 'Configuración'
		context['subtitle'] = 'Moneda'
		context['name'] = 'Nueva'
		context['href'] = 'monedas'
		context['accion'] = 'create'
		return context

class MonedaList(ListView):
	model = Moneda
	template_name = 'viewer/configuracion/moneda_list.html'

	def get_context_data(self, **kwargs):
		context = super(MonedaList, self).get_context_data(**kwargs)
		context['title'] = 'Configuración'
		context['subtitle'] = 'Moneda'
		context['name'] = 'Lista'
		context['href'] = 'monedas'
		
		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		queryset 	= Moneda.objects.filter(empresa_id=profile.empresa_id)

		return queryset

class MonedaDelete(DeleteView):
	model = Moneda
	success_url = reverse_lazy('/monedas/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.delete()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class MonedaUpdate(UpdateView):

	model = Moneda
	form_class = MonedaForm
	template_name = 'viewer/configuracion/moneda_new.html'
	success_url = '/monedas/list'

	def get_context_data(self, **kwargs):
		
		context = super(MonedaUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Configuración'
		context['subtitle'] = 'Moneda'
		context['name'] = 'Editar'
		context['href'] = 'monedas'
		context['accion'] = 'update'
		return context



class ClienteMixin(object):

	template_name 	= 'viewer/configuracion/cliente_new.html'
	form_class 		= ClienteForm
	success_url 	= '/clientes/list'

	def form_invalid(self, form):
		print ("invalido")
		response = super(ClienteMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		print ("valido")

		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		context 			= self.get_context_data()
		form_representante 	= context['representante_form']

		objeto 				= form.save(commit=False)
		objeto.empresa_id 	= profile.empresa_id
		objeto.save()

		if form_representante.is_valid():
			self.object = form.save(commit=False)
			form_representante.instance = self.object
			form_representante.save()

		response = super(ClienteMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class ClienteNew(ClienteMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(ClienteNew, self).get_context_data(**kwargs)
		context['title'] = 'Contrato'
		context['subtitle'] = 'Cliente'
		context['name'] = 'Nuevo'
		context['href'] = 'clientes'
		context['accion'] = 'create'

		if self.request.POST:
			context['representante_form'] = ClienteFormSet(self.request.POST)
		else:
			context['representante_form'] = ClienteFormSet()

		return context
	
class ClienteList(ListView):
	model = Cliente
	template_name = 'viewer/configuracion/cliente_list.html'

	def get_context_data(self, **kwargs):
		context = super(ClienteList, self).get_context_data(**kwargs)
		context['title'] 	= 'Configuración'
		context['subtitle'] = 'Cliente'
		context['name'] 	= 'Lista'
		context['href'] 	= 'clientes'
		
		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		queryset 	= Cliente.objects.filter(empresa=profile.empresa, visible=True)

		return queryset

class ClienteDelete(DeleteView):
	model = Cliente
	success_url = reverse_lazy('/clientes/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class ClienteUpdate(ClienteMixin, UpdateView):

	model 			= Cliente
	form_class 		= ClienteForm
	template_name 	= 'viewer/configuracion/cliente_new.html'
	success_url 	= '/clientes/list'

	def get_context_data(self, **kwargs):
		
		context = super(ClienteUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Configuración'
		context['subtitle'] = 'Cliente'
		context['name'] 	= 'Editar'
		context['href'] 	= 'clientes'
		context['accion'] 	= 'update'

		if self.request.POST:
			context['representante_form'] = ClienteFormSet(self.request.POST, instance=self.object)
		else:
			context['representante_form'] = ClienteFormSet(instance=self.object)

		return context

