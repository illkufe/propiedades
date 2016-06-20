# -*- coding: utf-8 -*-
from django import forms
from .models import Lectura_Electricidad, Lectura_Agua, Lectura_Gas

class LecturaElectricidadForm(forms.ModelForm):

	class Meta:

		model 	= Lectura_Electricidad
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'medidor_electricidad'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'					: forms.NumberInput(attrs={'class': 'form-control'}),
			'mes'					: forms.Select(attrs={'class': 'form-control'}),
			'anio'					: forms.NumberInput(attrs={'class': 'form-control'}),
			'imagen_file'			: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'medidor_electricidad' 	: {'required': 'campo requerido.'},
			'valor' 				: {'required': 'campo requerido.'},
			'mes' 					: {'required': 'campo requerido.'},
			'anio' 					: {'required': 'campo requerido.'},
		}

		labels = {
			'valor'			: 'Lectura',
			'anio'			: 'Año',
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
			'medidor_agua'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'anio'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'medidor_agua' 	: {'required': 'campo requerido.'},
			'valor' 		: {'required': 'campo requerido.'},
			'mes' 			: {'required': 'campo requerido.'},
			'anio' 			: {'required': 'campo requerido.'},
		}

		labels = {
			'valor'			: 'Lectura',
			'anio'			: 'Año',
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
			'medidor_gas'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'anio'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'medidor_gas' 	: {'required': 'campo requerido.'},
			'valor' 		: {'required': 'campo requerido.'},
			'mes' 			: {'required': 'campo requerido.'},
			'anio' 			: {'required': 'campo requerido.'},
		}

		labels = {
			'valor'			: 'Lectura',
			'anio'			: 'Año',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'valor'			: '...',
			'imagen_file'	: '...',
		}
