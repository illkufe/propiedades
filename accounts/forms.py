# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate, login
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

class UpdateUserProfileForm(forms.Form):

	first_name 		= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Nombres')
	last_name 		= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Apellidos')
	rut 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control format-rut'}), label='R.U.T.')
	cargo 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Cargo')
	ciudad 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Ciudad')
	comuna 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Comuna')
	direccion 		= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Dirección')
	descripcion 	= forms.CharField(max_length=100, required=False, widget=forms.Textarea(attrs={'class': 'form-control',  'rows':'2'}), label='Descripción')

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(UpdateUserProfileForm, self).__init__(*args, **kwargs)

		self.fields['first_name'].initial 	= self.user.first_name
		self.fields['last_name'].initial 	= self.user.last_name
		self.fields['rut'].initial 			= self.user.userprofile.rut
		self.fields['cargo'].initial 		= self.user.userprofile.cargo
		self.fields['ciudad'].initial 		= self.user.userprofile.ciudad
		self.fields['comuna'].initial 		= self.user.userprofile.comuna
		self.fields['direccion'].initial 	= self.user.userprofile.direccion
		self.fields['descripcion'].initial 	= self.user.userprofile.descripcion


class UpdatePasswordForm(forms.Form):

	password_actual = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Actual')
	password_nueva 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Nueva')
	password_copia 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repetir Contraseña')

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(UpdatePasswordForm, self).__init__(*args, **kwargs)

	def clean(self):

		cleaned_data 	= super(UpdatePasswordForm, self).clean()
		password_actual = cleaned_data.get("password_actual")
		authentication  = authenticate(username=self.user.email, password=password_actual)

		if authentication is None:
		    msg = "Tu contraseña es incorrecta"
		    self.add_error('password_actual', msg)


UserProfileFormSet 	= inlineformset_factory(User, UserProfile, form=UserProfileForm, extra=1, can_delete=False)

