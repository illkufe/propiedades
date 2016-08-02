from django import template

register = template.Library()

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