# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import Context, loader
from django.template.loader import get_template 
from django import forms
from datetime import date, datetime, timedelta
from suds.client import Client
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.generic import View

from utilidades.plugins.owncloud import *

from administrador.models import Configuracion_Monedas
from activos.models import Activo
from contrato.models import Contrato
from .models import *


import pdfkit
import calendar
import string
import random


# variables globales
def variables_globales(request):

	try:
		user 			= request.user
		empresa 		= user.userprofile.empresa
		configuracion 	= empresa.configuracion
		moneda_local 	= empresa.configuracion_monedas_set.get(moneda_local=True).moneda_id

		return {
		'lease_user_id' 		: user.id,
		'lease_format_dec' 		: ',' if configuracion.formato_decimales == 1 else '.',
		'lease_format_mil' 		: '.' if configuracion.formato_decimales == 1 else ',',
		'lease_decimales' 		: configuracion.cantidad_decimales,
		'lease_moneda_local' 	: 5 if not moneda_local else moneda_local
		}
	except Exception:
		return {'estado':'error'}


def configuracion_monedas(request, pk):

	data 			= []

	user 			= request.user
	empresa 		= user.userprofile.empresa
	configuracion 	= user.userprofile.empresa.configuracion

	moneda = Configuracion_Monedas.objects.get(moneda_id=int(pk), empresa=empresa)

	data.append({
		'id'			: moneda.moneda_id,
		'moneda'		: moneda.moneda.abrev,
		'decimal'		: moneda.cantidad_decimales,
		'format_dec' 	: ',' if configuracion.formato_decimales == 1 else '.',
		'format_mil'	: '.' if configuracion.formato_decimales == 1 else ',',
	})

	return JsonResponse(data, safe=False)

# funciones globales (fechas)

def primer_dia(fecha):

	dia 	= '01'
	mes 	= fecha.strftime('%m')
	anio 	= fecha.strftime('%Y')
	fecha 	= dia+'/'+mes+'/'+anio
	fecha 	= datetime.strptime(fecha, "%d/%m/%Y")

	return fecha.date()

def ultimo_dia(fecha):

	dia 	= str(calendar.monthrange(fecha.year, fecha.month)[1])
	mes 	= fecha.strftime('%m')
	anio 	= fecha.strftime('%Y')
	fecha 	= dia+'/'+mes+'/'+anio
	fecha 	= datetime.strptime(fecha, "%d/%m/%Y")

	return fecha.date()

def meses_entre_fechas(fecha_inicio, fecha_termino):

	delta = 0
	while True:

		dias = calendar.monthrange(fecha_inicio.year, fecha_inicio.month)[1]
		fecha_inicio += timedelta(days=dias)
		if fecha_inicio <= fecha_termino:
			delta += 1
		else:
			break

	return delta + 1

def sumar_meses(fecha, meses):

	month 	= fecha.month - 1 + meses
	year 	= int(fecha.year + month / 12 )
	month 	= month % 12 + 1
	day 	= min(fecha.day,calendar.monthrange(year,month)[1])
	fecha 	= str(day)+'/'+str(month)+'/'+str(year)

	return datetime.strptime(fecha, "%d/%m/%Y").date()

