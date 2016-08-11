# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group

from .models import Empresa, Cliente, Representante

class ClienteForm(forms.ModelForm):

	class Meta:
		model 	= Cliente
		fields	= '__all__'
		exclude = ['creado_en', 'visible', 'empresa']

		widgets = {
			'rut'			: forms.TextInput(attrs={'class': 'form-control format-rut'}),
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'razon_social'	: forms.TextInput(attrs={'class': 'form-control'}),
			'giro'			: forms.TextInput(attrs={'class': 'form-control'}),
			'region'		: forms.TextInput(attrs={'class': 'form-control'}),
			'comuna'		: forms.TextInput(attrs={'class': 'form-control'}),
			'direccion'		: forms.TextInput(attrs={'class': 'form-control'}),
			'telefono'		: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 	: {'required': 'campo requerido'},
			'rut' 		: {'required': 'campo requerido'},
			'direccion' : {'required': 'campo requerido'},
			'telefono' 	: {'required': 'campo requerido'},
		}

		labels = {
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

