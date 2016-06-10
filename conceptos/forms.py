# -*- coding: utf-8 -*-
from django import forms
from .models import Concepto

class ConceptoForm(forms.ModelForm):
	class Meta:
		model 	= Concepto
		fields 	= '__all__'
		exclude = ['empresa', 'creado_en', 'visible']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'orden'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'moneda'		: forms.Select(attrs={'class': 'form-control'}),
			'concepto_tipo'	: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'codigo' 		: {'required': 'campo requerido'},
			'orden' 		: {'required': 'campo requerido'},
			'moneda' 		: {'required': 'campo requerido'},
			'concepto_tipo' : {'required': 'campo requerido'},
		}

		labels = {
			'codigo'		: 'Código',
			'descripcion'	: 'Descripción',
			'concepto_tipo'	: 'Tipo de Concepto',
		}

		help_texts = {
			'nombre'		: '...',
			'codigo'		: '...',
			'orden'			: '...',
			'descripcion'	: '...',
			'moneda'		: '...',
			'concepto_tipo'	: '...',
		}
