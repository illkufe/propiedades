from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, FormView, CreateView, DeleteView, UpdateView
from django.contrib.auth.models import User

from .forms import LecturaMedidorForm
from .models import Lectura_Medidor

from accounts.models import UserProfile
from activos.models import Activo


class LecturaMedidorMixin(object):

	template_name = 'viewer/operaciones/lectura_medidor_new.html'
	form_class = LecturaMedidorForm
	success_url = '/lectura-medidores/list'

	def form_invalid(self, form):
		response = super(LecturaMedidorMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		obj = form.save(commit=False)
		obj.user = user
		# obj.empresa_id = profile.empresa_id
		obj.save()

		response = super(LecturaMedidorMixin, self).form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk': 'self.object.pk',
			}
			return JsonResponse(data)
		else:
			return response

class LecturaMedidorNew(LecturaMedidorMixin, FormView):
	def get_context_data(self, **kwargs):
		
		context = super(LecturaMedidorNew, self).get_context_data(**kwargs)
		context['title'] = 'Operaciones'
		context['subtitle'] = 'Lectura Medidor'
		context['name'] = 'Nueva'
		context['href'] = 'lectura-medidores'
		context['accion'] = 'create'
		return context

# {falta: refactorizar esta para que muestre la lectura de todos los medidores}
class LecturaMedidorList(ListView):
	model = Lectura_Medidor
	template_name = 'viewer/operaciones/lectura_medidor_list.html'

	def get_context_data(self, **kwargs):

		context = super(LecturaMedidorList, self).get_context_data(**kwargs)
		context['title'] = 'Operaciones'
		context['subtitle'] = 'Lectura Medidores'
		context['name'] = 'Lista'
		context['href'] = 'lectura-medidores'

		return context

	def get_queryset(self):

		meses = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		activos 	= Activo.objects.values_list('id', flat=True).filter(empresa=profile.empresa, visible=True)
		# medidores 	= Medidor.objects.values_list('id', flat=True).filter(activo__in=activos, visible=True)
		queryset 	= Lectura_Medidor.objects.all()

		for item in queryset:
			item.mes = meses[int(item.mes)]

		return queryset

class LecturaMedidorDelete(DeleteView):
	model = Lectura_Medidor
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class LecturaMedidorUpdate(LecturaMedidorMixin, UpdateView):

	model 			= Lectura_Medidor
	form_class 		= LecturaMedidorForm
	template_name 	= 'viewer/operaciones/lectura_medidor_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_object(self, queryset=None):

		queryset = Lectura_Medidor.objects.get(id=int(self.kwargs['pk']))

		if queryset.fecha:
			queryset.fecha = queryset.fecha.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):
		
		context = super(LecturaMedidorUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Operaciones'
		context['subtitle'] = 'Lectura Medidores'
		context['name'] 	= 'Editar'
		context['href'] 	= 'lectura-medidores'
		context['accion'] 	= 'update'
		return context












class LecturaElectricidadMixin(object):

	template_name = 'viewer/operaciones/lectura_medidor_new.html'
	form_class = LecturaMedidorForm
	success_url = '/lectura-medidores/list'

	def form_invalid(self, form):
		response = super(LecturaElectricidadMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		obj 		= form.save(commit=False)
		obj.user 	= user
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
		context['subtitle'] = 'Lectura Medidor'
		context['name'] = 'Nueva'
		context['href'] = 'lectura-medidores'
		context['accion'] = 'create'
		return context

class LecturaElectricidadDelete(DeleteView):
	model = Lectura_Medidor
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class LecturaElectricidadUpdate(LecturaElectricidadMixin, UpdateView):

	model 			= Lectura_Medidor
	form_class 		= LecturaMedidorForm
	template_name 	= 'viewer/operaciones/lectura_medidor_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_object(self, queryset=None):

		queryset = Lectura_Medidor.objects.get(id=int(self.kwargs['pk']))

		if queryset.fecha:
			queryset.fecha = queryset.fecha.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):
		
		context = super(LecturaElectricidadUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Operaciones'
		context['subtitle'] = 'Lectura Medidores'
		context['name'] 	= 'Editar'
		context['href'] 	= 'lectura-medidores'
		context['accion'] 	= 'update'
		return context



class LecturaAguaMixin(object):

	template_name = 'viewer/operaciones/lectura_medidor_new.html'
	form_class = LecturaMedidorForm
	success_url = '/lectura-medidores/list'

	def form_invalid(self, form):
		response = super(LecturaAguaMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		obj = form.save(commit=False)
		obj.user = user
		# obj.empresa_id = profile.empresa_id
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
	model = Lectura_Medidor
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class LecturaAguaUpdate(LecturaAguaMixin, UpdateView):

	model 			= Lectura_Medidor
	form_class 		= LecturaMedidorForm
	template_name 	= 'viewer/operaciones/lectura_medidor_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_object(self, queryset=None):

		queryset = Lectura_Medidor.objects.get(id=int(self.kwargs['pk']))

		if queryset.fecha:
			queryset.fecha = queryset.fecha.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):
		
		context = super(LecturaAguaUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Operaciones'
		context['subtitle'] = 'Lectura Medidor de Agua'
		context['name'] 	= 'Editar'
		context['href'] 	= 'lectura-medidores'
		context['accion'] 	= 'update'
		return context



class LecturaGasMixin(object):

	template_name = 'viewer/operaciones/lectura_medidor_new.html'
	form_class = LecturaMedidorForm
	success_url = '/lectura-medidores/list'

	def form_invalid(self, form):
		response = super(LecturaGasMixin, self).form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		user 	= User.objects.get(pk=self.request.user.pk)
		profile = UserProfile.objects.get(user=user)

		obj = form.save(commit=False)
		obj.user = user
		# obj.empresa_id = profile.empresa_id
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
	model = Lectura_Medidor
	success_url = reverse_lazy('/contratos-tipo/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.visible = False
		self.object.save()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)

class LecturaGasUpdate(LecturaGasMixin, UpdateView):

	model 			= Lectura_Medidor
	form_class 		= LecturaMedidorForm
	template_name 	= 'viewer/operaciones/lectura_medidor_new.html'
	success_url 	= '/lectura-medidores/list'

	def get_object(self, queryset=None):

		queryset = Lectura_Medidor.objects.get(id=int(self.kwargs['pk']))

		if queryset.fecha:
			queryset.fecha = queryset.fecha.strftime('%d/%m/%Y')

		return queryset

	def get_context_data(self, **kwargs):
		
		context = super(LecturaGasUpdate, self).get_context_data(**kwargs)
		context['title'] 	= 'Operaciones'
		context['subtitle'] = 'Lectura Medidor de Gas'
		context['name'] 	= 'Editar'
		context['href'] 	= 'lectura-medidores'
		context['accion'] 	= 'update'
		return context
