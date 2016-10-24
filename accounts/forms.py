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
			'first_name' 	: {'required': 'campo requerido'},
			'email' 		: {'required': 'campo requerido'},
		}

		labels = {
			'first_name'	: 'Nombre',
			'last_name'		: 'Apellido',
			'email'			: 'Correo',
		}
		help_texts ={
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
			'rut'			: forms.TextInput(attrs={'class': 'form-control format-rut'}),
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

		help_texts={
			'rut'			: 'R.U.T de Usuario',
			'tipo'			: 'Tipo de Usuario',
			'cargo'			: 'Cargo del Usuario',
			'direccion'		: 'Dirección del Usuario',
			'ciudad'		: 'Ciudad de Usuario',
			'comuna'		: 'Comuna del Usuario',
			'descripcion'	: 'Descripción',
		}

class UpdateUserProfileForm(forms.Form):

	first_name 		= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Nombres', help_text='Nombres del Usuario')
	last_name 		= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Apellidos', help_text='Apellidos del Usuario')
	rut 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control format-rut'}), label='RUT', help_text='R.U.T. del Usuario')
	cargo 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Cargo', help_text='Cargo del Usuario')
	ciudad 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Ciudad', help_text='Ciudad del Usuario')
	comuna 			= forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Comuna', help_text='Comuna del Usuario')
	direccion 		= forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Dirección', help_text='Dirección del Usuario')
	descripcion 	= forms.CharField(max_length=200, required=False, widget=forms.Textarea(attrs={'class': 'form-control',  'rows':'2'}), label='Descripción', help_text='Descripción')

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

	password_actual = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Actual', help_text='Contraseña Actual del Usuario')
	password_nueva 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Nueva', help_text='Nueva Contraseña del Usuario')
	password_copia 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repetir Contraseña', help_text='Repetición de Contraseña Nueva del Usuario')

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


class UpdatePasswordAdminForm(forms.Form):

	password_nueva 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Nueva')
	password_copia 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repetir Contraseña')



UserProfileFormSet 	= inlineformset_factory(User, UserProfile, form=UserProfileForm, extra=1, can_delete=False)

