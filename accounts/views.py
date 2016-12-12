from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse_lazy
from django.core.mail import send_mail
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from utilidades.views import *
from notificaciones.models import Alerta, Alerta_Miembro

from .models import *
from .forms import *

from datetime import datetime

# variables
modulo = 'Configuración'

# usuario
class UsuarioList(ListView):

	model 			= User
	template_name 	= 'usuario_list.html'

	def get_context_data(self, **kwargs):

		context 					= super(UsuarioList, self).get_context_data(**kwargs)
		context['title'] 			= modulo
		context['subtitle'] 		= 'usuarios'
		context['name'] 			= 'lista'
		context['href'] 			= '/usuarios/list'
		context['form_password'] 	= UpdatePasswordAdminForm()

		return context

	def get_queryset(self):

		# {falta: mejorar estas querys}
		profiles = UserProfile.objects.values_list('user_id', flat=True).filter(empresa=self.request.user.userprofile.empresa).exclude(id=self.request.user.userprofile.id)
		queryset = User.objects.filter(id__in=profiles, is_active=True)

		return queryset

class UsuarioUpdateMixin(object):

	template_name 	= 'usuario_new.html'
	form_class 		= UserForm
	success_url 	= '/usuarios/list'

	def form_invalid(self, form):

		response = super(UsuarioUpdateMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

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
				item.empresa = self.request.user.userprofile.empresa
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

class UsuarioMixin(object):

	template_name 	= 'usuario_new.html'
	form_class 		= UserProfileFormFinal
	success_url 	= '/usuarios/list'

	def form_invalid(self, form):

		response = super(UsuarioMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		user = User(
			email 		= form.cleaned_data['email'],
			first_name 	= form.cleaned_data['first_name'],
			last_name 	= form.cleaned_data['last_name'],
			username 	= form.cleaned_data['username'],
			)

		user.set_password(get_password_random(8))
		user.save()

		obj 		= form.save(commit=False)
		obj.user 	= user
		obj.empresa = self.request.user.userprofile.empresa
		obj.save()

		response = super(UsuarioMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {
				# 'tipo':'create',
				# 'nombre': obj.first_name,
				# 'apellido': obj.last_name,
				# 'password': password,
				# 'email': obj.email,
			}
			return JsonResponse(data)
		else:
			return response

class UsuarioNew(UsuarioMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(UsuarioNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'usuarios'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/usuarios/list'
		context['accion']	= 'create'

		if self.request.POST:
			context['userprofileform'] = UserProfileFormSet(self.request.POST)
		else:
			context['userprofileform'] = UserProfileFormSet()

		return context
	
class UsuarioUpdate(UsuarioUpdateMixin, UpdateView):

	model 			= User
	form_class 		= UserForm
	template_name 	= 'usuario_new.html'
	success_url 	= '/usuarios/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(UsuarioUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'usuarios'
		context['name'] 	= 'editar'
		context['href'] 	= '/usuarios/list'
		context['accion'] 	= 'update'

		if self.request.POST:
			context['userprofileform'] = UserProfileFormSet(self.request.POST, instance=self.object)
		else:
			context['userprofileform'] = UserProfileFormSet(instance=self.object)

		return context


class UsuarioDelete(DeleteView):

	model 		= User
	success_url = reverse_lazy('/usuarios/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.is_active = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

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


def profile(request):
	# data_alert 	= list()
	# alertas 	= Alerta.objects.all()
	# date 		= datetime.now()

	# for alerta in alertas:

	# 	if date >= alerta.fecha:

	# 		alerta_miembros = alerta.alerta_miembro_set.all()

	# 		for alerta_miembro in alerta_miembros:
	# 			if alerta_miembro.user == request.user:
	# 				data_alert.append({
	# 					"mensaje"		: alerta.nombre,
	# 					"descripcion"	: alerta.descripcion,
	# 					"emisor"		: alerta.creador.first_name
	# 					})



	form_profile    = UpdateUserProfileForm(user=request.user)
	form_password   = UpdatePasswordForm(user=request.user)

	return render(request, 'perfil.html', {
		# 'alertas'		: data_alert,
		'form_profile'	: form_profile,
		'form_password'	: form_password,
		'title' 		: 'Perfil',
		'subtitle' 		: 'perfil',
		'name' 			: 'editar',
		'href' 			: '/perfil',
		})


def update_profile(request):
	
	form    = UpdateUserProfileForm(request.POST, user=request.user)
	user    = User.objects.get(pk=request.user.pk)
	profile = UserProfile.objects.get(user=user)

	if form.is_valid():

		user.first_name 	= form.cleaned_data['first_name']
		user.last_name 		= form.cleaned_data['last_name']
		profile.rut 		= form.cleaned_data['rut']
		profile.cargo 		= form.cleaned_data['cargo']
		profile.ciudad 		= form.cleaned_data['ciudad']
		profile.comuna 		= form.cleaned_data['comuna']
		profile.direccion 	= form.cleaned_data['direccion']
		profile.descripcion = form.cleaned_data['descripcion']

		user.save()
		profile.save()

		return JsonResponse({'estado':'ok'})
	else:
		return JsonResponse(form.errors, status=400)
	
def update_password(request, pk=None):
	if pk is None:

		form  = UpdatePasswordForm(request.POST, user=request.user)
		user  = User.objects.get(pk=request.user.pk)

		if form.is_valid():

			password = form.cleaned_data['password_nueva']
			user.set_password(password)
			user.save()
			user = authenticate(username=request.user.email, password=password)
			login(request, user)

			return JsonResponse({'estado':'ok'})
		else:
			return JsonResponse(form.errors, status=400)

	else:

		form = UpdatePasswordAdminForm(request.POST)
		user = User.objects.get(pk=pk)
		
		if form.is_valid():
			password = form.cleaned_data['password_nueva']
			user.set_password(password)
			user.save()
			return JsonResponse({'estado':'ok'})
		else:
			return JsonResponse(form.errors, status=400)




# def custom_404(request):
#   return render(request, '404.html')
# def custom_500(request):
#   return render(request, '500.html')
# def custom_403(request):
#   return render(request, '403.html')
# def custom_400(request):
#   return render(request, '400.html')
