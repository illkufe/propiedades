# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from .models import UserProfile
from .forms import UserForm, UserProfileForm, UserProfileFormSet

import string
import random


class UsuarioUpdateMixin(object):

	template_name = 'viewer/configuracion/usuario_new.html'
	form_class = UserForm
	success_url = '/usuarios/list'

	def form_invalid(self, form):
		response = super(UsuarioUpdateMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		context 		= self.get_context_data()
		form_profile 	= context['userprofileform']

		obj 			= form.save(commit=False)
		obj.username 	= obj.email
		obj.save()

		if form_profile.is_valid():

			self.object 			= form.save(commit=False)
			form_profile.instance 	= self.object
			detalle_nuevo 			= form_profile.save(commit=False)

			for item in detalle_nuevo:
				item.empresa_id = profile.empresa_id
				item.save()

		response = super(UsuarioUpdateMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {
				'tipo':'update',
				'nombre': obj.first_name,
				'apellido': obj.last_name,
				'password': 'asd',
				'email': obj.email,
			}
			return JsonResponse(data)
		else:
			return response

class UsuarioNewMixin(object):

	template_name = 'viewer/configuracion/usuario_new.html'
	form_class = UserForm
	success_url = '/usuarios/list'

	def form_invalid(self, form):
		response = super(UsuarioNewMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		context 		= self.get_context_data()
		form_profile 	= context['userprofileform']
		password 		= password_random(8)

		obj 			= form.save(commit=False)
		obj.username 	= obj.email
		obj.set_password(password)
		obj.save()

		if form_profile.is_valid():

			self.object 			= form.save(commit=False)
			form_profile.instance 	= self.object
			detalle_nuevo 			= form_profile.save(commit=False)

			for item in detalle_nuevo:
				item.empresa_id = profile.empresa_id
				item.save()

		response = super(UsuarioNewMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {
				'tipo':'create',
				'nombre': obj.first_name,
				'apellido': obj.last_name,
				'password': password,
				'email': obj.email,
			}
			return JsonResponse(data)
		else:
			return response

class UsuarioNew(UsuarioNewMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(UsuarioNew, self).get_context_data(**kwargs)
		context['title'] = 'Configuración'
		context['subtitle'] = 'Usuario'
		context['name'] = 'Nuevo'
		context['href'] = 'usuarios'
		context['accion'] = 'create'

		if self.request.POST:
			context['userprofileform'] = UserProfileFormSet(self.request.POST)
		else:
			context['userprofileform'] = UserProfileFormSet()

		return context
	
class UsuarioList(ListView):

	model = User
	template_name = 'viewer/configuracion/usuario_list.html'

	def get_context_data(self, **kwargs):

		context = super(UsuarioList, self).get_context_data(**kwargs)
		context['title'] = 'Configuración'
		context['subtitle'] = 'Usuario'
		context['name'] = 'Lista'
		context['href'] = 'usuarios'

		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profiles 	= UserProfile.objects.values_list('user_id', flat=True).filter(empresa=user.userprofile.empresa)
		queryset 	= User.objects.filter(id__in=profiles, is_active=True)

		return queryset

class UsuarioDelete(DeleteView):
	model = User
	success_url = reverse_lazy('/usuarios/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.is_active = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class UsuarioUpdate(UsuarioUpdateMixin, UpdateView):

	model = User
	form_class = UserForm
	template_name = 'viewer/configuracion/usuario_new.html'
	success_url = '/usuarios/list'

	def get_context_data(self, **kwargs):
		
		context = super(UsuarioUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Configuración'
		context['subtitle'] = 'Usuario'
		context['name'] = 'Editar'
		context['href'] = 'usuarios'
		context['accion'] = 'update'

		if self.request.POST:
			context['userprofileform'] = UserProfileFormSet(self.request.POST, instance=self.object)
		else:
			context['userprofileform'] = UserProfileFormSet(instance=self.object)

		return context

def user_login(request):
	if request.method == 'POST':
		action = request.POST.get('action', None)
		username = request.POST.get('username', None)
		password = request.POST.get('password', None)
		user = authenticate(username=username, password=password)

		if user:
			login(request, user)
			return HttpResponseRedirect('/')
		else:
			return HttpResponseRedirect('/')
	else:
		return render(request, 'login.html', {})


@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')


def password_random(size):

	chars 		= string.letters + string.digits
	password 	= ''.join((random.choice(chars)) for x in range(size))

	return password

# def custom_404(request):
# 	return render(request, '404.html')
# def custom_500(request):
# 	return render(request, '500.html')
# def custom_403(request):
# 	return render(request, '403.html')
# def custom_400(request):
# 	return render(request, '400.html')
