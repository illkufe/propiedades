# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory

from administrador.models import Cliente
from activos.models import Activo
from locales.models import Local
from conceptos.models import Concepto
from utilidades.models import Moneda

from .models import *

from utilidades.views import *
from datetime import datetime, timedelta

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
			'nombre' 		: 'Nombre del Tipo de Contrato',
			'codigo' 		: 'Código del Tipo de Contrato',
			'descripcion' 	: 'Descripción del Tipo de Contrato',
		}

class ContratoForm(forms.ModelForm):

	fecha_contrato		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Contrato', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha de Contrato')
	fecha_inicio		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Inicio de Contrato', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha de Inicio de Contrato')
	fecha_termino		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Término de Contrato', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha de Término de Contrato')
	fecha_inicio_renta	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Inicio de Renta',error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha de Inicio de Renta')
	fecha_entrega		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Entrega Local', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha de Entrega de Local')
	fecha_habilitacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Habilitación', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha de Habilitación de Contrato')
	fecha_renovacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Renovación', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha de Renovación de Contrato')
	
	metros_bodega 		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number', 'disabled': 'disabled'}), help_text='Metros Cuadrados de la Bodega')

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
			'bodega'				: forms.CheckboxInput(attrs={'onclick': 'habilitar_input_metros(this)'}),
			'numero'				: forms.NumberInput(attrs={'class': 'form-control'}),
			'meses_contrato'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'meses_aviso_comercial'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'meses_remodelacion'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'dias_salida'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'nombre_local'			: forms.TextInput(attrs={'class': 'form-control'}),
			'destino_comercial'		: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'tipo' 					: forms.Select(attrs={'class': 'form-control'}),
			'cliente'				: forms.Select(attrs={'class': 'form-control'}),
			'locales'				: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
			'conceptos'				: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		
		labels = {
			'numero'				: 'Nº Contrato',
			'nombre_local'			: 'Marca Comercial',
			'fecha_renovacion'		: 'Fecha Renovación',
			'meses_contrato'		: 'Meses de Arriendo',
			'meses_aviso_comercial'	: 'Meses Aviso Comercial',
			'meses_remodelacion'	: 'Meses de Remodelación',
			'tipo' 					: 'Tipo de Contrato',
			'dias_salida'			: 'Meses aviso comercial'
		}

		error_messages = {
			'numero'				: {'required': 'campo requerido', 'invalid': 'campo invalido'},
			'nombre_local'			: {'required': 'campo requerido'},
			'destino_comercial'		: {'required': 'campo requerido'},
			'meses_contrato'		: {'required': 'campo requerido'},
			'meses_aviso_comercial'	: {'required': 'campo requerido'},
			'meses_remodelacion'	: {'required': 'campo requerido'},
			'tipo'					: {'required': 'campo requerido'},
			'cliente'				: {'required': 'campo requerido'},
			'locales'				: {'required': 'campo requerido'},
			'conceptos'				: {'required': 'campo requerido'},
		}

		help_texts = {
			'bodega'				: 'Local Presenta Bodega',
			'numero'				: 'Número de Contrato',
			'meses_contrato'		: 'Cantidad de Meses de Arriendo Local',
			'meses_aviso_comercial'	: 'Cantidad de Meses de Aviso Comercial',
			'meses_remodelacion'	: 'Cantidad de Meses Para Remodelación Local',
			'dias_salida'			: 'Cantidad de Meses de Aviso Comercial',
			'nombre_local'			: 'Marcar Comercial Cliente',
			'destino_comercial'		: 'Destino Comercial Contrato',
			'tipo' 					: 'Tipo de Contrato a Generar',
			'cliente'				: 'Cliente',
			'locales'				: 'Locales Asociados a Contrato',
			'conceptos'				: 'Conceptos Asociados a Contrato',
		}

class GarantiaForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de la Garantia')
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Asociada al Valor de la Garantia')

	class Meta:
		model 	= Garantia
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'nombre' 	: forms.TextInput(attrs={'class': 'form-control'}),
		}

		help_texts = {
			'nombre' : 'Nombre de la Garantia'
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
			'nombre' 		: 'Nombre del Tipo de Multa',
			'codigo' 		: 'Código del Tipo de Multa',
			'descripcion' 	: 'Descripción del Tipo de Multa',
		}

class MultaForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), label='Valor Multa', error_messages={'required': 'campo requerido'}, help_text='Valor de la Multa')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda_multa(this)'}), error_messages={'required': 'campo requerido'}, help_text='Tipo de Moneda Asociado a la Multa')

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
			'mes'			: 'Mes donde se aplica la Multa',
			'anio'			: 'Año donde se aplica la Multa',
			'contrato'		: 'Contrado Asociado',
			'multa_tipo' 	: 'Tipo de Multa',
			'descripcion'	: 'Descripción Asociada a la Multa'
		}

class InformacionForm(forms.ModelForm):

	class Meta:
		model 	= Contrato
		fields 	= ['id']

class ArriendoForm(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Reajuste')
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[2,3,4,6]), initial='6',widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Tipo de Moneda del Reajuste')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), help_text='Fecha Inicio de Aplicación del Reajuste')

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
			'reajuste' 		: 'Aplica Reajuste',
			'por_meses'		: 'Reajuste Por Meses',
			'meses' 		: 'Cada Cuantos Meses Aplica Reajuste',
			'moneda' 		: 'Tipo de Moneda del Reajuste',
			'fecha_inicio' 	: 'Fecha Inicio de Aplicación del Reajuste',
		}

class ArriendoDetalleForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor Asociado al Arriendo')
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Tipo de Moneda Aplicado al Arriendo')

	class Meta:
		model 	= Arriendo_Detalle
		fields 	= ['mes_inicio', 'mes_termino', 'valor', 'metro_cuadrado', 'moneda']

		widgets = {
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
		}

		help_texts ={
			'mes_inicio'	: 'Mes de Inicio del Arriendo',
			'mes_termino'	: 'Mes de Término del Arriendo',
			'metro_cuadrado': 'Valor Arriendo Aplicado al Metro Cuadrado'
		}

class ArriendoBodegaForm(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Arriendo Bodega')
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda' ,'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Valor del Arriendo')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), help_text='Fecha de Inicio Arriendo Bodega')

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
			'metro_cuadrado'	: {'required': 'campo requerido'},
			'periodicidad'		: {'required': 'campo requerido'},
			'fecha_inicio'		: {'required': 'campo requerido'},
		}

		labels = {

		}

		help_texts = {
			'periodicidad' 		: 'Periodicidad del Arriendo de Bodega',
			'metro_cuadrado'	: 'Valor Aplicado por Metro Cuadrado',
		}

class ArriendoVariableForm(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Arriendo Variable')
	moneda 			= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Valor de Arriendo variable')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False, help_text='Fecha de Inicio de Arriendo Variable')
	fecha_termino 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False, help_text='Fecha de Término de Arriendo Variable')

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
			'dia_reajuste'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'relacion'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'arriendo_minimo' 	: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'moneda'		: {'required': 'campo requerido'},
		}

		labels = {
			'anio_inicio' 	: 'Año inicio',
			'mes_termino'	: 'Mes término',
			'anio_termino' 	: 'Año término',
			'dia_reajuste'  : 'Día reajuste'
		}

		help_texts = {
			'mes_inicio'		: 'Mes de Inicio Arriendo Variable',
			'mes_termino'		: 'Mes de Término Arriendo Variable',
			'anio_inicio'		: 'Año de Inicio Arriendo Variable',
			'anio_termino'		: 'Año de Término Arriendo Variable',
			'dia_reajuste'		: '',
			'relacion'			: '',
			'arriendo_minimo' 	: '',
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

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Gasto Común')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Gasto Común')

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(GastoComunForm, self).__init__(*args, **kwargs)

	class Meta:
		model 	= Gasto_Comun
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'tipo' 				: forms.Select(attrs={'class': 'form-control'}),
			'metros_cuadrado' 	: forms.CheckboxInput(attrs={'class': 'form-control'}),
		}

		labels = {
			'metros_cuadrado' 	: 'Valor x m²',
		}

		error_messages = {
			'tipo'				: {'required': 'campo requerido'},
			'metros_cuadrado' 	: {'required': 'campo requerido'},
		}

		help_texts = {
			'tipo' 				: 'Tipo de Gasto Común',
			'metros_cuadrado'	: 'Valor Aplicado por Metro Cuadrado'
		}

