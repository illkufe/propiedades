from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, UpdateView, DeleteView
from django.contrib.auth.models import User

from accounts.models import UserProfile
from locales.models import Local, Medidor_Electricidad, Medidor_Agua, Medidor_Gas, Gasto_Servicio

from .forms import ActivoForm, SectorFormSet, NivelFormSet, GastoMensualForm, LocalForm, ElectricidadFormSet, AguaFormSet, GasFormSet, GastoServicioForm
from .models import Activo, Sector, Nivel, Gasto_Mensual


class ActivoMixin(object):

	template_name = 'viewer/activos/activo_new.html'
	form_class = ActivoForm
	success_url = '/activos/list'

	def form_invalid(self, form):
		response = super(ActivoMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		context 		= self.get_context_data()
		form_sector 	= context['sectorform']
		form_nivel 		= context['nivelform']

		obj = form.save(commit=False)
		obj.empresa_id = profile.empresa_id
		obj.save()

		if form_sector.is_valid():
			self.object = form.save(commit=False)
			form_sector.instance = self.object
			form_sector.save()

		if form_nivel.is_valid():
			self.object = form.save(commit=False)
			form_nivel.instance = self.object
			form_nivel.save()

		response = super(ActivoMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class ActivoNew(ActivoMixin, FormView):

	def get_context_data(self, **kwargs):

		context = super(ActivoNew, self).get_context_data(**kwargs)
		context['title'] = 'Activos'
		context['subtitle'] = 'Activo'
		context['name'] = 'Nuevo'
		context['href'] = 'activos'
		context['accion'] = 'create'

		if self.request.POST:
			context['sectorform'] = SectorFormSet(self.request.POST)
			context['nivelform'] = NivelFormSet(self.request.POST)
		else:
			context['sectorform'] = SectorFormSet()
			context['nivelform'] = NivelFormSet()

		return context

class ActivoList(ListView):
	model = Activo
	template_name = 'viewer/activos/activo_list.html'

	def get_context_data(self, **kwargs):
		context = super(ActivoList, self).get_context_data(**kwargs)
		context['title'] = 'Activos'
		context['subtitle'] = 'Activo'
		context['name'] = 'Lista'
		context['href'] = 'activos'
		
		return context

	def get_queryset(self):

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		queryset 	= Activo.objects.filter(empresa=profile.empresa, visible=True)

		return queryset

class ActivoDelete(DeleteView):
	model = Activo
	success_url = reverse_lazy('/activos/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class ActivoUpdate(ActivoMixin, UpdateView):

	model = Activo
	form_class = ActivoForm
	template_name = 'viewer/activos/activo_new.html'
	success_url = '/activos/list'

	def get_object(self, queryset=None):

		queryset = Activo.objects.get(id=int(self.kwargs['pk']))

		if queryset.fecha_firma_nomina:
			queryset.fecha_firma_nomina = queryset.fecha_firma_nomina.strftime('%d/%m/%Y')
		if queryset.fecha_servicio:
			queryset.fecha_servicio = queryset.fecha_servicio.strftime('%d/%m/%Y')
		if queryset.fecha_adquisicion:
			queryset.fecha_adquisicion = queryset.fecha_adquisicion.strftime('%d/%m/%Y')
		if queryset.fecha_tasacion:
			queryset.fecha_tasacion = queryset.fecha_tasacion.strftime('%d/%m/%Y')

		return queryset


	def get_context_data(self, **kwargs):

		context = super(ActivoUpdate, self).get_context_data(**kwargs)

		context['title'] = 'Activos'
		context['subtitle'] = 'Activo'
		context['name'] = 'Editar'
		context['href'] = 'activos'
		context['accion'] = 'update'

		if self.request.POST:
			context['sectorform'] = SectorFormSet(self.request.POST, instance=self.object)
			context['nivelform'] = NivelFormSet(self.request.POST, instance=self.object)
		else:
			context['sectorform'] = SectorFormSet(instance=self.object)
			context['nivelform'] = NivelFormSet(instance=self.object)

		return context



class GastoMensualMixin(object):

	template_name = 'viewer/activos/gasto_mensual_new.html'
	form_class = GastoMensualForm
	success_url = '/gastos-mensual/list'

	def get_form_kwargs(self):
		kwargs = super(GastoMensualMixin, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_invalid(self, form):
		response = super(GastoMensualMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		profile 	= UserProfile.objects.get(user=self.request.user)
		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			gasto = Gasto_Mensual.objects.get(activo_id= obj.activo.id, mes=obj.mes, anio=obj.anio)
			gasto.valor 	= obj.valor
			gasto.user 	= obj.user
			gasto.visible = True
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

		context = super(GastoMensualNew, self).get_context_data(**kwargs)
		context['title'] = 'Activos'
		context['subtitle'] = 'Gasto Común'
		context['name'] = 'Nuevo'
		context['href'] = 'gastos-mensual'
		context['accion'] = 'create'

		return context

class GastoMensualList(ListView):
	model = Gasto_Mensual
	template_name = 'viewer/activos/gasto_mensual_list.html'

	def get_context_data(self, **kwargs):
		context = super(GastoMensualList, self).get_context_data(**kwargs)
		context['title'] = 'Activos'
		context['subtitle'] = 'Gastos Mensuales'
		context['name'] = 'Lista'
		context['href'] = 'gastos-mensual'
		
		return context

	def get_queryset(self):

		meses 		= ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		activos   	= Activo.objects.values_list('id', flat=True).filter(empresa=profile.empresa)
		queryset 	= Gasto_Mensual.objects.filter(visible=True, activo__in=activos)

		for item in queryset:
			item.mes 		= meses[int(item.mes)-1]
			item.creado_en 	= item.creado_en.strftime('%d/%m/%Y')

		return queryset

class GastoMensualDelete(DeleteView):
	model = Gasto_Mensual
	success_url = reverse_lazy('/gastos-mensual/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class GastoMensualUpdate(GastoMensualMixin, UpdateView):

	model = Gasto_Mensual
	form_class = GastoMensualForm
	template_name = 'viewer/activos/gasto_mensual_new.html'
	success_url = '/gastos-mensual/list'


	def get_context_data(self, **kwargs):

		context = super(GastoMensualUpdate, self).get_context_data(**kwargs)

		context['title'] = 'Activos'
		context['subtitle'] = 'Activo'
		context['name'] = 'Editar'
		context['href'] = 'activos'
		context['accion'] = 'update'


		return context



class GastoServicioMixin(object):

	template_name = 'viewer/activos/gasto_servicio_new.html'
	form_class = GastoServicioForm
	success_url = '/gastos-servicios/list'

	def get_form_kwargs(self):
		kwargs = super(GastoServicioMixin, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_invalid(self, form):
		response = super(GastoServicioMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		profile 	= UserProfile.objects.get(user=self.request.user)
		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		obj.save()
		form.save_m2m()

		response = super(GastoServicioMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class GastoServicioNew(GastoServicioMixin, FormView):

	def get_context_data(self, **kwargs):

		context = super(GastoServicioNew, self).get_context_data(**kwargs)
		context['title'] 	= 'Activos'
		context['subtitle'] = 'Servicios Varios'
		context['name'] 	= 'Nuevo'
		context['href'] 	= 'gastos-servicios'
		context['accion'] 	= 'create'

		return context

class GastoServicioList(ListView):
	model = Gasto_Servicio
	template_name = 'viewer/activos/gasto_servicio_list.html'

	def get_context_data(self, **kwargs):
		context = super(GastoServicioList, self).get_context_data(**kwargs)
		context['title'] 	= 'Activos'
		context['subtitle'] = 'Servicios Varios'
		context['name'] 	= 'Lista'
		context['href'] 	= 'gastos-servicios'
		
		return context

	def get_queryset(self):

		meses 		= ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		activos   	= Activo.objects.values_list('id', flat=True).filter(empresa=profile.empresa)
		locales 	= Local.objects.filter(activo_id__in=activos)
		queryset 	= Gasto_Servicio.objects.filter(visible=True, locales__in=locales).distinct()

		for item in queryset:
			item.mes 		= meses[int(item.mes)-1]
			item.creado_en 	= item.creado_en.strftime('%d/%m/%Y')

		return queryset

class GastoServicioDelete(DeleteView):
	model = Gasto_Servicio
	success_url = reverse_lazy('/gastos-servicios/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class GastoServicioUpdate(GastoServicioMixin, UpdateView):

	model = Gasto_Servicio
	form_class = GastoServicioForm
	template_name = 'viewer/activos/gasto_servicio_new.html'
	success_url = '/gastos-servicios/list'


	def get_context_data(self, **kwargs):

		context = super(GastoServicioUpdate, self).get_context_data(**kwargs)

		context['title'] 	= 'Activos'
		context['subtitle'] = 'Servicios Varios'
		context['name'] 	= 'Editar'
		context['href'] 	= 'gastos-servicios'
		context['accion'] 	= 'update'


		return context



class ActivoLocaleMixin(object):

	template_name = 'viewer/activos/activo_local_new.html'
	form_class = LocalForm
	success_url = '/locales/list'

	def get_form_kwargs(self):

		kwargs = super(ActivoLocaleMixin, self).get_form_kwargs()

		kwargs['request'] 	= self.request
		kwargs['activo_id'] = self.kwargs['activo_id']

		return kwargs

	def form_invalid(self, form):
		response = super(ActivoLocaleMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context 		= self.get_context_data()
		obj 			= form.save(commit=False)
		obj.activo_id 	= self.kwargs['activo_id']
		obj.save()

		form_electricidad 	= context['form_electricidad']
		form_gas 			= context['form_gas']
		form_agua 			= context['form_agua']

		if form_electricidad.is_valid():
			self.object 				= form.save(commit=False)
			form_electricidad.instance 	= self.object
			form_electricidad.save()

		if form_gas.is_valid():
			self.object 		= form.save(commit=False)
			form_gas.instance 	= self.object
			form_gas.save()

		if form_agua.is_valid():
			self.object 		= form.save(commit=False)
			form_agua.instance 	= self.object
			form_agua.save()

		response = super(ActivoLocaleMixin, self).form_valid(form)

		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class ActivoLocalNew(ActivoLocaleMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context = super(ActivoLocalNew, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Local'
		context['name'] = 'Nuevo'
		context['href'] = 'locales'
		context['accion'] = 'create'

		if self.request.POST:
			context['form_electricidad'] 	= ElectricidadFormSet(self.request.POST)
			context['form_agua'] 			= AguaFormSet(self.request.POST)
			context['form_gas']				= GasFormSet(self.request.POST)
		else:
			context['form_electricidad'] 	= ElectricidadFormSet()
			context['form_agua'] 			= AguaFormSet()
			context['form_gas'] 			= GasFormSet()

		return context

class ActivoLocalUpdate(ActivoLocaleMixin, UpdateView):

	model = Local
	form_class = LocalForm
	template_name = 'viewer/activos/activo_local_new.html'
	success_url = '/locales/list'


	def get_context_data(self, **kwargs):
		
		context = super(ActivoLocalUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Local'
		context['name'] = 'Editar'
		context['href'] = 'locales'
		context['accion'] = 'update'

		if self.request.POST:
			context['form_electricidad'] 	= ElectricidadFormSet(self.request.POST, instance=self.object)
			context['form_agua'] 			= AguaFormSet(self.request.POST, instance=self.object)
			context['form_gas'] 			= GasFormSet(self.request.POST, instance=self.object)
		else:
			context['form_electricidad'] 	= ElectricidadFormSet(instance=self.object)
			context['form_agua'] 			= AguaFormSet(instance=self.object)
			context['form_gas'] 			= GasFormSet(instance=self.object)

		return context





# API -----------------
class ACTIVOS(View):

	http_method_names =  ['get']

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

