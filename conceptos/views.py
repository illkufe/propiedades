# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.core.urlresolvers import reverse_lazy

from django.views.generic import ListView, FormView, DeleteView, UpdateView

from .forms import ConceptoForm
from .models import Concepto

class ConceptoList(ListView):

	model 			= Concepto
	template_name 	= 'concepto_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ConceptoList, self).get_context_data(**kwargs)
		context['title'] 	= 'Configuración'
		context['subtitle'] = 'conceptos'
		context['name'] 	= 'lista'
		context['href'] 	= '/conceptos/list'
		
		return context

	def get_queryset(self):

		queryset = Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		return queryset

class ConceptoMixin(object):

	template_name 	= 'concepto_new.html'
	form_class 		= ConceptoForm
	success_url 	= '/conceptos/list'

	def get_form_kwargs(self):
		kwargs = super(ConceptoMixin, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_invalid(self, form):
		response = super(ConceptoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.empresa = self.request.user.userprofile.empresa
		obj.save()

		response = super(ConceptoMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'save': 'ok',
			}
			return JsonResponse(data)
		else:
			return response

class ConceptoNew(ConceptoMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(ConceptoNew, self).get_context_data(**kwargs)
		context['title'] 	= 'Configuración'
		context['subtitle'] = 'concepto'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/conceptos/list'
		context['accion'] 	= 'create'

		return context

class ConceptoDelete(DeleteView):

	model 		= Concepto
	success_url = reverse_lazy('/conceptos/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class ConceptoUpdate(ConceptoMixin, UpdateView):

	model 			= Concepto
	form_class 		= ConceptoForm
	template_name 	= 'concepto_new.html'
	success_url 	= '/conceptos/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(ConceptoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Configuración'
		context['subtitle'] = 'concepto'
		context['name'] 	= 'editar'
		context['href'] 	= '/conceptos/list'
		context['accion'] 	= 'update'

		return context
