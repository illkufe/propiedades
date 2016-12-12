from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from facturacion.models import *

class ParametrosFacturacionForms(ModelForm):

    def __init__(self, *args, **kwargs):

        super(ParametrosFacturacionForms, self).__init__(*args, **kwargs)

        self.fields['motor_emision'].queryset = MotorFacturacion.objects.all()

    class Meta:
        model   = ParametrosFacturacion
        fields  = ('codigo_conexion', 'motor_emision')

        widgets = {
            'codigo_conexion'	: forms.TextInput(attrs={'class': 'form-control'}),
            'motor_emision'		: forms.Select(attrs={'class': 'form-control'}),
        }

        error_messages = {
            'codigo_conexion' 	: {'required': 'campo requerido'},
            'motor_emision'     : {'required': 'campo requerido'},
        }

        labels = {
            'codigo_conexion'	    : 'Código Conexión',
            'motor_emision'	: 'Motor de Facturación',
        }

        help_texts = {
            'codigo_conexion' 	: 'Código de conexión, en el caso de IDTE el identificador de empresa.',
            'motor_emision' 	: 'Motor al cual pertenecen las conexiones de los Web Services a parametrizar.',
        }

class ConexionFacturacionForms(ModelForm):
    class Meta:
        model = ConexionFacturacion
        fields = '__all__'
        exclude= ('parametro_facturacion',)

        widgets = {
            'codigo_contexto'   : forms.TextInput(attrs={'class': 'form-control'}),
            'host'	            : forms.TextInput(attrs={'class': 'form-control'}),
            'url'               : forms.TextInput(attrs={'class': 'form-control'}),
            'puerto'            : forms.NumberInput(attrs={'class': 'form-control'}),
        }

        error_messages = {
            'codigo_contexto' 	: {'required': 'campo requerido'},
            'host'              : {'required': 'campo requerido'},
            'url'               : {'required': 'campo requerido'},
            'puerto'            : {'required': 'campo requerido'},
        }

        labels = {
            'codigo_contexto'	: 'Código Contexto',
            'host'	            : 'Host',
            'url'	            : 'URL',
            'puerto'	        : 'Puerto',
        }

        help_texts = {
            'codigo_contexto' 	: 'Nombre o código del contexto del Web Service',
            'host' 		        : 'Ip de servidor o nombre',
            'url'               : '6456tyert',
            'puerto' 		    : 'Puerto de conexión',
        }

ConexionFacturacionFormSet = inlineformset_factory(ParametrosFacturacion, ConexionFacturacion, form=ConexionFacturacionForms, extra=0, min_num=1, can_delete=True, validate_min=True)
