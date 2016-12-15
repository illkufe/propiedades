from django import template

register = template.Library()

@register.filter
def meses(valor):

	meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

	return meses[int(valor)-1]

@register.filter
def formato_moneda(valor):

	moneda = '${:,.0f}'.format(valor)
	
	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda

@register.filter
def formato_numero(valor):

	moneda = '{:,.4f}'.format(valor)
	
	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda

@register.filter
def formato_numero_sin_miles_decimales(valor):

	moneda = '{:.0f}'.format(valor)
    #
	# moneda = moneda.replace('.', ',')


	return moneda


@register.filter
def formato_boolean(valor):

	if valor is True:
		return 'Si'
	else:
		return 'No'

@register.filter
def calculo_total(valor):
	#TODO eliminar cuando se creen atributos en la tabla Facturas.

	valor_iva	= valor * (19 / 100)
	valor_total	= valor + valor_iva

	return formato_moneda(valor_total)

@register.filter
def is_number(valor):

	valor = str(valor).replace('.', '')
	valor = str(valor).replace('$', '')
	valor = str(valor).replace(',', '.')

	try:
		valor = float(valor)

		if isinstance(valor, float):
			return True
		else:
			return False
	except Exception as e:
		return False