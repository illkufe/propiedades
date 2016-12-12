# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, UpdateView, DeleteView
from locales.models import *
from utilidades.views import formato_moneda_local
from utilidades.plugins.owncloud import *
from .forms import *
from .models import *

# variables
modulo 	= 'Activos'

# activo
class ActivoMixin(object):

	template_name 	= 'activo_new.html'
	form_class 		= ActivoForm
	success_url 	= '/activos/list'

	def form_invalid(self, form):

		response = super(ActivoMixin, self).form_invalid(form)

		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context 		= self.get_context_data()
		form_sector 	= context['sectorform']
		form_nivel 		= context['nivelform']

		obj 			= form.save(commit=False)
		obj.empresa 	= self.request.user.userprofile.empresa
		obj.save()

		# validar sectores {falta: devolver y pintar los errores}
		if form_sector.is_valid():
			self.object = form.save(commit=False)
			form_sector.instance = self.object
			form_sector.save()

		# validar niveles {falta: devolver y pintar los errores}
		if form_nivel.is_valid():
			self.object = form.save(commit=False)
			form_nivel.instance = self.object
			form_nivel.save()

		response = super(ActivoMixin, self).form_valid(form)

		# path   = 'Iproperty/Activos/'
		# estado = create_directory(path, obj.nombre)

		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class ActivoNew(ActivoMixin, FormView):

	def get_context_data(self, **kwargs):

		context 			= super(ActivoNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'activos'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/activos/list'
		context['accion'] 	= 'create'

		if self.request.POST:
			context['sectorform'] = SectorFormSet(self.request.POST)
			context['nivelform'] = NivelFormSet(self.request.POST)
		else:
			context['sectorform'] = SectorFormSet()
			context['nivelform'] = NivelFormSet()

		return context

class ActivoList(ListView):

	model 			= Activo
	template_name 	= 'activo_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(ActivoList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'activos'
		context['name']	 	= 'lista'
		context['href'] 	= '/activos/list'
		
		return context

	def get_queryset(self):

		queryset 	= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		for item in queryset:

			item.tasacion_fiscal = formato_moneda_local(self.request, item.tasacion_fiscal, None)

		return queryset

class ActivoDelete(DeleteView):

	model 		= Activo
	success_url = reverse_lazy('/activos/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()

		# path   					= 'Iproperty/Activos/'
		# path_directory_backups 	= 'Iproperty/Activos/Respaldos/'
		# estado = backups_directory(path, self.object.nombre, path_directory_backups)

		data 				= {'estado': True}

		return JsonResponse(data, safe=False)

class ActivoUpdate(ActivoMixin, UpdateView):

	model 			= Activo
	form_class		= ActivoForm
	template_name 	= 'activo_new.html'
	success_url 	= '/activos/list'

	def get_object(self, queryset=None):

		queryset = Activo.objects.get(id=int(self.kwargs['pk']))

		# if queryset.fecha_firma_nomina:
		# 	queryset.fecha_firma_nomina = queryset.fecha_firma_nomina.strftime('%d/%m/%Y')
		if queryset.fecha_escritura:
			queryset.fecha_escritura = queryset.fecha_escritura.strftime('%d/%m/%Y')
		if queryset.fecha_adquisicion:
			queryset.fecha_adquisicion = queryset.fecha_adquisicion.strftime('%d/%m/%Y')
		if queryset.fecha_tasacion:
			queryset.fecha_tasacion = queryset.fecha_tasacion.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):

		context 			= super(ActivoUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'activo'
		context['name'] 	= 'editar'
		context['href'] 	= '/activos/list'
		context['accion'] 	= 'update'

		if self.request.POST:
			context['sectorform'] 	= SectorFormSet(self.request.POST, instance=self.object)
			context['nivelform'] 	= NivelFormSet(self.request.POST, instance=self.object)
		else:
			context['sectorform'] 	= SectorFormSet(instance=self.object)
			context['nivelform'] 	= NivelFormSet(instance=self.object)

		return context

class ActivoDocuments(ListView):

	model 			= Activo
	template_name 	= 'activo_documents.html'

	def get_context_data(self, **kwargs):

		context 			= super(ActivoDocuments, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'activo'
		context['name'] 	= 'documentos'
		context['href'] 	= '/activos/list'
		context['id'] 		= int(self.kwargs['pk'])

		activo 	= Activo.objects.get(id=self.kwargs['pk'])
		data 	= oc_list_directory(str(activo.nombre), 'Iproperty/Activos/'+str(activo.nombre))

		if data['status'] is False:
			oc_create_directory('Iproperty/Activos',str(activo.nombre))


		return context



# gasto mensual (gasto común)
class GastoMensualMixin(object):

	template_name 	= 'gasto_mensual_new.html'
	form_class 		= GastoMensualForm
	success_url 	= '/gastos-mensual/list'

	def get_form_kwargs(self):

		kwargs 				= super(GastoMensualMixin, self).get_form_kwargs()
		kwargs['request'] 	= self.request

		return kwargs

	def form_invalid(self, form):

		response = super(GastoMensualMixin, self).form_invalid(form)

		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			gasto 			= Gasto_Mensual.objects.get(activo_id= obj.activo.id, mes=obj.mes, anio=obj.anio)
			gasto.valor 	= obj.valor
			gasto.user 		= obj.user
			gasto.visible 	= True
			gasto.save()
		except Exception:
			obj.save()

		response = super(GastoMensualMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class GastoMensualNew(GastoMensualMixin, FormView):

	def get_context_data(self, **kwargs):

		context 			= super(GastoMensualNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'gasto común'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/gastos-mensual/list'
		context['accion'] 	= 'create'

		return context

class GastoMensualList(ListView):
	model 			= Gasto_Mensual
	template_name 	= 'gasto_mensual_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(GastoMensualList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'gastos común'
		context['name'] 	= 'lista'
		context['href'] 	= '/gastos-mensual/list'
		
		return context

	def get_queryset(self):

		meses 		= ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
		activos   	= Activo.objects.values_list('id', flat=True).filter(empresa=self.request.user.userprofile.empresa)
		queryset 	= Gasto_Mensual.objects.filter(visible=True, activo__in=activos)

		for item in queryset:

			item.mes 		= meses[int(item.mes)-1]
			item.creado_en 	= item.creado_en.strftime('%d/%m/%Y')
			item.valor		= formato_moneda_local(self.request, item.valor, None)

		return queryset

class GastoMensualDelete(DeleteView):

	model 		= Gasto_Mensual
	success_url = reverse_lazy('/gastos-mensual/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data 				= {'estado': True}

		return JsonResponse(data, safe=False)

class GastoMensualUpdate(GastoMensualMixin, UpdateView):

	model 			= Gasto_Mensual
	form_class 		= GastoMensualForm
	template_name 	= 'gasto_mensual_new.html'
	success_url 	= '/gastos-mensual/list'


	def get_context_data(self, **kwargs):

		context 			= super(GastoMensualUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'gastos común'
		context['name'] 	= 'editar'
		context['href'] 	= '/gastos-mensual/list'
		context['accion'] 	= 'update'

		return context


# gasto servicio (otros gastos)
class GastoServicioMixin(object):

	template_name 	= 'gasto_servicio_new.html'
	form_class 		= GastoServicioForm
	success_url 	= '/gastos-servicios/list'

	def get_form_kwargs(self):

		kwargs 				= super(GastoServicioMixin, self).get_form_kwargs()
		kwargs['request'] 	= self.request
		return kwargs

	def form_invalid(self, form):

		response = super(GastoServicioMixin, self).form_invalid(form)

		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		obj.save()
		form.save_m2m()

		response = super(GastoServicioMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {'estado': True,}
			return JsonResponse(data)
		else:
			return response

class GastoServicioNew(GastoServicioMixin, FormView):

	def get_context_data(self, **kwargs):

		context 			= super(GastoServicioNew, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'servicios varios'
		context['name'] 	= 'nuevo'
		context['href'] 	= '/gastos-servicios/list'
		context['accion'] 	= 'create'

		return context

class GastoServicioList(ListView):

	model 			= Gasto_Servicio
	template_name 	= 'gasto_servicio_list.html'

	def get_context_data(self, **kwargs):

		context 			= super(GastoServicioList, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'servicios varios'
		context['name'] 	= 'lista'
		context['href'] 	= '/gastos-servicios/list'
		
		return context

	def get_queryset(self):

		meses 		= ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
		activos   	= Activo.objects.values_list('id', flat=True).filter(empresa=self.request.user.userprofile.empresa)
		locales 	= Local.objects.filter(activo_id__in=activos)
		queryset 	= Gasto_Servicio.objects.filter(visible=True, locales__in=locales).distinct()

		for item in queryset:
			item.mes 		= meses[int(item.mes)-1]
			item.creado_en 	= item.creado_en.strftime('%d/%m/%Y')

		return queryset

class GastoServicioDelete(DeleteView):

	model 		= Gasto_Servicio
	success_url = reverse_lazy('/gastos-servicios/list')

	def delete(self, request, *args, **kwargs):

		self.object 		= self.get_object()
		self.object.visible = False
		self.object.save()
		data 				= {'estado': True}

		return JsonResponse(data, safe=False)

class GastoServicioUpdate(GastoServicioMixin, UpdateView):

	model 			= Gasto_Servicio
	form_class 		= GastoServicioForm
	template_name 	= 'gasto_servicio_new.html'
	success_url 	= '/gastos-servicios/list'

	def get_context_data(self, **kwargs):

		context 			= super(GastoServicioUpdate, self).get_context_data(**kwargs)
		context['title'] 	= modulo
		context['subtitle'] = 'servicios varios'
		context['name'] 	= 'editar'
		context['href'] 	= '/gastos-servicios/list'
		context['accion'] 	= 'update'

		return context

# api: activo
class ACTIVOS(View):

	http_method_names = ['get']

	def get(self, request, empresa_id, id=None):
		if id == None:
			self.object_list = Activo.objects.filter(empresa_id=empresa_id, visible=True)
		else:
			self.object_list = Activo.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def json_to_response(self):

		data = list()

		for activo in self.object_list:

			data.append({
				'id'		:activo.id,
				'nombre'	:activo.nombre,
				'codigo'	:activo.codigo,
				})

		return JsonResponse(data, safe=False)


class GET_ACTIVO_DOCUMENTS(View):

	http_method_names = ['get']

	def get(self, request, pk):

		activo = Activo.objects.get(id=pk)

		data = oc_list_directory(str(activo.nombre), 'Iproperty/Activos/'+str(activo.nombre))

		return JsonResponse(data, safe=False)