class ServicioBasicoForm(forms.ModelForm):

	valor_electricidad 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor Servicio Electricidad')
	valor_agua 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor Servicio Agua')
	valor_gas 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor Servicio Gas')

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
			'locales' 	: 'Locales donde Aplican Servicio Básico',
			}

class CuotaIncorporacionForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Cuota de Incorporación')
	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), help_text='Fecha')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada a la Cuota de Incorporación')

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


		help_texts = {
			'metro_cuadrado' : 'Valor Aplicado por Metro Cuadrado'
		}

class FondoPromocionForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Fondo Promoción')
	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Cobrar desde', help_text='Fecha de Inicio del Cobro Fondo Promoción')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Fondo Promoción')

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
			'periodicidad'	: 'Periodicidad de Fondo Promoción',
			'vinculo'		: ''
		}

class GastoAsociadoForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor del Gasto Asociado')
	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Cobrar a partir de:', help_text='Fecha de Inicio de Cobro del Gasto Asociado')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control moneda','onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Gasto Asociado')

	def __init__(self, *args, **kwargs):

		contrato = kwargs.pop('contrato', None)

		super(GastoAsociadoForm, self).__init__(*args, **kwargs)

		self.fields['vinculo'].queryset = Concepto.objects.filter(empresa=contrato.empresa).exclude(concepto_tipo_id=10)

		# if contrato is not None:
		# 	self.fields['fecha'].initial = contrato.fecha_inicio.strftime('%d/%m/%Y')
			

	class Meta:
		model 	= Gasto_Asociado
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
			'periodicidad'	: 'Periodicidad del Gasto Asociado',
			'vinculo'		: ''
		}

