from django import template

register = template.Library()

@register.filter
def meses(valor):

	meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

	return meses[int(valor)-1]

@register.filter
def formato_moneda(valor):

	moneda = '${:,.2f}'.format(valor)
	
	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda

@register.filter
def formato_numero(valor):

	moneda = '{:,.2f}'.format(valor)
	
	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda


@register.filter
def formato_boolean(valor):

	if valor is True:
		return 'Si'
	else:
		return 'No'