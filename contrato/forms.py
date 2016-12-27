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

	fecha_contrato		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Contrato', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Corresponde a la fecha en la cual quedará registrado en el sistema el ingreso de contrato')
	fecha_inicio		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Inicio de Contrato', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha en la cuál comenzará a regir el contrato. Está fecha será tomada en cuenta al momento de la facturación')
	fecha_termino		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Término de Contrato', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha que pondrá término a la vigencia del contrato.')
	fecha_inicio_renta	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Inicio de Renta',error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha en que se dará comienzo al cobro del arriendo del o los local(es)')
	fecha_entrega		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Entrega Local', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha en la cual el propietario hace entrega del local(es) al cliente')
	fecha_habilitacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Habilitación', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha correspondiente a la apertura del local')
	fecha_renovacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Fecha de Renovación', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido'}, help_text='Fecha previa al término de contrato para realizar el proceso de renovación')
	
	metros_bodega		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number text-right', 'disabled': 'disabled'}), help_text='Metros Cuadrados de la Bodega')
	meses_aviso_comercial = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control text-right'}), help_text='Cantidad de meses previos al término de contrato, para dar aviso al área comercial')
	meses_remodelacion	= forms.IntegerField(required=False, max_value=120, min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control text-right'}), help_text='Cantidad de Meses Para Remodelación Local', error_messages={'required': 'campo requerido', 'invalid': 'campo invalido', 'min':'asd'})


	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		activos 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

		super(ContratoForm, self).__init__(*args, **kwargs)

		if self.instance.pk is not None:

			locales_id = self.instance.locales.all().values_list('id', flat=True)
			locales_id = Local.objects.filter(activo__empresa=self.request.user.userprofile.empresa).values_list('id', flat=True).exclude(id=locales_id)

		else:
			
			locales_id = Local.objects.filter(activo__empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)

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
			'numero'				: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'meses_contrato'		: forms.NumberInput(attrs={'class': 'form-control text-right'}),
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
			'bodega'				: 'Establece si el contrato tendrá asociado bodega(s)',
			'numero'				: 'Número de identificación único del contrato',
			'meses_contrato'		: 'Cantidad de meses que se arrendará el o los local(es)',
			'meses_aviso_comercial'	: 'Cantidad de meses previos al término de contrato, para dar aviso al área comercial',
			'meses_remodelacion'	: 'Cantidad de Meses Para Remodelación Local',
			'nombre_local'			: 'Corresponde al nombre, término o  símbolo que identifica a las empresas que existen en el mercado.',
			'destino_comercial'		: 'Descripción de la actividad que realizará el local',
			'tipo' 					: 'Corresponde al tipo de contrato establecido en la negociación. Por ejemplo: “Contrato arrendamiento mensual tienda mayor”',
			'cliente'				: 'Persona natural o jurídica a la cual se le asigna el contrato',
			'locales'				: 'Locales asociados al contrato',
			'conceptos'				: 'Conceptos que serán facturados para el contrato',
		}

	def clean_numero(self):

		numero 		= self.cleaned_data['numero']
		is_insert 	= self.instance.id is None

		if is_insert:
			if Contrato.objects.filter(numero=numero, visible=True).exists():
				raise forms.ValidationError('Ya existe un contrato con este número.')
		else:
			if numero != Contrato.objects.get(id=self.instance.id).numero and Contrato.objects.filter(numero=numero, visible=True).exists():
				raise forms.ValidationError('Ya existe un contrato con este número.')

		return numero

