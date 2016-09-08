# -*- coding: utf-8 -*-a
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, FormView, CreateView, DeleteView, UpdateView


from activos.models import Activo
from locales.models import Local

from .forms import *
from .models import *


# variables
modulo 	= 'Operaciones'


# lecturas
class LecturaMedidorList(ListView):

	model 			= Lectura_Electricidad
	template_name 	= 'lectura_medidor_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(LecturaMedidorList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'Lectura Medidores'
		context['name'] 	= 'Lista'
		context['href'] 	= 'lectura-medidores'

		return context

	def get_queryset(self):

		queryset 		= []
		meses 			= ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

		activos 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)
		locales 		= Local.objects.filter(activo_id__in=activos, visible=True).values_list('id', flat=True)
		medidores_luz	= Medidor_Electricidad.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)
		medidores_agua 	= Medidor_Agua.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)
		medidores_gas 	= Medidor_Gas.objects.filter(local__in=locales, visible=True).values_list('id', flat=True)
	
		lectura_electricidad 	= Lectura_Electricidad.objects.filter(medidor_electricidad__in=medidores_luz, visible=True)
		lectura_agua 			= Lectura_Agua.objects.filter(medidor_agua__in=medidores_agua, visible=True)
		lectura_gas 			= Lectura_Gas.objects.filter(medidor_gas__in=medidores_gas, visible=True)

		for item in lectura_electricidad:
			item.local 	= item.medidor_electricidad.local
			item.activo = item.medidor_electricidad.local.activo
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= 'Electricidad'
			item.url 	= 'electricidad'
			queryset.append(item)

		for item in lectura_agua:
			item.local 	= item.medidor_agua.local
			item.activo = item.medidor_agua.local.activo
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= 'Agua'
			item.url 	= 'agua'
			queryset.append(item)

		for item in lectura_gas:
			item.local 	= item.medidor_gas.local
			item.activo = item.medidor_gas.local.activo
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= 'Gas'
			item.url 	= 'gas'
			queryset.append(item)

		return queryset


# lecturas electricidad
class LecturaElectricidadMixin(object):

	template_name 	= 'lectura_electricidad_new.html'
	form_class 		= LecturaElectricidadForm
	success_url 	= '/lectura-medidores/list'

	def form_invalid(self, form):

		response = super(LecturaElectricidadMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			lectura 		= Lectura_Electricidad.objects.get(medidor_electricidad_id= obj.medidor_electricidad.id, mes=obj.mes, anio=obj.anio)
			lectura.valor 	= obj.valor
			lectura.user 	= obj.user
			lectura.visible = True
			lectura.save()
		except Exception:
			obj.save()

		response = super(LecturaElectricidadMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class LecturaElectricidadNew(LecturaElectricidadMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaElectricidadNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de electricidad'
		context['name'] 	= 'nueva'
		context['href'] 	= '/lectura-medidores/list'
		context['accion']	 = 'create'

		return context

class LecturaElectricidadDelete(DeleteView):

	model 		= Lectura_Electricidad
	success_url = reverse_lazy('/lectura-medidores/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class LecturaElectricidadUpdate(LecturaElectricidadMixin, UpdateView):

	model 			= Lectura_Electricidad
	form_class 		= LecturaElectricidadForm
	template_name 	= 'lectura_electricidad_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaElectricidadUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor electricidad'
		context['name'] 	= 'editar'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'update'

		return context


# lecturas agua
class LecturaAguaMixin(object):

	template_name 	= 'lectura_agua_new.html'
	form_class 		= LecturaAguaForm
	success_url 	= '/lectura-medidores/list'

	def form_invalid(self, form):

		response = super(LecturaAguaMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			lectura 		= Lectura_Agua.objects.get(medidor_agua_id= obj.medidor_agua.id, mes=obj.mes, anio=obj.anio)
			lectura.valor 	= obj.valor
			lectura.user 	= obj.user
			lectura.visible = True
			lectura.save()
		except Exception:
			obj.save()

		response = super(LecturaAguaMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class LecturaAguaNew(LecturaAguaMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaAguaNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de Agua'
		context['name'] 	= 'nueva'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'create'

		return context

class LecturaAguaDelete(DeleteView):

	model 		= Lectura_Agua
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class LecturaAguaUpdate(LecturaAguaMixin, UpdateView):

	model 			= Lectura_Agua
	form_class 		= LecturaAguaForm
	template_name 	= 'lectura_agua_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaAguaUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de agua'
		context['name'] 	= 'editar'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'update'

		return context


# lecturas gas
class LecturaGasMixin(object):

	template_name 	= 'lectura_gas_new.html'
	form_class 		= LecturaGasForm
	success_url 	= '/lectura-medidores/list'

	def form_invalid(self, form):

		response = super(LecturaGasMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			lectura 		= Lectura_Gas.objects.get(medidor_gas_id= obj.medidor_gas.id, mes=obj.mes, anio=obj.anio)
			lectura.valor 	= obj.valor
			lectura.user 	= obj.user
			lectura.visible = True
			lectura.save()
		except Exception:
			obj.save()

		response = super(LecturaGasMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class LecturaGasNew(LecturaGasMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaGasNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de gas'
		context['name'] 	= 'nueva'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'create'
		return context

class LecturaGasDelete(DeleteView):

	model 		= Lectura_Gas
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data = {'estado': True}

		return JsonResponse(data, safe=False)

class LecturaGasUpdate(LecturaGasMixin, UpdateView):

	model 			= Lectura_Agua
	form_class 		= LecturaAguaForm
	template_name 	= 'lectura_agua_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context 			= super(LecturaGasUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'lectura medidor de gas'
		context['name'] 	= 'editar'
		context['href'] 	= '/lectura-medidores/list'
		context['accion'] 	= 'update'
		return context