# propuesta
class PropuestaForm(forms.ModelForm):

	fecha_contrato		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False, error_messages={'invalid': 'campo invalido'}, label='Fecha de Contrato', help_text='Fecha de Contrato')
	fecha_inicio		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False, error_messages={'invalid': 'campo invalido'}, label='Fecha de Inicio de Contrato', help_text='Fecha de Inicio de Contrato')
	fecha_termino		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False, error_messages={'invalid': 'campo invalido'}, label='Fecha de Término de Contrato', help_text='Fecha de Término de Contrato')
	fecha_inicio_renta	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False, error_messages={'invalid': 'campo invalido'}, label='Fecha de Incio de Renta', help_text='Fecha de Inicio de Renta')
	fecha_entrega		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False, error_messages={'invalid': 'campo invalido'}, label='Fecha de Entrega Local', help_text='Fecha de Entrega de Local')
	fecha_habilitacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False, error_messages={'invalid': 'campo invalido'}, label='Fecha de Habilitación', help_text='Fecha de Habilitación de Contrato')
	fecha_renovacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), required=False, error_messages={'invalid': 'campo invalido'}, label='Fecha de Renovación', help_text='Fecha de Renovación de Contrato')

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		activos 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)

		super(PropuestaForm, self).__init__(*args, **kwargs)

		locales_id = Contrato.objects.values_list('locales', flat=True).filter(estado=4, visible=True)

		self.fields['locales'].queryset = Local.objects.filter(activo__in=activos, visible=True).exclude(id__in=locales_id)
		self.fields['cliente'].queryset = Cliente.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		self.fields['tipo'].queryset 	= Contrato_Tipo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

	class Meta:
		model 	= Propuesta_Version
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'user', 'empresa', 'propuesta']

		widgets = {
			'numero'				: forms.NumberInput(attrs={'class': 'form-control'}),
			'nombre_local'			: forms.TextInput(attrs={'class': 'form-control'}),
			'destino_comercial'		: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'meses_contrato'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'meses_aviso_comercial' : forms.NumberInput(attrs={'class': 'form-control'}),
			'meses_remodelacion' 	: forms.NumberInput(attrs={'class': 'form-control'}),
			'arriendo_minimo'		: forms.CheckboxInput(attrs={'class': 'form-control concepto-activo', 'data-concepto':'arriendo_minimo_detalle'}),
			'arriendo_variable'		: forms.CheckboxInput(attrs={'class': 'form-control concepto-activo', 'data-concepto':'arriendo_variable'}),
			'arriendo_bodega'		: forms.CheckboxInput(attrs={'class': 'form-control concepto-activo', 'data-concepto':'arriendo_bodega'}),
			'cuota_incorporacion'	: forms.CheckboxInput(attrs={'class': 'form-control concepto-activo', 'data-concepto':'cuota_incorporacion'}),
			'fondo_promocion'		: forms.CheckboxInput(attrs={'class': 'form-control concepto-activo', 'data-concepto':'fondo_promocion'}),
			'gasto_comun'			: forms.CheckboxInput(attrs={'class': 'form-control concepto-activo', 'data-concepto':'gasto_comun'}),
			'tipo' 					: forms.Select(attrs={'class': 'form-control'}),
			'cliente'				: forms.Select(attrs={'class': 'form-control'}),
			'locales'				: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
			'conceptos'				: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		labels = {
			'numero'				: 'Número de Contrato',
			'nombre_local'			: 'Marca Comercial',
			'destino_comercial'		: 'Destino Comercial',
			'meses_contrato'		: 'Meses de Arriendo',
			'meses_aviso_comercial'	: 'Meses Aviso Comercial',
			'meses_remodelacion'	: 'Meses de Remodelación',
			'arriendo_minimo'		: 'Concepto Arriendo Mínimo',
			'arriendo_variable'		: 'Concepto Arriendo Variable',
			'arriendo_bodega'		: 'Concepto Arriendo Bodega',
			'cuota_incorporacion'	: 'Concepto Cuota de Incorporación',
			'fondo_promocion'		: 'Concepto Fondo de Promoción',
			'gasto_comun'			: 'Concepto Gasto Común',
			'tipo'					: 'Tipo de Contrato',
			'cliente'				: 'Cliente',
			'locales'				: 'Locales',
		}

		help_texts = {
			'bodega'				: 'Local Presenta Bodega',
			'numero'				: 'Número de Contrato',
			'meses_contrato'		: 'Cantidad de Meses de Arriendo Local',
			'meses_aviso_comercial'	: 'Cantidad de Meses de Aviso Comercial',
			'meses_remodelacion'	: 'Cantidad de Meses Para Remodelación Local',
			'dias_salida'			: 'Cantidad de Meses de Aviso Comercial',
			'nombre_local'			: 'Marcar Comercial Cliente',
			'destino_comercial'		: 'Destino Comercial Contrato',
			'tipo' 					: 'Tipo de Contrato a Generar',
			'cliente'				: 'Cliente',
			'locales'				: 'Locales Asociados a Contrato',
			'conceptos'				: 'Conceptos Asociados a Contrato',
		}

		error_messages = {
			'numero'			: {'required': 'campo requerido', 'invalid': 'campo invalido'},
			'nombre_local'		: {'required': 'campo requerido'},
			'tipo'				: {'required': 'campo requerido'},
			'cliente'			: {'required': 'campo requerido'},
			'locales'			: {'required': 'campo requerido'},
			'conceptos'			: {'required': 'campo requerido'},
		}

class FormPropuestaGarantia(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de la Garantia')
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Asociada al Valor de la Garantia')

	class Meta:
		model 	= Propuesta_Garantia
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'nombre' 	: forms.TextInput(attrs={'class': 'form-control'}),
		}

		help_texts = {
			'nombre' : 'Nombre de la Garantia'
		}

class FormPropuestaArriendo(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Reajuste')
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[2,3,4,6]), widget=forms.Select(attrs={'class': 'form-control moneda', 'onchange': 'cambio_format_moneda(this)'}), help_text='Tipo de Moneda del Reajuste')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), help_text='Fecha Inicio de Aplicación del Reajuste')

	class Meta:
		model 	= Propuesta_Arriendo_Minimo
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

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
			'reajuste' 		: 'Aplica Reajuste',
			'por_meses'		: 'Reajuste Por Meses',
			'meses' 		: 'Cada Cuantos Meses Aplica Reajuste',
			'moneda' 		: 'Tipo de Moneda del Reajuste',
			'fecha_inicio' 	: 'Fecha Inicio de Aplicación del Reajuste',
		}

