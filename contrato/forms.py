# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory

from locales.models import Local
from conceptos.models import Concepto
from administrador.models import Cliente, Moneda

from .models import Contrato_Tipo, Contrato_Estado, Contrato, Arriendo, Arriendo_Detalle, Arriendo_Variable, Gasto_Comun, Servicio_Basico

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
			'nombre' : {'required': 'campo requerido.'},
			'codigo' : {'required': 'campo requerido.'},
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

	fecha_contrato		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_inicio		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_termino		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_habilitacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_activacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_renovacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_remodelacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_plazo			= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_aviso			= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'}, label='Fecha aviso comercial')

	locales 			= forms.ModelMultipleChoiceField(queryset=Local.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}))
	conceptos 			= forms.ModelMultipleChoiceField(queryset=Concepto.objects.all(),required=False,widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}))

	contrato_estado 	= forms.ModelChoiceField(queryset=Contrato_Estado.objects.all(),initial="Borrador",widget=forms.Select(attrs={'class': 'form-control'}))
	cliente 			= forms.ModelChoiceField(queryset=Cliente.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.'})
	contrato_tipo 		= forms.ModelChoiceField(queryset=Contrato_Tipo.objects.all(),widget=forms.Select(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.'}, label='Tipo de Contrato')


	class Meta:
		model 	= Contrato
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'empresa']

		widgets = {
			'numero'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'nombre_local'	: forms.TextInput(attrs={'class': 'form-control'}),
			'comentario'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'numero'		: {'required': 'campo requerido.', 'invalid': 'campo invalido'},
			'nombre_local'	: {'required': 'campo requerido.'},
			'comentario'	: {'required': 'campo requerido.'},
		}

		labels = {
			'numero'			: 'Nº Contrato',
			'nombre_local'		: 'Nombre de Fantasía',
			'fecha_renovacion'	: 'Fecha Renovación',
		}

		help_texts = {
			'numero'		: 'numero',			
			'nombre_local' 	: 'nombre local',
			'comentario' 	: 'comentario',
		}

class InformacionForm(forms.ModelForm):

	class Meta:
		model 	= Contrato
		fields 	= ['id']


class ArriendoForm(forms.ModelForm):

	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[2,3,4,6]),
		widget 	= forms.Select(attrs={'class': 'form-control'})
		)

	class Meta:
		model 	= Arriendo
		fields 	= '__all__'
		exclude = ['visible']

		widgets = {
			'reajuste'		: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'meses'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'fecha_inicio'	: forms.TextInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'meses'			: {'required': 'campo requerido.'},
			'valor'			: {'required': 'campo requerido.'},
			'moneda'		: {'required': 'campo requerido.'},
			'fecha_inicio'	: {'required': 'campo requerido.'},
		}

		labels = {
			'meses'			: 'Meses',
			'fecha_inicio'	: 'Fecha Inicio',
		}

		help_texts = {
			'reajuste' 		: 'Reajuste',
			'meses' 		: 'Cada Cuantos',
			'valor' 		: 'Valor',
			'moneda' 		: 'Moneda',
			'fecha_inicio' 	: 'Fecha Inicio',
		}


class ArriendoDetalleForm(forms.ModelForm):

	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[2,3,4,5]),
		widget 	= forms.Select(attrs={'class': 'form-control'})
		)

	class Meta:
		model 	= Arriendo_Detalle
		fields 	= ['mes_inicio', 'mes_termino', 'valor', 'moneda', 'metro_cuadrado']

		widgets = {
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'_DELETE_'		: forms.NumberInput(attrs={'class': 'form-control'}),
		}


