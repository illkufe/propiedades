from django import forms
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from facturacion.models import *

class ParametrosFacturacionForms(ModelForm):

    def __init__(self, *args, **kwargs):

        super(ParametrosFacturacionForms, self).__init__(*args, **kwargs)

        self.fields['motor_emision'].queryset = Motor_Factura.objects.all()

    class Meta:
        model   = Parametro_Factura
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
        model = Conexion_Factura
        fields = '__all__'
        exclude= ('parametro_facturacion',)

        widgets = {
            'host'	                : forms.TextInput(attrs={'class': 'form-control'}),
            'puerto'                : forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre_contexto'       : forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_web_service'    : forms.TextInput(attrs={'class': 'form-control'}),

        }

        error_messages = {

            'host'                  : {'required': 'campo requerido'},
            'puerto'                : {'required': 'campo requerido'},
            'nombre_contexto'       : {'required': 'campo requerido'},
            'nombre_web_service'    : {'required': 'campo requerido'},
        }

        labels = {

            'host'	                : 'Host',
            'puerto'	            : 'Puerto',
            'nombre_contexto'	    : 'Nombre contexto',
            'nombre_web_service'    : 'Nombre web service',

        }

        help_texts = {

            'host' 		            : 'Ip de servidor o nombre',
            'puerto' 		        : 'Puerto de conexión',
            'nombre_contexto'       : 'Nombre o código del contexto del web service',
            'nombre_web_service'    : 'Nombre de web service',

        }

ConexionFacturacionFormSet = inlineformset_factory(Parametro_Factura, Conexion_Factura, form=ConexionFacturacionForms, extra=0, min_num=1, can_delete=True, validate_min=True)
