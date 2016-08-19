# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from django.shortcuts import render
from django.views.generic import View
from django.template import Context, loader
from django.template.loader import get_template 
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.views.generic import View, ListView, FormView, DeleteView, UpdateView

from administrador.models import Empresa, Cliente
from accounts.models import UserProfile
from locales.models import Local, Venta, Medidor_Electricidad, Medidor_Agua, Medidor_Gas, Gasto_Servicio
from activos.models import Activo, Gasto_Mensual
from conceptos.models import Concepto
from contrato.models import Contrato, Contrato_Tipo, Multa, Arriendo, Arriendo_Detalle, Arriendo_Variable, Arriendo_Bodega, Gasto_Comun, Servicio_Basico, Cuota_Incorporacion, Fondo_Promocion
from procesos.models import *
from operaciones.models import Lectura_Electricidad, Lectura_Agua, Lectura_Gas

from django.db.models import Sum, Q
from datetime import datetime, timedelta
import os
import json
import pdfkit

from utilidades.views import primer_dia, ultimo_dia, meses_entre_fechas, sumar_meses, formato_moneda

from suds.client import Client

import xml.etree.ElementTree as ET


class PropuestaGenerarList(ListView):

	model 			= Proceso
	template_name 	= 'propuesta_generar_list.html'

	def get_context_data(self, **kwargs):		
		context = super(PropuestaGenerarList, self).get_context_data(**kwargs)
		context['title'] 		= 'Proceso de Facturación'
		context['subtitle'] 	= 'propuestas de facturación'
		context['name'] 		= 'lista'
		context['href'] 		= 'procesos'

		context['conceptos'] 	= Concepto.objects.all()
		context['activos'] 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		
		return context

class PropuestaProcesarList(ListView):

	model 			= Proceso
	template_name 	= 'propuesta_procesar_list.html'

	def get_context_data(self, **kwargs):

		context = super(PropuestaProcesarList, self).get_context_data(**kwargs)
		context['title'] 		= 'Proceso de Facturación'
		context['subtitle'] 	= 'propuestas de facturación'
		context['name'] 		= 'lista'
		context['href'] 		= 'propuesta/procesar'

		context['conceptos'] 	= Concepto.objects.all()
		context['activos'] 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		
		return context








class ProcesoList(ListView):
	model = Proceso
	template_name = 'viewer/procesos/procesos_list.html'

	def get_context_data(self, **kwargs):		
		context = super(ProcesoList, self).get_context_data(**kwargs)
		context['title'] 		= 'Cálculo de Conceptos'
		context['subtitle'] 	= 'Procesos de Facturación'
		context['name'] 		= 'Lista'
		context['href'] 		= 'procesos'

		context['conceptos'] 	= Concepto.objects.all()
		context['activos'] 		= Activo.objects.filter(empresa=self.request.user.userprofile.empresa, visible=True)
		
		return context