class ArriendoVariableForm(forms.ModelForm):

	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[6]),
		widget 	= forms.Select(attrs={'class': 'form-control'})
		)

	class Meta:
		model 	= Arriendo_Variable
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'periodicidad'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'mes_inicio'	: {'required': 'campo requerido.'},
			'mes_termino'	: {'required': 'campo requerido.'},
			'periodicidad'	: {'required': 'campo requerido.'},
			'valor'			: {'required': 'campo requerido.'},
			'moneda'		: {'required': 'campo requerido.'},
		}

		labels = {
			'mes_inicio'	: 'Meses Inicio',
			'mes_termino'	: 'Mes Termino',
		}

		help_texts = {
			'mes_inicio' 	: 'mes inicio',
			'mes_termino' 	: 'mes termino',
			'periodicidad' 	: 'periodicidad',
			'valor' 		: 'valor',
			'moneda' 		: 'moneda',
		}


class GastoComunForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		contrato = kwargs.pop('contrato', None)
		super(GastoComunForm, self).__init__(*args, **kwargs)

		# user 		= User.objects.get(pk=self.request.user.pk)
		# profile 	= UserProfile.objects.get(user=user)

		if contrato is not None:
			self.fields['local'].queryset = contrato.locales.all()


	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[2,4,5]),
		widget 	= forms.Select(attrs={'class': 'form-control moneda','disabled':'disabled'})

		)

	class Meta:
		model 	= Gasto_Comun
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'mes_inicio'		: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'		: forms.Select(attrs={'class': 'form-control'}),
			'valor'				: forms.NumberInput(attrs={'class': 'form-control'}),
			'prorrateo'			: forms.CheckboxInput(attrs={'class': 'form-control prorrateo'}),
			'valor_prorrateo' 	: forms.NumberInput(attrs={'class': 'form-control valor_prorrateo','disabled':'disabled'}),
		}

		error_messages = {
			'mes_inicio'		: {'required': 'campo requerido.'},
			'mes_termino'		: {'required': 'campo requerido.'},
			'valor'				: {'required': 'campo requerido.'},
			'prorrateo'			: {'required': 'campo requerido.'},
			'valor_prorrateo' 	: {'required': 'campo requerido.'},
		}

		labels = {
			'mes_inicio'	: 'Meses Inicio',
			'mes_termino'	: 'Mes Termino',
		}

		help_texts = {
			'mes_inicio' 		: 'mes inicio',
			'mes_termino' 		: 'mes termino',
			'valor' 			: 'valor',
			'prorrateo' 		: 'prorrateo',
			'valor_prorrateo'	: 'valor prorrateo',
		}


class ServicioBasicoForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):

		contrato = kwargs.pop('contrato', None)
		super(ServicioBasicoForm, self).__init__(*args, **kwargs)

		if contrato is not None:
			self.fields['local'].queryset = contrato.locales.all()

	class Meta:
		model 	= Servicio_Basico
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'tipo'			: forms.Select(attrs={'class': 'form-control tipo-asd'}),
			'local'			: forms.Select(attrs={'class': 'form-control'}),
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'tipo'			: {'required': 'campo requerido.'},
			'mes_inicio'	: {'required': 'campo requerido.'},
			'mes_termino'	: {'required': 'campo requerido.'},
			'valor'			: {'required': 'campo requerido.'},
		}

		labels = {
			'tipo'			: 'Tipo',
			'mes_inicio'	: 'Meses Inicio',
			'mes_termino'	: 'Mes Termino',
		}

		help_texts = {
			'tipo' 			: 'tipo',
			'mes_inicio' 	: 'mes inicio',
			'mes_termino' 	: 'mes termino',
			'valor' 		: 'valor',
		}



ArriendoDetalleFormSet 	= inlineformset_factory(Arriendo, Arriendo_Detalle, form=ArriendoDetalleForm, extra=1, can_delete=True)
ArriendoVariableFormSet = inlineformset_factory(Contrato, Arriendo_Variable, form=ArriendoVariableForm, extra=1, can_delete=True)
GastoComunFormSet 		= inlineformset_factory(Contrato, Gasto_Comun, form=GastoComunForm, extra=1, can_delete=True)
ServicioBasicoFormSet 	= inlineformset_factory(Contrato, Servicio_Basico, form=ServicioBasicoForm, extra=1, can_delete=True)


