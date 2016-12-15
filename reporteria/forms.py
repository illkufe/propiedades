# -*- coding: utf-8 -*-
from django import forms
from accounts.models import UserProfile
from activos.models import *
from administrador.models import Cliente, Clasificacion
from locales.models import Local_Tipo
from conceptos.models import Concepto
from .models import *


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

PERIODICIDAD = (
    (1, 'MENSUAL'),
    (2, 'TRIMESTRAL'),
    (3, 'SEMESTRAL'),
    (4, 'ANUAL'),
)

class FormIngresoMetrosCuadrados(forms.Form):

	activos = forms.ModelChoiceField(
		queryset = None,
		empty_label = None,
		widget = forms.Select(attrs={'class': 'form-control selectpicker', 'multiple':'multiple', 'data-actions-box':'true', 'title':'seleccionar'}),
		label = 'Activos',
		help_text = 'activos de la empresa',
		)

	cantidad = forms.ChoiceField(
		choices = CANTIDAD_PERIODO[:6],
		widget = forms.Select(attrs={'class': 'form-control selectpicker', 'title':'seleccionar'}),
		label = 'Cantidad de Periodos',
		help_text = 'cantidad de periodos antecesores al período actual'
		)

	conceptos = forms.ModelChoiceField(
		queryset = None,
		empty_label = None,
		widget = forms.Select(attrs={'class': 'form-control selectpicker', 'multiple':'multiple', 'data-actions-box':'true', 'title':'seleccionar'}),
		label = 'Conceptos',
		help_text = 'conceptos de la empresa',
		)

	def __init__(self, *args, **kwargs):

		self.request = kwargs.pop('request')

		super(FormIngresoMetrosCuadrados, self).__init__(*args, **kwargs)

		self.fields['activos'].queryset 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		self.fields['conceptos'].queryset 	= Concepto.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)

class FiltroIngresoActivo(forms.Form):


    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request')
        user            = User.objects.get(pk=self.request.user.pk)
        profile         = UserProfile.objects.get(user=user)

        super(FiltroIngresoActivo, self).__init__(*args, **kwargs)

        self.fields['activo'].queryset      = Activo.objects.filter(empresa=profile.empresa, visible=True)
        self.fields['cliente'].queryset     = Cliente.objects.filter(empresa=profile.empresa, visible=True)
        self.fields['conceptos'].queryset   = Concepto.objects.filter(empresa=profile.empresa, visible=True)


    activo = forms.ModelChoiceField(
        queryset    = None,
        empty_label = None,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'              : 'form-control selectpicker',
                                   'multiple'           : 'multiple',
                                   'data-actions-box'   : 'true',
                                   'title'              : 'seleccionar'
                            }
                        ),
        label       = 'Activos',
        help_text   = 'Activos de la Empresa')

    periodos = forms.ChoiceField(
        choices     = PERIODICIDAD,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'  : 'form-control selectpicker',
                                   'title'  : 'seleccionar'
                            }
                        ),
        label       = 'Periodos',
        help_text   = 'Periodos de Tiempo'
        )

    cantidad_periodos = forms.ChoiceField(
        choices     = CANTIDAD_PERIODO,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'  : 'form-control selectpicker',
                                   'title'  : 'seleccionar'
                            }
                        ),
        label       = 'Cantidad Periodos',
        help_text   = 'Cantidad de periodos antecesores al periodo actual'
    )

    cliente = forms.ModelChoiceField(
        queryset    = None,
        empty_label = None,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'              : 'form-control selectpicker',
                                   'multiple'           : 'multiple',
                                   'data-actions-box'   : 'true',
                                   'title'              : 'seleccionar'
                            }
                        ),
        label       = 'Clientes',
        help_text   = 'Clientes de la Empresa'
    )

    conceptos = forms.ModelChoiceField(
        queryset    = None,
        empty_label = None,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'              : 'form-control selectpicker',
                                   'multiple'           :'multiple',
                                   'data-actions-box'   :'true',
                                   'title'              :'seleccionar'
                            }
                        ),
        label       = 'Conceptos',
        help_text   = 'Conceptos manejados por la empresa')

