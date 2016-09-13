from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from facturacion.models import *

class ParametrosFacturacionForms(ModelForm):
    class Meta:
        model = ParametrosFacturacion
        fields = ('id', 'persona', 'codigo_conexion')

        widgets = {
            "persona": forms.TextInput(attrs={'class': 'form-control', 'type': 'hidden'}),
        }

    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    codigo_conexion = forms.CharField(
                                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                                        label='Código Conexión')


class ConexionFacturacionForms(ModelForm):
    class Meta:
        model = ConexionFacturacion
        fields = '__all__'
        exclude= ('parametro_facturacion',)

    codigo_contexto = forms.CharField(
                                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                                        label='Código Contexto')

    host = forms.CharField(
                            widget=forms.TextInput(attrs={'class': 'form-control format-ip'}),
                            label='Host')

    url = forms.CharField(
                            widget=forms.TextInput(attrs={'class': 'form-control'}),
                            label='URL', strip=True)

    puerto = forms.IntegerField(
                                widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                label='Puerto')

# ConexionFacturacionFormSet = inlineformset_factory(ParametrosFacturacion, ConexionFacturacion, ConexionFacturacionForms, extra=1, can_delete=True)