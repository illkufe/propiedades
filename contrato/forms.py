# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User

from accounts.models import UserProfile
from administrador.models import Cliente, Moneda
from activos.models import Activo
from locales.models import Local
from conceptos.models import Concepto

from .models import Contrato_Tipo, Contrato_Estado, Contrato, Arriendo, Arriendo_Detalle, Arriendo_Bodega, Arriendo_Variable, Gasto_Comun, Servicio_Basico, Cuota_Incorporacion, Fondo_Promocion

class ContratoTipoForm(forms.ModelForm):
	class Meta:
		model 	= Contrato_Tipo
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'empresa']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' : {'required': 'campo requerido'},
			'codigo' : {'required': 'campo requerido'},
		}

		labels = {
			'codigo'		: 'Código',
			'descripcion'	: 'Descripción',
		}

		help_texts = {
			'nombre'		: '...',
			'codigo'		: '...',
			'descripcion'	: '...',
		}

class ContratoForm(forms.ModelForm):

	fecha_contrato		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'})
	fecha_inicio		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'})
	fecha_termino		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'})
	fecha_habilitacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'})
	fecha_renovacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'})
	fecha_remodelacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False)
	fecha_plazo			= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False)
	fecha_aviso			= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, label='Fecha aviso comercial')
	conceptos 			= forms.ModelMultipleChoiceField(queryset=Concepto.objects.all(),required=False,widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}))

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		user 			= User.objects.get(pk=self.request.user.pk)
		profile 		= UserProfile.objects.get(user=user)
		activos 		= Activo.objects.filter(empresa_id=profile.empresa_id).values_list('id', flat=True)

		super(ContratoForm, self).__init__(*args, **kwargs)

		self.fields['locales'].queryset 		= Local.objects.filter(activo__in=activos, visible=True)
		self.fields['cliente'].queryset 		= Cliente.objects.filter(empresa=profile.empresa, visible=True)
		self.fields['contrato_tipo'].queryset 	= Contrato_Tipo.objects.filter(empresa=profile.empresa, visible=True)
		self.fields['contrato_estado'].required = False

	class Meta:
		model 	= Contrato
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'empresa']

		widgets = {
			'bodega'			: forms.CheckboxInput(attrs={'onclick': 'habilitar_input_metros(this)'}),
			'numero'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'meses'				: forms.NumberInput(attrs={'class': 'form-control'}),
			'dias_salida'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_bodega'		: forms.NumberInput(attrs={'class': 'form-control', 'disabled': 'disabled'}),
			'nombre_local'		: forms.TextInput(attrs={'class': 'form-control'}),
			'destino_comercial'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'contrato_tipo' 	: forms.Select(attrs={'class': 'form-control'}),
			'cliente'			: forms.Select(attrs={'class': 'form-control'}),
			'locales'			: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		error_messages = {
			'numero'			: {'required': 'campo requerido', 'invalid': 'campo invalido'},
			'nombre_local'		: {'required': 'campo requerido'},
			'destino_comercial'	: {'required': 'campo requerido'},
			'meses'				: {'required': 'campo requerido'},
			'dias_salida'		: {'required': 'campo requerido'},
			# 'fecha_salida'		: {'required': 'campo requerido'},
			'contrato_tipo'		: {'required': 'campo requerido'},
			'cliente'			: {'required': 'campo requerido'},
			'locales'			: {'required': 'campo requerido'},

		}

		labels = {
			'numero'			: 'Nº Contrato',
			'nombre_local'		: 'Marca Comercial',
			'fecha_renovacion'	: 'Fecha Renovación',
			'contrato_tipo' 	: 'Tipo de Contrato',
		}

		help_texts = {
			'numero'			: 'numero',			
			'nombre_local' 		: 'nombre local',
			'destino_comercial' : 'Destino Comercial',
		}

class InformacionForm(forms.ModelForm):

	class Meta:
		model 	= Contrato
		fields 	= ['id']

class ArriendoForm(forms.ModelForm):

	fecha_inicio = forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ArriendoForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['fecha_inicio'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')
			

	moneda = forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[2,3,4,6]), initial='6',widget=forms.Select(attrs={'class': 'form-control'}))

	class Meta:
		model 	= Arriendo
		fields 	= '__all__'
		exclude = ['visible']

		widgets = {
			'reajuste'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'por_meses'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'meses'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'fecha_inicio'	: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'meses'			: {'required': 'campo requerido'},
			'valor'			: {'required': 'campo requerido'},
			'moneda'		: {'required': 'campo requerido'},
			'fecha_inicio'	: {'required': 'campo requerido'},
		}

		labels = {
			'meses'			: 'Meses',
			'por_meses' 	: 'Por Meses',
			'fecha_inicio'	: 'Fecha Inicio',
		}

		help_texts = {
			'reajuste' 		: 'Reajuste',
			'por_meses'		: 'Por Meses',
			'meses' 		: 'Cada Cuantos',
			'valor' 		: 'Valor',
			'moneda' 		: 'Moneda',
			'fecha_inicio' 	: 'Fecha Inicio',
		}

class ArriendoDetalleForm(forms.ModelForm):


	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[3,5]),
		widget 	= forms.Select(attrs={'class': 'form-control'})
		)

	class Meta:
		model 	= Arriendo_Detalle
		fields 	= ['mes_inicio', 'mes_termino', 'valor', 'moneda', 'metro_cuadrado']

		widgets = {
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
		}

