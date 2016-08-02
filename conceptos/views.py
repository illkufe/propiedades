from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from accounts.models import UserProfile
from django.core.urlresolvers import reverse_lazy

from django.views.generic import ListView, FormView, DeleteView, UpdateView

from .forms import ConceptoForm
from .models import Concepto

import json

class AjaxableResponseMixin(object):

	template_name = 'viewer/conceptos/concepto_new.html'
	form_class = ConceptoForm
	success_url = '/conceptos/list'

	def form_invalid(self, form):
		response = super(AjaxableResponseMixin, self).form_invalid(form)
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

		response = super(AjaxableResponseMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class ConceptoNew(AjaxableResponseMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(ConceptoNew, self).get_context_data(**kwargs)
		context['title'] = 'Conceptos'
		context['subtitle'] = 'Concepto'
		context['name'] = 'Nuevo'
		context['href'] = 'conceptos'
		context['accion'] = 'create'
		return context
	
class ConceptoList(ListView):

	model = Concepto
	template_name = 'viewer/conceptos/concepto_list.html'

	def get_context_data(self, **kwargs):

		context = super(ConceptoList, self).get_context_data(**kwargs)
		context['title'] 	= 'Conceptos'
		context['subtitle'] = 'Concepto'
		context['name'] 	= 'Lista'
		context['href'] 	= 'conceptos'
		
		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		queryset 	= Concepto.objects.filter(empresa=profile.empresa, visible=True)

		return queryset

class ConceptoDelete(DeleteView):
	model = Concepto
	success_url = reverse_lazy('/conceptos/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class ConceptoUpdate(UpdateView):

	model = Concepto
	form_class = ConceptoForm
	template_name = 'viewer/conceptos/concepto_new.html'
	success_url = '/conceptos/list'

	def get_context_data(self, **kwargs):
		
		context = super(ConceptoUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Conceptos'
		context['subtitle'] = 'Concepto'
		context['name'] = 'Editar'
		context['href'] = 'conceptos'
		context['accion'] = 'update'
		return context
