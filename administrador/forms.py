# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group

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
			'giro'			    : forms.Select(attrs={'class': 'form-control'}),
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
			'rut'			: 'rut',
			'nombre'		: 'nombre',
			'razon_social'	: 'razon social',
			'giro'			: 'giro',
			'region'		: 'region',
			'comuna'		: 'comuna',
			'direccion'		: 'direccion',
			'telefono'		: 'telefono',
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
			'nombre'		        : 'nombre',
			'tipo_clasificacion'    : 'tipo clasificación',
			'descripcion'		    : 'descripción',
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
            'nombre'		: 'nombre',
        }

        labels = {
        }

ClasificacionFormSet = inlineformset_factory(Clasificacion, Clasificacion_Detalle, form=ClasificacionDetalleForm, extra=1, can_delete=True)