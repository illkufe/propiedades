# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from utilidades.views import NumberField, primer_dia, ultimo_dia

from accounts.models import UserProfile
from administrador.models import Cliente
from activos.models import Activo
from locales.models import Local
from conceptos.models import Concepto
from utilidades.models import Moneda

from datetime import datetime, timedelta

from .models import *

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
			'nombre' 		: {'required': 'campo requerido'},
		}

		labels = {
			'codigo'		: 'Código',
			'descripcion'	: 'Descripción',
		}

		help_texts = {
			'nombre' 		: 'nombre del tipo de contrato',
			'codigo' 		: 'código del tipo de contrato',
			'descripcion' 	: 'descripción del tipo de contrato',
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
	metros_bodega 		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number', 'disabled': 'disabled'}))

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		activos 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)

		super(ContratoForm, self).__init__(*args, **kwargs)	

		if self.instance.pk is not None:
			locales_id = Contrato.objects.values_list('locales', flat=True).filter(estado=4, visible=True).exclude(id=self.instance.pk)
		else:
			locales_id = Contrato.objects.values_list('locales', flat=True).filter(estado=4, visible=True)

		self.fields['locales'].queryset 	= Local.objects.filter(activo__in=activos, visible=True).exclude(id__in=locales_id)
		self.fields['conceptos'].queryset 	= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		self.fields['cliente'].queryset 	= Cliente.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		self.fields['tipo'].queryset 		= Contrato_Tipo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		self.fields['estado'].required 		= False

	class Meta:
		model 	= Contrato
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'empresa']

		widgets = {
			'bodega'			: forms.CheckboxInput(attrs={'onclick': 'habilitar_input_metros(this)'}),
			'numero'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'meses'				: forms.NumberInput(attrs={'class': 'form-control'}),
			'dias_salida'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'nombre_local'		: forms.TextInput(attrs={'class': 'form-control'}),
			'destino_comercial'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'tipo' 				: forms.Select(attrs={'class': 'form-control'}),
			'cliente'			: forms.Select(attrs={'class': 'form-control'}),
			'locales'			: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
			'conceptos'			: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		error_messages = {
			'numero'			: {'required': 'campo requerido', 'invalid': 'campo invalido'},
			'nombre_local'		: {'required': 'campo requerido'},
			'destino_comercial'	: {'required': 'campo requerido'},
			'meses'				: {'required': 'campo requerido'},
			'dias_salida'		: {'required': 'campo requerido'},
			'tipo'				: {'required': 'campo requerido'},
			'cliente'			: {'required': 'campo requerido'},
			'locales'			: {'required': 'campo requerido'},
			'conceptos'			: {'required': 'campo requerido'},
		}

		labels = {
			'numero'			: 'Nº Contrato',
			'nombre_local'		: 'Marca Comercial',
			'fecha_renovacion'	: 'Fecha Renovación',
			'tipo' 				: 'Tipo de Contrato',
		}

		help_texts = {
			'numero'			: 'numero',
			'nombre_local' 		: 'nombre local',
			'destino_comercial' : 'Destino Comercial',
		}

class GarantiaForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control'}))

	class Meta:
		model 	= Garantia
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'nombre' 	: forms.TextInput(attrs={'class': 'form-control'}),
		}

class MultaTipoForm(forms.ModelForm):
	
	class Meta:

		model 	= Multa_Tipo
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'empresa']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo requerido'},
		}

		labels = {
			'codigo' 		: 'Código',
			'descripcion' 	: 'Descripción',
		}

		help_texts = {
			'nombre' 		: 'nombre del tipo de multa',
			'codigo' 		: 'código del tipo de multa',
			'descripcion' 	: 'descripción del tipo de multa',
		}

class MultaForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), label='Valor Multa', error_messages={'required': 'campo requerido'})
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido'})

	def __init__(self, *args, **kwargs):

		self.request = kwargs.pop('request')

		super(MultaForm, self).__init__(*args, **kwargs)

		self.fields['multa_tipo'].queryset 	= Multa_Tipo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		self.fields['contrato'].queryset 	= Contrato.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

	class Meta:

		model 	= Multa
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'empresa']

		widgets = {
			'mes'	 		: forms.Select(attrs={'class': 'form-control'}),
			'anio' 			: forms.NumberInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'multa_tipo'	: forms.Select(attrs={'class': 'form-control'}),
			'contrato'		: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'mes' 			: {'required': 'campo requerido'},
			'anio' 			: {'required': 'campo requerido'},
			'contrato' 		: {'required': 'campo requerido'},
			'multa_tipo' 	: {'required': 'campo requerido'},
			'moneda' 		: {'required': 'campo requerido'},
		}

		labels = {
			'anio'			: 'Año',
			'multa_tipo' 	: 'Tipo de Multa',
		}

		help_texts = {
			'mes'			: '',
			'anio'			: '',
			'contrato'		: '',
			'multa_tipo' 	: '',
		}

class InformacionForm(forms.ModelForm):

	class Meta:
		model 	= Contrato
		fields 	= ['id']

