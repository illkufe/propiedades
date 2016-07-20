# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from accounts.models import UserProfile
from administrador.models import Empresa
from activos.models import Activo, Nivel, Sector

from .models import Local, Local_Tipo


class LocalTipoForm(forms.ModelForm):
	class Meta:
		model 	= Local_Tipo
		fields 	= ['nombre', 'descripcion']

		widgets = {
			'nombre'		: forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion'	: forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo es requerido'},
			'descripcion' 	: {'required': 'campo es requerido'}
		}

		labels = {
			'descripcion' 	: 'Descripción',
		}


class LocalForm(forms.ModelForm):

	# medidores = forms.ModelMultipleChoiceField(
	# 	queryset=Medidor.objects.filter(estado=False),
	# 	# queryset=Medidor.objects.filter(Q(estado=False) | Q(id__in=()))),
	# 	required=False,
	# 	widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'})
	# 	)

	
	def __init__(self, *args, **kwargs):
		# contrato = kwargs.pop('activo', None)
		super(LocalForm, self).__init__(*args, **kwargs)
		asd = kwargs.pop('activo')
		print (asd)
		# user 		= User.objects.get(pk=self.request.user.pk)
		# profile 	= UserProfile.objects.get(user=user)
		# if contrato is not None:
		# 	self.fields['local'].queryset = contrato.locales.all()



	# def __init__(self, *args, **kwargs):
	# 	self.request = kwargs.pop('request')
	# 	super(LocalForm, self).__init__(*args, **kwargs)

	# 	user 		= User.objects.get(pk=self.request.user.pk)
	# 	profile 	= UserProfile.objects.get(user=user)
	# 	activos 	= Activo.objects.filter(empresa_id=profile.empresa_id).values_list('id', flat=True)

	# 	self.fields['activo'].queryset 		= Activo.objects.filter(empresa_id=profile.empresa_id)
	# 	self.fields['local_tipo'].queryset 	= Local_Tipo.objects.filter(empresa_id=profile.empresa_id)
	# 	self.fields['sector'].queryset 		= Sector.objects.filter(activo_id__in=activos)
	# 	self.fields['nivel'].queryset		= Nivel.objects.filter(activo_id__in=activos)


	class Meta:
		model 	= Local
		fields 	= '__all__'
		exclude = ['creado_en', 'visible']

		widgets = {
			'nombre'				: forms.TextInput(attrs={'class': 'form-control'}),
			'codigo'				: forms.TextInput(attrs={'class': 'form-control'}),
			'metros_cuadrados'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_lineales'		: forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_compartidos'	: forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_bodega'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'descripcion'			: forms.TextInput(attrs={'class': 'form-control'}),
			'activo'				: forms.Select(attrs={'class': 'select2 form-control'}),
			'sector'				: forms.Select(attrs={'class': 'select2 form-control'}),
			'nivel'					: forms.Select(attrs={'class': 'select2 form-control'}),
			'local_tipo'			: forms.Select(attrs={'class': 'select2 form-control'}),
			'prorrateo'				: forms.CheckboxInput(attrs={'class': 'form-control prorrateo'}),
		}

		error_messages = {
			'nombre' 		: {'required': 'campo es requerido'},
			'codigo' 		: {'required': 'campo es requerido'},
			'activo' 		: {'required': 'campo es requerido'},
			'sector' 		: {'required': 'campo es requerido'},
			'nivel' 		: {'required': 'campo es requerido'},
			'local_tipo' 	: {'required': 'campo es requerido'},
		}

		help_texts = {
			'nombre'				: '...',
			'codigo'				: '...',
			'metros_cuadrados'		: '...',
			'metros_lineales'		: '...',
			'metros_compartidos'	: '...',
			'metros_bodega'			: '...',
			'descripcion'			: '...',
			'activo'				: '...',
			'sector'				: '...',
			'nivel'					: '...',
			'local_tipo'			: '...',
		}

		labels = {
			'descripcion'	: 'Descripción',
			'codigo'		: 'Código',
			'local_tipo'	: 'Tipo de Local',
		}



