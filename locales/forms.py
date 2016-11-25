# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User

from contrato.models import Contrato
from utilidades.views import NumberField
from accounts.models import UserProfile
from activos.models import *
from datetime import datetime

import datetime

from .models import *


class LocalTipoForm(forms.ModelForm):
	class Meta:
		model 	= Local_Tipo
		fields 	= ['nombre', 'descripcion']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'descripcion' 	: {'required': 'campo requerido'}
		}

		labels = {
			'descripcion' 	: 'Descripción',
		}

		help_texts={
			'nombre' 		: 'Nombre del Tipo de Local',
			'descripcion' 	: 'Descripción del Tipo de Local'
		}

class VentasForm(forms.ModelForm):

	fecha_inicio = forms.DateField(
									input_formats	= ['%d/%m/%Y'],
									widget			= forms.TextInput(attrs={'class': 'form-control format-date'}),
									label			= 'Fecha',
									error_messages	= {'required': 'campo requerido', 'invalid': 'campo invalido'},
								    initial			= datetime.datetime.today(),
									help_text		= 'Fecha Venta Diaria'
	)

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number', 'data-es-moneda': 'true', 'data-moneda': '', 'data-select': 'false'}), label='Valor', error_messages={'required': 'campo requerido'}, help_text='Valor de la Venta')

	def __init__(self, *args, **kwargs):

		request = kwargs.pop('request', None)

		super(VentasForm, self).__init__(*args, **kwargs)

		activos = Activo.objects.filter(empresa_id=request.user.userprofile.empresa, visible=True).values_list('id', flat=True)
		locales = Local.objects.filter(activo_id__in=activos, visible=True)

		self.fields['local'].queryset = locales

	class Meta:
		model 	= Venta
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'periodicidad', 'fecha_termino']

		widgets = {
			'local'		: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'local' 	: {'required': 'campo requerido'},
		}

		help_texts = {
			'local'			: 'local de la Venta',
		}

		labels = {
			'local'		: 'Local',
		}

class LocalForm(forms.ModelForm):

	metros_cuadrados 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number', 'data-es-moneda': 'false', 'data-moneda': '', 'data-select': 'false'}), error_messages={'required': 'campo requerido'}, help_text='Metros Cuadrados del Local')
	metros_lineales 	= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number', 'data-es-moneda': 'false', 'data-moneda': '', 'data-select': 'false'}), error_messages={'required': 'campo requerido'}, help_text='Metros Lineales del Local')
	metros_compartidos 	= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number', 'data-es-moneda': 'false', 'data-moneda': '', 'data-select': 'false'}), error_messages={'required': 'campo requerido'}, help_text='Metros Compartidos del Local')
	metros_bodega 		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number', 'data-es-moneda': 'false', 'data-moneda': '', 'data-select': 'false'}), error_messages={'required': 'campo requerido'}, help_text='Metros de Bodega del Local')

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		activo_id 		= kwargs.pop('activo_id', None)
		user 			= User.objects.get(pk=self.request.user.pk)
		profile 		= UserProfile.objects.get(user=user)

		super(LocalForm, self).__init__(*args, **kwargs)

		activo = Activo.objects.get(id=activo_id)

		self.fields['local_tipo'].queryset 		= Local_Tipo.objects.filter(empresa=profile.empresa, visible=True)
		self.fields['sector'].queryset 			= Sector.objects.filter(activo=activo)
		self.fields['nivel'].queryset 			= Nivel.objects.filter(activo=activo)
		self.fields['clasificaciones'].required = False

	class Meta:
		model 	= Local
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'activo']

		widgets = {
			'nombre'					: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'					: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'				: forms.TextInput(attrs={'class': 'form-control'}),
			'sector'					: forms.Select(attrs={'class': 'form-control'}),
			'nivel'						: forms.Select(attrs={'class': 'form-control'}),
			'local_tipo'				: forms.Select(attrs={'class': 'form-control'}),
			'clasificaciones'			: forms.SelectMultiple(),
		}

		error_messages = {
			'nombre' 			: {'required': 'campo requerido'},
			'codigo' 			: {'required': 'campo requerido'},
			'sector' 			: {'required': 'campo requerido'},
			'nivel' 			: {'required': 'campo requerido'},
			'local_tipo' 		: {'required': 'campo requerido'},
		}

		help_texts = {
			'nombre'			: 'Nombre de Local',
			'codigo'			: 'Código de Local',
			'descripcion'		: 'Descripción de Local',
			'sector'			: 'Sector del Local',
			'nivel'				: 'Nivel del Local',
			'local_tipo'		: 'Tipo de Local',
			'prorrateo'			: 'Prorrateo del Local'
		}

		labels = {
			'descripcion'	: 'Descripción',
			'codigo'		: 'Código',
			'local_tipo'	: 'Tipo de Local',
		}

class ElectricidadForm(forms.ModelForm):

	potencia 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), help_text='Potencia de Medidor Electricidad')
	potencia_presente 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), help_text='Potencia Presente Medidor Electricidad')
	potencia_fuera 		= NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), help_text='Potencia Fuera Medidor Electricidad')

	class Meta:
		model 	= Medidor_Electricidad
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'local']

		widgets = {
			'nombre'				: forms.TextInput(attrs={'class': 'form-control'}),
			'numero_rotulo'			: forms.TextInput(attrs={'class': 'form-control'}),
			'tarifa_electricidad'	: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'numero_rotulo' : {'required': 'campo requerido'},
		}

		help_texts = {
			'nombre'				: 'Nombre Medidor Electricidad',
			'numero_rotulo'			: 'Número de Rótulo de Electricidad',
			'tarifa_electricidad'	: 'Tarifa de Electricidad',
		}

		labels = {
			'numero_rotulo'			: 'Nº Rótulo',
			'tarifa_electricidad'	: 'Tarifa',
		}

class AguaForm(forms.ModelForm):

	potencia = NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), help_text='Potencia Medidor Agua')

	class Meta:
		model 	= Medidor_Agua
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'local']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'numero_rotulo'	: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'numero_rotulo' : {'required': 'campo requerido'},
		}

		help_texts = {
			'nombre'			: 'Nombre Medidor Agua',
			'numero_rotulo'		: 'Número Rótulo Agua',
		}

		labels = {
			'numero_rotulo'		: 'Nº Rótulo',
		}

class GasForm(forms.ModelForm):

	potencia = NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), help_text='Potencia Medidor Gas')

	class Meta:
		model 	= Medidor_Gas
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'local']

		widgets = {
			'nombre'			: forms.TextInput(attrs={'class': 'form-control'}),
			'numero_rotulo'		: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
			'numero_rotulo' : {'required': 'campo requerido'},
		}

		help_texts = {
			'nombre'			: 'Nombre Medidor Gas',
			'numero_rotulo'		: 'Número Rótulo Gas',
		}

		labels = {
			'numero_rotulo'		: 'Nº Rótulo',
		}

AguaFormSet 		= inlineformset_factory(Local, Medidor_Agua, form=AguaForm, extra=1, can_delete=True)
GasFormSet 			= inlineformset_factory(Local, Medidor_Gas, form=GasForm, extra=1, can_delete=True)
ElectricidadFormSet = inlineformset_factory(Local, Medidor_Electricidad, form=ElectricidadForm, extra=1, can_delete=True)