def calcular_periodos(tipo, periodos, operacion):

	response 		= list()
	fecha_actual 	= datetime.now()

	if tipo == 1:

		for periodo in range(0, periodos):


			if operacion == 'sumar':
				response.insert(len(response), {
					'fecha_inicio': primer_dia(fecha_actual),
					'fecha_termino': ultimo_dia(fecha_actual),
				})
				fecha_actual = sumar_meses(fecha_actual, 1)
			else:
				response.insert(0, {
					'fecha_inicio': primer_dia(fecha_actual),
					'fecha_termino': ultimo_dia(fecha_actual),
				})
				fecha_actual = sumar_meses(fecha_actual, -1)

	elif tipo == 2:

		for periodo in range(0, periodos):

			if fecha_actual.month <= 3:
				fecha_inicio 	= date(int(fecha_actual.year), 1, 1)
				fecha_termino 	= date(int(fecha_actual.year), 3, 31)
			elif fecha_actual.month <= 6:
				fecha_inicio 	= date(int(fecha_actual.year), 4, 1)
				fecha_termino 	= date(int(fecha_actual.year), 6, 30)
			elif fecha_actual.month <= 9:
				fecha_inicio 	= date(int(fecha_actual.year), 7, 1)
				fecha_termino 	= date(int(fecha_actual.year), 9, 30)
			elif fecha_actual.month <= 12:
				fecha_inicio 	= date(int(fecha_actual.year), 10, 1)
				fecha_termino 	= date(int(fecha_actual.year), 12, 31)
			else:
				pass


			if operacion == 'sumar':
				response.insert(len(response), {
					'fecha_inicio': fecha_inicio,
					'fecha_termino': fecha_termino,
				})
				fecha_actual = sumar_meses(fecha_actual, 3)
			else:
				response.insert(0, {
					'fecha_inicio': fecha_inicio,
					'fecha_termino': fecha_termino,
				})
				fecha_actual = sumar_meses(fecha_actual, -3)

	elif tipo == 3:

		for periodo in range(0, periodos):

			if fecha_actual.month <= 6:
				fecha_inicio 	= date(int(fecha_actual.year), 1, 1)
				fecha_termino 	= date(int(fecha_actual.year), 6, 30)
			elif fecha_actual.month >= 7:
				fecha_inicio 	= date(int(fecha_actual.year), 7, 1)
				fecha_termino 	= date(int(fecha_actual.year), 12, 31)
			else:
				pass

			if operacion == 'sumar':
				response.insert(len(response), {
					'fecha_inicio': fecha_inicio,
					'fecha_termino': fecha_termino,
				})
				fecha_actual = sumar_meses(fecha_actual, 6)
			else:
				response.insert(0, {
					'fecha_inicio': fecha_inicio,
					'fecha_termino': fecha_termino,
				})

				fecha_actual = sumar_meses(fecha_actual, -6)

	elif tipo == 4:

		for periodo in range(0, periodos):

			if operacion == 'sumar':
				response.insert(len(response), {
					'fecha_inicio': primer_dia(datetime.strptime('01/01/' + str(fecha_actual.year), "%d/%m/%Y")),
					'fecha_termino': ultimo_dia(fecha_actual),
				})

				fecha_actual = primer_dia(datetime.strptime('01/12/' + str(fecha_actual.year), "%d/%m/%Y"))
				fecha_actual = sumar_meses(fecha_actual, 12)
			else:

				response.insert(0, {
					'fecha_inicio': primer_dia(datetime.strptime('01/01/' + str(fecha_actual.year), "%d/%m/%Y")),
					'fecha_termino': ultimo_dia(fecha_actual),
				})

				fecha_actual = primer_dia(datetime.strptime('01/12/' + str(fecha_actual.year), "%d/%m/%Y"))
				fecha_actual = sumar_meses(fecha_actual, -12)
	else:
		pass

	return response

def meses(valor):

	meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

	return meses[int(valor)-1]

# funciones globales (numeros)
def formato_numero(valor):

	moneda = '{:,.4f}'.format(valor)

	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda


def formato_moneda_local(request, valor, moneda=None):


	try:

		empresa 		= request.user.userprofile.empresa
		configuracion 	= empresa.configuracion

		if moneda is None:
			moneda_local    = empresa.configuracion_monedas_set.get(moneda_local=True)
		else:
			moneda_local	= empresa.configuracion_monedas_set.get(moneda=moneda)

		decimales       = configuracion.cantidad_decimales if moneda_local.cantidad_decimales is None else moneda_local.cantidad_decimales

		formato = '${:,.'+str(decimales)+'f}'
		moneda  = formato.format(valor)

	except Exception:
		formato = '${:,.'+str(configuracion.cantidad_decimales)+'f}'
		moneda 	= formato.format(valor)

	moneda = moneda.replace('.', '*')
	moneda = moneda.replace(',', '.')
	moneda = moneda.replace('*', ',')

	return moneda

def format_number(request, value, local):

	configuracion 	= request.user.userprofile.empresa.configuracion	
	moneda_local 	= request.user.userprofile.empresa.configuracion_monedas_set.get(moneda_local=True)

	if local is True:
		decimales = configuracion.cantidad_decimales if moneda_local.cantidad_decimales is None else moneda_local.cantidad_decimales
	else:
		decimales = configuracion.cantidad_decimales

	return round(value, decimales)



