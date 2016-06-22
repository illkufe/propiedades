from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, FormView, CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User

from .forms import LecturaElectricidadForm, LecturaAguaForm, LecturaGasForm
from .models import Lectura_Electricidad, Lectura_Agua, Lectura_Gas

from accounts.models import UserProfile
from activos.models import Activo


class LecturaMedidorList(ListView):

	model = Lectura_Electricidad
	template_name = 'viewer/operaciones/lectura_medidor_list.html'

	def get_context_data(self, **kwargs):

		context = super(LecturaMedidorList, self).get_context_data(**kwargs)
		context['title'] = 'Operaciones'
		context['subtitle'] = 'Lectura Medidores'
		context['name'] = 'Lista'
		context['href'] = 'lectura-medidores'

		return context

	def get_queryset(self):

		profile 	= UserProfile.objects.get(user=self.request.user)
		profiles 	= profile.empresa.userprofile_set.all().values_list('id', flat=True)
		users 		= User.objects.filter(userprofile__in=profiles).values_list('id', flat=True)

		queryset 	= []
		meses 		= ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

		electricidad 	= Lectura_Electricidad.objects.filter(visible=True, user__in=users)
		agua 			= Lectura_Agua.objects.filter(visible=True, user__in=users)
		gas 			= Lectura_Gas.objects.filter(visible=True, user__in=users)

		for item in electricidad:
			item.local 	= item.medidor_electricidad.local
			item.activo = item.medidor_electricidad.local.activo
			item.mes 	= meses[int(item.mes)-1]
			item.tipo 	= 'Electricidad'
			item.url 	= 'electricidad'
			queryset.append(item)

		for item in agua:
			item.local 	= item.medidor_agua.local
			item.activo = item.medidor_electricidad.local.activo
			item.mes = meses[int(item.mes)-1]
			item.tipo 	= 'Agua'
			item.url 	= 'agua'
			queryset.append(item)

		for item in gas:
			item.local 	= item.medidor_gas.local
			item.activo = item.medidor_electricidad.local.activo
			item.mes = meses[int(item.mes)-1]
			item.tipo 	= 'Gas'
			item.url 	= 'gas'
			queryset.append(item)

		return queryset


class LecturaElectricidadMixin(object):

	template_name = 'viewer/operaciones/lectura_electricidad_new.html'
	form_class = LecturaElectricidadForm
	success_url = '/lectura-medidores/list'

	def form_invalid(self, form):
		response = super(LecturaElectricidadMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		profile 	= UserProfile.objects.get(user=self.request.user)
		obj 		= form.save(commit=False)
		obj.user 	= self.request.user

		try:
			lectura = Lectura_Electricidad.objects.get(medidor_electricidad_id= obj.medidor_electricidad.id, mes=obj.mes, anio=obj.anio)
			lectura.valor 	= obj.valor
			lectura.user 	= obj.user
			lectura.visible = True
			lectura.save()
		except Exception:
			obj.save()

		response = super(LecturaElectricidadMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class LecturaElectricidadNew(LecturaElectricidadMixin, FormView):

	def get_context_data(self, **kwargs):
		
		context = super(LecturaElectricidadNew, self).get_context_data(**kwargs)
		context['title'] = 'Operaciones'
		context['subtitle'] = 'Lectura Medidor Electricidad'
		context['name'] = 'Nueva'
		context['href'] = 'lectura-medidores'
		context['accion'] = 'create'

		return context

class LecturaElectricidadDelete(DeleteView):

	model = Lectura_Electricidad
	success_url = reverse_lazy('/lectura-medidores/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class LecturaElectricidadUpdate(LecturaElectricidadMixin, UpdateView):

	model 			= Lectura_Electricidad
	form_class 		= LecturaElectricidadForm
	template_name 	= 'viewer/operaciones/lectura_electricidad_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context = super(LecturaElectricidadUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Operaciones'
		context['subtitle'] = 'Lectura Medidor Electricidad'
		context['name'] 	= 'Editar'
		context['href'] 	= 'lectura-medidores'
		context['accion'] 	= 'update'
		return context


class LecturaAguaMixin(object):

	template_name = 'viewer/operaciones/lectura_agua_new.html'
	form_class = LecturaAguaForm
	success_url = '/lectura-medidores/list'

	def form_invalid(self, form):
		response = super(LecturaAguaMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		profile 	= UserProfile.objects.get(user=self.request.user)
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
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class LecturaAguaNew(LecturaAguaMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(LecturaAguaNew, self).get_context_data(**kwargs)
		context['title'] = 'Operaciones'
		context['subtitle'] = 'Lectura Medidor de Agua'
		context['name'] = 'Nueva'
		context['href'] = 'lectura-medidores'
		context['accion'] = 'create'
		return context

class LecturaAguaDelete(DeleteView):

	model = Lectura_Agua
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class LecturaAguaUpdate(LecturaAguaMixin, UpdateView):

	model 			= Lectura_Agua
	form_class 		= LecturaAguaForm
	template_name 	= 'viewer/operaciones/lectura_agua_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context = super(LecturaAguaUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Operaciones'
		context['subtitle'] = 'Lectura Medidor de Agua'
		context['name'] 	= 'Editar'
		context['href'] 	= 'lectura-medidores'
		context['accion'] 	= 'update'
		return context


class LecturaGasMixin(object):

	template_name = 'viewer/operaciones/lectura_gas_new.html'
	form_class = LecturaGasForm
	success_url = '/lectura-medidores/list'

	def form_invalid(self, form):
		response = super(LecturaGasMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):

		profile 	= UserProfile.objects.get(user=self.request.user)
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
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class LecturaGasNew(LecturaGasMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(LecturaGasNew, self).get_context_data(**kwargs)
		context['title'] = 'Operaciones'
		context['subtitle'] = 'Lectura Medidor de Gas'
		context['name'] = 'Nueva'
		context['href'] = 'lectura-medidores'
		context['accion'] = 'create'
		return context

class LecturaGasDelete(DeleteView):

	model = Lectura_Gas
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):

		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}

		return JsonResponse(payload, safe=False)

class LecturaGasUpdate(LecturaGasMixin, UpdateView):

	model 			= Lectura_Agua
	form_class 		= LecturaAguaForm
	template_name 	= 'viewer/operaciones/lectura_agua_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_context_data(self, **kwargs):
		
		context = super(LecturaGasUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Operaciones'
		context['subtitle'] = 'Lectura Medidor de Gas'
		context['name'] 	= 'Editar'
		context['href'] 	= 'lectura-medidores'
		context['accion'] 	= 'update'
		return context
