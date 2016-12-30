# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.core.urlresolvers import reverse_lazy

from django.views.generic import ListView, FormView, DeleteView, UpdateView, View

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

		concepto = self.get_object()

		if concepto.contrato_set.filter(visible=True).exists():
			status 	= False
			message = 'contratos con este concepto'
		else:
			status 	= True
			message = 'concepto eliminado correctamente'
			concepto.visible = False
			concepto.save()

		response = {
			'status'	: status,
			'message'	: message,
		}

		return JsonResponse(response, safe=False)

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


# get - concepto
class CONCEPTO(View):

	http_method_names = ['get']
	
	def get(self, request, id=None):

		if id == None:
			self.object_list = Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		else:
			self.object_list = Concepto.objects.filter(pk=id)

		if request.is_ajax() or self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def json_to_response(self):

		data = list()

		for item in self.object_list:

			tipo = {
				'id' 		: item.concepto_tipo.id,
				'nombre' 	: item.concepto_tipo.nombre,
				'codigo' 	: item.concepto_tipo.codigo,
			}

			data.append({
				'id' 			: item.id,
				'nombre'		: item.nombre,
				'codigo'		: item.codigo,
				'descripcion'	: item.descripcion,
				'tipo'			: tipo,
			})

		return JsonResponse(data, safe=False)

