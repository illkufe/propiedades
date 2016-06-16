# -*- coding: utf-8 -*-
from django import forms
from .models import Lectura_Medidor, Lectura_Electricidad, Lectura_Agua, Lectura_Gas

class LecturaMedidorForm(forms.ModelForm):

	fecha = forms.DateField(input_formats=['%d/%m/%Y'], widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})

	class Meta:

		model 	= Lectura_Medidor
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'valor' 		: {'required': 'campo requerido.'},
		}

		labels = {
			'valor'			: 'Lectura',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'valor'			: '...',
			'imagen_file'	: '...',
		}

class LecturaElectricidadForm(forms.ModelForm):

	class Meta:

		model 	= Lectura_Electricidad
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'valor' 		: {'required': 'campo requerido.'},
		}

		labels = {
			'valor'			: 'Lectura',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'valor'			: '...',
			'imagen_file'	: '...',
		}

class LecturaAguaForm(forms.ModelForm):

	class Meta:

		model 	= Lectura_Agua
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'valor' 		: {'required': 'campo requerido.'},
		}

		labels = {
			'valor'			: 'Lectura',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'valor'			: '...',
			'imagen_file'	: '...',
		}

class LecturaGasForm(forms.ModelForm):

	class Meta:

		model 	= Lectura_Gas
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'valor' 		: {'required': 'campo requerido.'},
		}

		labels = {
			'valor'			: 'Lectura',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'valor'			: '...',
			'imagen_file'	: '...',
		}
