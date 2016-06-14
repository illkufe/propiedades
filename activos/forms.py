# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User, Group

from accounts.models import UserProfile
from administrador.models import Empresa
from locales.models import Local, Local_Tipo

from .models import Activo, Sector, Nivel, Medidor_Electricidad, Medidor_Agua, Medidor_Gas

class ActivoForm(forms.ModelForm):

	fecha_firma_nomina 	= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	fecha_servicio 		= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	fecha_adquisicion 	= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))
	fecha_tasacion 		= forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.TextInput(attrs={'class': 'form-control format-date'}))

	class Meta:
		model 	= Activo
		fields 	= '__all__'
		exclude = ['empresa', 'creado_en', 'visible']

		widgets = {
			# identificacion Activo
			'nombre'				: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'				: forms.TextInput(attrs={'class': 'form-control'}),
			'tipo'					: forms.TextInput(attrs={'class': 'form-control'}),
			'unidad_negocio'		: forms.Select(attrs={'class': 'form-control'}),
			'direccion'				: forms.TextInput(attrs={'class': 'form-control'}),
			'comuna'				: forms.TextInput(attrs={'class': 'form-control'}),
			'ciudad'				: forms.TextInput(attrs={'class': 'form-control'}),
			'cabidad_terreno'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'cabidad_construccion'	: forms.NumberInput(attrs={'class': 'form-control'}),

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
			'tasacion_fiscal'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'avaluo_comercial'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'contibuciones'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'precio_compra'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'valor_tasacion'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'tasacion_por'		: forms.TextInput(attrs={'class': 'form-control'}),
			'leasing'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
			'hipoteca'			: forms.CheckboxInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'Esta campo es requerido.'},
			'codigo' 		: {'required': 'Esta campo es requerido.'},
			'unidad_negocio': {'required': 'Esta campo es requerido.'},
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
			'unidad_negocio' 		: '...',
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
			'nombre' : {'required': 'Esta campo es requerido.'},
			'codigo' : {'required': 'Esta campo es requerido.'},
		}

class ActivoMedidoForm(forms.ModelForm):

	class Meta:
		model 	= Activo
		fields 	= ['id']

class ElectricidadForm(forms.ModelForm):

	class Meta:
		model 	= Medidor_Electricidad
		fields 	= '__all__'
		exclude = ['creado_en', 'visible']

		widgets = {
			'nombre'				: forms.TextInput(attrs={'class': 'form-control'}),
			'numero_rotulo'			: forms.TextInput(attrs={'class': 'form-control'}),
			'potencia'				: forms.NumberInput(attrs={'class': 'form-control'}),
			'potencia_presente'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'potencia_fuera'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'tarifa_electricidad'	: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'Esta campo es requerido.'},
			'numero_rotulo' : {'required': 'Esta campo es requerido.'},
		}

		help_texts = {
            'nombre'				: '...',
            'numero_rotulo'			: '...',
            'potencia'				: '...',
            'potencia_presente'		: '...',
            'potencia_fuera'		: '...',
            'tarifa_electricidad'	: '...',
        }

		labels = {
			'numero_rotulo'			: 'Nº Rótulo',
			'tarifa_electricidad'	: 'Tarifa',
		}

class AguaForm(forms.ModelForm):

	class Meta:
		model 	= Medidor_Agua
		fields 	= '__all__'
		exclude = ['creado_en', 'visible']

		widgets = {
			'nombre'			: forms.TextInput(attrs={'class': 'form-control'}),
			'numero_rotulo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'potencia'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'potencia_presente'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'potencia_fuera'	: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'Esta campo es requerido.'},
			'numero_rotulo' : {'required': 'Esta campo es requerido.'},
		}

		help_texts = {
            'nombre'			: '...',
            'numero_rotulo'		: '...',
            'potencia'			: '...',
            'potencia_presente'	: '...',
            'potencia_fuera'	: '...',
        }

		labels = {
			'numero_rotulo'	: 'Número Rótulo',
		}