class ArriendoForm(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[2,3,4,6]), initial='6',widget=forms.Select(attrs={'class': 'form-control'}))
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ArriendoForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['fecha_inicio'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')

	class Meta:
		model 	= Arriendo
		fields 	= '__all__'
		exclude = ['visible', 'concepto']

		widgets = {
			'reajuste'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'por_meses'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'meses'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'fecha_inicio'	: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'meses'			: {'required': 'campo requerido'},
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
			'moneda' 		: 'Moneda',
			'fecha_inicio' 	: 'Fecha Inicio',
		}

class ArriendoDetalleForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control'}))

	class Meta:
		model 	= Arriendo_Detalle
		fields 	= ['mes_inicio', 'mes_termino', 'valor', 'metro_cuadrado', 'moneda']

		widgets = {
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
		}

class ArriendoBodegaForm(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control'}))
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ArriendoBodegaForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['fecha_inicio'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')

	class Meta:
		model 	= Arriendo_Bodega
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'metro_cuadrado'	: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'periodicidad'		: forms.Select(attrs={'class': 'form-control'}),
			'fecha_inicio'		: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'meses'			: {'required': 'campo requerido'},
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
			'moneda' 		: 'Moneda',
			'fecha_inicio' 	: 'Fecha Inicio',
		}

class ArriendoVariableForm(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	moneda 			= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control'}))
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False)
	fecha_termino 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False)

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ArriendoVariableForm, self).__init__(*args, **kwargs)
		self.fields['arriendo_minimo'].queryset = Concepto.objects.filter(concepto_tipo_id=1, empresa=contrato.empresa)
	
	class Meta:
		model 	= Arriendo_Variable
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {		
			'mes_inicio'		: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'		: forms.Select(attrs={'class': 'form-control'}),
			'anio_inicio'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'anio_termino'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'relacion'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'arriendo_minimo' 	: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'moneda'		: {'required': 'campo requerido'},
		}

		labels = {
			'anio_inicio' 	: 'Año inicio',
			'anio_termino' 	: 'Año término',
		}

		help_texts = {
			'moneda' 		: 'moneda',
		}

	def clean_fecha_inicio(self):

		mes_inicio 	= str(self.cleaned_data.get("mes_inicio")).zfill(2)
		anio_inicio = str(self.cleaned_data.get("anio_inicio"))

		return datetime.strptime('01/'+mes_inicio+'/'+anio_inicio+'', "%d/%m/%Y").date()

	def clean_fecha_termino(self):

		mes_termino 	= str(self.cleaned_data.get("mes_termino")).zfill(2)
		anio_termino 	= str(self.cleaned_data.get("anio_termino"))

		return ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+anio_termino+'', "%d/%m/%Y"))

class GastoComunForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[4,5,6]), widget=forms.Select(attrs={'class': 'form-control moneda'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(GastoComunForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			print ('gasto comunnnnnnnn')
			self.fields['local'].queryset = contrato.locales.all()
		else:
			print ('no tengo contrato')

	class Meta:
		model 	= Gasto_Comun
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'local' 	: forms.Select(attrs={'class': 'form-control'}),
			'prorrateo'	: forms.CheckboxInput(attrs={'class': 'form-control prorrateo'}),
		}

		error_messages = {
			'local'		: {'required': 'campo requerido'},
		}

		help_texts = {
			'prorrateo' : 'prorrateo',
		}

class ServicioBasicoForm(forms.ModelForm):

	valor_electricidad 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	valor_agua 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	valor_gas 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ServicioBasicoForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['locales'].queryset = contrato.locales.all()

	class Meta:
		model 	= Servicio_Basico
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'locales'	: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
			}

		error_messages = {
			'locales' 	: {'required': 'campo requerido'},		
			}

		help_texts = {
			'locales' 	: 'Locales',
			}

class CuotaIncorporacionForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
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
		exclude = ['visible', 'creado_en', 'concepto']

class FondoPromocionForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Cobrar desde')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control'}))

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(FondoPromocionForm, self).__init__(*args, **kwargs)

		self.fields['vinculo'].queryset = Concepto.objects.filter(concepto_tipo_id=1)

		if contrato is not None:
			self.fields['fecha'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')
			

	class Meta:
		model 	= Fondo_Promocion
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'periodicidad'	: forms.Select(attrs={'class': 'form-control'}),
			'vinculo'		: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'periodicidad'	: {'required': 'campo requerido'},
		}

		help_texts = {
			'periodicidad'	: 'periodicidad',
		}


ArriendoVariableFormSet 	= inlineformset_factory(Contrato, Arriendo_Variable, form=ArriendoVariableForm, extra=1, can_delete=True)
GastoComunFormSet 			= inlineformset_factory(Contrato, Gasto_Comun, form=GastoComunForm, extra=1, can_delete=True)
ServicioBasicoFormSet 		= inlineformset_factory(Contrato, Servicio_Basico, form=ServicioBasicoForm, extra=1, can_delete=True)
CuotaIncorporacionFormet 	= inlineformset_factory(Contrato, Cuota_Incorporacion, form=CuotaIncorporacionForm, extra=1, can_delete=True)
ArriendoBodegaFormSet 		= inlineformset_factory(Contrato, Arriendo_Bodega, form=ArriendoBodegaForm, extra=1, can_delete=True)
GarantiaFormSet 			= inlineformset_factory(Contrato, Garantia, form=GarantiaForm, extra=1, can_delete=True)
ArriendoDetalleFormSet 		= inlineformset_factory(Arriendo, Arriendo_Detalle, form=ArriendoDetalleForm, extra=1, can_delete=True)
FondoPromocionFormSet 		= inlineformset_factory(Contrato, Fondo_Promocion, form=FondoPromocionForm, extra=1, can_delete=True)


