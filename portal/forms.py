from django import forms
from datetime import datetime

from contrato.models import Contrato
from locales.models import Venta, Local
from utilidades.views import NumberField

class VentasForm(forms.ModelForm):

	fecha_inicio = forms.DateField(
									input_formats	= ['%d/%m/%Y'],
									widget			= forms.TextInput(attrs={'class': 'form-control format-date'}),
									label			= 'Fecha',
									error_messages	= {'required': 'campo requerido', 'invalid': 'campo invalido'},
									help_text		= 'Fecha de ingreso de la venta'
	)

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number'}), label='Valor', error_messages={'required': 'campo requerido'}, help_text='Monto de la venta')

	def __init__(self, *args, **kwargs):

		request = kwargs.pop('request', None)

		super(VentasForm, self).__init__(*args, **kwargs)

		contrato	= Contrato.objects.filter(cliente_id=request.user.userprofile.cliente, visible=True).values_list('locales', flat=True)
		locales 	= Local.objects.filter(id__in=contrato, visible=True)


		self.fields['local'].queryset = locales

	class Meta:
		model 	= Venta
		fields 	= '__all__'
		exclude = ['creado_en', 'visible', 'periodicidad', 'fecha_termino']

		widgets = {
			'local'		: forms.Select(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'local' 	: {'required': 'campo requerido'},
		}

		help_texts = {
			'local'			: 'local a ingresar venta diaria',
		}

		labels = {
			'local'		: 'Local',
		}