class FormPropuestaArriendoDetalle(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number config-moneda'}), help_text='Valor Asociado al Arriendo')
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'onchange': 'cambio_format_moneda(this)'}), help_text='Tipo de Moneda Aplicado al Arriendo')

	class Meta:
		model 	= Propuesta_Arriendo_Minimo_Detalle
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'metros' 		: forms.CheckboxInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'mes_inicio' 	: {'required': 'campo requerido'},
			'mes_termino' 	: {'required': 'campo requerido'},
			'metros' 		: {'required': 'campo requerido'},
		}

		labels = {
			'mes_inicio' 	: 'Año inicio',
			'mes_termino' 	: 'Año término',
			'metros' 		: 'Valor x m²',
		}

		help_texts = {
			'mes_inicio'	: 'Mes de Inicio del Arriendo',
			'mes_termino'	: 'Mes de Término del Arriendo',
			'metro_cuadrado': 'Valor Arriendo Aplicado al Metro Cuadrado'
		}

	def clean_fecha_inicio(self):

		mes_inicio 	= str(self.cleaned_data.get("mes_inicio")).zfill(2)
		anio_inicio = str(self.cleaned_data.get("anio_inicio"))

		return datetime.strptime('01/'+mes_inicio+'/'+anio_inicio+'', "%d/%m/%Y").date()

	def clean_fecha_termino(self):

		mes_termino 	= str(self.cleaned_data.get("mes_termino")).zfill(2)
		anio_termino 	= str(self.cleaned_data.get("anio_termino"))

		return ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+anio_termino+'', "%d/%m/%Y"))

class FormPropuestaVariable(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Arriendo Variable')
	moneda 			= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control moneda', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Valor de Arriendo variable')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False, help_text='Fecha de Inicio de Arriendo Variable')
	fecha_termino 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False, help_text='Fecha de Término de Arriendo Variable')

	class Meta:
		model 	= Arriendo_Variable
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'mes_inicio'		: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'		: forms.Select(attrs={'class': 'form-control'}),
			'anio_inicio'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'anio_termino'		: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'moneda' : {'required': 'campo requerido'},
		}

		labels = {
			'anio_inicio' 	: 'Año inicio',
			'anio_termino' 	: 'Año término',
		}

		help_texts = {
			'mes_inicio'		: 'Mes de Inicio Arriendo Variable',
			'mes_termino'		: 'Mes de Término Arriendo Variable',
			'anio_inicio'		: 'Año de Inicio Arriendo Variable',
			'anio_termino'		: 'Año de Término Arriendo Variable',
			'dia_reajuste'		: '',
			'relacion'			: '',
			'arriendo_minimo' 	: '',
		}

	def clean_fecha_inicio(self):

		mes_inicio 	= str(self.cleaned_data.get("mes_inicio")).zfill(2)
		anio_inicio = str(self.cleaned_data.get("anio_inicio"))

		return datetime.strptime('01/'+mes_inicio+'/'+anio_inicio+'', "%d/%m/%Y").date()

	def clean_fecha_termino(self):

		mes_termino 	= str(self.cleaned_data.get("mes_termino")).zfill(2)
		anio_termino 	= str(self.cleaned_data.get("anio_termino"))

		return ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+anio_termino+'', "%d/%m/%Y"))

class FormPropuestaBodega(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number field-required'}), error_messages={'required': 'campo requerido'}, help_text='Valor de Arriendo Bodega')
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control field-required moneda', 'onchange': 'cambio_format_moneda(this)'}), error_messages={'required': 'campo requerido'}, help_text='Moneda Aplicada al Valor del Arriendo')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'invalid': 'campo invalido'}, label='Fecha de Inicio', help_text='Fecha de Inicio Arriendo Bodega')

	class Meta:
		model 	= Propuesta_Arriendo_Bodega
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'periodicidad'		: forms.Select(attrs={'class': 'form-control'}),
			'metros' 			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'cantidad_metros' 	: forms.NumberInput(attrs={'class': 'form-control field-required'}),
		}

		labels = {
			'metros' 			: 'Valor x m²',
			'cantidad_metros' 	: 'Cantidad de m²',
		}

		help_texts = {
			'periodicidad' 		: 'Periodicidad del Arriendo de Bodega',
			'metro_cuadrado'	: 'Valor Aplicado por Metro Cuadrado',
		}

	def clean(self):

		cleaned_data = super(FormPropuestaBodega, self).clean()
		
		if cleaned_data.get("metros") is True and cleaned_data.get("cantidad_metros") is None:
		
			self.add_error('cantidad_metros', 'campo requerido')

