# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User, Group
from django.db.models import Q
from accounts.models import UserProfile
from administrador.models import Empresa
from activos.models import Activo, Nivel, Sector, Medidor
from .models import Local, Local_Tipo

class LocalTipoForm(forms.ModelForm):
	class Meta:
		model 	= Local_Tipo
		fields 	= ['nombre', 'descripcion']

		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows':'1'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},
			'descripcion' : {'required': 'Esta campo es requerido.'}
		}

		labels = {
			'descripcion': _(u'Descripción'),
		}


class LocalForm(forms.ModelForm):

	medidores = forms.ModelMultipleChoiceField(
		queryset=Medidor.objects.filter(estado=False),
		# queryset=Medidor.objects.filter(Q(estado=False) | Q(id__in=()))),
		required=False,
		widget=forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'})
		)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		super(LocalForm, self).__init__(*args, **kwargs)

		user 		= User.objects.get(pk=self.request.user.pk)
		profile 	= UserProfile.objects.get(user=user)
		activos 	= Activo.objects.filter(empresa_id=profile.empresa_id).values_list('id', flat=True)

		self.fields['activo'].queryset = Activo.objects.filter(empresa_id=profile.empresa_id)
		self.fields['local_tipo'].queryset = Local_Tipo.objects.filter(empresa_id=profile.empresa_id)
		self.fields['sector'].queryset = Sector.objects.filter(activo_id__in=activos)
		self.fields['nivel'].queryset = Nivel.objects.filter(activo_id__in=activos)


	class Meta:
		model 	= Local
		fields 	= ['nombre','codigo','metros_cuadrados','metros_lineales','metros_compartidos','metros_bodega','descripcion','activo','sector','nivel','local_tipo', 'medidores']

		widgets = {
			'nombre': forms.TextInput(attrs={'class': 'form-control'}),
			'codigo': forms.TextInput(attrs={'class': 'form-control'}),
			'metros_cuadrados': forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_lineales': forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_compartidos': forms.NumberInput(attrs={'class': 'form-control'}),
			'metros_bodega': forms.NumberInput(attrs={'class': 'form-control'}),
			'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
			'activo': forms.Select(attrs={'class': 'select2 form-control'}),
			'sector': forms.Select(attrs={'class': 'select2 form-control'}),
			'nivel': forms.Select(attrs={'class': 'select2 form-control'}),
			'local_tipo': forms.Select(attrs={'class': 'select2 form-control'}),
			'medidores': forms.SelectMultiple(attrs={'class': 'select2 form-control', 'multiple':'multiple'}),
		}

		error_messages = {
			'nombre' : {'required': 'Esta campo es requerido.'},
			'codigo' : {'required': 'Esta campo es requerido.'},
			'activo' : {'required': 'Esta campo es requerido.'},
			'sector' : {'required': 'Esta campo es requerido.'},
			'nivel' : {'required': 'Esta campo es requerido.'},
			'local_tipo' : {'required': 'Esta campo es requerido.'},
		}

		help_texts = {
			'nombre': _('...'),
			'codigo': _('...'),
			'metros_cuadrados': _('...'),
			'metros_lineales': _('...'),
			'metros_compartidos': _('...'),
			'metros_bodega': _('...'),
			'descripcion': _('...'),
			'activo': _('...'),
			'sector': _('...'),
			'nivel': _('...'),
			'local_tipo': _('...'),
			'medidores': _('...'),
		}

		labels = {
			'descripcion': _(u'Descripción'),
			'codigo': _(u'Código'),
			'local_tipo': _(u'Tipo de Local'),
		}