class GarantiaForm(forms.ModelForm):

	valor = NumberField(
		widget = forms.TextInput(attrs={'class': 'form-control format-number text-right'}),
		help_text = 'Monto de la garantía',
		error_messages = {'required': 'campo requerido'},
		)

	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in = [3,5]), 
		widget = forms.Select(attrs = {'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}),
		help_text = 'Moneda asociada al monto de la garantía',
		error_messages = {'required': 'campo requerido'},
		)


	def __init__(self, *args, **kwargs):

		super(GarantiaForm, self).__init__(*args, **kwargs)	

		# if self.instance.pk is not None:
			# print ('1')
			# locales_id = Contrato.objects.values_list('locales', flat=True).filter(visible=True).exclude(id=self.instance.pk)
		# else:
			# print ('2')
			# locales_id = Contrato.objects.values_list('locales', flat=True).filter(visible=True)

	class Meta:
		model 	= Garantia
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'codigo'	: forms.TextInput(attrs={'class': 'form-control'}),
			'nombre' 	: forms.TextInput(attrs={'class': 'form-control'}),
			'local'		: forms.Select(attrs={'class': 'form-control'}),
		}

		help_texts = {
			'codigo' 	: 'Código identificador de la garantía',
			'nombre' 	: 'Nombre o descripción asociado a la garantía',
			'local' 	: 'Local(es) vinculados a la garantía',
		}

		error_messages = {
			'codigo' 	: {'unique': 'este código ya existe'},
			'nombre' 	: {'required': 'campo requerido'},
			'local' 	: {'required': 'campo requerido'},
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

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), label='Valor Multa', error_messages={'required': 'campo requerido'}, help_text='Valor de la Multa')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'onchange': 'cambio_format_moneda(this)', 'data-table': 'false'}), error_messages={'required': 'campo requerido'}, help_text='Tipo de Moneda Asociado a la Multa')

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
			'anio' 			: forms.NumberInput(attrs={'class': 'form-control text-right'}),
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

class ArriendoMinimoForm(forms.ModelForm):

	valor = NumberField(
		widget = forms.TextInput(attrs={'class': 'form-control format-number text-right'}),
		error_messages = {'required': 'campo requerido', 'invalid': 'campo invalido'},
		help_text = 'Valor Asociado al Arriendo Mínimo',
		)

	moneda = forms.ModelChoiceField(
		widget = forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}),
		help_text = 'Tipo de Moneda Aplicado al Arriendo Mínimo',
		queryset = Moneda.objects.filter(id__in=[3,5]),
		)

	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False)
	fecha_termino 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False)

	class Meta:

		model 	= Arriendo_Minimo
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'mes_inicio'		: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'		: forms.Select(attrs={'class': 'form-control'}),
			'anio_inicio'		: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'anio_termino'		: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'metro_cuadrado' 	: forms.CheckboxInput(attrs={'class': ''}),
		}

		labels = {
			'mes_inicio'		: 'Mes de inicio',
			'mes_termino'		: 'Mes de término',
			'anio_inicio' 		: 'Año de inicio',
			'anio_termino' 		: 'Año de término',
			'metro_cuadrado' 	: 'Valor x m²',
		}

		help_texts ={
			'mes_inicio'		: 'mes de inicio del arriendo',
			'mes_termino'		: 'mes de término del arriendo',
			'anio_inicio'		: 'año de inicio del arriendo',
			'anio_termino'		: 'año de término del arriendo',
			'metro_cuadrado'	: 'valor arriendo aplicado al metro cuadrado'
		}

		error_messages = {
			'mes_inicio' 		: {'required': 'campo requerido'},
			'mes_termino' 		: {'required': 'campo requerido'},
			'anio_inicio' 		: {'required': 'campo requerido'},
			'anio_termino' 		: {'required': 'campo requerido'},
		}

	def clean_fecha_inicio(self):

		mes_inicio 	= str(self.cleaned_data.get("mes_inicio")).zfill(2)
		anio_inicio = str(self.cleaned_data.get("anio_inicio"))

		return datetime.strptime('01/'+mes_inicio+'/'+anio_inicio+'', "%d/%m/%Y").date()

	def clean_fecha_termino(self):

		mes_termino 	= str(self.cleaned_data.get("mes_termino")).zfill(2)
		anio_termino 	= str(self.cleaned_data.get("anio_termino"))

		return ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+anio_termino+'', "%d/%m/%Y"))

