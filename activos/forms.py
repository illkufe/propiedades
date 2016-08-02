# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group
from utilidades.views import NumberField

from accounts.models import UserProfile
from administrador.models import Empresa
from locales.models import Local, Local_Tipo, Medidor_Electricidad, Medidor_Agua, Medidor_Gas, Gasto_Servicio
from .models import Activo, Sector, Nivel, Gasto_Mensual


class ActivoForm(forms.ModelForm):

	cabidad_terreno 		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	cabidad_construccion 	= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	avaluo_comercial 		= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	contibuciones 			= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	precio_compra 			= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	valor_tasacion 			= NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	tasacion_fiscal 		= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})
	fecha_firma_nomina 		= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	fecha_servicio 			= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
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
			'inscripcion'			: forms.TextInput(attrs={'class': 'form-control'}),
			'vendedor'				: forms.TextInput(attrs={'class': 'form-control'}),
			'rut_vendedor'			: forms.TextInput(attrs={'class': 'form-control format-rut'}),
			'datos_escritura'		: forms.TextInput(attrs={'class': 'form-control'}),
			'nomina_numero'			: forms.TextInput(attrs={'class': 'form-control'}),
			'nomina_repertorio'		: forms.TextInput(attrs={'class': 'form-control'}),
			'nomina_fojas'			: forms.TextInput(attrs={'class': 'form-control'}),
			'servicio_nomina'		: forms.TextInput(attrs={'class': 'form-control'}),
			'servicio_repertorio'	: forms.TextInput(attrs={'class': 'form-control'}),
			'servicio_fojas'		: forms.TextInput(attrs={'class': 'form-control'}),

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

class ElectricidadForm(forms.ModelForm):

	potencia 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	potencia_presente 	= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))
	potencia_fuera 		= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))

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
			'nombre'				: '...',
			'numero_rotulo'			: '...',
			'tarifa_electricidad'	: '...',
		}

		labels = {
			'numero_rotulo'			: 'Nº Rótulo',
			'tarifa_electricidad'	: 'Tarifa',
		}

class AguaForm(forms.ModelForm):

	potencia 			= NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))

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
			'nombre'			: '...',
			'numero_rotulo'		: '...',
		}

		labels = {
			'numero_rotulo'		: 'Nº Rótulo',
		}

class GasForm(forms.ModelForm):

	potencia = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}))

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
			'nombre'			: '...',
			'numero_rotulo'		: '...',
		}

		labels = {
			'numero_rotulo'		: 'Nº Rótulo',
		}

class LocalForm(forms.ModelForm):

	metros_cuadrados = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})
	metros_lineales = NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})
	metros_compartidos = NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})
	metros_bodega = NumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-control format-number'}), error_messages={'required': 'campo requerido'})

	def __init__(self, *args, **kwargs):

		self.request 	= kwargs.pop('request')
		activo_id 		= kwargs.pop('activo_id', None)
		user 			= User.objects.get(pk=self.request.user.pk)
		profile 		= UserProfile.objects.get(user=user)

		super(LocalForm, self).__init__(*args, **kwargs)

		activo = Activo.objects.get(id=activo_id)

		self.fields['local_tipo'].queryset 	= Local_Tipo.objects.filter(empresa=profile.empresa)
		self.fields['sector'].queryset 		= Sector.objects.filter(activo=activo)
		self.fields['nivel'].queryset 		= Nivel.objects.filter(activo=activo)

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
		}

		error_messages = {
			'nombre' 			: {'required': 'campo requerido'},
			'codigo' 			: {'required': 'campo requerido'},
			'sector' 			: {'required': 'campo requerido'},
			'nivel' 			: {'required': 'campo requerido'},
			'local_tipo' 		: {'required': 'campo requerido'},
		}

		help_texts = {
			'nombre'			: '...',
			'codigo'			: '...',
			'descripcion'		: '...',
			'sector'			: '...',
			'nivel'				: '...',
			'local_tipo'		: '...',
		}

		labels = {
			'descripcion'	: 'Descripción',
			'codigo'		: 'Código',
			'local_tipo'	: 'Tipo de Local',
		}

SectorFormSet 		= inlineformset_factory(Activo, Sector, form=SectorForm, extra=1, can_delete=True)
NivelFormSet 		= inlineformset_factory(Activo, Nivel, form=NivelForm, extra=1, can_delete=True)
AguaFormSet 		= inlineformset_factory(Local, Medidor_Agua, form=AguaForm, extra=1, can_delete=True)
GasFormSet 			= inlineformset_factory(Local, Medidor_Gas, form=GasForm, extra=1, can_delete=True)
ElectricidadFormSet = inlineformset_factory(Local, Medidor_Electricidad, form=ElectricidadForm, extra=1, can_delete=True)


