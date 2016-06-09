# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group
from .models import Moneda, Empresa, Cliente, Representante, Unidad_Negocio

# from accounts.models import UserProfile


class MonedaForm(forms.ModelForm):

	class Meta:
		model 	= Moneda
		fields 	= ['nombre', 'descripcion']

		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			# 'valor': forms.NumberInput(attrs={'class': 'form-control'}),
			'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},
			# 'valor' : {'required': 'Esta campo es requerido.'}
		}

		labels = {
			'descripcion': _(u'Descripción'),
		}

		help_texts = {
			'nombre': _('...'),
			# 'valor': _('...'),
			'descripcion': _('...'),
		}


class ClienteForm(forms.ModelForm):

	class Meta:
		model 	= Cliente
		fields 	= ['rut', 'nombre', 'razon_social', 'giro', 'region', 'comuna', 'direccion', 'telefono', 'cliente_tipo']

		widgets = {
			'rut': forms.TextInput(attrs={'class': 'form-control', 'data-mask': '000.000.000-0',  'data-mask-reverse': 'true'}),
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
			'giro': forms.TextInput(attrs={'class': 'form-control'}),
			'region': forms.TextInput(attrs={'class': 'form-control'}),
			'comuna': forms.TextInput(attrs={'class': 'form-control'}),
			'direccion': forms.TextInput(attrs={'class': 'form-control'}),
			'telefono': forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},
			'rut' : {'required': 'Esta campo es requerido.'},
		}

		labels = {
			'razon_social': (u'Razón Social'),
			'region': (u'Región'),
			'direccion': (u'Dirección'),
			'telefono': (u'Teléfono'),
		}

		help_texts = {
			'razon_social': ('razon_social'),
			'giro': ('giro'),
			'rut': ('rut'),
		}


class RepresentanteForm(forms.ModelForm):

	class Meta:
		model 	= Representante
		fields 	= ['nombre','rut','nacionalidad','profesion','domicilio', 'estado_civil']

		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'rut': forms.TextInput(attrs={'class': 'form-control', 'data-mask': '000.000.000-0',  'data-mask-reverse': 'true'}),
			'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
			'profesion': forms.TextInput(attrs={'class': 'form-control'}),
			'estado_civil': forms.Select(attrs={'class': 'form-control'}),
			'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},
			'numero_rotulo' : {'required': 'Esta campo es requerido.'},
			'activo' : {'required': 'Esta campo es requerido.'},
			'medidor_tipo' : {'required': 'Esta campo es requerido.'},
		}

		help_texts = {
			'nombre': _('nombre'),
			'rut': _('rut'),
			'nacionalidad': _('nacionalidad'),
			'profesion': _('profesion'),
			'estado_civil': _('estado_civil'),
			'domicilio': _('domicilio'),
		}

		labels = {
			'profesion': _(u'Profesión u Oficio'),
			'estado_civil': _(u'Estado Civil'),
		}


class UnidadNegocioForm(forms.ModelForm):
	class Meta:
		model 	= Unidad_Negocio
		fields 	= ['nombre', 'codigo', 'descripcion']
		# fields 	= '__all__'

		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'codigo': forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},
			'codigo' : {'required': 'Esta campo es requerido.'},
		}


# class UserForm(forms.ModelForm):

# 	class Meta:
# 		model 	= User
# 		fields 	= ['first_name', 'last_name', 'email']

# 		widgets = {
# 			'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
# 			'last_name': forms.TextInput(attrs={'class': 'form-control'}),
# 			'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
# 		}

# 		error_messages = {
# 			'first_name' : {'required': 'Esta campo es requerido.'},
# 			'email' : {'required': 'Esta campo es requerido.'}
# 		}

# 		labels = {
# 			'first_name': _(u'Nombre'),
# 			'last_name': _(u'Apellido'),
# 			'email': _(u'Correo'),
# 		}


# class UserProfileForm(forms.ModelForm):

# 	class Meta:
# 		model 	= UserProfile
# 		fields 	= '__all__'
# 		exclude = [ 'visible', 'creado_en', 'user', 'empresa']
# 		# fields 	= ['cargo', 'direccion', 'ciudad', 'comuna', 'descripcion']

# 		widgets = {
# 			'rut'			: forms.TextInput(attrs={'class': 'form-control'}),
# 			'cargo'			: forms.TextInput(attrs={'class': 'form-control'}),
# 			'direccion'		: forms.TextInput(attrs={'class': 'form-control'}),
# 			'ciudad'		: forms.TextInput(attrs={'class': 'form-control'}),
# 			'comuna'		: forms.TextInput(attrs={'class': 'form-control'}),
# 			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
# 		}

# 		labels = {
# 			'rut'			: _(u'RUT'),
# 			'direccion'		: _(u'Dirección'),
# 			'descripcion'	: _(u'Descripción'),
# 		}


ClienteFormSet 		= inlineformset_factory(Cliente, Representante, form=RepresentanteForm, extra=1, can_delete=True)
# UserProfileFormSet 	= inlineformset_factory(User, UserProfile, form=UserProfileForm, extra=1, can_delete=False)