class ArriendoVariableForm(forms.ModelForm):

	valor = NumberField(
		widget = forms.TextInput(attrs={'class': 'form-control format-number text-right'}),
		help_text='Valor de Arriendo Variable'
		)

	moneda = forms.ModelChoiceField(
		widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}),
		help_text='Moneda Aplicada al Valor de Arriendo variable',
		queryset=Moneda.objects.filter(id__in=[6]),
		)

	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False,)
	fecha_termino 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False,)

	def __init__(self, *args, **kwargs):

		contrato = kwargs.pop('contrato', None)

		super(ArriendoVariableForm, self).__init__(*args, **kwargs)

		self.fields['vinculo'].queryset = Concepto.objects.filter(concepto_tipo_id=1, empresa=contrato.empresa, visible=True)
	
	class Meta:
		model 	= Arriendo_Variable
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {		
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'anio_inicio'	: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'anio_termino'	: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'dia_reajuste'	: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'relacion'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'vinculo' 		: forms.Select(attrs={'class': 'form-control'}),
		}

		labels = {
			'mes_inicio'		: 'Mes de inicio',
			'mes_termino'		: 'Mes de término',
			'anio_inicio' 		: 'Año de inicio',
			'anio_termino' 		: 'Año de término',
			'relacion' 			: 'Relación',
			'vinculo' 			: 'Concepto',
			'dia_reajuste'  	: 'Día reajuste',
		}

		help_texts = {
			'mes_inicio'	: 'Mes de Inicio Arriendo Variable',
			'mes_termino'	: 'Mes de Término Arriendo Variable',
			'anio_inicio'	: 'Año de Inicio Arriendo Variable',
			'anio_termino'	: 'Año de Término Arriendo Variable',
			'dia_reajuste'	: 'Día del mes para reajustar las ventas',
			'relacion'		: 'Si esta relacionado a un concepto o solo a las ventas',
			'vinculo' 		: 'Concepto asociado',
		}

		error_messages = {
			'mes_inicio' 	: {'required': 'campo requerido'},
			'mes_termino' 	: {'required': 'campo requerido'},
			'anio_inicio' 	: {'required': 'campo requerido'},
			'anio_termino' 	: {'required': 'campo requerido'},
			'dia_reajuste' 	: {'required': 'campo requerido'},
			'relacion' 		: {'required': 'campo requerido'},
			'vinculo' 		: {'required': 'campo requerido'},
		}

	def clean_fecha_inicio(self):

		mes_inicio 	= str(self.cleaned_data.get("mes_inicio")).zfill(2)
		anio_inicio = str(self.cleaned_data.get("anio_inicio"))

		return datetime.strptime('01/'+mes_inicio+'/'+anio_inicio+'', "%d/%m/%Y").date()

	def clean_fecha_termino(self):

		mes_termino 	= str(self.cleaned_data.get("mes_termino")).zfill(2)
		anio_termino 	= str(self.cleaned_data.get("anio_termino"))

		return ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+anio_termino+'', "%d/%m/%Y"))

class ArriendoBodegaForm(forms.ModelForm):

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Arriendo Bodega')
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Valor del Arriendo')
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

class GastoComunForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Gasto Común')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Gasto Común')

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

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor Servicio')

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(ServicioBasicoForm, self).__init__(*args, **kwargs)

		# if contrato is not None:
		# 	self.fields['locales'].queryset = contrato.locales.all()

	class Meta:
		model 	= Servicio_Basico
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'tipo_servicio' : forms.Select(attrs={'class': 'form-control'}),
			'tipo_cobro' 	: forms.Select(attrs={'class': 'form-control'}),
			# 'locales'		: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
			}

		error_messages = {
			# 'locales' 	: {'required': 'campo requerido'},
			}

		help_texts = {
			# 'locales' 	: 'Locales donde Aplican Servicio Básico',
			}


class CuotaIncorporacionForm(forms.ModelForm):

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Cuota de Incorporación')
	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), help_text='Fecha')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada a la Cuota de Incorporación')

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

class GastoAsociadoForm(forms.ModelForm):

	valor = NumberField(
		widget 			= forms.TextInput(attrs={'class': 'form-control format-number text-right'}),
		error_messages 	= {'required': 'campo requerido', 'invalid': 'campo invalido'},
		help_text 		= 'Valor del Gasto',
		)

	fecha = forms.DateField(
		widget 			= forms.TextInput(attrs={'class': 'form-control format-date'}),
		error_messages 	= {'required': 'campo requerido', 'invalid': 'campo invalido'},
		help_text 		= 'Fecha de Inicio del Cobro',
		label 			= 'Cobrar desde:', 
		input_formats 	= ['%d/%m/%Y'],
		required 		= True,
		)

	moneda = forms.ModelChoiceField(
		widget 			= forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}),
		error_messages 	= {'required': 'campo requerido'},
		help_text 		= 'Moneda Aplicada al Gasto',
		queryset 		= Moneda.objects.filter(id__in=[3,5,6]), 
		)

	def __init__(self, *args, **kwargs):

		contrato = kwargs.pop('contrato', None)

		super(GastoAsociadoForm, self).__init__(*args, **kwargs)

		self.fields['vinculo'].queryset = Concepto.objects.filter(empresa=contrato.empresa, visible=True).exclude(concepto_tipo_id__in=[6,10])

	class Meta:
		model 	= Gasto_Asociado
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {
			'periodicidad'	: forms.Select(attrs={'class': 'form-control'}),
			'vinculo'		: forms.Select(attrs={'class': 'form-control'}),
			'valor_fijo' 	: forms.CheckboxInput(attrs={'class': ''}),
		}

		labels = {
			'vinculo' 		: 'Concepto asociado',
		}

		error_messages = {
			'periodicidad'	: {'required': 'campo requerido'},
		}

		help_texts = {
			'periodicidad'	: 'Periodicidad del Gasto',
			'vinculo'		: 'Concepto Asociado',
			'valor_fijo' 	: 'Valor Fijo',
		}

	def clean(self):

		fijo 		= self.cleaned_data.get('valor_fijo')
		vinculo 	= self.cleaned_data.get('vinculo', None)
		moneda 		= self.cleaned_data.get('moneda', None)

		if fijo and vinculo is not None:
			self.add_error('vinculo', 'campo no requerido')
		elif fijo and vinculo is None:
			if moneda is not None and moneda.id == 6:
				self.add_error('moneda', 'seleccionar otra moneda')
		else:
			if vinculo is None:
				self.add_error('vinculo', 'campo requerido')
			else:
				if moneda is not None and moneda.id != 6:
					self.add_error('moneda', 'seleccionar otra moneda')

