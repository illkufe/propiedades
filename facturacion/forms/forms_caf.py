from django import forms
from django.forms import ModelForm
from facturacion.models import Folio_Documento_Electronico

class FiltroFoliosDocumentosForm(ModelForm):
    class Meta:
        model= Folio_Documento_Electronico
        fields= ['tipo_dte']

        widgets = {
            'tipo_dte': forms.TextInput(
                attrs={'placeholder': 'tipo DTE', 'class': 'form-control col1_filter', 'data-column': 1,
                       'onkeyup': "search_column_table_reference_products(this, '#filtrofolio')"}),
        }

        labels = {
            'tipo_dte': ('Tipo Documento Electrónico'),
        }