from django import forms
from django.contrib.auth import authenticate, login
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group
from utilidades.views import *

from .models import *

class UserProfileForm(forms.ModelForm):

	email = forms.EmailField(
		widget = forms.EmailInput(attrs={'class': 'form-control'}),
		label = 'Email (*)',
		help_text = 'email del usuario',
		error_messages = {'required': 'campo requerido', 'invalid': 'ingrese un correo valido'},
		)

	first_name = forms.CharField(
		widget = forms.TextInput(attrs={'class': 'form-control'}),
		label = 'Nombre (*)',
		help_text = 'nombre del usuario',
		error_messages = {'required': 'campo requerido'},
		)

	last_name = forms.CharField(
		widget = forms.TextInput(attrs={'class': 'form-control'}),
		label = 'Apellido (*)',
		help_text = 'apellido del usuario',
		error_messages = {'required': 'campo requerido'},
		)

	username = forms.CharField(
		widget = forms.TextInput(attrs={'class': 'form-control'}),
		label = 'Nombre de Usuario(*)',
		help_text = 'nombre de usuario',
		max_length = 30,
		error_messages = {'required': 'campo requerido', 'max_length': 'largo máximo de 30 caracteres'},
		)

	def __init__(self, *args, **kwargs):

		super(UserProfileForm, self).__init__(*args, **kwargs)

		if self.instance.pk is not None:

			self.fields['username'].initial 	= self.instance.user.username
			self.fields['first_name'].initial 	= self.instance.user.first_name
			self.fields['last_name'].initial 	= self.instance.user.last_name
			self.fields['email'].initial 		= self.instance.user.email

	class Meta:

		model 	= UserProfile
		fields 	= '__all__'
		exclude = ['creado_en', 'empresa', 'user', 'visible', 'proceso']

		widgets = {
			'cargo'			: forms.TextInput(attrs={'class': 'form-control'}),
			'ciudad'		: forms.TextInput(attrs={'class': 'form-control'}),
			'cliente'		: forms.Select(attrs={'class': 'form-control'}),
			'comuna'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'direccion'		: forms.TextInput(attrs={'class': 'form-control'}),
			'rut'			: forms.TextInput(attrs={'class': 'form-control format-rut'}),
			'tipo'			: forms.Select(attrs={'class': 'form-control'}),
		}

		labels = {
			'descripcion'	: 'Descripción',
			'direccion'		: 'Dirección',
			'rut'			: 'RUT (*)',
			'tipo' 			: 'Tipo de Usuario (*)',
		}

		help_texts = {
			'cargo'			: 'cargo del usuario',
			'ciudad'		: 'ciudad de usuario',
			'cliente'		: 'cliente asocioado',
			'comuna'		: 'comuna del usuario',
			'descripcion'	: 'descripción',
			'direccion'		: 'dirección del usuario',
			'rut'			: 'RUT de usuario',
			'tipo'			: 'tipo de usuario',
		}

		error_messages = {
			'cargo' 		: {'required': 'campo requerido'},
			'rut' 			: {'required': 'campo requerido'},
			'tipo' 			: {'required': 'campo requerido'},
		}

	def clean(self):

		cleaned_data 	= super(UserProfileForm, self).clean()
		tipo 			= cleaned_data.get('tipo')
		cliente 		= cleaned_data.get('cliente')
	
		if tipo is not None and tipo.id == 2 and cliente is None:

			self.add_error('cliente', 'campo requerido')


	def clean_rut(self):

		rut = self.cleaned_data['rut']

		if validate_rut(rut) is False:

			raise forms.ValidationError('rut invalido')

		return rut

	def clean_username(self):

		username = self.cleaned_data['username']

		if User.objects.filter(username=username).exists() and self.instance.pk is None:

			raise forms.ValidationError('nombre de usuario ya utilizado')

		return username

class UpdatePasswordForm(forms.Form):

	password_actual = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Actual (*)', help_text='Contraseña Actual del Usuario')
	password_nueva 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Nueva (*)', help_text='Nueva Contraseña del Usuario')
	password_copia 	= forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repetir Contraseña (*)', help_text='Repetición de Contraseña Nueva del Usuario')

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(UpdatePasswordForm, self).__init__(*args, **kwargs)

	def clean(self):

		cleaned_data 	= super(UpdatePasswordForm, self).clean()
		password_actual = cleaned_data.get("password_actual")
		authentication  = authenticate(username=self.user.username, password=password_actual)

		if authentication is None:
			msg = "Tu contraseña es incorrecta"
			self.add_error('password_actual', msg)

class UpdatePasswordAdminForm(forms.Form):

	password_nueva = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Nueva')
	password_copia = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repetir Contraseña')

class ConfiguracionOwnCloudForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):

		super(ConfiguracionOwnCloudForm, self).__init__(*args, **kwargs)

		if self.instance.pk is not None:

			self.fields['url'].initial 		= self.instance.url
			self.fields['usuario'].initial 	= self.instance.usuario
			self.fields['password'].initial = self.instance.password
		else:
			self.fields['url'].initial 		= ''
			self.fields['usuario'].initial 	= ''
			self.fields['password'].initial = ''

	class Meta:
		model 	= ConfiguracionOwnCloud
		fields 	= '__all__'
		exclude = ['user', 'creado_en']

		widgets = {
			'usuario'	: forms.TextInput(attrs={'class': 'form-control'}),
			'password' 	: forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete':'new-password'}),
			'url'		: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		labels = {
			'usuario' 	: 'Nombre de Usuario (*)',
			'password' 	: 'Contraseña (*)',
			'url' 		: 'Dirección OwnCloud (*)',
		}

		help_texts = {
			'usuario'	: 'Nombre de Usuario',
			'password'	: 'Contraseña',
			'url' 		: 'Dirección OwnCloud',
		}

		error_messages = {
			'usuario' 	: {'required': 'campo requerido'},
			'password' 	: {'required': 'campo requerido'},
			'url' 		: {'required': 'campo requerido'},
		}