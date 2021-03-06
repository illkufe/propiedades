from django import forms
from datetime import datetime, timedelta

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

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control format-number', 'data-es-moneda': 'true', 'data-moneda': '', 'data-select': 'false'}), label='Valor', error_messages={'required': 'campo requerido'}, help_text='Monto de la venta')

	def __init__(self, *args, **kwargs):

		request = kwargs.pop('request', None)

		super(VentasForm, self).__init__(*args, **kwargs)

		contrato	= Contrato.objects.filter(cliente_id=request.user.userprofile.cliente, visible=True).values_list('locales', flat=True)
		locales 	= Local.objects.filter(id__in=contrato, visible=True)


		self.fields['local'].queryset = locales
	def clean(self):

		fecha_inicio = self.cleaned_data.get('fecha_inicio')

		fecha_hoy = datetime.now().date()

		fecha_hasta = datetime.now().date() - timedelta(days=5)

		if fecha_inicio > fecha_hoy:
			self.add_error('fecha_inicio', 'Fecha no puede ser mayor a la fecha actual')

		if  fecha_inicio < fecha_hasta  or fecha_inicio > fecha_hoy:
			self.add_error('fecha_inicio', 'Fecha no puede ser menor a 5 días desde fecha actual')

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
