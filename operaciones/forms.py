from django import forms
from utilidades.views import NumberField
from .models import *

class LecturaElectricidadForm(forms.ModelForm):

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido'}, help_text='Valor Asociado a la Lectura de Medidor')

	class Meta:

		model 	= Lectura_Electricidad
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'medidor_electricidad'	: forms.Select(attrs={'class': 'form-control'}),
			'mes'					: forms.Select(attrs={'class': 'form-control'}),
			'anio'					: forms.NumberInput(attrs={'class': 'form-control'}),
			'imagen_file'			: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'medidor_electricidad' 	: {'required': 'campo requerido'},
			'mes' 					: {'required': 'campo requerido'},
			'anio' 					: {'required': 'campo requerido'},
		}

		labels = {
			'anio'			: 'Año',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'medidor_electricidad'	: 'Medidor de Electricidad',
			'mes'					: 'Mes de Lectura',
			'anio'					: 'Año de Lectura',
			'imagen_file'			: 'Imagen Asociada a Lectura',
		}

class LecturaAguaForm(forms.ModelForm):

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido'}, help_text='Valor Asociado a la Lectura de Medidor')

	class Meta:

		model 	= Lectura_Agua
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'medidor_agua'	: forms.Select(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'anio'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'medidor_agua' 	: {'required': 'campo requerido'},
			'mes' 			: {'required': 'campo requerido'},
			'anio' 			: {'required': 'campo requerido'},
		}

		labels = {
			'anio'			: 'Año',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'medidor_agua'	: 'Medidor de Agua',
			'mes'			: 'Mes de Lectura',
			'anio'			: 'Año de Lectura',
			'imagen_file'	: 'Imagen Asociada a Lectura',
		}

class LecturaGasForm(forms.ModelForm):

	valor = NumberField(widget=forms.TextInput(attrs={'class': 'form-control'}), error_messages={'required': 'campo requerido'}, help_text='Valor Asociado a la Lectura de Medidor')

	class Meta:

		model 	= Lectura_Gas
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en', 'user', 'imagen_type', 'imagen_size']

		widgets = {
			'medidor_gas'	: forms.Select(attrs={'class': 'form-control'}),
			'mes'			: forms.Select(attrs={'class': 'form-control'}),
			'anio'			: forms.NumberInput(attrs={'class': 'form-control'}),
			'imagen_file'	: forms.FileInput(attrs={'class': 'file-format'}),
		}

		error_messages = {
			'medidor_gas' 	: {'required': 'campo requerido'},
			'mes' 			: {'required': 'campo requerido'},
			'anio' 			: {'required': 'campo requerido'},
		}

		labels = {
			'anio'			: 'Año',
			'imagen_file'	: 'Cargar Imagen',
		}

		help_texts = {
			'medidor_gas'	: 'Medidor de Gas',
			'mes'			: 'Mes de Lectura',
			'anio'			: 'Año de Lectura',
			'imagen_file'	: 'Imagen Asociada a Lectura',
		}

class GastoServicioBasicoForm(forms.ModelForm):

	valor = NumberField(
		widget = forms.TextInput(attrs={'class': 'form-control format-number'}),
		error_messages = {'required': 'campo requerido'},
		help_text = 'valor asociado al gasto',
		)

	moneda = forms.ModelChoiceField(
		queryset = Moneda.objects.filter(id__in=[3,5]),
		widget = forms.Select(attrs={'class': 'form-control moneda', 'data-table': 'false', 'onchange': 'cambio_format_moneda(this, 1)'}),
		error_messages = {'required': 'campo requerido'},
		help_text = 'moneda asociada al gasto',
		)

	def __init__(self, *args, **kwargs):

		self.request = kwargs.pop('request')

		super(GastoServicioBasicoForm, self).__init__(*args, **kwargs)

		self.fields['activo'].queryset = Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

	class Meta:

		model 	= Gasto_Servicio_Basico
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en']

		widgets = {
			'activo'	: forms.Select(attrs={'class': 'form-control'}),
			'tipo'		: forms.Select(attrs={'class': 'form-control'}),
			'mes'		: forms.Select(attrs={'class': 'form-control'}),
			'anio'		: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'activo' 	: {'required': 'campo requerido'},
			'tipo' 		: {'required': 'campo requerido'},
			'mes' 		: {'required': 'campo requerido'},
			'anio' 		: {'required': 'campo requerido'},
		}

		labels = {
			'activo'	: 'Activo',
			'tipo'		: 'Tipo de gasto',
			'mes'		: 'Mes',
			'anio'		: 'Año',
		}

		help_texts = {
			'activo'	: 'activo asociado el gasto',
			'tipo'		: 'tipo de gasto',
			'mes'		: 'mes del gasto',
			'anio'		: 'año del gasto',
		}

class TarifaServicioBasicoForm(forms.ModelForm):

	valor = NumberField(
		widget = forms.TextInput(attrs={'class': 'form-control format-number'}),
		error_messages = {'required': 'campo requerido'},
		help_text = 'valor de la tarifa',
		)

	def __init__(self, *args, **kwargs):

		self.request = kwargs.pop('request')

		super(TarifaServicioBasicoForm, self).__init__(*args, **kwargs)

		self.fields['activo'].queryset = Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

	class Meta:

		model 	= Tarifa_Servicio_Basico
		fields 	= '__all__'
		exclude = [ 'visible', 'creado_en']

		widgets = {
			'activo'	: forms.Select(attrs={'class': 'form-control'}),
			'tipo'		: forms.Select(attrs={'class': 'form-control'}),
			'mes'		: forms.Select(attrs={'class': 'form-control'}),
			'anio'		: forms.NumberInput(attrs={'class': 'form-control'}),
		}

		error_messages = {
			'activo' 	: {'required': 'campo requerido'},
			'tipo' 		: {'required': 'campo requerido'},
			'mes' 		: {'required': 'campo requerido'},
			'anio' 		: {'required': 'campo requerido'},
		}

		labels = {
			'activo'	: 'Activo',
			'tipo'		: 'Tipo de Tarifa',
			'mes'		: 'Mes',
			'anio'		: 'Año',
		}

		help_texts = {
			'activo'	: 'activo asociado a la tarifa',
			'tipo'		: 'tipo de tarifa',
			'mes'		: 'mes de la tarifa',
			'anio'		: 'año de la tarifa',
		}
