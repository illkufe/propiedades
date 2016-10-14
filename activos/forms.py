# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group

from utilidades.views import NumberField
from accounts.models import UserProfile
from locales.models import *

from .models import *


class ActivoForm(forms.ModelForm):

	cabidad_terreno 		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	cabidad_construccion 	= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	avaluo_comercial 		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	contibuciones 			= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	precio_compra 			= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	valor_tasacion 			= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	tasacion_fiscal 		= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})
	fecha_firma_nomina 		= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	fecha_escritura 		= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	fecha_adquisicion 		= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	fecha_tasacion 			= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))

	class Meta:
		model 	= Activo
		fields 	= '__all__'
		exclude = ['empresa', 'creado_en', 'visible']

		widgets = {

			# identificacion Activo
			'nombre'				: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'				: forms.TextInput(attrs={'class': 'form-control'}),
			'tipo'					: forms.TextInput(attrs={'class': 'form-control'}),
			'direccion'				: forms.TextInput(attrs={'class': 'form-control'}),
			'comuna'				: forms.TextInput(attrs={'class': 'form-control'}),
			'ciudad'				: forms.TextInput(attrs={'class': 'form-control'}),

			# informacion legal
			'propietario'			: forms.TextInput(attrs={'class': 'form-control'}),
			'rut_propietario'		: forms.TextInput(attrs={'class': 'form-control format-rut'}),
			'rol_avaluo'			: forms.TextInput(attrs={'class': 'form-control'}),
			# inscripcion vigente
			'inscripcion'			: forms.TextInput(attrs={'class': 'form-control'}),
			'foja'					: forms.TextInput(attrs={'class': 'form-control'}),
			'numero_inscripcion'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'año'					: forms.NumberInput(attrs={'class': 'form-control'}),
			'conservador_bienes'	: forms.TextInput(attrs={'class': 'form-control'}),
			# datos de escritura
			'repertorio'			: forms.TextInput(attrs={'class': 'form-control'}),
			'notaria'				: forms.TextInput(attrs={'class': 'form-control'}),		
			'vendedor'				: forms.TextInput(attrs={'class': 'form-control'}),
			'rut_vendedor'			: forms.TextInput(attrs={'class': 'form-control format-rut'}),

			# datos economicos
			'tasacion_por'		: forms.TextInput(attrs={'class': 'form-control'}),
			'leasing'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'hipoteca'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 			: {'required': 'campo requerido'},
			'codigo' 			: {'required': 'campo requerido'},
			'propietario' 		: {'required': 'campo requerido'},
			'rut_propietario' 	: {'required': 'campo requerido'},
			'tasacion_fiscal' 	: {'required': 'campo requerido'},
		}

		labels = {		
			'codigo'		: 'Código',
			'inscripcion' 	: 'Inscripción Vigente',
			'vendedor'		: 'Propietario Anterior',
			'rut_vendedor'	: 'Rut Propietario Anterior',
		}

		help_texts = {
			'nombre'				: '...',
			'codigo' 				: '...',
			'tipo' 					: '...',
			'direccion' 			: '...',
			'comuna' 				: '...',
			'ciudad' 				: '...',
			'cabidad_terreno' 		: '...',
			'cabidad_construccion' 	: '...',
			'propietario' 			: '...',
			'rut_propietario' 		: '...',
			'rol_avaluo' 			: '...',
			'inscripcion' 			: '...',
			'vendedor' 				: '...',
			'rut_vendedor' 			: '...',
			'datos_escritura' 		: '...',
			'nomina_numero' 		: '...',
			'nomina_repertorio' 	: '...',
			'nomina_fojas' 			: '...',
			'servicio_nomina' 		: '...',
			'servicio_repertorio' 	: '...',
			'servicio_fojas' 		: '...',
			'fecha_adquisicion' 	: '...',
			'tasacion_fiscal' 		: '...',
			'avaluo_comercial' 		: '...',
			'contibuciones' 		: '...',
			'precio_compra' 		: '...',
			'valor_tasacion' 		: '...',
			'tasacion_por' 			: '...',
			'leasing' 				: '...',
			'hipoteca' 				: '...',
		}

class SectorForm(forms.ModelForm):

	class Meta:
		model 	= Sector
		fields 	= ['nombre', 'codigo']

		widgets = {
			'nombre' : forms.TextInput(attrs={'class': 'form-control'}),
			'codigo' : forms.TextInput(attrs={'class': 'form-control'}),
		}

class NivelForm(forms.ModelForm):

	class Meta:
		model 	= Nivel
		fields 	= ['nombre', 'codigo']

		widgets = {
			'nombre' : forms.TextInput(attrs={'class': 'form-control'}),
			'codigo' : forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' : {'required': 'campo requerido'},
			'codigo' : {'required': 'campo requerido'},
		}

class GastoMensualForm(forms.ModelForm):

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		user 			= User.objects.get(pk=self.request.user.pk)
		profile 		= UserProfile.objects.get(user=user)

		super(GastoMensualForm, self).__init__(*args, **kwargs)

		self.fields['activo'].queryset = Activo.objects.filter(empresa=profile.empresa, visible=True)

	class Meta:

		model 	= Gasto_Mensual
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user']

		widgets = {
			'activo' 	: forms.Select(attrs={'class': 'form-control'}),
			'mes'	 	: forms.Select(attrs={'class': 'form-control'}),
			'anio' 		: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'activo' 	: {'required': 'campo requerido'},
			'mes' 		: {'required': 'campo requerido'},
			'anio' 		: {'required': 'campo requerido'},
		}

		labels = {
			'anio'		: 'Año',
		}

		help_texts = {
			'anio'		: '...',
		}

class GastoServicioForm(forms.ModelForm):

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		user 			= User.objects.get(pk=self.request.user.pk)
		profile 		= UserProfile.objects.get(user=user)
		activos 		= Activo.objects.filter(empresa_id=profile.empresa_id).values_list('id', flat=True)

		super(GastoServicioForm, self).__init__(*args, **kwargs)

		self.fields['locales'].queryset = Local.objects.filter(activo__in=activos, visible=True)

	class Meta:

		model 	= Gasto_Servicio
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'mes'	 		: forms.Select(attrs={'class': 'form-control'}),
			'anio' 			: forms.NumberInput(attrs={'class': 'form-control'}),
			'imagen_file' 	: forms.FileInput(attrs={'class': 'file-format'}),
			'locales'		: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		error_messages = {
			'nombre' 	: {'required': 'campo requerido'},
			'mes' 		: {'required': 'campo requerido'},
			'anio' 		: {'required': 'campo requerido'},
			'locales' 	: {'required': 'campo requerido'},
		}

		labels = {
			'anio'			: 'Año',
			'imagen_file'	: 'Archivo',
		}

		help_texts = {
			'anio'			: '...',
		}

SectorFormSet 		= inlineformset_factory(Activo, Sector, form=SectorForm, extra=1, can_delete=True)
NivelFormSet 		= inlineformset_factory(Activo, Nivel, form=NivelForm, extra=1, can_delete=True)