class FormPropuestaCuota(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Cuota de Incorporación')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada a la Cuota de Incorporación')

	class Meta:
		model 	= Cuota_Incorporacion
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'mes'		: forms.Select(attrs={'class': 'form-control'}),
			'anio'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'metros' 	: forms.CheckboxInput(attrs={'class': 'form-control'}),
		}

		labels = {
			'anio' 		: 'Año',
			'metros' 	: 'Valor x m²',
		}

		error_messages = {
			'mes' 		: {'required': 'campo requerido'},
			'anio' 		: {'required': 'campo requerido'},
		}

		help_texts = {
			'metro_cuadrado' : 'Valor Aplicado por Metro Cuadrado'
		}

class FormPropuestaPromocion(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Fondo Promoción')
	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date', 'onchange': 'cambio_format_moneda(this)'}), label='Cobrar a partir de:', help_text='Fecha de Inicio del Cobro Fondo Promoción')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control moneda'}), help_text='Moneda Aplicada al Fondo Promoción')

	class Meta:
		model 	= Propuesta_Fondo_Promocion
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'periodicidad' : forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'periodicidad' : {'required': 'campo requerido'},
		}

		help_texts = {
			'periodicidad'	: 'Periodicidad de Fondo Promoción',
			'vinculo'		: ''
		}

class FormPropuestaComun(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), help_text='Valor de Gasto Común')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Gasto Común')

	class Meta:
		model 	= Propuesta_Gasto_Comun
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'tipo'	: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'tipo'		: {'required': 'campo requerido'},
		}

		help_texts = {
			'tipo' 				: 'Tipo de Gasto Común',
			'metros_cuadrado'	: 'Valor Aplicado por Metro Cuadrado'
		}


# inlines de propuesta
InlineFormPropuestaGarantia 		= inlineformset_factory(Propuesta_Version, Propuesta_Garantia, form=FormPropuestaGarantia, extra=1, can_delete=True)
InlineFormPropuestaMinimoDetalle 	= inlineformset_factory(Propuesta_Arriendo_Minimo, Propuesta_Arriendo_Minimo_Detalle, form=FormPropuestaArriendoDetalle, extra=1, can_delete=True)
InlineFormPropuestaVariable 		= inlineformset_factory(Propuesta_Version, Propuesta_Arriendo_Variable, form=FormPropuestaVariable, extra=1, can_delete=True)
InlineFormPropuestaBodega 			= inlineformset_factory(Propuesta_Version, Propuesta_Arriendo_Bodega, form=FormPropuestaBodega, extra=1, can_delete=True)
InlineFormPropuestaCuota 			= inlineformset_factory(Propuesta_Version, Propuesta_Cuota_Incorporacion, form=FormPropuestaCuota, extra=1, can_delete=True)
InlineFormPropuestaPromocion 		= inlineformset_factory(Propuesta_Version, Propuesta_Fondo_Promocion, form=FormPropuestaPromocion, extra=1, can_delete=True)
InlineFormPropuestaComun 			= inlineformset_factory(Propuesta_Version, Propuesta_Gasto_Comun, form=FormPropuestaComun, extra=1, can_delete=True)


ArriendoVariableFormSet 	= inlineformset_factory(Contrato, Arriendo_Variable, form=ArriendoVariableForm, extra=1, can_delete=True)
GastoComunFormSet 			= inlineformset_factory(Contrato, Gasto_Comun, form=GastoComunForm, extra=1, can_delete=True)
ServicioBasicoFormSet 		= inlineformset_factory(Contrato, Servicio_Basico, form=ServicioBasicoForm, extra=1, can_delete=True)
CuotaIncorporacionFormet 	= inlineformset_factory(Contrato, Cuota_Incorporacion, form=CuotaIncorporacionForm, extra=1, can_delete=True)
ArriendoBodegaFormSet 		= inlineformset_factory(Contrato, Arriendo_Bodega, form=ArriendoBodegaForm, extra=1, can_delete=True)
GarantiaFormSet 			= inlineformset_factory(Contrato, Garantia, form=GarantiaForm, extra=1, can_delete=True)
ArriendoDetalleFormSet 		= inlineformset_factory(Arriendo, Arriendo_Detalle, form=ArriendoDetalleForm, extra=1, can_delete=True)
FondoPromocionFormSet 		= inlineformset_factory(Contrato, Fondo_Promocion, form=FondoPromocionForm, extra=1, can_delete=True)
GastoAsociadoFormSet 		= inlineformset_factory(Contrato, Gasto_Asociado, form=GastoAsociadoForm, extra=1, can_delete=True)