class ProcesoDelete(DeleteView):
	model = Proceso
	success_url = reverse_lazy('/procesos/list')

	def delete(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.delete()
		payload = {'delete': 'ok'}
		return JsonResponse(payload, safe=False)



# API -----------------
class PROPUESTA_PROCESAR(View):

	http_method_names =  ['post']

	def post(self, request):

		data 		= list()
		var_post 	= request.POST.copy()
		proceso 	= Proceso.objects.get(id=var_post.get('id'))

		for detalle in proceso.proceso_detalle_set.all():
			data.append(enviar_detalle_propuesta(detalle.id))

		return JsonResponse({'response': data}, safe=False)


class PROCESOS(View):

	http_method_names =  ['get', 'post']

	def get(self, request, id=None):

		profile 	= UserProfile.objects.get(user=self.request.user)
		profiles 	= profile.empresa.userprofile_set.all().values_list('id', flat=True)
		users 		= User.objects.filter(userprofile__in=profiles).values_list('id', flat=True)

		if id == None:
			self.object_list = Proceso.objects.filter(visible=True, user__in=users)
		else:
			self.object_list = Proceso.objects.filter(pk=id)

		if request.is_ajax():
			return self.json_to_response()

		if self.request.GET.get('format', None) == 'json':
			return self.json_to_response()
	
	def post(self, request):

		
		var_post 		= request.POST.copy()
		contratos 		= var_post.get('contratos').split(",")
		fecha_inicio 	= var_post.get('fecha_inicio')
		fecha_termino 	= var_post.get('fecha_termino')
		conceptos 		= var_post.get('conceptos').split(",")

		user 			= User.objects.get(pk=request.user.pk)
		contratos 		= contratos
		f_inicio 		= primer_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y")).date()
		f_termino 		= ultimo_dia(datetime.strptime(fecha_termino, "%d/%m/%Y")).date()
		fecha 			= ultimo_dia(datetime.strptime(fecha_inicio, "%d/%m/%Y")).date()
		meses			= meses_entre_fechas(f_inicio, f_termino)
		data 			= []

		proceso = Proceso(
			fecha_inicio		= f_inicio.strftime('%Y-%m-%d'),
			fecha_termino		= f_termino.strftime('%Y-%m-%d'),
			user				= user,
			proceso_estado_id 	= 1,
		)
		proceso.save()

		for item in conceptos:

			concepto = Concepto.objects.get(id=item)
			proceso.conceptos.add(concepto)
			
			if concepto.concepto_tipo.id == 1:
				detalle = calculo_arriendo_minimo(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 2:
				detalle = calculo_arriendo_variable(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 3:
				detalle = calculo_gasto_comun(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 4:
				detalle = calculo_servicios_basico(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 5:
				detalle = calculo_cuota_incorporacion(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 6:
				detalle = calculo_fondo_promocion(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 7:
				detalle = calculo_arriendo_bodega(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 8:
				detalle = calculo_servicios_varios(request, proceso, contratos, meses, fecha, concepto)
			elif concepto.concepto_tipo.id == 9:
				detalle = calculo_multas(request, proceso, contratos, meses, fecha, concepto)
			else:
				detalle = []

		return JsonResponse({'id': proceso.id}, safe=False)

	def json_to_response(self):
		data = list()

		for proceso in self.object_list:

			# usuario
			usuario = {
				'id'		:proceso.user.id,
				'first_name':proceso.user.first_name,
				'last_name'	:proceso.user.last_name,
				'email'		:proceso.user.email,
			}

			# conceptos
			conceptos 		= []
			contratos_id 	= []

			for concepto in proceso.conceptos.all():

				conceptos.append({
					'id'		: concepto.id,
					'nombre' 	: concepto.nombre,
					})

				if concepto.id == 1:
					contratos_id += Detalle_Arriendo_Minimo.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 2:
					contratos_id += Detalle_Arriendo_Variable.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 3:
					contratos_id += Detalle_Gasto_Comun.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 4:
					contratos_id += Detalle_Electricidad.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
					contratos_id += Detalle_Agua.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
					contratos_id += Detalle_Gas.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 5:
					contratos_id += Detalle_Cuota_Incorporacion.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				elif concepto.id == 6:
					contratos_id += Detalle_Fondo_Promocion.objects.filter(proceso=proceso).values_list('contrato_id', flat=True).distinct().exclude(contrato_id__in=contratos_id)
				else:
					pass

			contratos = []
			for contrato_id in contratos_id:
				contrato = Contrato.objects.get(id=contrato_id)
				contratos.append({
					'id'		: contrato.id,
					'numero' 	: contrato.numero,
					})

			data.append({
				'id'			: proceso.id,
				'nombre'		: proceso.nombre,
				'fecha_creacion': proceso.creado_en.strftime('%d/%m/%Y'),
				'fecha_inicio'	: proceso.fecha_inicio.strftime('%d/%m/%Y'),
				'fecha_termino'	: proceso.fecha_termino.strftime('%d/%m/%Y'),
				'estado_id'		: proceso.proceso_estado.id,
				'estado_nombre'	: proceso.proceso_estado.nombre,
				'estado_color'	: proceso.proceso_estado.color,
				'usuario'		: usuario,
				'conceptos'		: conceptos,
				'contratos'		: contratos,
				})

		return JsonResponse(data, safe=False)



# Funciones ----------------------------
def enviar_detalle_propuesta(id):

	data 	= list()
	detalle = Proceso_Detalle.objects.get(id=id)

	SDT_DocVentaExt = ET.Element('SDT_DocVentaExt')
	SDT_DocVentaExt.set('xmlns', 'http://www.informat.cl/ws')
	
	# SDT_DocVentaExt
	EncDoc 		= ET.SubElement(SDT_DocVentaExt, 'EncDoc')
	DetDoc 		= ET.SubElement(SDT_DocVentaExt, 'DetDoc')
	ResumenDoc 	= ET.SubElement(SDT_DocVentaExt, 'ResumenDoc')
	Recaudacion = ET.SubElement(SDT_DocVentaExt, 'Recaudacion')

	# SDT_DocVentaExt/EncDoc
	RefDoc	= ET.SubElement(EncDoc, 'RefDoc')
	Cliente	= ET.SubElement(EncDoc, 'Cliente')

	# SDT_DocVentaExt/EncDoc/RefDoc
	ET.SubElement(RefDoc, 'NroRefCliente')
	ET.SubElement(RefDoc, 'Modulo')
	ET.SubElement(RefDoc, 'NroOrdCom')

	# SDT_DocVentaExt/EncDoc/RefDoc
	Identificacion 	= ET.SubElement(Cliente, 'Identificacion')
	Facturacion 	= ET.SubElement(Cliente, 'Facturacion')

	# SDT_DocVentaExt/EncDoc/RefDoc/Identificacion
	ET.SubElement(Identificacion, 'IdCliente').text='77304990'
	ET.SubElement(Identificacion, 'Nombre_Completo').text='VALVERDE NORAMBUENA SPA'
	ET.SubElement(Identificacion, 'Secuencia').text='1'# IDENTIIFCAR SI ES CLIENTE O PROVEEDOR
	ET.SubElement(Identificacion, 'Direccion').text='JOSE M.ESCRIBA BALAGER 13105, OF 813'
	ET.SubElement(Identificacion, 'Comuna').text='LO BARNECHEA'
	ET.SubElement(Identificacion, 'Ciudad').text='SANTIAGO'
	ET.SubElement(Identificacion, 'Telefono')
	ET.SubElement(Identificacion, 'Email')

	# SDT_DocVentaExt/EncDoc/RefDoc/Facturacion
	ET.SubElement(Facturacion, 'Moneda').text='1'
	ET.SubElement(Facturacion, 'Tasa').text='1'
	ET.SubElement(Facturacion, 'CondVenta').text='0'# SI ES CONTADO, EN CREDITO ETC
	ET.SubElement(Facturacion, 'Origen').text='0'
	ET.SubElement(Facturacion, 'DocAGenerar').text='200'
	ET.SubElement(Facturacion, 'DocRef').text='0'
	ET.SubElement(Facturacion, 'NroDocRef').text='0'
	ET.SubElement(Facturacion, 'NroDoc').text='0'
	ET.SubElement(Facturacion, 'Estado').text='0'
	ET.SubElement(Facturacion, 'Equipo').text='1'# AVERIGUAR QUE ES
	ET.SubElement(Facturacion, 'Bodega_Salida').text='1'
	ET.SubElement(Facturacion, 'IdVendedor').text='6395133'
	ET.SubElement(Facturacion, 'Sucursal_Cod').text='1'
	ET.SubElement(Facturacion, 'ListaPrecio_Cod')
	ET.SubElement(Facturacion, 'Fecha_Atencion').text='2016-08-19'
	ET.SubElement(Facturacion, 'Fecha_Documento').text='2016-08-19'


	# SDT_DocVentaExtDetDoc/DetDoc
	Items = ET.SubElement(DetDoc, 'Items')
	
	# SDT_DocVentaExtDetDoc/DetDoc/Items
	Item = ET.SubElement(Items, 'Item')

	ET.SubElement(Item, 'NumItem').text='1'
	ET.SubElement(Item, 'FechaEntrega').text='0'
	ET.SubElement(Item, 'PrecioRef').text='1000'
	ET.SubElement(Item, 'Cantidad').text='1'
	ET.SubElement(Item, 'PorcUno').text='0'
	ET.SubElement(Item, 'MontoUno').text='1000'
	ET.SubElement(Item, 'DescDos_Cod').text='0'
	ET.SubElement(Item, 'DescTre_Cod')
	ET.SubElement(Item, 'MontoImpUno').text='0'
	ET.SubElement(Item, 'PorcImpUno').text='0'
	ET.SubElement(Item, 'MontoImpDos').text='0'
	ET.SubElement(Item, 'PorcImpDos').text='0'
	ET.SubElement(Item, 'TotalDocLin').text='1000'

	Producto = ET.SubElement(Item, 'Producto')

	Producto_Vta 	= ET.SubElement(Producto, 'Producto_Vta').text='01010045001217'
	Unidad 			= ET.SubElement(Producto, 'Unidad').text='Unid'

	# SDT_DocVentaExtDetDoc/ResumenDoc
	ET.SubElement(ResumenDoc, 'TotalNeto').text='1000'
	ET.SubElement(ResumenDoc, 'CodigoDescuento')
	ET.SubElement(ResumenDoc, 'TotalDescuento').text='0'
	ET.SubElement(ResumenDoc, 'TotalIVA').text='190'
	ET.SubElement(ResumenDoc, 'TotalOtrosImpuestos').text='0'
	ET.SubElement(ResumenDoc, 'TotalDoc').text='1190'
	TotalConceptos = ET.SubElement(ResumenDoc, 'TotalConceptos')

	# SDT_DocVentaExtDetDoc/ResumenDoc/TotalConceptos
	# CREAR UN FOR 
	Conceptos = ET.SubElement(TotalConceptos, 'Conceptos')
	ET.SubElement(Conceptos, 'Concepto_Cod').text='200'
	ET.SubElement(Conceptos, 'ValorConcepto').text='1190'

	Conceptos = ET.SubElement(TotalConceptos, 'Conceptos')
	ET.SubElement(Conceptos, 'Concepto_Cod').text='170'
	ET.SubElement(Conceptos, 'ValorConcepto').text='190'

	Conceptos = ET.SubElement(TotalConceptos, 'Conceptos')
	ET.SubElement(Conceptos, 'Concepto_Cod').text='100'
	ET.SubElement(Conceptos, 'ValorConcepto').text='1000'


	# Recaudacion
	Encabezado	= ET.SubElement(Recaudacion, 'Encabezado')
	Detalle		= ET.SubElement(Recaudacion, 'Detalle')

	# Recaudacion/Encabezado
	ET.SubElement(Encabezado, 'IdCajero')
	ET.SubElement(Encabezado, 'Tipo_Vuelto')
	ET.SubElement(Encabezado, 'IdCliente')
	ET.SubElement(Encabezado, 'DigitoVerificador')
	ET.SubElement(Encabezado, 'NombreCompleto')
	ET.SubElement(Encabezado, 'Direccion')
	ET.SubElement(Encabezado, 'Ciudad')
	ET.SubElement(Encabezado, 'Comuna')
	ET.SubElement(Encabezado, 'Telefono')
	ET.SubElement(Encabezado, 'Email')
	ET.SubElement(Encabezado, 'TotalaRecaudar')
	RecaudacionEnc_ext = ET.SubElement(Encabezado, 'RecaudacionEnc_ext')

	# Recaudacion/Encabezado/RecaudacionEnc_ext
	REnExt_Item = ET.SubElement(RecaudacionEnc_ext, 'REnExt_Item')
	ET.SubElement(REnExt_Item, 'RecEnc_opcion')
	ET.SubElement(REnExt_Item, 'RecEnd_datos')


	# Recaudacion/Detalle/FormaPago
	FormaPago = ET.SubElement(Detalle, 'FormaPago')
	ET.SubElement(FormaPago, 'Cod_FormaPago')
	ET.SubElement(FormaPago, 'Cod_MonedaFP')
	ET.SubElement(FormaPago, 'NroCheque')
	ET.SubElement(FormaPago, 'FechaCheque')
	ET.SubElement(FormaPago, 'FechaVencto')
	ET.SubElement(FormaPago, 'Cod_Banco')
	ET.SubElement(FormaPago, 'Cod_Plaza')
	ET.SubElement(FormaPago, 'Referencia')
	ET.SubElement(FormaPago, 'MontoaRec')
	ET.SubElement(FormaPago, 'ParidadRec')
	
	print ("---------------------------------")
	# ET.dump(SDT_DocVentaExt)
	xml = ET.tostring(SDT_DocVentaExt, short_empty_elements=False,  method='xml')


	# xml_1 = '&lt;SDT_DocVentaExt xmlns=&quot;http://www.informat.cl/ws&quot;&gt;&lt;EncDoc&gt;&lt;RefDoc&gt;&lt;NroRefCliente&gt;2-2-101-101&lt;/NroRefCliente&gt;&lt;Modulo&gt;PDV&lt;/Modulo&gt;&lt;NroOrdCom&gt;2&lt;/NroOrdCom&gt;&lt;/RefDoc&gt;&lt;Cliente&gt;&lt;Identificacion&gt;&lt;IdCliente&gt;66666666&lt;/IdCliente&gt;&lt;Nombre_Completo&gt;CLIENTES VARIOS&lt;/Nombre_Completo&gt;&lt;Secuencia&gt;0&lt;/Secuencia&gt;&lt;Direccion&gt;CLIENTES VARIOS&lt;/Direccion&gt;&lt;Comuna&gt;CLIENTES VARIOS&lt;/Comuna&gt;&lt;Ciudad&gt;CLIENTES VARIOS&lt;/Ciudad&gt;&lt;Telefono&gt;CLIENTES VARIOS&lt;/Telefono&gt;&lt;Email /&gt;&lt;/Identificacion&gt;&lt;Facturacion&gt;&lt;Moneda&gt;1&lt;/Moneda&gt;&lt;Tasa&gt;1&lt;/Tasa&gt;&lt;CondVenta&gt;0&lt;/CondVenta&gt;&lt;Origen&gt;0&lt;/Origen&gt;&lt;DocAGenerar&gt;101&lt;/DocAGenerar&gt;&lt;DocRef&gt;0&lt;/DocRef&gt;&lt;NroDocRef&gt;0&lt;/NroDocRef&gt;&lt;NroDoc&gt;10001&lt;/NroDoc&gt;&lt;Estado&gt;0&lt;/Estado&gt;&lt;Equipo&gt;201&lt;/Equipo&gt;&lt;Bodega_Salida&gt;102&lt;/Bodega_Salida&gt;&lt;IdVendedor&gt;4839396&lt;/IdVendedor&gt;&lt;Sucursal_Cod&gt;2&lt;/Sucursal_Cod&gt;&lt;ListaPrecio_Cod /&gt;&lt;Fecha_Atencion&gt;2015-12-15&lt;/Fecha_Atencion&gt;&lt;Fecha_Documento&gt;2016-04-03&lt;/Fecha_Documento&gt;&lt;/Facturacion&gt;&lt;/Cliente&gt;&lt;/EncDoc&gt;&lt;DetDoc&gt;&lt;Items&gt;&lt;Item&gt;&lt;NumItem&gt;1&lt;/NumItem&gt;&lt;FechaEntrega&gt;0&lt;/FechaEntrega&gt;&lt;PrecioRef&gt;1000&lt;/PrecioRef&gt;&lt;Cantidad&gt;1.000000&lt;/Cantidad&gt;&lt;PorcUno&gt;0.00&lt;/PorcUno&gt;&lt;MontoUno&gt;0&lt;/MontoUno&gt;&lt;DescDos_Cod&gt;0&lt;/DescDos_Cod&gt;&lt;DescTre_Cod /&gt;&lt;MontoImpUno&gt;0&lt;/MontoImpUno&gt;&lt;PorcImpUno&gt;0.00&lt;/PorcImpUno&gt;&lt;MontoImpDos&gt;0&lt;/MontoImpDos&gt;&lt;PorcImpDos&gt;0.00&lt;/PorcImpDos&gt;&lt;TotalDocLin&gt;1000&lt;/TotalDocLin&gt;&lt;Producto&gt;&lt;Producto_Vta&gt;0000002572703&lt;/Producto_Vta&gt;&lt;Unidad&gt;Unid&lt;/Unidad&gt;&lt;/Producto&gt;&lt;/Item&gt;&lt;/Items&gt;&lt;/DetDoc&gt;&lt;ResumenDoc&gt;&lt;TotalNeto&gt;840&lt;/TotalNeto&gt;&lt;CodigoDescuento /&gt;&lt;TotalDescuento&gt;0&lt;/TotalDescuento&gt;&lt;TotalIVA&gt;160&lt;/TotalIVA&gt;&lt;TotalOtrosImpuestos&gt;0&lt;/TotalOtrosImpuestos&gt;&lt;TotalDoc&gt;1000&lt;/TotalDoc&gt;&lt;TotalConceptos&gt;&lt;Conceptos&gt;&lt;Concepto_Cod&gt;1&lt;/Concepto_Cod&gt;&lt;ValorConcepto&gt;0&lt;/ValorConcepto&gt;&lt;/Conceptos&gt;&lt;Conceptos&gt;&lt;Concepto_Cod&gt;2&lt;/Concepto_Cod&gt;&lt;ValorConcepto&gt;160&lt;/ValorConcepto&gt;&lt;/Conceptos&gt;&lt;Conceptos&gt;&lt;Concepto_Cod&gt;3&lt;/Concepto_Cod&gt;&lt;ValorConcepto&gt;840&lt;/ValorConcepto&gt;&lt;/Conceptos&gt;&lt;/TotalConceptos&gt;&lt;/ResumenDoc&gt;&lt;Recaudacion&gt;&lt;Encabezado&gt;&lt;IdCajero&gt;4839396&lt;/IdCajero&gt;&lt;Tipo_Vuelto&gt;1&lt;/Tipo_Vuelto&gt;&lt;IdCliente&gt;66666666&lt;/IdCliente&gt;&lt;DigitoVerificador&gt;6&lt;/DigitoVerificador&gt;&lt;NombreCompleto&gt;CLIENTES VARIOS&lt;/NombreCompleto&gt;&lt;Direccion&gt;CLIENTES VARIOS&lt;/Direccion&gt;&lt;Ciudad&gt;CLIENTES VARIOS&lt;/Ciudad&gt;&lt;Comuna&gt;CLIENTES VARIOS&lt;/Comuna&gt;&lt;Telefono&gt;CLIENTES VARIOS&lt;/Telefono&gt;&lt;Email /&gt;&lt;TotalaRecaudar&gt;1000&lt;/TotalaRecaudar&gt;&lt;RecaudacionEnc_ext&gt;&lt;REnExt_Item&gt;&lt;RecEnc_opcion /&gt;&lt;RecEnd_datos /&gt;&lt;/REnExt_Item&gt;&lt;/RecaudacionEnc_ext&gt;&lt;/Encabezado&gt;&lt;Detalle&gt;&lt;FormaPago&gt;&lt;Cod_FormaPago&gt;0&lt;/Cod_FormaPago&gt;&lt;Cod_MonedaFP&gt;1&lt;/Cod_MonedaFP&gt;&lt;NroCheque /&gt;&lt;FechaCheque&gt;2015-12-15&lt;/FechaCheque&gt;&lt;FechaVencto /&gt;&lt;Cod_Banco /&gt;&lt;Cod_Plaza /&gt;&lt;Referencia /&gt;&lt;MontoaRec&gt;1000&lt;/MontoaRec&gt;&lt;ParidadRec&gt;1&lt;/ParidadRec&gt;&lt;/FormaPago&gt;&lt;/Detalle&gt;&lt;/Recaudacion&gt;&lt;/SDT_DocVentaExt&gt;'
	# xml1 = '<SDT_DocVentaExt xmlns="http://www.informat.cl/ws"><EncDoc><RefDoc><NroRefCliente>2-2-101-101</NroRefCliente><Modulo>PDV</Modulo><NroOrdCom>2</NroOrdCom></RefDoc><Cliente><Identificacion><IdCliente>66666666</IdCliente><Nombre_Completo>CLIENTES VARIOS</Nombre_Completo><Secuencia>0</Secuencia><Direccion>CLIENTES VARIOS</Direccion><Comuna>CLIENTES VARIOS</Comuna><Ciudad>CLIENTES VARIOS</Ciudad><Telefono>CLIENTES VARIOS</Telefono><Email /></Identificacion><Facturacion><Moneda>1</Moneda><Tasa>1</Tasa><CondVenta>0</CondVenta><Origen>0</Origen><DocAGenerar>101</DocAGenerar><DocRef>0</DocRef><NroDocRef>0</NroDocRef><NroDoc>101</NroDoc><Estado>0</Estado><Equipo>201</Equipo><Bodega_Salida>102</Bodega_Salida><IdVendedor>4839396</IdVendedor><Sucursal_Cod>2</Sucursal_Cod><ListaPrecio_Cod /><Fecha_Atencion>2015-12-15</Fecha_Atencion><Fecha_Documento>2015-12-15</Fecha_Documento></Facturacion></Cliente></EncDoc><DetDoc><Items><Item><NumItem>1</NumItem><FechaEntrega>0</FechaEntrega><PrecioRef>1000</PrecioRef><Cantidad>1.000000</Cantidad><PorcUno>0.00</PorcUno><MontoUno>0</MontoUno><DescDos_Cod>0</DescDos_Cod><DescTre_Cod /><MontoImpUno>0</MontoImpUno><PorcImpUno>0.00</PorcImpUno><MontoImpDos>0</MontoImpDos><PorcImpDos>0.00</PorcImpDos><TotalDocLin>1000</TotalDocLin><Producto><Producto_Vta>0000002572703</Producto_Vta><Unidad>Unid</Unidad></Producto></Item></Items></DetDoc><ResumenDoc><TotalNeto>840</TotalNeto><CodigoDescuento /><TotalDescuento>0</TotalDescuento><TotalIVA>160</TotalIVA><TotalOtrosImpuestos>0</TotalOtrosImpuestos><TotalDoc>1000</TotalDoc><TotalConceptos><Conceptos><Concepto_Cod>1</Concepto_Cod><ValorConcepto>0</ValorConcepto></Conceptos><Conceptos><Concepto_Cod>2</Concepto_Cod><ValorConcepto>160</ValorConcepto></Conceptos><Conceptos><Concepto_Cod>3</Concepto_Cod><ValorConcepto>840</ValorConcepto></Conceptos></TotalConceptos></ResumenDoc><Recaudacion><Encabezado><IdCajero>4839396</IdCajero><Tipo_Vuelto>1</Tipo_Vuelto><IdCliente>66666666</IdCliente><DigitoVerificador>6</DigitoVerificador><NombreCompleto>CLIENTES VARIOS</NombreCompleto><Direccion>CLIENTES VARIOS</Direccion><Ciudad>CLIENTES VARIOS</Ciudad><Comuna>CLIENTES VARIOS</Comuna><Telefono>CLIENTES VARIOS</Telefono><Email /><TotalaRecaudar>1000</TotalaRecaudar><RecaudacionEnc_ext><REnExt_Item><RecEnc_opcion /><RecEnd_datos /></REnExt_Item></RecaudacionEnc_ext></Encabezado><Detalle><FormaPago><Cod_FormaPago>0</Cod_FormaPago><Cod_MonedaFP>1</Cod_MonedaFP><NroCheque /><FechaCheque>2015-12-15</FechaCheque><FechaVencto /><Cod_Banco /><Cod_Plaza /><Referencia /><MontoaRec>1000</MontoaRec><ParidadRec>1</ParidadRec></FormaPago></Detalle></Recaudacion></SDT_DocVentaExt>'
	# url = 'http://192.168.231.21:8080/wshcvm/servlet/axmldocvtaext?wsdl' # jaime
	# url = 'http://192.168.231.114:8080/ws_inet_clp/servlet/axmldocvta?wsdl'# nuevo
	url = 'http://192.168.231.114:8080/ws_inet_clp/servlet/axmldocvtaext?wsdl' #nuevo2
	client1 = Client(url)
	response = client1.service.Execute(xml.decode())

	for error in response.SDT_ERRORES_ERROR:
		print (error.DESCERROR)

	# return response

	

	return data


def filtrar_contratos(request):

	data 		= list()
	var_post 	= request.POST.copy()

	mes_inicio	= var_post['mes_inicio']
	ano_inicio	= var_post['ano_inicio']
	mes_termino	= var_post['mes_termino']
	ano_termino	= var_post['ano_termino']
	activo_id	= var_post['activo']
	# concepto 	= var_post['concepto'] {falta: buscar los contratos con estos conceptos}

	fecha_inicio 	= ultimo_dia(datetime.strptime('01/'+mes_inicio+'/'+ano_inicio+'', "%d/%m/%Y"))
	fecha_termino 	= ultimo_dia(datetime.strptime('01/'+mes_termino+'/'+ano_termino+'', "%d/%m/%Y"))
	activo 			= Activo.objects.get(id=activo_id)
	locales 		= activo.local_set.all().values_list('id', flat=True)
	contratos 		= Contrato.objects.filter(locales__in=locales, fecha_habilitacion__lte=fecha_inicio, fecha_termino__gte=fecha_termino, visible=True).distinct() # {falta: buscar por la fecha de activació del contrato}

	for contrato in contratos:
		data.append({
			'id'					: contrato.id,
			'numero'				: contrato.numero,
			'fecha_inicio'			: contrato.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'			: contrato.fecha_termino.strftime('%d/%m/%Y'),
			'fecha_habilitacion'	: contrato.fecha_habilitacion.strftime('%d/%m/%Y'),
			'cliente'				: contrato.cliente.nombre,
			'locales'				: 'locales', # {falta: poner locales}
		})	

	return JsonResponse(data, safe=False)



def calculo_arriendo_minimo(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):

		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato, concepto=concepto)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle = Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)

					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor 			= detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros 			= metros_total['metros_cuadrados__sum']
						metros_local 	= metros_total['metros_cuadrados__sum']
					else:
						factor 			= detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros 			= 1
						metros_local 	=  None

					valor = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and arriendo.por_meses is False and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):
						reajuste = True

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						total = valor * reajuste_valor

					elif arriendo.reajuste is True and arriendo.por_meses is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						reajuste_factor = int((meses_entre_fechas(arriendo.fecha_inicio, fecha) -1)/arriendo.meses)

						if arriendo.moneda.id == 6:
							reajuste_valor = ((arriendo.valor * reajuste_factor)/100)+1
						else:
							reajuste_valor = (arriendo.valor * reajuste_factor) * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						total = valor * reajuste_valor
						reajuste = True

					else:
						reajuste 		= False
						reajuste_valor 	= None
						total 			= valor

				else:
					valor			= None
					metro_cuadrado	= False
					metros_local    = None
					reajuste		= False
					reajuste_valor	= None
					total 			= None

			except Arriendo.DoesNotExist:
				valor			= None
				metro_cuadrado	= False
				metros_local 	= None
				reajuste		= False
				reajuste_valor	= None
				total 			= None


			# Detalle_Arriendo_Minimo(
			# 	valor			= valor,
			# 	metro_cuadrado	= metro_cuadrado,
			# 	metros_local	= metros_local,
			# 	reajuste		= reajuste,
			# 	reajuste_valor	= reajuste_valor,
			# 	total 			= total,
			# 	fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
			# 	fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
			# 	proceso 		= proceso,
			# 	contrato 		= contrato,
			# ).save()

			Proceso_Detalle(
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				total 			= total,
				proceso 		= proceso,
				contrato 		= contrato,
				concepto 		= concepto,
			).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_arriendo_variable(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):

		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()

			# cálculo arriendo mínimo {falta: ver que el valor sea del mes anterior}
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato, concepto=concepto)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)
					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = metros_total['metros_cuadrados__sum']
					else:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = 1

					valor = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and arriendo.por_meses is False and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):
						reajuste = True

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					elif arriendo.reajuste is True and arriendo.por_meses is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						reajuste_factor = int((meses_entre_fechas(arriendo.fecha_inicio, fecha) -1)/arriendo.meses)

						if arriendo.moneda.id == 6:
							reajuste_valor = ((arriendo.valor * reajuste_factor)/100)+1
						else:
							reajuste_valor = (arriendo.valor * reajuste_factor) * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					else:
						arriendo_minimo = valor

				else:
					arriendo_minimo = None

			except Arriendo.DoesNotExist:
				arriendo_minimo = None






			# try:

			# 	arriendos = Arriendo_Variable.objects.filter(contrato=contrato)

			# 	for arriendo_variable in arriendos:

			# 		mes_inicio 		= arriendo_variable.mes_inicio if arriendo_variable.mes_inicio > 9 else '0'+str(arriendo_variable.mes_inicio)
			# 		mes_termino 	= arriendo_variable.mes_termino if arriendo_variable.mes_termino > 9 else '0'+str(arriendo_variable.mes_termino)
			# 		anio_inicio 	= arriendo_variable.anio_inicio
			# 		anio_termino 	= arriendo_variable.anio_termino

			# 		fecha_inicio 	= primer_dia(datetime.strptime('01/'+str(mes_inicio)+'/'+str(anio_inicio), "%d/%m/%Y")).date()
			# 		fecha_termino 	= ultimo_dia(datetime.strptime('01/'+str(mes_termino)+'/'+str(anio_termino), "%d/%m/%Y")).date()
				
			# 		if fecha >= fecha_inicio and fecha <= fecha_termino

				

			# except Exception:
			# 	pass
			# 	# valor 	= None
			# 	# ventas 	= None
			# 	# total 	= None


			


			try:
				existe = Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()
				# existe = Arriendo_Variable.objects.filter(contrato=contrato, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()

				if existe is True:
					# detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					valor 			= detalle[0].valor
					ventas 			= 0
					ventas_local 	= Venta.objects.filter(local_id__in=locales).\
					extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
					values('year', 'month', 'local_id').\
					annotate(Sum('valor'))

					for venta in ventas_local:
						if fecha.month == venta['month'] and fecha.year == venta['year']:
							ventas += venta['valor__sum']

					if ((ventas * valor) / 100) >= arriendo_minimo and arriendo_minimo is not None:
						total = ((ventas * valor) / 100) - arriendo_minimo
					else:
						total = 0

				else:
					valor 	= None
					ventas 	= None
					total 	= None

			except Exception:
				valor 	= None
				ventas 	= None
				total 	= None

			Detalle_Arriendo_Variable(
				valor 			= valor,
				ventas 			= ventas,
				arriendo_minimo = arriendo_minimo,
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_gasto_comun(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):
		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
						
			activos 		= contrato.locales.all().values_list('activo_id', flat=True)
			metros_total   	= Local.objects.filter(activo__in=activos, prorrateo=True).aggregate(Sum('metros_cuadrados'))

			for local in locales:

				if Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto, local=local).exists():
					gasto_comun = Gasto_Comun.objects.filter(contrato=contrato, concepto=concepto, local=local)
					if gasto_comun[0].prorrateo == True:
						valor 		= gasto_comun[0].valor
						prorrateo 	= True
						try:
							gasto_mensual 	= Gasto_Mensual.objects.get(activo=local.activo, mes=fecha.month, anio=fecha.year).valor
							total 		 	= ((local.metros_cuadrados * gasto_mensual) / metros_total['metros_cuadrados__sum'])*((100+valor))/100

						except Exception:
							gasto_mensual	= None
							total 			= None
					else:
						factor 			= gasto_comun[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						valor 			= gasto_comun[0].valor
						gasto_mensual 	= None
						prorrateo 		= False
						total 			= valor * factor
				else:
					valor 			= None
					gasto_mensual 	= None
					prorrateo 		= False
					total 			= None

				Detalle_Gasto_Comun(
					valor 			= valor,
					prorrateo		= prorrateo,
					gasto_mensual 	= gasto_mensual,
					metros_total 	= metros_total['metros_cuadrados__sum'],
					total 			= total, 
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso 		= proceso,
					contrato 		= contrato,
					local 			= local,
				).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_servicios_basico(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):

		for item in contratos:
			
			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.values_list('id', flat=True).all()	
			medidores_luz  	= Medidor_Electricidad.objects.filter(local__in=locales)
			medidores_agua  = Medidor_Agua.objects.filter(local__in=locales)
			medidores_gas  	= Medidor_Gas.objects.filter(local__in=locales)


			for medidor in medidores_luz:
				try:
					valor_anterior 	= Lectura_Electricidad.objects.get(medidor_electricidad=medidor, mes=(fecha.month-1), anio=fecha.year).valor
				except Exception:
					valor_anterior	= None
				try:
					valor_actual 	= Lectura_Electricidad.objects.get(medidor_electricidad=medidor, mes=fecha.month, anio=fecha.year).valor
				except Exception:
					valor_actual	= None
				try:
					if medidor.local.servicio_basico_set.all().exists():
						servicios_basicos = medidor.local.servicio_basico_set.all()
						valor_luz = servicios_basicos[0].valor_electricidad
					else:
						valor_luz	= None
				except Exception:
					valor_luz	= None

				Detalle_Electricidad(
					valor			= valor_luz,
					valor_anterior	= valor_anterior,
					valor_actual	= valor_actual,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso			= proceso,
					contrato		= contrato,
					medidor			= medidor,
				).save()

			for medidor in medidores_agua:
				try:
					lectura_anterior 	= Lectura_Agua.objects.get(medidor_electricidad=medidor, mes=(fecha.month-1), anio=fecha.year)
				except Exception as error:
					lectura_anterior	= None
				try:
					lectura_actual 		= Lectura_Agua.objects.get(medidor_electricidad=medidor, mes=fecha.month, anio=fecha.year)
				except Exception as error:
					lectura_actual		= None
				try:
					if medidor.local.servicio_basico_set.all().exists():
						servicios_basicos = medidor.local.servicio_basico_set.all()
						valor_agua = servicios_basicos[0].valor_agua
					else:
						valor_agua	= None
				except Exception:
					valor_agua	= None

				Detalle_Agua(
					valor			= valor_agua,
					valor_anterior	= lectura_anterior,
					valor_actual	= lectura_actual,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso			= proceso,
					contrato		= contrato,
					medidor			= medidor,
				).save()

			for medidor in medidores_gas:
				try:
					lectura_anterior 	= Lectura_Gas.objects.get(medidor_electricidad=medidor, mes=(fecha.month-1), anio=fecha.year)
				except Exception as error:
					lectura_anterior	= None
				try:
					lectura_actual 		= Lectura_Gas.objects.get(medidor_electricidad=medidor, mes=fecha.month, anio=fecha.year)
				except Exception as error:
					lectura_actual		= None
				try:
					if medidor.local.servicio_basico_set.all().exists():
						servicios_basicos = medidor.local.servicio_basico_set.all()
						valor_gas = servicios_basicos[0].valor_gas
					else:
						valor_gas	= None
				except Exception:
					valor_gas	= None

				Detalle_Gas(
					valor			= valor_gas,
					valor_anterior	= lectura_actual,
					valor_actual	= lectura_actual,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso			= proceso,
					contrato		= contrato,
					medidor			= medidor,
				).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_cuota_incorporacion(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):
		for item in contratos:

			contrato = Contrato.objects.get(id=item)
			
			try:
				existe = Cuota_Incorporacion.objects.filter(contrato=contrato, concepto=concepto, fecha__year=fecha.year, fecha__month=fecha.month).exists()

				if existe is True:
					cuota_incorporacion = Cuota_Incorporacion.objects.filter(contrato=contrato, concepto=concepto, fecha__year=fecha.year, fecha__month=fecha.month)

					if cuota_incorporacion[0].metro_cuadrado == True:
						metros_cuadrados = cuota_incorporacion[0].contrato.locales.all().aggregate(Sum('metros_cuadrados'))['metros_cuadrados__sum']
					else:
						metros_cuadrados = 1

					valor 				= cuota_incorporacion[0].valor
					factor 				= cuota_incorporacion[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
					total 				= valor * factor * metros_cuadrados
				else:
					valor 	= None
					factor 	= None
					total 	= None

			except Cuota_Incorporacion.DoesNotExist:
				valor 			= None
				factor 			= None
				total 			= None

			Detalle_Cuota_Incorporacion(
				valor 			= valor,
				factor 			= factor,
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_fondo_promocion(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):
		for item in contratos:

			contrato = Contrato.objects.get(id=item)

			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato, concepto=concepto)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)
					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = metros_total['metros_cuadrados__sum']
					else:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = 1

					valor = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and arriendo.por_meses is False and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):
						reajuste = True

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					elif arriendo.reajuste is True and arriendo.por_meses is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						reajuste_factor = int((meses_entre_fechas(arriendo.fecha_inicio, fecha) -1)/arriendo.meses)

						if arriendo.moneda.id == 6:
							reajuste_valor = ((arriendo.valor * reajuste_factor)/100)+1
						else:
							reajuste_valor = (arriendo.valor * reajuste_factor) * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor * reajuste_valor

					else:
						arriendo_minimo = valor

				else:
					arriendo_minimo = None

			except Arriendo.DoesNotExist:
				arriendo_minimo = None

			try:
				# existe = Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()
				existe = Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year).exists()
				if existe is True:
					# detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, concepto=concepto, anio_inicio__lte=fecha.year, anio_termino__gte=fecha.year)	
					valor 			= detalle[0].valor
					ventas 			= 0
					ventas_local 	= Venta.objects.filter(local_id__in=locales).\
					extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
					values('year', 'month', 'local_id').\
					annotate(Sum('valor'))

					for venta in ventas_local:
						if fecha.month == venta['month'] and fecha.year == venta['year']:
							ventas += venta['valor__sum']

					if ((ventas * valor) / 100) >= arriendo_minimo and arriendo_minimo is not None:
						arriendo_reajustable = ((ventas * valor) / 100)
					elif arriendo_minimo is not None:
						arriendo_reajustable = arriendo_minimo
					else:
						arriendo_reajustable = 0

				else:
					arriendo_reajustable 	= None

			except Exception:
				arriendo_reajustable = None

			try:
				fondos_promocion = Fondo_Promocion.objects.filter(contrato=contrato, concepto=concepto)

				for fondo_promocion in fondos_promocion:
					
					if fondo_promocion.periodicidad == 0:

						mes_1 = sumar_meses(fondo_promocion.fecha, 11)

						try:
							if fecha.month == mes_1.month and fecha.month >= fondo_promocion.fecha.month and fecha.year >= fondo_promocion.fecha.year:
								valor 	= fondo_promocion.valor
								factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
								total 	= valor * factor
							else:
								valor 	= None
								factor 	= None
								total 	= None
							
						except Exception:
							valor 	= None
							factor 	= None
							total 	= None

					elif fondo_promocion.periodicidad == 1:

						mes_1 = sumar_meses(fondo_promocion.fecha, 5)
						mes_2 = sumar_meses(fondo_promocion.fecha, 11)

						try:
							if (fecha.month == mes_1.month or fecha.month==mes_2.month) and fecha.month >= fondo_promocion.fecha.month and fecha.year >= fondo_promocion.fecha.year:
								valor 	= fondo_promocion.valor
								factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
								total 	= valor * factor
							else:
								valor 	= None
								factor 	= None
								total 	= None
							
						except Exception:
							valor 	= None
							factor 	= None
							total 	= None

					elif fondo_promocion.periodicidad == 2:

						mes_1 = sumar_meses(fondo_promocion.fecha, 2)
						mes_2 = sumar_meses(fondo_promocion.fecha, 5)
						mes_3 = sumar_meses(fondo_promocion.fecha, 8)
						mes_4 = sumar_meses(fondo_promocion.fecha, 11)

						try:
							if (fecha.month == mes_1.month or fecha.month==mes_2.month or fecha.month==mes_3.month or fecha.month==mes_4.month) and fecha.month >= fondo_promocion.fecha.month and fecha.year >= fondo_promocion.fecha.year:
								valor 	= fondo_promocion.valor
								factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
								total 	= valor * factor
							else:
								valor 	= None
								factor 	= None
								total 	= None
						except Exception:
							valor 	= None
							factor 	= None
							total 	= None

					elif fondo_promocion.periodicidad == 3 and fecha.month >= fondo_promocion.fecha.month and fecha.year >= fondo_promocion.fecha.year:

						valor 	= fondo_promocion.valor
						factor 	= fondo_promocion.moneda.moneda_historial_set.all().order_by('-id').first().valor
						total 	= valor * factor

					else:
						valor 			= None
						factor 			= None
						total 			= None

					if arriendo_reajustable is not None and valor is not None:
						total = (arriendo_reajustable * valor) / 100
					else:
						total = None

					Detalle_Fondo_Promocion(
						valor 			= valor,
						factor 			= factor,
						total 			= total,
						fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
						fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
						proceso 		= proceso,
						contrato 		= contrato,
					).save()

			except Fondo_Promocion.DoesNotExist:

				Detalle_Fondo_Promocion(
					valor 			= None,
					factor 			= None,
					total 			= None,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso 		= proceso,
					contrato 		= contrato,
				).save()

		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_arriendo_bodega(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):
			
		for item in contratos:

			contrato = Contrato.objects.get(id=item)

			try:
				arriendo_bodegas 	= Arriendo_Bodega.objects.filter(contrato=contrato, concepto=concepto)
				total 				= 0

				for arriendo_bodega in arriendo_bodegas:
					
					if arriendo_bodega.periodicidad == 0 and fecha.month >= arriendo_bodega.fecha_inicio.month and fecha.year >= arriendo_bodega.fecha_inicio.year:

						mes_1 = sumar_meses(arriendo_bodega.fecha_inicio, 11)
						
						if fecha.month == mes_1.month:
							valor 	= arriendo_bodega.valor
							factor 	= arriendo_bodega.moneda.moneda_historial_set.all().order_by('-id').first().valor

							if arriendo_bodega.metro_cuadrado == True:
								if contrato.bodega is True:
									metros = contrato.metros_bodega
								else:
									metros = 0
							else:
								metros = 1

							total += valor * factor * metros
						else:
							total += 0

					elif arriendo_bodega.periodicidad == 1:

						mes_1 = sumar_meses(arriendo_bodega.fecha_inicio, 5)
						mes_2 = sumar_meses(arriendo_bodega.fecha_inicio, 11)

						if (fecha.month == mes_1.month or fecha.month==mes_2.month) and fecha.month >= arriendo_bodega.fecha_inicio.month and fecha.year >= arriendo_bodega.fecha_inicio.year:
							valor 	= arriendo_bodega.valor
							factor 	= arriendo_bodega.moneda.moneda_historial_set.all().order_by('-id').first().valor

							if arriendo_bodega.metro_cuadrado == True:
								if contrato.bodega is True:
									metros = contrato.metros_bodega
								else:
									metros = 0
							else:
								metros = 1

							total += valor * factor * metros
						else:
							total += 0

					elif arriendo_bodega.periodicidad == 2:

						mes_1 = sumar_meses(arriendo_bodega.fecha_inicio, 2)
						mes_2 = sumar_meses(arriendo_bodega.fecha_inicio, 5)
						mes_3 = sumar_meses(arriendo_bodega.fecha_inicio, 8)
						mes_4 = sumar_meses(arriendo_bodega.fecha_inicio, 11)

						if (fecha.month == mes_1.month or fecha.month==mes_2.month or fecha.month==mes_3.month or fecha.month==mes_4.month) and fecha.month >= arriendo_bodega.fecha_inicio.month and fecha.year >= arriendo_bodega.fecha_inicio.year:
							valor 	= arriendo_bodega.valor
							factor 	= arriendo_bodega.moneda.moneda_historial_set.all().order_by('-id').first().valor

							if arriendo_bodega.metro_cuadrado == True:
								if contrato.bodega is True:
									metros = contrato.metros_bodega
								else:
									metros = 0
							else:
								metros = 1

							total += valor * factor * metros
						else:
							total += 0

					elif arriendo_bodega.periodicidad == 3:

						if fecha.month >= arriendo_bodega.fecha_inicio.month and fecha.year >= arriendo_bodega.fecha_inicio.year:
							valor 	= arriendo_bodega.valor
							factor 	= arriendo_bodega.moneda.moneda_historial_set.all().order_by('-id').first().valor

							if arriendo_bodega.metro_cuadrado == True:
								if contrato.bodega is True:
									metros = contrato.metros_bodega
								else:
									metros = 0
							else:
								metros = 1

							total += valor * factor * metros
						else:
							total += 0

					else:
						total += 0

			except Arriendo_Bodega.DoesNotExist:
				total = None

			
			Detalle_Arriendo_Bodega(
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()


		fecha = sumar_meses(fecha, 1)

	return 'ok'

def calculo_servicios_varios(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):
		for item in contratos:

			contrato 	= Contrato.objects.get(id=item)
			locales 	= contrato.locales.all()

			for local in locales:
				
				if local.gasto_servicio_set.all().filter(mes=fecha.month, anio=fecha.year).exists():
					total = 0
					servicios = local.gasto_servicio_set.all().filter(mes=fecha.month, anio=fecha.year)
					for servicio in servicios:
						cantidad_locales = servicio.locales.all().count()
						total 			+= servicio.valor / cantidad_locales
				else:
					total = None

				Detalle_Gasto_Servicio(
					total 			= total,
					fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
					fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
					proceso 		= proceso,
					contrato 		= contrato,
					local 			= local,
				).save()

		fecha = sumar_meses(fecha, 1)

def calculo_multas(request, proceso, contratos, meses, fecha, concepto):

	for x in range(meses):
		for item in contratos:

			contrato = Contrato.objects.get(id=item)

			if Multa.objects.filter(contrato=contrato, mes=fecha.month, anio=fecha.year).exists():
				multas 	= Multa.objects.filter(contrato=contrato, mes=fecha.month, anio=fecha.year)
				total 	= 0
				for multa in multas:
					total += multa.valor * multa.moneda.moneda_historial_set.all().order_by('-id').first().valor
			else:
				total = None

			Detalle_Multa(
				total 			= total,
				fecha_inicio	= primer_dia(fecha).strftime('%Y-%m-%d'),
				fecha_termino	= ultimo_dia(fecha).strftime('%Y-%m-%d'),
				proceso 		= proceso,
				contrato 		= contrato,
			).save()

		fecha = sumar_meses(fecha, 1)



def data_arriendo_minimo(proceso, concepto):

	data 	= {}
	detalle = []
	total 	= 0
	
	detalles = Proceso_Detalle.objects.filter(proceso=proceso, concepto=concepto)

	for item in detalles:

		contrato = item.contrato
		locales = contrato.locales.all()

		detalle.append({
			# 'valor'				: item.valor if item.valor is not None else '---',
			# 'metro_cuadrado'	: 'SI' if item.metro_cuadrado == True else 'No',
			# 'metros_local'		: item.metros_local if item.metro_cuadrado is True and item.metros_local is not None else '---',
			# 'reajuste'			: 'SI' if item.reajuste == True else 'No',
			# 'reajuste_valor'	: item.reajuste_valor if item.reajuste_valor is not None else '---',
			'total'				: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
			# 'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_arriendo_variable(proceso):

	data 	= {}
	detalle = []
	total 	= 0

	detalles = Detalle_Arriendo_Variable.objects.filter(proceso=proceso)

	for item in detalles:

		contrato = item.contrato
		locales = contrato.locales.all()

		detalle.append({
			'valor' 			: item.valor if item.valor is not None else '---',
			'ventas' 			: item.ventas if item.ventas is not None else '---',
			'arriendo_minimo' 	: item.arriendo_minimo if item.arriendo_minimo is not None else '---',
			'total' 			: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
			'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_servicios_basicos(proceso):

	data 			= {}
	detalles 		= []
	detalle 		= []
	total			= 0

	detalles_luz 	= Detalle_Electricidad.objects.filter(proceso=proceso)
	detalles_agua 	= Detalle_Agua.objects.filter(proceso=proceso)
	detalles_gas 	= Detalle_Gas.objects.filter(proceso=proceso)

	for item in detalles_luz:
		detalles.append(item)

	for item in detalles_agua:
		detalles.append(item)

	for item in detalles_gas:
		detalles.append(item)


	for item in detalles:
		detalle.append({
			'medidor'			: item.medidor.nombre,
			'lectura_anterior' 	: item.valor_anterior if item.valor_anterior is not None else '---',
			'lectura_actual' 	: item.valor_actual if item.valor_actual is not None else '---',
			'valor' 			: item.valor if item.valor is not None else '---',
			'diferencia'		: (item.valor_actual - item.valor_anterior) if item.valor_anterior is not None and item.valor_actual is not None else '---',
			'total'				: formato_moneda((item.valor_actual - item.valor_anterior) * item.valor) if item.valor_anterior is not None and item.valor_actual is not None and item.valor is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'cliente'			: item.contrato.cliente.nombre,
			'nombre_local'		: item.contrato.nombre_local,
			'local'				: item.medidor.local.nombre,
		})

		total += (item.valor_actual - item.valor_anterior) * item.valor if item.valor_anterior is not None and item.valor_actual is not None and item.valor is not None else 0

	
	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_gastos_comunes(proceso):

	data 			= {}
	detalle 		= []
	total			= 0

	detalles = Detalle_Gasto_Comun.objects.filter(proceso=proceso)

	for item in detalles:
		detalle.append({
			'proratea' 			: 'si' if item.prorrateo == True else '---',
			'valor' 			: item.valor if item.valor is not None else '---',
			'metros_local' 		: item.local.metros_cuadrados,
			'factor' 			: item.gasto_mensual if item.gasto_mensual is not None else '---',
			'total' 			: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'cliente'			: item.contrato.cliente.nombre,
			'nombre_local'		: item.contrato.nombre_local,
			'local'				: item.local.nombre,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_cuota_incorporacion(proceso):

	data 	= {}
	detalle = []
	total 	= 0
	
	detalles = Detalle_Cuota_Incorporacion.objects.filter(proceso=proceso)

	for item in detalles:

		contrato 	= item.contrato
		locales 	= contrato.locales.all()

		detalle.append({
			'valor'				: item.valor if item.valor is not None else '---',
			'factor'			: item.factor if item.factor is not None else '---',
			'total'				: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
			'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_fondo_promocion(proceso):

	data 	= {}
	detalle = []
	total 	= 0
	
	detalles = Detalle_Fondo_Promocion.objects.filter(proceso=proceso)

	for item in detalles:

		contrato 	= item.contrato
		locales 	= contrato.locales.all()

		detalle.append({
			'valor'				: item.valor if item.valor is not None else '---',
			'factor'			: item.factor if item.factor is not None else '---',
			'total'				: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: contrato.numero,
			'cliente'			: contrato.cliente.nombre,
			'nombre_local'		: contrato.nombre_local,
			'locales'			: locales,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_arriendo_bodega(proceso):

	data 			= {}
	detalle 		= []
	total			= 0

	detalles = Detalle_Arriendo_Bodega.objects.filter(proceso=proceso)

	for item in detalles:
		detalle.append({
			'total' 			: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'cliente'			: item.contrato.cliente.nombre,
			'nombre_local'		: item.contrato.nombre_local,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_servicios_varios(proceso):

	data 			= {}
	detalle 		= []
	total			= 0

	detalles = Detalle_Gasto_Servicio.objects.filter(proceso=proceso)

	for item in detalles:
		detalle.append({
			'total' 			: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'cliente'			: item.contrato.cliente.nombre,
			'nombre_local'		: item.contrato.nombre_local,
			'local'				: item.local.nombre,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data

def data_multas(proceso):

	data 			= {}
	detalle 		= []
	total			= 0

	detalles = Detalle_Multa.objects.filter(proceso=proceso)

	for item in detalles:
		detalle.append({
			'total' 			: formato_moneda(item.total) if item.total is not None else '---',
			'fecha_inicio'		: item.fecha_inicio.strftime('%d/%m/%Y'),
			'fecha_termino'		: item.fecha_termino.strftime('%d/%m/%Y'),
			'contrato'			: item.contrato.numero,
			'cliente'			: item.contrato.cliente.nombre,
			'nombre_local'		: item.contrato.nombre_local,
		})

		total += item.total if item.total is not None else 0

	data['detalle'] = detalle
	data['total'] 	= total

	return data


# funciones globales

def arriendo_minimo_reajustable(contratos, meses, fecha):

	data = list()

	for x in range(meses):

		for item in contratos:

			contrato 		= Contrato.objects.get(id=item)
			locales 		= contrato.locales.all()
			metros_total 	= contrato.locales.all().aggregate(Sum('metros_cuadrados'))

			try:
				arriendo 	= Arriendo.objects.get(contrato=contrato)
				existe 		= Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()

				if existe is True:
					detalle = Arriendo_Detalle.objects.filter(arriendo=arriendo, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)

					metro_cuadrado	= detalle[0].metro_cuadrado
					
					if metro_cuadrado is True:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = metros_total['metros_cuadrados__sum']
					else:
						factor = detalle[0].moneda.moneda_historial_set.all().order_by('-id').first().valor
						metros = 1

					valor_arriendo_minimo = detalle[0].valor * factor * metros

					if arriendo.reajuste is True and fecha >= sumar_meses(arriendo.fecha_inicio, arriendo.meses):

						if arriendo.moneda.id == 6:
							reajuste_valor = (arriendo.valor/100)+1
						else:
							reajuste_valor = arriendo.valor * arriendo.moneda.moneda_historial_set.all().order_by('-id').first().valor

						arriendo_minimo = valor_arriendo_minimo * reajuste_valor

					else:
						arriendo_minimo = valor_arriendo_minimo

				else:
					arriendo_minimo = 0

			except Arriendo.DoesNotExist:
				arriendo_minimo = 0

			try:
				existe = Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month).exists()
				if existe is True:
					detalle 		= Arriendo_Variable.objects.filter(contrato=contrato, mes_inicio__lte=fecha.month, mes_termino__gte=fecha.month)	
					valor 			= detalle[0].valor
					ventas 			= 0
					ventas_local 	= Venta.objects.filter(local_id__in=locales).\
					extra(select={'year': "EXTRACT(year FROM fecha_inicio)",'month': "EXTRACT(month FROM fecha_inicio)", 'id': "id"}).\
					values('year', 'month', 'local_id').\
					annotate(Sum('valor'))

					for venta in ventas_local:
						if fecha.month == venta['month'] and fecha.year == venta['year']:
							ventas += venta['valor__sum']

					arriendo_variable = ((ventas * valor) / 100)

					if arriendo_variable >= arriendo_minimo:
						total = arriendo_variable
					else:
						total = arriendo_minimo

				else:
					valor 			= None
					ventas 			= None
					total 			= None

			except Exception:

				valor 			= None
				ventas 			= None
				total 			= None

			data.append({
				'arriendo_minimo' 	: arriendo_minimo,
				'arriendo_variable' : arriendo_variable,
				'total' 			: total,
				'fecha_inicio'		: primer_dia(fecha).strftime('%Y-%m-%d'),
				'fecha_termino'		: ultimo_dia(fecha).strftime('%Y-%m-%d'),
				'contrato' 			: contrato,
				})

		fecha = sumar_meses(fecha, 1)

	return data

def propuesta_pdf(proceso, pk=None):

	if pk is not None:
		proceso = Proceso.objects.get(id=pk)

	options = {
		# 'orientation': 'Landscape',
		'margin-top': '0.5in',
		'margin-right': '0.2in',
		'margin-left': '0.2in',
		'margin-bottom': '0.5in',
		'encoding': "UTF-8",
		}

	css 		= 'static/assets/css/bootstrap.min.css'
	template 	= get_template('pdf/procesos/propuesta_facturacion.html')

	total 		= 0
	detalle 	= []


	conceptos_id = Proceso_Detalle.objects.filter(proceso=proceso).values_list('concepto_id', flat=True)

	for concepto_id in conceptos_id:
		concepto = Concepto.objects.get(id=concepto_id)

		if concepto.concepto_tipo.id == 1:
			data = data_arriendo_minimo(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 2:
			data = data_arriendo_variable(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 3:
			data = data_gastos_comunes(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 4:
			data = data_servicios_basicos(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 5:
			data = data_cuota_incorporacion(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 6:
			data = data_fondo_promocion(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 7:
			data = data_arriendo_bodega(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 8:
			data = data_servicios_varios(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		elif concepto.concepto_tipo.id == 9:
			data = data_multas(proceso, concepto)
			item = {'tipo': concepto.concepto_tipo.id, 'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

		else:
			print ('error: concepto no definido')

		detalle.append(item)
		total += data['total']




	# for concepto in proceso.conceptos.all():

	# 	if concepto.id == 1:
	# 		data = data_arriendo_minimo(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 2:
	# 		data = data_arriendo_variable(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 3:
	# 		data = data_gastos_comunes(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 4:
	# 		data = data_servicios_basicos(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 5:
	# 		data = data_cuota_incorporacion(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 6:
	# 		data = data_fondo_promocion(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 7:
	# 		data = data_arriendo_bodega(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 8:
	# 		data = data_servicios_varios(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	elif concepto.id == 9:
	# 		data = data_multas(proceso)
	# 		item = {'id': concepto.id, 'nombre': concepto.nombre, 'detalle': data['detalle'], 'total': formato_moneda(data['total'])}

	# 	else:
	# 		print ('error: concepto no definido')

	# 	detalle.append(item)
	# 	total += data['total']

	print (detalle)

	context = Context({
		'proceso' 	: proceso,
		'detalle' 	: detalle,
		'total'		: formato_moneda(total),
	})

	html 		= template.render(context)
	pdfkit.from_string(html, 'public/media/contratos/propuesta_facturacion.pdf', options=options, css=css)
	pdf 		= open('public/media/contratos/propuesta_facturacion.pdf', 'rb')
	response 	= HttpResponse(pdf.read(), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename=propuesta_facturacion.pdf'
	pdf.close()

	return response






