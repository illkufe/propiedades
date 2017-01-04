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
			'codigo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'concepto_tipo' : forms.Select(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'iva'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'proporcional'	: forms.CheckboxInput(attrs={'class': 'form-control'}),
		}

		labels = {
			'codigo' 		: 'Código (*)',
			'concepto_tipo' : 'Tipo de Concepto (*)',
			'descripcion' 	: 'Descripción',
			'iva' 			: 'Con iva',
			'nombre' 		: 'Nombre (*)',
			'proporcional' 	: 'Proporcional',
		}

		help_texts = {
			'codigo' 		: 'código del concepto, este código o abreviación será mostrado en algunas tablas para reducir el espacio',
			'concepto_tipo' : 'tipo de concepto',
			'descripcion' 	: 'descripción de concepto',
			'iva' 			: 'esta opción definie si el concepto tiene asociado i.v.a.',
			'nombre' 		: 'nombre de nombre',
			'proporcional' 	: 'esta opción define si el cálculo del concepto debe ser proporcional a los dias en caso de que sea necesario',
		}

		error_messages = {
			'codigo' 		: {'required': 'campo requerido'},
			'concepto_tipo' : {'required': 'campo requerido'},
			'nombre' 		: {'required': 'campo requerido'},
		}
