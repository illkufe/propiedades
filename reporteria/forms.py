# -*- coding: utf-8 -*-
from django import forms
from accounts.models import UserProfile
from activos.models import *
from administrador.models import Cliente
from locales.models import Local
from conceptos.models import Concepto
from .models import *

class FiltroIngresoActivo(forms.Form):
    PERIODICIDAD = (
        (0, 'MENSUAL'),
        (1, 'TRIMESTRAL'),
        (2, 'SEMESTRAL'),
        (3, 'ANUAL'),
    )

    CANTIDAD_PERIODO = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
        (11, 11),
        (12, 12),
    )

    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request')
        user            = User.objects.get(pk=self.request.user.pk)
        profile         = UserProfile.objects.get(user=user)

        super(FiltroIngresoActivo, self).__init__(*args, **kwargs)

        activos = Activo.objects.filter(empresa=self.request.user.userprofile.empresa).values_list('id', flat=True)

        self.fields['activo'].queryset      = Activo.objects.filter(empresa=profile.empresa, visible=True)
        self.fields['cliente'].queryset     = Cliente.objects.filter(empresa=profile.empresa, visible=True)
        self.fields['conceptos'].queryset   = Concepto.objects.filter(empresa=profile.empresa, visible=True)


    activo = forms.ModelChoiceField(queryset=None, empty_label='Todos', required=False, widget=forms.Select(attrs={'class': 'form-control'}), label='Activos', help_text='Activos de la Empresa')

    periodos = forms.ChoiceField(choices=PERIODICIDAD,required=False, widget=forms.Select(attrs={'class': 'form-control'}),
                                    label='Periodos', help_text='Periodos de Tiempo')

    cantidad_periodos = forms.ChoiceField(choices=CANTIDAD_PERIODO, required=False, widget=forms.Select(attrs={'class': 'form-control'}),
                                    label='Cantidad Periodos', help_text='Cantidad de periodos antecesores al periodo actual')

    cliente = forms.ModelChoiceField(queryset=None,empty_label='Todos', required=False, widget=forms.Select(attrs={'class': 'form-control'}),
                                    label='Clientes', help_text='Clientes de la Empresa')
    conceptos = forms.ModelChoiceField(queryset=None,empty_label='Todos', required=False, widget=forms.Select(attrs={'class': 'form-control'}),
                                    label='Conceptos', help_text='Conceptos manejados por la empresa')