class ArriendoBodegaForm(forms.ModelForm):

	fecha_inicio = forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ArriendoBodegaForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['fecha_inicio'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')
			

	moneda = forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control'}))

	class Meta:
		model 	= Arriendo_Bodega
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'metro_cuadrado'	: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'periodicidad'		: forms.Select(attrs={'class': 'form-control'}),
			'valor'				: forms.NumberInput(attrs={'class': 'form-control'}),
			'fecha_inicio'		: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'meses'			: {'required': 'campo requerido'},
			'valor'			: {'required': 'campo requerido'},
			'moneda'		: {'required': 'campo requerido'},
			'fecha_inicio'	: {'required': 'campo requerido'},
		}

		labels = {
			'meses'			: 'Meses',
			'por_meses' 	: 'Por Meses',
			'fecha_inicio'	: 'Fecha Inicio',
		}

		help_texts = {
			'reajuste' 		: 'Reajuste',
			'por_meses'		: 'Por Meses',
			'meses' 		: 'Cada Cuantos',
			'valor' 		: 'Valor',
			'moneda' 		: 'Moneda',
			'fecha_inicio' 	: 'Fecha Inicio',
		}

class ArriendoVariableForm(forms.ModelForm):
	
	moneda = forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control'}))

	class Meta:
		model 	= Arriendo_Variable
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'anio_inicio'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'anio_termino'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'valor'			: {'required': 'campo requerido'},
			'moneda'		: {'required': 'campo requerido'},
		}

		labels = {
		}

		help_texts = {
			'valor' 		: 'valor',
			'moneda' 		: 'moneda',
		}

class GastoComunForm(forms.ModelForm):

	moneda = forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[4,5,6]), widget=forms.Select(attrs={'class': 'form-control moneda'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(GastoComunForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['local'].queryset = contrato.locales.all()

	class Meta:
		model 	= Gasto_Comun
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'local' 	: forms.Select(attrs={'class': 'form-control'}),
			'valor'		: forms.NumberInput(attrs={'class': 'form-control valor_no_prorrateo'}),
			'prorrateo'	: forms.CheckboxInput(attrs={'class': 'form-control prorrateo'}),
		}

		error_messages = {
			'valor'		: {'required': 'campo requerido'},
		}

		help_texts = {
			'valor' 	: 'valor',
			'prorrateo' : 'prorrateo',
		}

class ServicioBasicoForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ServicioBasicoForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['locales'].queryset = contrato.locales.all()

	class Meta:
		model 	= Servicio_Basico
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'locales'				: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
			'valor_electricidad' 	: forms.NumberInput(attrs={'class': 'form-control'}),
			'valor_agua' 			: forms.NumberInput(attrs={'class': 'form-control'}),
			'valor_gas' 			: forms.NumberInput(attrs={'class': 'form-control'}),
			}

		error_messages = {
			'valor_electricidad' 	: {'required': 'campo requerido'},
			'valor_agua' 			: {'required': 'campo requerido'},
			'valor_gas' 			: {'required': 'campo requerido'},
			}

		help_texts = {
			'valor_electricidad' 	: 'Valor Electricidad',
			'valor_agua' 			: 'Valor Agua',
			'valor_gas' 			: 'Valor Gas',
			}

class CuotaIncorporacionForm(forms.ModelForm):


	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(CuotaIncorporacionForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			pass
			self.fields['fecha'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')

	class Meta:
		model 	= Cuota_Incorporacion
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'valor'		: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'valor'		: {'required': 'campo requerido'},
		}

		help_texts = {
			'valor' 	: 'valor',
		}

class FondoPromocionForm(forms.ModelForm):

	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Cobrar desde')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(FondoPromocionForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['fecha'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')
			self.fields['concepto'].queryset = Concepto.objects.filter(id__in=[1])

	class Meta:
		model 	= Fondo_Promocion
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'periodicidad'	: forms.Select(attrs={'class': 'form-control'}),
			'concepto'		: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'valor'			: {'required': 'campo requerido'},
			'periodicidad'	: {'required': 'campo requerido'},
		}

		help_texts = {
			'valor' 		: 'valor',
			'periodicidad'	: 'periodicidad',
		}




ArriendoDetalleFormSet 		= inlineformset_factory(Arriendo, Arriendo_Detalle, form=ArriendoDetalleForm, extra=1, can_delete=True)
ArriendoVariableFormSet 	= inlineformset_factory(Contrato, Arriendo_Variable, form=ArriendoVariableForm, extra=1, can_delete=True)
ArriendoBodegaFormSet 		= inlineformset_factory(Contrato, Arriendo_Bodega, form=ArriendoBodegaForm, extra=1, can_delete=True)
GastoComunFormSet 			= inlineformset_factory(Contrato, Gasto_Comun, form=GastoComunForm, extra=1, can_delete=True)
ServicioBasicoFormSet 		= inlineformset_factory(Contrato, Servicio_Basico, form=ServicioBasicoForm, extra=1, can_delete=True)
CuotaIncorporacionFormet 	= inlineformset_factory(Contrato, Cuota_Incorporacion, form=CuotaIncorporacionForm, extra=1, can_delete=True)
FondoPromocionFormSet 		= inlineformset_factory(Contrato, Fondo_Promocion, form=FondoPromocionForm, extra=1, can_delete=True)