class FiltroIngresoClasificacion(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request')
        user            = User.objects.get(pk=self.request.user.pk)
        profile         = UserProfile.objects.get(user=user)

        super(FiltroIngresoClasificacion, self).__init__(*args, **kwargs)

        self.fields['clasificacion'].queryset   = Clasificacion.objects.filter(empresa=profile.empresa, visible=True, tipo_clasificacion_id=1)
        self.fields['conceptos'].queryset       = Concepto.objects.filter(empresa=profile.empresa, visible=True)


    clasificacion   = forms.ModelChoiceField(
        queryset    = None,
        empty_label = None,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'              : 'form-control selectpicker',
                                   'multiple'           : 'multiple',
                                   'data-actions-box'   : 'true',
                                   'title'              : 'seleccionar'
                            }
                        ),
        label       = 'Clasificaciones',
        help_text   = 'Clasificaciones de la Empresa')

    periodos        = forms.ChoiceField(
        choices     = PERIODICIDAD,
        required    = False,
        widget      = forms.Select(
                            attrs={'class': 'form-control selectpicker', 'title':'seleccionar'}
                        ),
        label       = 'Periodos',
        help_text   = 'Periodos de Tiempo')

    cantidad_periodos   = forms.ChoiceField(
        choices     = CANTIDAD_PERIODO,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'  : 'form-control selectpicker',
                                   'title'  : 'seleccionar'
                            }
                        ),
        label       = 'Cantidad Periodos',
        help_text   = 'Cantidad de periodos antecesores al periodo actual')

    conceptos       = forms.ModelChoiceField(
        queryset    = None,
        empty_label = None,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'              : 'form-control selectpicker',
                                   'multiple'           : 'multiple',
                                   'data-actions-box'   : 'true',
                                   'title'              : 'seleccionar'
                                   }
                        ),
        label       = 'Conceptos',
        help_text   = 'Conceptos manejados por la empresa')

class FiltroVacancia(forms.Form):


    AGRUPADOR = (
        (1, 'Todos'),
        (2,'Tipo de Local'),
        (3, 'Nivel'),
        (4, 'Sector'),
    )
    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request')
        user            = User.objects.get(pk=self.request.user.pk)
        profile         = UserProfile.objects.get(user=user)

        super(FiltroVacancia, self).__init__(*args, **kwargs)

        self.fields['activo'].queryset = Activo.objects.filter(empresa=profile.empresa, visible=True)

    activo              = forms.ModelChoiceField(
        queryset        =None,
        empty_label     =None,
        required        =False,
        widget          =forms.Select(
                                attrs={'class'              : 'form-control selectpicker',
                                       'multiple'           : 'multiple',
                                       'data-actions-box'   : 'true',
                                       'title'              : 'seleccionar'
                                }
                            ),
        label           ='Activos',
        help_text       ='Activos de la Empresa')


    agrupador           = forms.ChoiceField(
        choices         = AGRUPADOR,
        required        = False,
        widget          = forms.Select(
                                attrs={'class'  : 'form-control selectpicker',
                                       'title'  : 'seleccionar'
                                }
                            ),
        label           = 'Agrupador',
        help_text       = 'Agrupado de Vacancia de Activos')

    periodos            = forms.ChoiceField(
        choices         = PERIODICIDAD,
        required        = False,
        widget          = forms.Select(
                                attrs={'class'  : 'form-control selectpicker',
                                       'title'  : 'seleccionar'
                                }
                            ),
        label           = 'Periodos',
        help_text       = 'Periodos de Tiempo')

    cantidad_periodos   = forms.ChoiceField(
        choices         = CANTIDAD_PERIODO,
        required        = False,
        widget          = forms.Select(
                                    attrs={ 'class'  : 'form-control selectpicker',
                                            'title'  : 'seleccionar'
                                    }
                                ),
        label           = 'Cantidad Periodos',
        help_text       = 'Cantidad de periodos antecesores al periodo actual')

