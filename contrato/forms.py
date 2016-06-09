# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
from django.forms import formset_factory
from .models import Contrato_Tipo, Contrato_Estado, Contrato, Arriendo, Arriendo_Detalle, Arriendo_Variable, Gasto_Comun, Servicio_Basico
from locales.models import Local
from conceptos.models import Concepto
from administrador.models import Moneda
from activos.models import Medidor

class ContratoTipoForm(forms.ModelForm):
	class Meta:
		model 	= Contrato_Tipo
		fields 	= ['nombre', 'codigo', 'descripcion']

		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'codigo': forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' : {'required': 'campo requerido.'},
		}

		labels = {
			'codigo': (u'Código'),
			'descripcion': (u'Descripción'),
		}

		help_texts = {
			'nombre': ('...'),
			'codigo': ('...'),
			'descripcion': ('...'),
		}

class ContratoForm(forms.ModelForm):

	locales 			= forms.ModelMultipleChoiceField(queryset=Local.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}))
	conceptos 			= forms.ModelMultipleChoiceField(queryset=Concepto.objects.all(),required=False,widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}))
	contrato_estado 	= forms.ModelChoiceField(queryset=Contrato_Estado.objects.all(),initial="Borrador",widget=forms.Select(attrs={'class': 'select2 form-control'}))

	fecha_contrato		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_inicio		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_termino		= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_habilitacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_activacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	fecha_renovacion	= forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido.', 'invalid': 'campo invalido'})
	

	class Meta:
		model 	= Contrato
		fields 	= '__all__'
		exclude = ['empresa', 'creado_en', 'visible']

		widgets = {
			'numero': forms.NumberInput(attrs={'class': 'form-control'}),
			'nombre_local': forms.TextInput(attrs={'class': 'form-control'}),
			'plazo': forms.NumberInput(attrs={'class': 'form-control'}),
			'aviso': forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_local': forms.TextInput(attrs={'class': 'form-control'}),
			'metros_otros': forms.TextInput(attrs={'class': 'form-control'}),
			'arriendo_local': forms.TextInput(attrs={'class': 'form-control'}),
			'arriendo_otros': forms.TextInput(attrs={'class': 'form-control'}),
			'arriendo_porcentual': forms.TextInput(attrs={'class': 'form-control'}),
			'reajuste_porcentaje': forms.TextInput(attrs={'class': 'form-control'}),
			'reajuste_meses': forms.TextInput(attrs={'class': 'form-control'}),
			'fondo_promocion': forms.TextInput(attrs={'class': 'form-control'}),
			'cuota_promocion': forms.TextInput(attrs={'class': 'form-control'}),
			'arriendo_diciembre': forms.TextInput(attrs={'class': 'form-control'}),
			'inicio_renta': forms.TextInput(attrs={'class': 'form-control'}),
			'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
			'gasto_comun_local': forms.TextInput(attrs={'class': 'form-control'}),
			'gasto_comun_otros': forms.TextInput(attrs={'class': 'form-control'}),
			'cliente': forms.Select(attrs={'class': 'select2 form-control'}),
			'contrato_tipo': forms.Select(attrs={'class': 'select2 form-control'}),
		}

		error_messages = {
			'numero': {'required': 'campo requerido.', 'invalid': 'campo invalido'},
			'nombre_local': {'required': 'campo requerido.'},
			'fecha_contrato': {'required': 'campo requerido.', 'invalid': 'campo invalido'},
			'fecha_inicio': {'required': 'campo requerido.', 'invalid': 'campo invalido'},
			'fecha_termino': {'required': 'campo requerido.', 'invalid': 'campo invalido'},
			'fecha_habilitacion': {'required': 'campo requerido.', 'invalid': 'campo invalido'},
			'fecha_activacion': {'required': 'campo requerido.', 'invalid': 'campo invalido'},
			'plazo': {'required': 'campo requerido.'},
			'fecha_renovacion': {'required': 'campo requerido.'},
			'aviso': {'required': 'campo requerido.'},
			'metros_local': {'required': 'campo requerido.'},
			'metros_otros': {'required': 'campo requerido.'},
			'arriendo_local': {'required': 'campo requerido.'},
			'arriendo_otros': {'required': 'campo requerido.'},
			'arriendo_porcentual': {'required': 'campo requerido.'},
			'reajuste_porcentaje': {'required': 'campo requerido.'},
			'reajuste_meses': {'required': 'campo requerido.'},
			'fondo_promocion': {'required': 'campo requerido.'},
			'cuota_promocion': {'required': 'campo requerido.'},
			'arriendo_diciembre': {'required': 'campo requerido.'},
			'inicio_renta': {'required': 'campo requerido.'},
			'comentario': {'required': 'campo requerido.'},
			'gasto_comun_local': {'required': 'campo requerido.'},
			'gasto_comun_otros': {'required': 'campo requerido.'},
			'cliente': {'required': 'campo requerido.'},
			'contrato_tipo': {'required': 'campo requerido.'},
			'contrato_estado': {'required': 'campo requerido.'},
			'locales': {'required': 'campo requerido.'},
			'conceptos': {'required': 'campo requerido.'},
		}

		labels = {
			'numero': _(u'Número'),
			'nombre_local': _(u'Nombre Local'),
			'fecha_renovacion': _(u'Fecha Renovacion'),
		}

		help_texts = {
			'numero': _('numero'),
		}

