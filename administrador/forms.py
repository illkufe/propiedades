# -*- coding: utf-8 -*-
from django import forms
from django.forms import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.contrib.auth.models import User, Group

from accounts.models import UserProfile
from .models import *

class ClienteForm(forms.ModelForm):


	def __init__(self, *args, **kwargs):
		super(ClienteForm, self).__init__(*args, **kwargs)
		self.fields['clasificaciones'].required = False

	class Meta:
		model 	= Cliente
		fields	= '__all__'
		exclude = ['creado_en', 'visible', 'empresa']

		widgets = {
			'tipo'			    : forms.Select(attrs={'class': 'form-control'}),
			'rut'			    : forms.TextInput(attrs={'class': 'form-control format-rut'}),
			'nombre'		    : forms.TextInput(attrs={'class': 'form-control'}),
			'razon_social'	    : forms.TextInput(attrs={'class': 'form-control'}),
			'email'			    : forms.EmailInput(attrs={'class': 'form-control'}),
			'giro'			    : forms.Select(attrs={'class': 'form-control select2'}),
			'region'		    : forms.TextInput(attrs={'class': 'form-control'}),
			'ciudad'		    : forms.TextInput(attrs={'class': 'form-control'}),
			'comuna'		    : forms.TextInput(attrs={'class': 'form-control'}),
			'direccion'		    : forms.TextInput(attrs={'class': 'form-control'}),
			'telefono'		    : forms.TextInput(attrs={'class': 'form-control'}),
			'clasificaciones'	: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		error_messages = {
			'tipo' 		: {'required': 'campo requerido'},
			'rut' 		: {'required': 'campo requerido'},
			'email' 	: {'required': 'campo requerido'},
			'telefono' 	: {'required': 'campo requerido'},
			'nombre' 	: {'required': 'campo requerido'},
			'ciudad' 	: {'required': 'campo requerido'},
			'comuna' 	: {'required': 'campo requerido'},
			'direccion' : {'required': 'campo requerido'},
		}

		labels = {
			'tipo'			: 'Tipo de Persona',
			'razon_social'	: 'Razón Social',
			'region'		: 'Región',
			'direccion'		: 'Dirección',
			'telefono'		: 'Teléfono',
		}

		help_texts = {
			'tipo'			    : 'Tipo de Persona',
			'rut'			    : 'R.U.T. del Cliente',
			'nombre'		    : 'Nombre del Cliente',
			'razon_social'	    : 'Razón Social del Cliente',
			'email'			    : 'Email del Cliente',
			'giro'			    : 'Giro del Cliente',
			'region'		    : 'Región',
			'ciudad'		    : 'Ciudad',
			'comuna'		    : 'Comuna',
			'direccion'		    : 'Dirección del Cliente',
			'telefono'		    : 'Número Teléfono del Cliente',
		}

class RepresentanteForm(forms.ModelForm):

	class Meta:
		model 	= Representante
		fields	= '__all__'
		exclude = ['creado_en', 'visible', 'cliente']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'rut'			: forms.TextInput(attrs={'class': 'form-control format-rut'}),
			'nacionalidad'	: forms.TextInput(attrs={'class': 'form-control'}),
			'profesion'		: forms.TextInput(attrs={'class': 'form-control'}),
			'estado_civil'	: forms.Select(attrs={'class': 'form-control'}),
			'domicilio'		: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'numero_rotulo' : {'required': 'campo requerido'},
			'activo' 		: {'required': 'campo requerido'},
			'medidor_tipo' 	: {'required': 'campo requerido'},
		}

		help_texts = {
			'nombre'		: 'nombre',
			'rut'			: 'rut',
			'nacionalidad'	: 'nacionalidad',
			'profesion'		: 'profesion',
			'estado_civil'	: 'estado_civil',
			'domicilio'		: 'domicilio',
		}

		labels = {
			'profesion'		: 'Profesión u Oficio',
			'estado_civil'	: 'Estado Civil',
		}


ClienteFormSet = inlineformset_factory(Cliente, Representante, form=RepresentanteForm, extra=1, can_delete=True)

class ClasificacionForm(forms.ModelForm):

	class Meta:
		model 	= Clasificacion
		fields	= '__all__'
		exclude = ['creado_en', 'visible', 'empresa']

		widgets = {
			'nombre'	            : forms.TextInput(attrs={'class': 'form-control'}),
			'tipo_clasificacion'    : forms.Select(attrs={'class': 'form-control'}),
			'descripcion'	        : forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 	            : {'required': 'campo requerido'},
			'tipo_clasificacion' 	: {'required': 'campo requerido'},
			'descripcion' 	        : {'required': 'campo requerido'},
		}

		labels = {
			'tipo_clasificacion'	: 'Tipo de Clasificación',
		}

		help_texts = {
			'nombre'		        : 'Nombre de la Clasificación',
			'tipo_clasificacion'    : 'Tipo  de Clasificación',
			'descripcion'		    : 'Descripción de la Clasificación',
		}

class ClasificacionDetalleForm(forms.ModelForm):
    class Meta:
        model = Clasificacion_Detalle
        fields = '__all__'
        exclude = ['clasificacion']

        widgets = {
            'nombre'	: forms.TextInput(attrs={'class': 'form-control'}),
        }

        error_messages = {
            'nombre' 		: {'required': 'campo requerido'},
        }

        help_texts = {
            'nombre'		: 'Nombre',
        }

        labels = {
        }

