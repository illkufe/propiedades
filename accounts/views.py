from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse_lazy
from django.core.mail import send_mail
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView
from utilidades.views import *
from notificaciones.models import Alerta, Alerta_Miembro

from .models import *
from .forms import *

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
		context['href'] 			= '/usuarios/list/'
		context['form_password'] 	= UpdatePasswordAdminForm()

		return context

	def get_queryset(self):

		user 		= self.request.user
		profiles 	= UserProfile.objects.values_list('user_id', flat=True).filter(empresa=user.userprofile.empresa).exclude(id=user.userprofile.id)
		queryset 	= User.objects.filter(id__in=profiles, is_active=True)

		return queryset

class UsuarioMixin(object):

	template_name 	= 'usuario_new.html'
	form_class 		= UserProfileForm
	success_url 	= '/usuarios/list/'

	def form_invalid(self, form):

		response = super(UsuarioMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form, **kwargs):
		
		context 	= self.get_context_data(**kwargs)
		password 	= False

		if context['accion'] == 'create':

			user = User(
				email 		= form.cleaned_data['email'],
				first_name 	= form.cleaned_data['first_name'],
				last_name 	= form.cleaned_data['last_name'],
				username 	= form.cleaned_data['username'],
				)

			password = get_password_random(8)
			user.set_password(password)
			user.save()

			obj 		= form.save(commit=False)
			obj.user 	= user
			obj.empresa = self.request.user.userprofile.empresa
			obj.save()

		else:

			obj 			= form.save(commit=False)
			user 			= obj.user
			user.first_name = form.cleaned_data['first_name']
			user.last_name 	= form.cleaned_data['last_name']
			user.save()
			obj.save()

		response = super(UsuarioMixin, self).form_valid(form)
		
		if self.request.is_ajax():

			response = {
				'status'	: True,
				'message'	: 'creada o actualizada correctamente',
				'data'		: {
					'tipo'		: context['accion'],
					'nombre'	: user.first_name,
					'apellido'	: user.last_name,
					'email'		: user.email,
				}
			}

			return JsonResponse(response)
		else:
			return response

class UsuarioNew(UsuarioMixin, FormView):

	def get_context_data(self, **kwargs):

		context 			= super(UsuarioNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'usuario'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/usuarios/list/'
		context['accion']	= 'create'

		return context

class UsuarioUpdate(UsuarioMixin, UpdateView):

	model 			= UserProfile
	form_class 		= UserProfileForm
	template_name 	= 'usuario_new.html'
	success_url 	= '/usuarios/list'

	def get_context_data(self, **kwargs):

		context 			= super(UsuarioUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'usuario'
		context['name'] 	= 'editar'
		context['href'] 	= '/usuarios/list/'
		context['accion']	= 'update'

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

# perfil
class PerfilList(ListView):

	model 			= User
	template_name 	= 'perfil.html'

	def get_context_data(self, **kwargs):

		context 					= super(PerfilList, self).get_context_data(**kwargs)
		context['title'] 			= modulo
		context['subtitle'] 		= 'perfil'
		context['name'] 			= 'editar'
		context['href'] 			= '/perfil/'

		user  		= self.request.user
		owncloud 	= user.configuracionowncloud if hasattr(user, 'configuracionowncloud') else None

		context['user'] 			= user
		context['form_profile'] 	= UserProfileForm(instance=user.userprofile)
		context['form_owncloud']	= ConfiguracionOwnCloudForm(instance=owncloud)
		context['form_password']	= UpdatePasswordForm(user=user)

		return context

def user_login(request):

	if request.method == 'POST':

		action 		= request.POST.get('action', None)
		username 	= request.POST.get('username', None)
		password 	= request.POST.get('password', None)
		user 		= authenticate(username=username, password=password)

		if user:

			login(request, user)

			if ConfiguracionOwnCloud.objects.filter(user=user).exists():
				request.session['oc_url'] 		= user.configuracionowncloud.url
				request.session['oc_username'] 	= user.configuracionowncloud.usuario
				request.session['oc_password'] 	= user.configuracionowncloud.password
			else:
				request.session['oc_url'] 		= ''
				request.session['oc_username'] 	= ''
				request.session['oc_password'] 	= ''

			return HttpResponseRedirect('/')
		else:
			return HttpResponseRedirect('/')
	else:
		return render(request, 'login.html', {})

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required
def update_password(request, pk=None):

	if pk is None:

		form  = UpdatePasswordForm(request.POST, user=request.user)
		user  = User.objects.get(pk=request.user.pk)

		if form.is_valid():

			password 	= form.cleaned_data['password_nueva']
			user.set_password(password)
			user.save()
			user 		= authenticate(username=request.user.username, password=password)
			login(request, user)

		else:
			return JsonResponse(form.errors, status=400)

	else:

		form = UpdatePasswordAdminForm(request.POST)
		user = User.objects.get(pk=pk)
		
		if form.is_valid():
			password = form.cleaned_data['password_nueva']
			user.set_password(password)
			user.save()
			
		else:
			return JsonResponse(form.errors, status=400)

	response = {
		'status'	: True,
		'message'	: 'actualizada correctamente',
		}

	return JsonResponse(response)

@login_required
def update_owncloud(request, pk=None):

	try:

		user = request.user
		post = request.POST.copy()
		form = ConfiguracionOwnCloudForm(request.POST)

		if form.is_valid():

			if hasattr(user, 'configuracionowncloud'):

				user.configuracionowncloud.url 		= post['url']
				user.configuracionowncloud.usuario 	= post['usuario']
				user.configuracionowncloud.password = post['password']
				user.configuracionowncloud.save()

			else:

				owncloud = ConfiguracionOwnCloud(
					url 		= post['url'],
					usuario 	= post['usuario'],
					password 	= post['password'],
					user 		= user,
					)
				owncloud.save()

			response = {
				'status'	: True,
				'message'	: 'actualizado correctamente',
			}

			request.session['oc_url'] 		= user.configuracionowncloud.url
			request.session['oc_username'] 	= user.configuracionowncloud.usuario
			request.session['oc_password'] 	= user.configuracionowncloud.password

		else:
			return JsonResponse(form.errors, status=400)

	except Exception as error:

		response = {
			'status'	: False,
			'message'	: error,
		}

	return JsonResponse(response)


# def custom_404(request):
#   return render(request, '404.html')
# def custom_500(request):
#   return render(request, '500.html')
# def custom_403(request):
#   return render(request, '403.html')
# def custom_400(request):
#   return render(request, '400.html')