class ReajusteForm(forms.ModelForm):
		
	valor = NumberField(
		widget 			= forms.TextInput(attrs={'class': 'form-control format-number text-right'}),
		error_messages 	= {'required': 'campo requerido', 'invalid': 'campo invalido'},
		help_text 		= 'Valor del Gasto',
		)

	moneda = forms.ModelChoiceField(
		widget 			= forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}),
		error_messages 	= {'required': 'campo requerido'},
		help_text 		= 'Moneda Aplicada al Gasto',
		queryset 		= Moneda.objects.filter(id__in=[6]), 
		)

	fecha_inicio = forms.DateField(
		input_formats=['%d/%m/%Y'],
		required=False
		)

	fecha_termino = forms.DateField(
		input_formats=['%d/%m/%Y'],
		required=False
		)

	def __init__(self, *args, **kwargs):

		contrato = kwargs.pop('contrato', None)

		super(ReajusteForm, self).__init__(*args, **kwargs)

		self.fields['vinculo'].queryset = Concepto.objects.filter(empresa=contrato.empresa, visible=True).exclude(concepto_tipo_id=6)
	
	class Meta:
		model 	= Reajuste
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'concepto']

		widgets = {		
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'anio_inicio'	: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'anio_termino'	: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'vinculo' 		: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'mes_inicio' 	: {'required': 'campo requerido'},
			'mes_termino' 	: {'required': 'campo requerido'},
			'anio_inicio' 	: {'required': 'campo requerido'},
			'anio_termino' 	: {'required': 'campo requerido'},
			'vinculo' 		: {'required': 'campo requerido'},
		}

		labels = {
			'mes_inicio' 	: 'Mes inicio',
			'mes_termino'	: 'Mes término',
			'anio_inicio' 	: 'Año inicio',
			'anio_termino'  : 'Año término',
			'vinculo'		: 'Concepto'
		}

		help_texts = {
			'mes_inicio'	: 'mes de Inicio Arriendo Variable',
			'mes_termino'	: 'mes de Término Arriendo Variable',
			'anio_inicio'	: 'año de Inicio Arriendo Variable',
			'anio_termino'	: 'año de Término Arriendo Variable',
			'vinculo'		: 'concepto vinculado al reajuste',
		}

	def clean_fecha_inicio(self):

		mes_inicio 	= str(self.cleaned_data.get("mes_inicio")).zfill(2)
		anio_inicio = str(self.cleaned_data.get("anio_inicio"))

		return datetime.strptime('01/'+mes_inicio+'/'+anio_inicio+'', "%d/%m/%Y").date()

	def clean_fecha_termino(self):

		mes_termino 	= str(self.cleaned_data.get("mes_termino")).zfill(2)
		anio_termino 	= str(self.cleaned_data.get("anio_termino"))

		return ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+anio_termino+'', "%d/%m/%Y"))


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
			'numero'				: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'nombre_local'			: forms.TextInput(attrs={'class': 'form-control'}),
			'destino_comercial'		: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'meses_contrato'		: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'meses_aviso_comercial' : forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'meses_remodelacion' 	: forms.NumberInput(attrs={'class': 'form-control text-right'}),
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

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de la Garantia')
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Asociada al Valor de la Garantia')

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

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Reajuste')
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[2,3,4,6]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'data-es-moneda': 'true', 'data-moneda': '', 'data-select': 'false', 'onchange': 'cambio_format_moneda(this)'}), help_text='Tipo de Moneda del Reajuste')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), help_text='Fecha Inicio de Aplicación del Reajuste')

	class Meta:
		model 	= Propuesta_Arriendo_Minimo
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'reajuste'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'por_meses'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'meses'			: forms.NumberInput(attrs={'class': 'form-control text-right'}),
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

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor Asociado al Arriendo')
	moneda 	= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Tipo de Moneda Aplicado al Arriendo')

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
			'mes_inicio' 	: 'Mes inicio',
			'mes_termino' 	: 'Mes término',
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

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Arriendo Variable')
	moneda 			= forms.ModelChoiceField(queryset=Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Valor de Arriendo variable')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False, help_text='Fecha de Inicio de Arriendo Variable')
	fecha_termino 	= forms.DateField(input_formats=['%d/%m/%Y'], required=False, help_text='Fecha de Término de Arriendo Variable')

	class Meta:
		model 	= Arriendo_Variable
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'mes_inicio'		: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'		: forms.Select(attrs={'class': 'form-control'}),
			'anio_inicio'		: forms.NumberInput(attrs={'class': 'form-control text-right'}),
			'anio_termino'		: forms.NumberInput(attrs={'class': 'form-control text-right'}),
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

	valor 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number field-required text-right'}), error_messages={'required': 'campo requerido'}, help_text='Valor de Arriendo Bodega')
	moneda 			= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control field-required moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), error_messages={'required': 'campo requerido'}, help_text='Moneda Aplicada al Valor del Arriendo')
	fecha_inicio 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'invalid': 'campo invalido'}, label='Fecha de Inicio', help_text='Fecha de Inicio Arriendo Bodega')

	class Meta:
		model 	= Propuesta_Arriendo_Bodega
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'periodicidad'		: forms.Select(attrs={'class': 'form-control'}),
			'metros' 			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'cantidad_metros' 	: forms.NumberInput(attrs={'class': 'form-control field-required text-right'}),
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

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Cuota de Incorporación')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada a la Cuota de Incorporación')

	class Meta:
		model 	= Cuota_Incorporacion
		fields 	= '__all__'
		exclude = ['visible', 'creado_en', 'propuesta']

		widgets = {
			'mes'		: forms.Select(attrs={'class': 'form-control'}),
			'anio'		: forms.NumberInput(attrs={'class': 'form-control text-right'}),
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

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Fondo Promoción')
	fecha 	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), label='Cobrar a partir de:', help_text='Fecha de Inicio del Cobro Fondo Promoción')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[6]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)' }), help_text='Moneda Aplicada al Fondo Promoción')

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

	valor 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number text-right'}), help_text='Valor de Gasto Común')
	moneda 	= forms.ModelChoiceField(queryset = Moneda.objects.filter(id__in=[3,5]), widget=forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'true', 'onchange': 'cambio_format_moneda(this)'}), help_text='Moneda Aplicada al Gasto Común')

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