ClasificacionFormSet = inlineformset_factory(Clasificacion, Clasificacion_Detalle, form=ClasificacionDetalleForm, extra=1, can_delete=True)


class ProcesosBorradorForm(forms.Form):

	id 			= forms.IntegerField(required=False, widget=forms.HiddenInput())

	tipo_estado	= forms.ModelChoiceField(
											queryset		= Tipo_Estado_Proceso.objects.all(),
											widget			= forms.Select(
																		attrs={
																				'class': 'form-control',
																		}
																	),
											label			= 'Tipo de Estado',
											help_text		= 'Tipo estado del proceso',
											error_messages	= {
																'required': 'campo requerido'
											}
	)

	nombre		= forms.CharField(
									max_length		= 100,
									widget			= forms.TextInput(
																	attrs={'class': 'form-control'}
																),
									label			= 'Nombre',
									help_text		= 'Nombres de Proceso del WorkFlow',
									error_messages	= {
														'required'	: 'campo requerido',
														'unique'	: 'Nombre de proceso, ya existe.'
									}
	)

	responsable	= forms.ModelMultipleChoiceField(
												queryset	= None,
												widget		= forms.SelectMultiple(
																					attrs={'class'		: 'select2 form-control',
																						   'multiple'	: 'multiple'
																						   }
																				),
												label		= 'Responsable',
												help_text	= 'responsable')

	antecesor	= forms.ModelMultipleChoiceField(
												queryset   	 	= Proceso.objects.all(),
												required		= False,
												widget      	= forms.SelectMultiple(
																						attrs={'class'      : 'select2 form-control',
																							   'multiple'	: 'multiple'
																							   }
																					),
												label       	= 'Antecesor',
												help_text   	= 'Proceso que es necesario cumplir para realizar este proceso',
												error_messages	= {
																	'required': 'campo requerido'
												}
	)

	def __init__(self, *args, **kwargs):

		request 	= kwargs.pop('request', None)

		super(ProcesosBorradorForm, self).__init__(*args, **kwargs)
		self.fields['responsable'].queryset		= UserProfile.objects.filter(empresa=request.user.userprofile.empresa).exclude(tipo_id=2)

	def clean_nombre(self):

		nombre 		= self.cleaned_data['nombre']
		is_insert 	= self.cleaned_data['id'] is None

		if is_insert:
			if Proceso.objects.filter(nombre=nombre, visible=True).exists():
				raise forms.ValidationError('Ya existe un proceso con este nombre.')
		else:
			if nombre != Proceso.objects.get(id=self.cleaned_data['id']).nombre and Proceso.objects.filter(nombre=nombre, visible=True).exists():
				raise forms.ValidationError('Ya existe un proceso con este nombre.')

		return nombre

class ProcesoCondicionForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):

		super(ProcesoCondicionForm, self).__init__(*args, **kwargs)
		self.fields['operacion'].queryset 	= Tipo_Operacion.objects.all().order_by('id')
		self.fields['entidad'].queryset 	= Entidad_Asociacion.objects.all().order_by('id')

	class Meta:
		model 	= Proceso_Condicion
		fields 	= '__all__'
		exclude = [ 'descripcion']

		widgets = {
			'proceso'		: forms.HiddenInput(attrs={'class': 'form-control id_proceso'}),
			'valor'			: forms.TextInput(attrs={'class': 'form-control'}),
			'operacion'		: forms.Select(attrs={'class': 'form-control'}),
			'entidad'		: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'valor' 		: {'required': 'campo requerido'},
			'operacion' 	: {'required': 'campo requerido'},
			'entidad' 		: {'required': 'campo requerido'},
		}

		labels = {
			'tipo_estado'	: 'Tipo de Estado',
		}

		help_texts = {
			'proceso'		: 'proceso',
			'valor'			: 'valor',
			'operacion'		: 'operacion',
			'entidad'		: 'entidad',
		}

ProcesoCondicionFormSet = modelformset_factory(Proceso_Condicion, form=ProcesoCondicionForm, extra=1, exclude=[ 'descripcion'], can_delete=True)

class ConfiguracionMonedaForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):

		super(ConfiguracionMonedaForm, self).__init__(*args, **kwargs)

	def clean(self):

		cantidad_decimales 	= self.cleaned_data.get('cantidad_decimales')

		if cantidad_decimales <0:
			self.add_error('cantidad_decimales', 'Cantidad de decimales no puede ser negativo')

		if cantidad_decimales > 4:
			self.add_error('cantidad_decimales', 'Cantidad de decimales no puede ser mayor a 4')

	class Meta:
		model 	= Configuracion_Monedas
		fields 	= '__all__'
		exclude = [ 'visible', 'empresa', 'moneda_local']

		widgets = {
			'moneda'				: forms.Select(attrs={'class': 'form-control inactiva validate'}),
			'cantidad_decimales'	: forms.NumberInput(attrs={'class': 'form-control validate numeric'}),


		}
		error_messages = {
			'moneda' 				: {'required': 'campo requerido'},
			'cantidad_decimales' 	: {'required': 'campo requerido'},
		}

		labels = {
			'moneda'				: 'Moneda',
			'cantidad_decimales'	: 'Cantidad Decimales',
		}

		help_texts = {
			'moneda'				: 'Moneda',
			'cantidad_decimales'	: 'Cantidad Decimales para la Moneda',
		}



ConfiguracionMonedaFormSet = modelformset_factory(Configuracion_Monedas, form=ConfiguracionMonedaForm, extra=0, min_num=1, can_delete=False)