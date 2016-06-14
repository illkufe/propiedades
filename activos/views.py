from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, UpdateView, DeleteView
from django.contrib.auth.models import User

from .forms import ActivoForm, SectorFormSet, NivelFormSet, LocalForm, ActivoMedidoForm, ElectricidadFormSet, AguaFormSet, GasFormSet
from .models import Activo, Sector, Nivel, Medidor_Electricidad, Medidor_Agua, Medidor_Gas

from locales.models import Local
from accounts.models import UserProfile


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
		# form_medidor 	= context['medidorform']

		obj = form.save(commit=False)
		obj.empresa_id = profile.empresa_id
		obj.save()



		# self.object = form.save(commit=False)
		# self.object.empresa_id = profile.empresa_id
		# self.object = self.object.save()

		if form_sector.is_valid():
			self.object = form.save(commit=False)
			form_sector.instance = self.object
			form_sector.save()

		if form_nivel.is_valid():
			self.object = form.save(commit=False)
			form_nivel.instance = self.object
			form_nivel.save()

		# if form_medidor.is_valid():
		# 	form_medidor.instance = self.object
		# 	form_medidor.save()

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



class ActivoMedidorMixin(object):

	template_name = 'viewer/activos/activo_medidor_new.html'
	form_class = ActivoMedidoForm
	success_url = '/activos/list'

	def form_invalid(self, form):

		response = super(ActivoMedidorMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		context 			= self.get_context_data()
		form_electricidad 	= context['form_electricidad']
		form_gas 			= context['form_gas']
		form_agua 			= context['form_agua']

		if form_electricidad.is_valid():
			form_electricidad.save()

		if form_agua.is_valid():
			form_agua.save()

		if form_gas.is_valid():
			form_gas.save()

		response = super(ActivoMedidorMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'status': 'ok',
			}
			return JsonResponse(data)
		else:
			return response

class ActivoMedidorNew(ActivoMedidorMixin, FormView):

	def get_context_data(self, **kwargs):

		context 				= super(ActivoMedidorNew, self).get_context_data(**kwargs)
		context['title'] 		= 'Activos'
		context['subtitle'] 	= 'Medidor'
		context['name'] 		= 'Nuevo'
		context['href'] 		= 'activos'
		context['accion'] 		= 'update'
		context['activo_id']	= self.kwargs['activo_id']

		if self.request.POST:

			activo 	= Activo.objects.get(id=self.kwargs['activo_id'])

			try:
				medidor_electricidad = Medidor_Electricidad.objects.filter(activo_id=self.kwargs['activo_id'])
				context['form_electricidad'] = ElectricidadFormSet(self.request.POST, instance=activo)
			except Medidor_Electricidad.DoesNotExist:
				context['form_electricidad'] = ElectricidadFormSet(self.request.POST)

			try:
				medidor_agua = Medidor_Agua.objects.filter(activo_id=self.kwargs['activo_id'])
				context['form_agua'] = AguaFormSet(self.request.POST, instance=activo)
			except Medidor_Agua.DoesNotExist:
				context['form_agua'] = AguaFormSet(self.request.POST)

			try:
				medidor_gas = Medidor_Gas.objects.filter(activo_id=self.kwargs['activo_id'])
				context['form_gas'] = GasFormSet(self.request.POST, instance=activo)
			except Medidor_Gas.DoesNotExist:
				context['form_gas'] = GasFormSet(self.request.POST)

		else:

			activo 	= Activo.objects.get(id=self.kwargs['activo_id'])

			try:
				medidor_electricidad = Medidor_Electricidad.objects.filter(activo_id=self.kwargs['activo_id'])
				context['form_electricidad'] = ElectricidadFormSet(instance=activo)
			except Medidor_Electricidad.DoesNotExist:
				context['form_electricidad'] = ElectricidadFormSet()

			try:
				medidor_agua = Medidor_Agua.objects.filter(activo_id=self.kwargs['activo_id'])
				context['form_agua'] = AguaFormSet(instance=activo)
			except Medidor_Agua.DoesNotExist:
				context['form_agua'] = AguaFormSet()

			try:
				medidor_gas = Medidor_Gas.objects.filter(activo_id=self.kwargs['activo_id'])
				context['form_gas'] = GasFormSet(instance=activo)
			except Medidor_Gas.DoesNotExist:
				context['form_gas'] = GasFormSet()

		return context



class ActivoLocaleMixin(object):

	template_name = 'viewer/activos/activo_local_new.html'
	form_class = LocalForm
	success_url = '/locales/list'

	def get_form_kwargs(self):
		kwargs = super(ActivoLocaleMixin, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def form_invalid(self, form):
		response = super(ActivoLocaleMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):


		obj = form.save(commit=False)
		obj.activo_id = self.kwargs['activo_id']
		obj.save()
		
		form.save_m2m()
		for medidor in form.cleaned_data['medidores']:
			medidor.estado = True
			medidor.save()

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

		return context

class ActivoLocalUpdate(UpdateView):

	model = Local
	form_class = LocalForm
	template_name = 'viewer/activos/activo_local_new.html'
	success_url = '/locales/list'

	def get_form_kwargs(self):
		kwargs = super(ActivoLocalUpdate, self).get_form_kwargs()
		kwargs['request'] = self.request
		return kwargs

	def get_context_data(self, **kwargs):
		
		context = super(ActivoLocalUpdate, self).get_context_data(**kwargs)
		context['title'] = 'Locales'
		context['subtitle'] = 'Local'
		context['name'] = 'Editar'
		context['href'] = 'locales'
		context['accion'] = 'update'

		return context




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