class GasForm(forms.ModelForm):

	class Meta:
		model 	= Medidor_Gas
		fields 	= '__all__'
		exclude = ['creado_en', 'visible']

		widgets = {
			'nombre'			: forms.TextInput(attrs={'class': 'form-control'}),
			'numero_rotulo'		: forms.TextInput(attrs={'class': 'form-control'}),
			'potencia'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'potencia_presente'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'potencia_fuera'	: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'Esta campo es requerido.'},
			'numero_rotulo' : {'required': 'Esta campo es requerido.'},
		}

		help_texts = {
            'nombre'			: '...',
            'numero_rotulo'		: '...',
            'potencia'			: '...',
            'potencia_presente'	: '...',
            'potencia_fuera'	: '...',
        }

		labels = {
			'numero_rotulo'	: 'Número Rótulo',
		}


class LocalForm(forms.ModelForm):

	# medidores = forms.ModelMultipleChoiceField(
	# 	queryset=Medidor.objects.filter(estado=False),
	# 	# queryset=Medidor.objects.filter(Q(estado=False) | Q(id__in=()))),
	# 	required=False,
	# 	widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'})
	# 	)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		super(LocalForm, self).__init__(*args, **kwargs)

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		activos 	= Activo.objects.filter(empresa_id=profile.empresa_id).values_list('id', flat=True)

		self.fields['local_tipo'].queryset = Local_Tipo.objects.filter(empresa_id=profile.empresa_id)
		self.fields['sector'].queryset = Sector.objects.filter(activo_id__in=activos)
		self.fields['nivel'].queryset = Nivel.objects.filter(activo_id__in=activos)


	class Meta:
		model 	= Local
		fields 	= ['nombre','codigo','metros_cuadrados','metros_lineales','metros_compartidos','metros_bodega','local_tipo_volumen', 'descripcion','sector','nivel','local_tipo', 'medidores']

		widgets = {
			'nombre'			: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'			: forms.TextInput(attrs={'class': 'form-control'}),
			'metros_cuadrados'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_lineales'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_compartidos': forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_bodega'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'local_tipo_volumen': forms.Select(attrs={'class': 'select2 form-control'}),
			'descripcion'		: forms.TextInput(attrs={'class': 'form-control'}),
			'sector'			: forms.Select(attrs={'class': 'select2 form-control'}),
			'nivel'				: forms.Select(attrs={'class': 'select2 form-control'}),
			'local_tipo'		: forms.Select(attrs={'class': 'select2 form-control'}),
			'medidores'			: forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		error_messages = {
			'nombre' 				: {'required': 'Esta campo es requerido.'},
			'codigo' 				: {'required': 'Esta campo es requerido.'},
			'sector' 				: {'required': 'Esta campo es requerido.'},
			'nivel' 				: {'required': 'Esta campo es requerido.'},
			'local_tipo' 			: {'required': 'Esta campo es requerido.'},
			'local_tipo_volumen' 	: {'required': 'Esta campo es requerido.'},
		}

		help_texts = {
			'nombre'			: '...',
			'codigo'			: '...',
			'metros_cuadrados'	: '...',
			'metros_lineales'	: '...',
			'metros_compartidos': '...',
			'metros_bodega'		: '...',
			'descripcion'		: '...',
			'sector'			: '...',
			'nivel'				: '...',
			'local_tipo'		: '...',
			'medidores'			: '...',
		}

		labels = {
			'descripcion'	: 'Descripción',
			'codigo'		: 'Código',
			'local_tipo'	: 'Tipo de Local',
		}


SectorFormSet 		= inlineformset_factory(Activo, Sector, form=SectorForm, extra=1, can_delete=True)
NivelFormSet 		= inlineformset_factory(Activo, Nivel, form=NivelForm, extra=1, can_delete=True)
AguaFormSet 		= inlineformset_factory(Activo, Medidor_Agua, form=AguaForm, extra=1, can_delete=True)
GasFormSet 			= inlineformset_factory(Activo, Medidor_Gas, form=GasForm, extra=1, can_delete=True)
ElectricidadFormSet = inlineformset_factory(Activo, Medidor_Electricidad, form=ElectricidadForm, extra=1, can_delete=True)