class FiltroVencimientoContrato(forms.Form):


    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request')
        user            = User.objects.get(pk=self.request.user.pk)
        profile         = UserProfile.objects.get(user=user)

        super(FiltroVencimientoContrato, self).__init__(*args, **kwargs)
        self.fields['activo'].queryset      = Activo.objects.filter(empresa=profile.empresa, visible=True)
        self.fields['cliente'].queryset     = Cliente.objects.filter(empresa=profile.empresa, visible=True)
        self.fields['tipo_local'].queryset  = Local_Tipo.objects.filter(empresa=profile.empresa, visible=True)

    activo              = forms.ModelChoiceField(
        queryset        = None,
        empty_label     = None,
        required        = False,
        widget          = forms.Select(
                                attrs={ 'class'                 : 'form-control selectpicker',
                                        'multiple'              : 'multiple',
                                        'data-actions-box'      : 'true',
                                        'title'                 : 'seleccionar'
                                }
                             ),
        label           = 'Activos',
        help_text       = 'Activos de la Empresa'
    )

    tipo_local      = forms.ModelChoiceField(
        queryset        = None,
        empty_label     = None,
        required        = False,
        widget          = forms.Select(
                                attrs={'class'              : 'form-control selectpicker',
                                       'multiple'           : 'multiple',
                                       'data-actions-box'   : 'true',
                                       'title'              : 'seleccionar'
                                }
                            ),
        label           = 'Tipos de Locales',
        help_text       = 'Tipos de Locales manejados por la empresa'
    )

    cliente         = forms.ModelChoiceField(
        queryset        = None,
        empty_label     = None,
        required        = False,
        widget          = forms.Select(
                                attrs={'class'              : 'form-control selectpicker',
                                       'multiple'           : 'multiple',
                                       'data-actions-box'   : 'true',
                                       'title'              : 'seleccionar'
                                }
                            ),
        label           = 'Clientes',
        help_text       = 'Clientes de la Empresa'
    )

    periodos = forms.ChoiceField(
        choices         = PERIODICIDAD,
        required        = False,
        widget          = forms.Select(
                                attrs={ 'class'  : 'form-control selectpicker',
                                        'title'  : 'seleccionar'
                                }
                            ),
        label           = 'Periodos',
        help_text       = 'Periodos de Tiempo'
    )

    cantidad_periodos = forms.ChoiceField(
        choices         = CANTIDAD_PERIODO,
        required        = False,
        widget          = forms.Select(
                                attrs={ 'class'  : 'form-control selectpicker',
                                        'title'  : 'seleccionar'
                                }
                            ),
        label           = 'Cantidad Periodos',
        help_text       = 'Cantidad de periodos antecesores al periodo actual'
    )

class FiltroMCuadradosClasificacion(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request    = kwargs.pop('request')
        user            = User.objects.get(pk=self.request.user.pk)
        profile         = UserProfile.objects.get(user=user)

        super(FiltroMCuadradosClasificacion, self).__init__(*args, **kwargs)

        self.fields['activo'].queryset          = Activo.objects.filter(empresa=profile.empresa, visible=True)
        self.fields['clasificacion'].queryset   = Clasificacion.objects.filter(empresa=profile.empresa, visible=True, tipo_clasificacion_id=1)


    activo          = forms.ModelChoiceField(
        queryset    = None,
        empty_label = None,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'              : 'form-control selectpicker',
                                   'multiple'           : 'multiple',
                                   'data-actions-box'   : 'true',
                                   'title'              : 'seleccionar'
                            }
                        ),
        label       = 'Activos',
        help_text   = 'Activos de la Empresa'
    )

    clasificacion   = forms.ModelChoiceField(
        queryset    = None,
        empty_label = None,
        required    = False,
        widget      = forms.Select(
                            attrs={'class'              : 'form-control selectpicker',
                                   'multiple'           : 'multiple',
                                   'data-actions-box'   : 'true',
                                   'title'              : 'seleccionar'
                            }
                        ),
        label       = 'Clasificaciones',
        help_text   = 'Clasificaciones de la Empresa'
    )