class InformacionForm(forms.ModelForm):

	class Meta:
		model 	= Contrato
		fields 	= ['id']


class ArriendoForm(forms.ModelForm):

	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[2,4,6]),
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
			'meses'			: (u'Meses'),
			'fecha_inicio'	: (u'Fecha Inicio'),
		}

		help_texts = {
			'reajuste' 		: (u'Reajuste'),
			'meses' 		: (u'Cada Cuantos'),
			'valor' 		: (u'Valor'),
			'moneda' 		: (u'Moneda'),
			'fecha_inicio' 	: (u'Fecha Inicio'),
		}


class ArriendoDetalleForm(forms.ModelForm):

	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[2,4,5]),
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
			'mes_inicio'	: (u'Meses Inicio'),
			'mes_termino'	: (u'Mes Termino'),
		}

		help_texts = {
			'mes_inicio' 	: (u'mes inicio'),
			'mes_termino' 	: (u'mes termino'),
			'periodicidad' 	: (u'periodicidad'),
			'valor' 		: (u'valor'),
			'moneda' 		: (u'moneda'),
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
			'mes_inicio'	: forms.Select(attrs={'class': 'form-control'}),
			'mes_termino'	: forms.Select(attrs={'class': 'form-control'}),
			'valor'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'prorrateo'		: forms.CheckboxInput(attrs={'class': 'form-control prorrateo'}),
			'valor_prorrateo' : forms.NumberInput(attrs={'class': 'form-control valor_prorrateo','disabled':'disabled'}),
		}

		error_messages = {
			'mes_inicio'	: {'required': 'campo requerido.'},
			'mes_termino'	: {'required': 'campo requerido.'},
			'valor'			: {'required': 'campo requerido.'},
			'prorrateo'		: {'required': 'campo requerido.'},
			'valor_prorrateo' : {'required': 'campo requerido.'},
		}

		labels = {
			'mes_inicio'	: (u'Meses Inicio'),
			'mes_termino'	: (u'Mes Termino'),
		}

		help_texts = {
			'mes_inicio' 	: (u'mes inicio'),
			'mes_termino' 	: (u'mes termino'),
			'valor' 		: (u'valor'),
			'prorrateo' 	: (u'prorrateo'),
			'valor_prorrateo': (u'valor prorrateo'),
		}


class ServicioBasicoForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):

		contrato = kwargs.pop('contrato', None)
		super(ServicioBasicoForm, self).__init__(*args, **kwargs)

		if contrato is not None:

			locales_list = contrato.locales.all().values_list('id', flat=True)
			self.fields['local'].queryset = contrato.locales.all()
			self.fields['medidor'].queryset = Medidor.objects.filter(local__in=locales_list)

	class Meta:
		model 	= Servicio_Basico
		fields 	= '__all__'
		exclude = ['visible', 'creado_en']

		widgets = {
			'tipo'			: forms.Select(attrs={'class': 'form-control tipo-asd'}),
			'local'			: forms.Select(attrs={'class': 'form-control'}),
			'medidor'		: forms.Select(attrs={'class': 'form-control medidor-asd'}),
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
			'tipo'			: (u'Tipo'),
			'mes_inicio'	: (u'Meses Inicio'),
			'mes_termino'	: (u'Mes Termino'),
		}

		help_texts = {
			'tipo' 			: (u'tipo'),
			'mes_inicio' 	: (u'mes inicio'),
			'mes_termino' 	: (u'mes termino'),
			'valor' 		: (u'valor'),
		}



ArriendoDetalleFormSet 	= inlineformset_factory(Arriendo, Arriendo_Detalle, form=ArriendoDetalleForm, extra=1, can_delete=True)
ArriendoVariableFormSet = inlineformset_factory(Contrato, Arriendo_Variable, form=ArriendoVariableForm, extra=1, can_delete=True)
GastoComunFormSet 		= inlineformset_factory(Contrato, Gasto_Comun, form=GastoComunForm, extra=1, can_delete=True)
ServicioBasicoFormSet 	= inlineformset_factory(Contrato, Servicio_Basico, form=ServicioBasicoForm, extra=1, can_delete=True)