# funciones avatar
def avatar_usuario(user):

	template 		= ''
	primary_avatar 	= user.avatar_set.all().order_by('-primary')[:1]
	full_name 		= str(user.first_name)+' '+str(user.last_name)
	short_name 		= str(user.first_name)[:1]+''+str(user.last_name)[:1]

	if primary_avatar:
		url 	= str(primary_avatar[0].avatar)

		template += '<a style="margin:0px 1px;" data-toggle="tooltip" data-placement="top" title="'+full_name+'">'
		template += '<img src="/media/'+url+'" width="80" height="80">'
		template += '</a>'
	else:
		template  += '<a class="avatar-default" data-toggle="tooltip" data-placement="top" title="'+full_name+'">'
		template  += short_name
		template  += '</a>'

	return template


# funciones globales (correo)
def enviar_correo(configuracion):

	try:
		msg = EmailMultiAlternatives(configuracion['asunto'], 'mensaje', settings.EMAIL_HOST_USER, configuracion['destinatarios'])
		msg.attach_file('public/media/contratos/propuestas/propuesta_version_'+configuracion['id']+'.pdf')
		msg.attach_alternative(configuracion['contenido'], "text/html")
		msg.send()

		estado 	= True
		mensaje = None

	except Exception as error:

		estado 	= False
		mensaje = error

	return {'estado':estado, 'mensaje':mensaje}