ArriendoMinimoFormSet 		= inlineformset_factory(Contrato, Arriendo_Minimo, form=ArriendoMinimoForm, extra=1, can_delete=True)
ArriendoVariableFormSet 	= inlineformset_factory(Contrato, Arriendo_Variable, form=ArriendoVariableForm, extra=1, can_delete=True)
GastoComunFormSet 			= inlineformset_factory(Contrato, Gasto_Comun, form=GastoComunForm, extra=1, can_delete=True)
ServicioBasicoFormSet 		= inlineformset_factory(Contrato, Servicio_Basico, form=ServicioBasicoForm, extra=1, max_num=1, can_delete=True)
CuotaIncorporacionFormet 	= inlineformset_factory(Contrato, Cuota_Incorporacion, form=CuotaIncorporacionForm, extra=1, can_delete=True)
ArriendoBodegaFormSet 		= inlineformset_factory(Contrato, Arriendo_Bodega, form=ArriendoBodegaForm, extra=1, can_delete=True)
GarantiaFormSet 			= inlineformset_factory(Contrato, Garantia, form=GarantiaForm, extra=1, can_delete=True)
GastoAsociadoFormSet 		= inlineformset_factory(Contrato, Gasto_Asociado, form=GastoAsociadoForm, extra=1, can_delete=True)
ReajusteFormSet 			= inlineformset_factory(Contrato, Reajuste, form=ReajusteForm, extra=1, can_delete=True)
