# -*- coding: utf-8 -*-
from django import forms
from .models import Alerta

class AlertaForm(forms.ModelForm):

	fecha = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'],widget=forms.TextInput(attrs={'class': 'form-control format-datetime'}), error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'})

	class Meta:
		model 	= Alerta
		fields 	= '__all__'
		exclude = ['creador', 'creado_en', 'visible']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'miembros'		: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'descripcion' 	: {'required': 'campo requerido'},
			'miembros' 		: {'required': 'campo requerido'},
		}

		labels = {
			'nombre'		: 'Nombre',
			'descripcion'	: 'Descripción',
			'miembros'		: 'Miembros',
		}

		help_texts = {
			'nombre'		: '...',
			'descripcion'	: '...',
			'miembros'		: '...',
		}
