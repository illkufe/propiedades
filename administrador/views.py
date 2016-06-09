# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse_lazy
from django.forms import formset_factory, inlineformset_factory
from django.forms.models import modelformset_factory
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from accounts.models import UserProfile

from .models import Moneda, Empresa, Cliente, Representante, Unidad_Negocio
from .forms import MonedaForm, ClienteForm, ClienteFormSet, UnidadNegocioForm

import json

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
		response = super(ClienteMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

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




class UnidadNegocioMixin(object):

	template_name = 'viewer/configuracion/unidad_negocio_new.html'
	form_class = UnidadNegocioForm
	success_url = '/unidades-negocio/list'

	def form_invalid(self, form):
		response = super(UnidadNegocioMixin, self).form_invalid(form)
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

		response = super(UnidadNegocioMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class UnidadNegocioNew(UnidadNegocioMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context = super(UnidadNegocioNew, self).get_context_data(**kwargs)
		context['title'] = 'Unidades de Negocio'
		context['subtitle'] = 'Unidad de Negocio'
		context['name'] = 'Nueva'
		context['href'] = 'unidades-negocio'
		context['accion'] = 'create'

		return context

class UnidadNegocioList(ListView):
	model = Unidad_Negocio
	template_name = 'viewer/configuracion/unidad_negocio_list.html'

	def get_context_data(self, **kwargs):
		context = super(UnidadNegocioList, self).get_context_data(**kwargs)
		context['title'] = 'Unidades de Negocio'
		context['subtitle'] = 'Unidad de Negocio'
		context['name'] = 'Lista'
		context['href'] = 'unidades-negocio'

		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		queryset 	= Unidad_Negocio.objects.filter(empresa=profile.empresa, visible=True)

		return queryset

class UnidadNegocioDelete(DeleteView):
	model = Unidad_Negocio
	success_url = reverse_lazy('/unidades-negocio/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class UnidadNegocioUpdate(UpdateView):

	model = Unidad_Negocio
	form_class = UnidadNegocioForm
	template_name = 'viewer/configuracion/unidad_negocio_new.html'
	success_url = '/unidades-negocio/list'

	def get_context_data(self, **kwargs):
		
		context = super(UnidadNegocioUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Unidades de Negocio'
		context['subtitle'] = 'Unidad de Negocio'
		context['name'] = 'Editar'
		context['href'] = 'unidades-negocio'
		context['accion'] = 'update'
		return context





# Create your views here.
# class UsuarioMixin(object):

# 	template_name = 'viewer/configuracion/usuario_new.html'
# 	form_class = UserForm
# 	success_url = '/usuarios/list'

# 	def form_invalid(self, form):
# 		response = super(UsuarioMixin, self).form_invalid(form)
# 		if self.request.is_ajax():
# 			return JsonResponse(form.errors, status=400)
# 		else:
# 			return response

# 	def form_valid(self, form):
# 		user 	= User.objects.get(pk=self.request.user.pk)
# 		profile = UserProfile.objects.get(user=user)

# 		context 			= self.get_context_data()
# 		form_userprofile 	= context['userprofileform']

# 		obj = form.save(commit=False)
# 		obj.username = obj.email
# 		obj.set_password('1234qwer')
# 		obj.save()

# 		if form_userprofile.is_valid():

# 			self.object = form.save(commit=False)
# 			form_userprofile.instance = self.object
# 			detalle_nuevo = form_userprofile.save(commit=False)

# 			for di in detalle_nuevo:
# 				di.empresa_id = profile.empresa_id
# 				di.save()



# 			# obj2 = form_userprofile.save(commit=False)
# 			# obj2.empresa_id = profile.empresa_id

# 			# self.object = form.save(commit=False)
# 			# form_userprofile.instance = self.object
# 			# obj = form_userprofile
			
# 			# form_userprofile
# 			# form_userprofile.save()


# 		response = super(UsuarioMixin, self).form_valid(form)
# 		if self.request.is_ajax():
# 			data = {
# 				'pk': 'self.object.pk',
# 			}
# 			return JsonResponse(data)
# 		else:
# 			return response

# class UsuarioNew(UsuarioMixin, FormView):
# 	def get_context_data(self, **kwargs):
		
# 		context = super(UsuarioNew, self).get_context_data(**kwargs)
# 		context['title'] = 'Configuración'
# 		context['subtitle'] = 'Usuario'
# 		context['name'] = 'Nuevo'
# 		context['href'] = 'usuarios'
# 		context['accion'] = 'create'

# 		if self.request.POST:
# 			context['userprofileform'] = UserProfileFormSet(self.request.POST)
# 		else:
# 			context['userprofileform'] = UserProfileFormSet()


# 		return context
	
# class UsuarioList(ListView):

# 	model = User
# 	template_name = 'viewer/configuracion/usuario_list.html'

# 	def get_context_data(self, **kwargs):

# 		context = super(UsuarioList, self).get_context_data(**kwargs)
# 		context['title'] = 'Configuración'
# 		context['subtitle'] = 'Usuario'
# 		context['name'] = 'Lista'
# 		context['href'] = 'usuarios'

# 		return context

# 	def get_queryset(self):

# 		user 		= User.objects.get(pk=self.request.user.pk)
# 		profiles 	= UserProfile.objects.values_list('user_id', flat=True).filter(empresa=user.userprofile.empresa)
# 		queryset 	= User.objects.filter(id__in=profiles, is_active=True)

# 		return queryset

# class UsuarioDelete(DeleteView):
# 	model = User
# 	success_url = reverse_lazy('/usuarios/list')

# 	def delete(self, request, *args, **kwargs):
# 		self.object = self.get_object()
# 		self.object.is_active = False
# 		self.object.save()
# 		payload = {'delete': 'ok'}
# 		return JsonResponse(payload, safe=False)

# class UsuarioUpdate(UpdateView):

# 	model = User
# 	form_class = UserForm
# 	template_name = 'viewer/configuracion/usuario_new.html'
# 	success_url = '/usuarios/list'

# 	def get_context_data(self, **kwargs):
		
# 		context = super(UsuarioUpdate, self).get_context_data(**kwargs)
# 		context['title'] = 'Configuración'
# 		context['subtitle'] = 'Usuario'
# 		context['name'] = 'Editar'
# 		context['href'] = 'usuarios'
# 		context['accion'] = 'update'

# 		if self.request.POST:
# 			context['userprofileform'] = UserProfileFormSet(self.request.POST, instance=self.object)
# 		else:
# 			context['userprofileform'] = UserProfileFormSet(instance=self.object)

# 		return context




# def custom_404(request):
# 	return render(request, '404.html')
# def custom_500(request):
# 	return render(request, '500.html')
# def custom_403(request):
# 	return render(request, '403.html')
# def custom_400(request):
# 	return render(request, '400.html')