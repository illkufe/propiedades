# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group

from .models import Moneda, Empresa, Cliente, Representante, Unidad_Negocio

class MonedaForm(forms.ModelForm):

	class Meta:
		model 	= Moneda
		fields 	= ['nombre', 'descripcion']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},		
		}

		labels = {
			'descripcion': 'Descripción',
		}

		help_texts = {
			'nombre'		: '...',
			'descripcion'	: '...',
		}


class ClienteForm(forms.ModelForm):

	class Meta:
		model 	= Cliente
		fields 	= ['rut', 'nombre', 'razon_social', 'giro', 'region', 'comuna', 'direccion', 'telefono', 'cliente_tipo']

		widgets = {
			'rut'			: forms.TextInput(attrs={'class': 'form-control', 'data-mask': '000.000.000-0',  'data-mask-reverse': 'true'}),
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'razon_social'	: forms.TextInput(attrs={'class': 'form-control'}),
			'giro'			: forms.TextInput(attrs={'class': 'form-control'}),
			'region'		: forms.TextInput(attrs={'class': 'form-control'}),
			'comuna'		: forms.TextInput(attrs={'class': 'form-control'}),
			'direccion'		: forms.TextInput(attrs={'class': 'form-control'}),
			'telefono'		: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 	: {'required': 'Esta campo es requerido.'},
			'rut' 		: {'required': 'Esta campo es requerido.'},
		}

		labels = {
			'razon_social'	: 'Razón Social',
			'region'		: 'Región',
			'direccion'		: 'Dirección',
			'telefono'		: 'Teléfono',
		}

		help_texts = {
			'razon_social'	: 'razon_social',
			'giro'			: 'giro',
			'rut'			: 'rut',
		}


class RepresentanteForm(forms.ModelForm):

	class Meta:
		model 	= Representante
		fields 	= ['nombre','rut','nacionalidad','profesion','domicilio', 'estado_civil']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'rut'			: forms.TextInput(attrs={'class': 'form-control', 'data-mask': '000.000.000-0',  'data-mask-reverse': 'true'}),
			'nacionalidad'	: forms.TextInput(attrs={'class': 'form-control'}),
			'profesion'		: forms.TextInput(attrs={'class': 'form-control'}),
			'estado_civil'	: forms.Select(attrs={'class': 'form-control'}),
			'domicilio'		: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'Esta campo es requerido.'},
			'numero_rotulo' : {'required': 'Esta campo es requerido.'},
			'activo' 		: {'required': 'Esta campo es requerido.'},
			'medidor_tipo' 	: {'required': 'Esta campo es requerido.'},
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


class UnidadNegocioForm(forms.ModelForm):

	class Meta:
		model 	= Unidad_Negocio
		fields 	= ['nombre', 'codigo', 'descripcion']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},
			'codigo' : {'required': 'Esta campo es requerido.'},
		}



ClienteFormSet = inlineformset_factory(Cliente, Representante, form=RepresentanteForm, extra=1, can_delete=True)

