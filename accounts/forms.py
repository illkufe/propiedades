# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group

from .models import UserProfile

class UserForm(forms.ModelForm):

	class Meta:
		model 	= User
		fields 	= ['first_name', 'last_name', 'email']

		widgets = {
			'first_name'	: forms.TextInput(attrs={'class': 'form-control'}),
			'last_name'		: forms.TextInput(attrs={'class': 'form-control'}),
			'email'			: forms.EmailInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'first_name' 	: {'required': 'Esta campo es requerido.'},
			'email' 		: {'required': 'Esta campo es requerido.'},
		}

		labels = {
			'first_name'	: 'Nombre',
			'last_name'		: 'Apellido',
			'email'			: 'Correo',
		}

class UserProfileForm(forms.ModelForm):

	class Meta:
		model 	= UserProfile
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'empresa']

		widgets = {
			'rut'			: forms.TextInput(attrs={'class': 'form-control', 'data-mask': '000.000.000-0',  'data-mask-reverse': 'true'}),
			'tipo'			: forms.Select(attrs={'class': 'form-control'}),
			'cargo'			: forms.TextInput(attrs={'class': 'form-control'}),
			'direccion'		: forms.TextInput(attrs={'class': 'form-control'}),
			'ciudad'		: forms.TextInput(attrs={'class': 'form-control'}),
			'comuna'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		labels = {
			'rut'			: 'RUT',
			'direccion'		: 'Dirección',
			'descripcion'	: 'Descripción',
		}

UserProfileFormSet 	= inlineformset_factory(User, UserProfile, form=UserProfileForm, extra=1, can_delete=False)

