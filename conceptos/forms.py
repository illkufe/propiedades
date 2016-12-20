# -*- coding: utf-8 -*-
from django import forms
from .models import Concepto, Concepto_Tipo

class ConceptoForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		empresa 		= self.request.user.userprofile.empresa

		super(ConceptoForm, self).__init__(*args, **kwargs)

		self.fields['concepto_tipo'].queryset = empresa.concepto_tipo_set.all()

	class Meta:
		model 	= Concepto
		fields 	= '__all__'
		exclude = ['empresa', 'creado_en', 'visible', 'configuracion']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'concepto_tipo' : forms.Select(attrs={'class': 'form-control'}),
			'iva'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'codigo' 		: {'required': 'campo requerido'},
			'concepto_tipo' : {'required': 'campo requerido'},
			'iva' 			: {'required': 'campo requerido'},
			'descripcion' 	: {'required': 'campo requerido'},
		}

		labels = {
			'codigo' 		: 'Código',
			'concepto_tipo' : 'Tipo de Concepto',
			'iva' 			: 'Con IVA',
			'descripcion' 	: 'Descripción',
		}

		help_texts = {
			'nombre'		: 'Nombre de Concepto',
			'codigo'		: 'Código de Concepto',
			'concepto_tipo' : 'Tipo de Concepto',
			'iva'			: 'Concepto tiene Asociado I.V.A.',
			'descripcion'	: 'Descripción de Concepto',
		}
