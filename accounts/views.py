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
		context['href'] 			= '/usuarios/list'
		context['form_password'] 	= UpdatePasswordAdminForm()

		return context

	def get_queryset(self):

		# {falta: mejorar estas querys}
		profiles = UserProfile.objects.values_list('user_id', flat=True).filter(empresa=self.request.user.userprofile.empresa).exclude(id=self.request.user.userprofile.id)
		queryset = User.objects.filter(id__in=profiles, is_active=True)

		return queryset

class UsuarioMixin(object):

	template_name 	= 'usuario_new.html'
	form_class 		= UserProfileForm
	success_url 	= '/usuarios/list'

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

		response 	= super(UsuarioMixin, self).form_valid(form)
		data 		= {
			'tipo'		: context['accion'],
			'nombre'	: user.first_name,
			'apellido'	: user.last_name,
			'email'		: user.email,
		}

		if self.request.is_ajax():
			return JsonResponse(data)
		else:
			return response

class UsuarioNew(UsuarioMixin, FormView):

	def get_context_data(self, **kwargs):

		context 			= super(UsuarioNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'usuario'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/usuarios/list'
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
		context['href'] 	= '/usuarios/list'
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






def user_login(request):

	if request.method == 'POST':

		action 		= request.POST.get('action', None)
		username 	= request.POST.get('username', None)
		password 	= request.POST.get('password', None)
		user 		= authenticate(username=username, password=password)

		if user:

			login(request, user)

			if ConfigOwnCloud.objects.filter(user=user).exists():
				request.session['oc_url'] 		= user.configowncloud.url
				request.session['oc_username'] 	= user.configowncloud.usuario
				request.session['oc_password'] 	= user.configowncloud.password
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

def profile(request):
	
	form_owncloud    = ConfigOwnCloudForm()

	form 			= UserProfileForm(instance=request.user.userprofile)
	form_password   = UpdatePasswordForm(user=request.user)

	return render(request, 'perfil.html', {
		'user'			: request.user,
		'form'			: form,
		'form_owncloud'	: form_owncloud,
		'form_password'	: form_password,
		'title' 		: 'Perfil',
		'subtitle' 		: 'perfil',
		'name' 			: 'editar',
		'href' 			: '/perfil',
		})

def update_profile(request):
	
	form    = UserProfileForm(request.POST, user=request.user)
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