# funciones globales (pdf)
def generar_pdf(configuracion, data):

	context = Context(data)
	
	try:
		template = get_template(configuracion['template'])
	except Exception:
		template = get_template('pdf/default.html')

	html = template.render(context)
	pdfkit.from_string(html, configuracion['archive']['directory']+'/'+configuracion['archive']['name']+'.pdf', options=configuracion['options'], css=configuracion['css'])
	pdf 		= open(configuracion['archive']['directory']+'/'+configuracion['archive']['name']+'.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename='+configuracion['archive']['name']+'.pdf'
	pdf.close()

	return response

# funciones conectar web service
def concectar_web_service(url):

	xml_1 = '&lt;SDT_DocVentaExt xmlns=&quot;http://www.informat.cl/ws&quot;&gt;&lt;EncDoc&gt;&lt;RefDoc&gt;&lt;NroRefCliente&gt;2-2-101-101&lt;/NroRefCliente&gt;&lt;Modulo&gt;PDV&lt;/Modulo&gt;&lt;NroOrdCom&gt;2&lt;/NroOrdCom&gt;&lt;/RefDoc&gt;&lt;Cliente&gt;&lt;Identificacion&gt;&lt;IdCliente&gt;66666666&lt;/IdCliente&gt;&lt;Nombre_Completo&gt;CLIENTES VARIOS&lt;/Nombre_Completo&gt;&lt;Secuencia&gt;0&lt;/Secuencia&gt;&lt;Direccion&gt;CLIENTES VARIOS&lt;/Direccion&gt;&lt;Comuna&gt;CLIENTES VARIOS&lt;/Comuna&gt;&lt;Ciudad&gt;CLIENTES VARIOS&lt;/Ciudad&gt;&lt;Telefono&gt;CLIENTES VARIOS&lt;/Telefono&gt;&lt;Email /&gt;&lt;/Identificacion&gt;&lt;Facturacion&gt;&lt;Moneda&gt;1&lt;/Moneda&gt;&lt;Tasa&gt;1&lt;/Tasa&gt;&lt;CondVenta&gt;0&lt;/CondVenta&gt;&lt;Origen&gt;0&lt;/Origen&gt;&lt;DocAGenerar&gt;101&lt;/DocAGenerar&gt;&lt;DocRef&gt;0&lt;/DocRef&gt;&lt;NroDocRef&gt;0&lt;/NroDocRef&gt;&lt;NroDoc&gt;10001&lt;/NroDoc&gt;&lt;Estado&gt;0&lt;/Estado&gt;&lt;Equipo&gt;201&lt;/Equipo&gt;&lt;Bodega_Salida&gt;102&lt;/Bodega_Salida&gt;&lt;IdVendedor&gt;4839396&lt;/IdVendedor&gt;&lt;Sucursal_Cod&gt;2&lt;/Sucursal_Cod&gt;&lt;ListaPrecio_Cod /&gt;&lt;Fecha_Atencion&gt;2015-12-15&lt;/Fecha_Atencion&gt;&lt;Fecha_Documento&gt;2016-04-03&lt;/Fecha_Documento&gt;&lt;/Facturacion&gt;&lt;/Cliente&gt;&lt;/EncDoc&gt;&lt;DetDoc&gt;&lt;Items&gt;&lt;Item&gt;&lt;NumItem&gt;1&lt;/NumItem&gt;&lt;FechaEntrega&gt;0&lt;/FechaEntrega&gt;&lt;PrecioRef&gt;1000&lt;/PrecioRef&gt;&lt;Cantidad&gt;1.000000&lt;/Cantidad&gt;&lt;PorcUno&gt;0.00&lt;/PorcUno&gt;&lt;MontoUno&gt;0&lt;/MontoUno&gt;&lt;DescDos_Cod&gt;0&lt;/DescDos_Cod&gt;&lt;DescTre_Cod /&gt;&lt;MontoImpUno&gt;0&lt;/MontoImpUno&gt;&lt;PorcImpUno&gt;0.00&lt;/PorcImpUno&gt;&lt;MontoImpDos&gt;0&lt;/MontoImpDos&gt;&lt;PorcImpDos&gt;0.00&lt;/PorcImpDos&gt;&lt;TotalDocLin&gt;1000&lt;/TotalDocLin&gt;&lt;Producto&gt;&lt;Producto_Vta&gt;0000002572703&lt;/Producto_Vta&gt;&lt;Unidad&gt;Unid&lt;/Unidad&gt;&lt;/Producto&gt;&lt;/Item&gt;&lt;/Items&gt;&lt;/DetDoc&gt;&lt;ResumenDoc&gt;&lt;TotalNeto&gt;840&lt;/TotalNeto&gt;&lt;CodigoDescuento /&gt;&lt;TotalDescuento&gt;0&lt;/TotalDescuento&gt;&lt;TotalIVA&gt;160&lt;/TotalIVA&gt;&lt;TotalOtrosImpuestos&gt;0&lt;/TotalOtrosImpuestos&gt;&lt;TotalDoc&gt;1000&lt;/TotalDoc&gt;&lt;TotalConceptos&gt;&lt;Conceptos&gt;&lt;Concepto_Cod&gt;1&lt;/Concepto_Cod&gt;&lt;ValorConcepto&gt;0&lt;/ValorConcepto&gt;&lt;/Conceptos&gt;&lt;Conceptos&gt;&lt;Concepto_Cod&gt;2&lt;/Concepto_Cod&gt;&lt;ValorConcepto&gt;160&lt;/ValorConcepto&gt;&lt;/Conceptos&gt;&lt;Conceptos&gt;&lt;Concepto_Cod&gt;3&lt;/Concepto_Cod&gt;&lt;ValorConcepto&gt;840&lt;/ValorConcepto&gt;&lt;/Conceptos&gt;&lt;/TotalConceptos&gt;&lt;/ResumenDoc&gt;&lt;Recaudacion&gt;&lt;Encabezado&gt;&lt;IdCajero&gt;4839396&lt;/IdCajero&gt;&lt;Tipo_Vuelto&gt;1&lt;/Tipo_Vuelto&gt;&lt;IdCliente&gt;66666666&lt;/IdCliente&gt;&lt;DigitoVerificador&gt;6&lt;/DigitoVerificador&gt;&lt;NombreCompleto&gt;CLIENTES VARIOS&lt;/NombreCompleto&gt;&lt;Direccion&gt;CLIENTES VARIOS&lt;/Direccion&gt;&lt;Ciudad&gt;CLIENTES VARIOS&lt;/Ciudad&gt;&lt;Comuna&gt;CLIENTES VARIOS&lt;/Comuna&gt;&lt;Telefono&gt;CLIENTES VARIOS&lt;/Telefono&gt;&lt;Email /&gt;&lt;TotalaRecaudar&gt;1000&lt;/TotalaRecaudar&gt;&lt;RecaudacionEnc_ext&gt;&lt;REnExt_Item&gt;&lt;RecEnc_opcion /&gt;&lt;RecEnd_datos /&gt;&lt;/REnExt_Item&gt;&lt;/RecaudacionEnc_ext&gt;&lt;/Encabezado&gt;&lt;Detalle&gt;&lt;FormaPago&gt;&lt;Cod_FormaPago&gt;0&lt;/Cod_FormaPago&gt;&lt;Cod_MonedaFP&gt;1&lt;/Cod_MonedaFP&gt;&lt;NroCheque /&gt;&lt;FechaCheque&gt;2015-12-15&lt;/FechaCheque&gt;&lt;FechaVencto /&gt;&lt;Cod_Banco /&gt;&lt;Cod_Plaza /&gt;&lt;Referencia /&gt;&lt;MontoaRec&gt;1000&lt;/MontoaRec&gt;&lt;ParidadRec&gt;1&lt;/ParidadRec&gt;&lt;/FormaPago&gt;&lt;/Detalle&gt;&lt;/Recaudacion&gt;&lt;/SDT_DocVentaExt&gt;'
	xml_2 = '<SDT_DocVentaExt xmlns="http://www.informat.cl/ws"><EncDoc><RefDoc><NroRefCliente>2-2-101-101</NroRefCliente><Modulo>PDV</Modulo><NroOrdCom>2</NroOrdCom></RefDoc><Cliente><Identificacion><IdCliente>66666666</IdCliente><Nombre_Completo>CLIENTES VARIOS</Nombre_Completo><Secuencia>0</Secuencia><Direccion>CLIENTES VARIOS</Direccion><Comuna>CLIENTES VARIOS</Comuna><Ciudad>CLIENTES VARIOS</Ciudad><Telefono>CLIENTES VARIOS</Telefono><Email /></Identificacion><Facturacion><Moneda>1</Moneda><Tasa>1</Tasa><CondVenta>0</CondVenta><Origen>0</Origen><DocAGenerar>101</DocAGenerar><DocRef>0</DocRef><NroDocRef>0</NroDocRef><NroDoc>101</NroDoc><Estado>0</Estado><Equipo>201</Equipo><Bodega_Salida>102</Bodega_Salida><IdVendedor>4839396</IdVendedor><Sucursal_Cod>2</Sucursal_Cod><ListaPrecio_Cod /><Fecha_Atencion>2015-12-15</Fecha_Atencion><Fecha_Documento>2015-12-15</Fecha_Documento></Facturacion></Cliente></EncDoc><DetDoc><Items><Item><NumItem>1</NumItem><FechaEntrega>0</FechaEntrega><PrecioRef>1000</PrecioRef><Cantidad>1.000000</Cantidad><PorcUno>0.00</PorcUno><MontoUno>0</MontoUno><DescDos_Cod>0</DescDos_Cod><DescTre_Cod /><MontoImpUno>0</MontoImpUno><PorcImpUno>0.00</PorcImpUno><MontoImpDos>0</MontoImpDos><PorcImpDos>0.00</PorcImpDos><TotalDocLin>1000</TotalDocLin><Producto><Producto_Vta>0000002572703</Producto_Vta><Unidad>Unid</Unidad></Producto></Item></Items></DetDoc><ResumenDoc><TotalNeto>840</TotalNeto><CodigoDescuento /><TotalDescuento>0</TotalDescuento><TotalIVA>160</TotalIVA><TotalOtrosImpuestos>0</TotalOtrosImpuestos><TotalDoc>1000</TotalDoc><TotalConceptos><Conceptos><Concepto_Cod>1</Concepto_Cod><ValorConcepto>0</ValorConcepto></Conceptos><Conceptos><Concepto_Cod>2</Concepto_Cod><ValorConcepto>160</ValorConcepto></Conceptos><Conceptos><Concepto_Cod>3</Concepto_Cod><ValorConcepto>840</ValorConcepto></Conceptos></TotalConceptos></ResumenDoc><Recaudacion><Encabezado><IdCajero>4839396</IdCajero><Tipo_Vuelto>1</Tipo_Vuelto><IdCliente>66666666</IdCliente><DigitoVerificador>6</DigitoVerificador><NombreCompleto>CLIENTES VARIOS</NombreCompleto><Direccion>CLIENTES VARIOS</Direccion><Ciudad>CLIENTES VARIOS</Ciudad><Comuna>CLIENTES VARIOS</Comuna><Telefono>CLIENTES VARIOS</Telefono><Email /><TotalaRecaudar>1000</TotalaRecaudar><RecaudacionEnc_ext><REnExt_Item><RecEnc_opcion /><RecEnd_datos /></REnExt_Item></RecaudacionEnc_ext></Encabezado><Detalle><FormaPago><Cod_FormaPago>0</Cod_FormaPago><Cod_MonedaFP>1</Cod_MonedaFP><NroCheque /><FechaCheque>2015-12-15</FechaCheque><FechaVencto /><Cod_Banco /><Cod_Plaza /><Referencia /><MontoaRec>1000</MontoaRec><ParidadRec>1</ParidadRec></FormaPago></Detalle></Recaudacion></SDT_DocVentaExt>'

	# call_service(url)
	# test('http://dati.meteotrentino.it/service.asmx?WSDL')
	client1 = Client(url)
	response = client1.service.Execute(xml_2)

	# for error in response.SDT_ERRORES_ERROR:
	# 	print (error.DESCERROR)

	return response




# CLASES
class NumberField(forms.Field):
	def to_python(self, value):
		if value is not '' and value is not None:
			return value.replace(".", "").replace(",", ".")

# get
class CURRENCIES_LAST(View):
	http_method_names = ['get']
	
	def get(self, request, id=None):

		currencies 	= []

		if id is None:

			currencies.append({'id':1})
			currencies.append({'id':2})
			currencies.append({'id':3})
			currencies.append({'id':4})

			self.object_list = currencies
		else:

			currencies.append({'id':int(id)})

			self.object_list = currencies

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()

	def json_to_response(self):

		data = list()

		for currency in self.object_list:

			moneda 		= Moneda.objects.get(id=int(currency['id']))
			historial 	= Moneda_Historial.objects.filter(moneda=moneda).last()

			data.append({
				'id'		: moneda.id,
				'nombre'	: moneda.nombre,
				'abrev'		: moneda.abrev,
				'simbolo'	: moneda.simbolo,
				'value'		: formato_numero(historial.valor),
				'fecha'		: historial.fecha.strftime('%d/%m/%Y %H:%M'),
				})

		return JsonResponse(data, safe=False)





		













# Funciones Finales -------------------


# get
def get_password_random(size):

	chars 		= string.ascii_letters + string.digits
	password 	= ''.join((random.choice(chars)) for x in range(size))

	return password

# validaciones
def validate_rut(rut):

	if '-' in rut:

		[rut, digito] = rut.replace('.', '').split('-')

		return True if digito == validate_digito(rut) else False

	else:
		return False

def validate_digito(rut):

	value = 11 - sum([ int(a)*int(b)  for a,b in zip(str(rut).zfill(8), '32765432')])%11

	return {10: 'K', 11: '0'}.get(value, str(value))


# funciones owncloud
def data_concetion(request):

	oc_concetion = { 
		'url' 		: request.session['oc_url'] ,
		'username' 	: request.session['oc_username'],
		'password' 	: request.session['oc_password'],
		}

	return  oc_concetion

def owncloud_list_directory(request):

	var_post 	= request.POST.copy()
	item_id 	= var_post.get('id')

	if var_post.get('model') == 'activo':

		item 		= Activo.objects.get(id=item_id)
		item_nombre = item.nombre

	elif var_post.get('model') == 'contrato':

		item 		= Contrato.objects.get(id=item_id)
		item_nombre = item.nombre_local

	else:
		pass

	response = oc_list_directory(str(item_nombre), str(var_post.get('url'))+'/'+str(item_nombre), data_concetion(request))

	return JsonResponse(response, safe=False)

def owncloud_create_folder(request):

	var_post	= request.POST.copy()
	oc_path 	= var_post.get('path')
	oc_name 	= var_post.get('name')

	response 	= oc_create_directory(oc_path, oc_name, data_concetion(request))

	return JsonResponse(response, safe=False)

def owncloud_delete(request):

	var_post	= request.POST.copy()
	oc_path 	= var_post.get('path')
	oc_name 	= var_post.get('name')
	oc_type 	= var_post.get('type')

	response 	= oc_delete(oc_path, oc_name, oc_type, data_concetion(request))

	return JsonResponse(response, safe=False)

def owncloud_upload_file(request):
	
	var_file 	= request.FILES.copy()
	var_post	= request.POST.copy()
	
	oc_file 	= var_file['file']
	oc_path 	= var_post.get('path')

	path 		= default_storage.save('tmp/'+str(oc_file), ContentFile(oc_file.read()))
	tmp_file 	= os.path.join(settings.MEDIA_ROOT, path)

	response 	= oc_upload_file(oc_path+'/', tmp_file, data_concetion(request))

	os.remove(tmp_file)

	return JsonResponse(response, safe=False)

def owncloud_create_path(request, names):

	path 	 	= ''
	oc_path 	= ''
	response 	= list()

	for name in names:

		path += name if path == '' else '/'+name

		if oc_path_exists(path, data_concetion(request))['status'] is False:
			response = oc_create_directory(oc_path, name, data_concetion(request))

		oc_path += name if oc_path == '' else '/'+name


	return JsonResponse(response, safe=False)




