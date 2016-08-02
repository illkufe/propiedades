from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from django.core.urlresolvers import reverse_lazy

from django.views.generic import ListView, FormView, DeleteView, UpdateView

from .forms import AlertaForm
from .models import Alerta, Alerta_Miembro

import json


class AlertaMixin(object):

	template_name = 'alerta_new.html'
	form_class = AlertaForm
	success_url = '/alertas/list'

	def form_invalid(self, form):
		response = super(AlertaMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.creador = self.request.user
		obj.save()

		for user in form.cleaned_data['miembros']:
			m1 = Alerta_Miembro(user=user, alerta=obj)
			m1.save()

		response = super(AlertaMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class AlertaNew(AlertaMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(AlertaNew, self).get_context_data(**kwargs)
		context['title'] = 'Notificaciones'
		context['subtitle'] = 'Alerta'
		context['name'] = 'Nuevo'
		context['href'] = 'alertas'
		context['accion'] = 'create'
		return context
	
class AlertasList(ListView):

	model = Alerta
	template_name = 'alertas_list.html'

	def get_context_data(self, **kwargs):

		context = super(AlertasList, self).get_context_data(**kwargs)
		context['title'] 	= 'Notificaciones'
		context['subtitle'] = 'Alertas'
		context['name'] 	= 'Lista'
		context['href'] 	= 'alertas'
		
		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		# queryset 	= Alerta.objects.filter(empresa=profile.empresa, visible=True)
		queryset 	= Alerta.objects.all()

		return queryset

class AlertaDelete(DeleteView):
	model = Alerta
	success_url = reverse_lazy('/alertas/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class AlertaUpdate(AlertaMixin, UpdateView):

	model = Alerta
	form_class = AlertaForm
	template_name = 'alerta_new.html'
	success_url = '/alertas/list'

	def get_context_data(self, **kwargs):
		
		context = super(AlertaUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Notificaciones'
		context['subtitle'] = 'Alerta'
		context['name'] = 'Editar'
		context['href'] = 'alertas'
		context['accion'] = 'update'
		return context