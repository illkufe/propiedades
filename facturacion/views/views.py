from django.views.generic import  FormView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.exceptions import *
from django.shortcuts import render, get_object_or_404
from django.http import *

from accounts.models import UserProfile
from facturacion.forms.forms_parametros import *
from facturacion.app.parametros_facturacion import *
from facturacion.forms.forms_caf import FiltroFoliosDocumentosForm
from facturacion.app.facturacion import *
from facturacion.models import *

from administrador.views import Cliente, Empresa
from procesos.models import Factura
from utilidades.views import formato_numero_sin_miles

from datetime import timedelta


import datetime
import xml.etree.ElementTree as etree


##-------------------------TIPOS DE PRODUCTOS---------------------------------------------------------------------------



def visualizar_configuracion(request):

    name = 'Lista'
    title = 'Facturación'
    subtitle = 'Parametros de Configuración'
    href = '/configuracion/visualizar/'
    parametros = ParametrosFacturacion.objects.all()

    return render(request, 'configuracion/visualizar_configuracion.html', {
                  'name': name,
                  'title': title,
                  'subtitle': subtitle,
                  'href': href,
                  'parametros': parametros
    })

class AjaxableResponseMixinParametroFacturacion(object):
    template_name = 'configuracion/crea_configuracion.html'
    form_class = ParametrosFacturacionForms
    success_url =  '/configuracion/list'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.save()


    def form_invalid(self, form):
        pass

class ParametroFacturacionNew(AjaxableResponseMixinParametroFacturacion, FormView):

    def get_context_data(self, **kwargs):

        context = super(ParametroFacturacionNew, self).get_context_data(**kwargs)
        context['title'] = 'Facturación'
        context['subtitle'] = 'Parametros de Facturación'
        context['name'] = ['Nuevo']
        context['href'] = 'configuracion/list'
        context['accion'] = 'create'

        # if self.request.POST:
        #     context['parametro'] = ParametrosFacturacionForms(self.request.POST)
        #     context['conexion'] = ConexionFacturacionFormSet(self.request.POST)
        # else:
        #     context['parametro'] = ParametrosFacturacionForms()
        #     context['conexion'] = ConexionFacturacionFormSet()

        return context


@login_required
@csrf_exempt
def crear_configuracion(request):
    name = 'Nuevo'
    title = 'Facturación'
    subtitle = 'Parametros de Configuración'
    href = '/configuracion/visualizar/'

    po = request.method
    lista_error = list()
    kwargs = {}


    if request.method == 'POST':
        parametros = ParametrosFacturacionForms(request.POST)
        conexion = ConexionFacturacionForms()
        if parametros.is_valid():
            kwargs['persona'] = request.POST.get('persona')
            kwargs['codigo_conexion'] = request.POST.get('codigo_conexion')
            kwargs['detalle_conexion'] = request.POST.get('detalle_conexion')
            kwargs['motor_emision'] = request.POST.get('motor_emision')

            error = guarda_parametros_facturacion(**kwargs)
            if not error:
                data = {
                    'success': True,
                }
                return JsonResponse(data)
            else:
                data={
                    'success':False,
                    'error':error
                }
                return JsonResponse(data, status=400)

        else:
            if request.is_ajax():
                return JsonResponse(parametros.errors, status=400)

    else:
        parametros = ParametrosFacturacionForms()
        conexion = ConexionFacturacionForms()

    return render(request, 'configuracion/crea_configuracion.html', {
        'name': name,
        'title': title,
        'subtitle': subtitle,
        'href': href,
        'parametros': parametros,
        'conexion' : conexion
    })

@csrf_exempt
def busca_personas(request):

    lista_cliente = list()


    personas = Cliente.objects.filter().all()

    for a in personas:
        data = {
            'id':a.id,
            'id_fiscal':a.rut,
            'razon_social':a.razon_social,
            'nombre_fantasia':a.nombre

        }
        lista_cliente.append(data)

    return JsonResponse({'lista_cliente':lista_cliente})

@csrf_exempt
def valida_rut_cliente(request):

    id_fiscal = request.POST.get('id_fiscal')
    id = request.POST.get('id_cliente')
    tipo = request.POST.get('type')
    list_error = list()
    context = {}

    try:
            persona = Cliente.objects.filter(Q(rut=id_fiscal) | Q(id=id), visible=True).get()

            context = {
                'error': list_error,
                'id': persona.id,
                'id_fiscal': persona.rut,
                'razon': persona.razon_social,
                'nombre': persona.nombre
            }
    except Exception as e:
        error = "No se encuentra el Cliente ingresado."
        list_error.append(error)
        context = {
            'error': list_error
        }

    return JsonResponse(context)

@login_required
@csrf_exempt
def editar_configuracion(request, pk):
    name = 'Edita'
    title = 'Facturación'
    subtitle = 'Parametros de Configuración'
    href = '/configuracion/visualizar/'
    kwargs = {}

    parametro = get_object_or_404(ParametrosFacturacion, pk=pk)

    if request.method == 'POST':
        parametro = ParametrosFacturacionForms(request.POST, instance=parametro)
        if parametro.is_valid():

            kwargs['id_parametro']      = request.POST.get('id_parametro')
            kwargs['persona']           = request.POST.get('persona')
            kwargs['codigo_conexion']   = request.POST.get('codigo_conexion')
            kwargs['motor_emision']     = request.POST.get('motor_emision')
            kwargs['detalle_conexion']  = request.POST.get('detalle_conexion')

            error = editar_parametros_facturacion(**kwargs)

            if not error:
                data = {
                    'success': True,
                }
                return JsonResponse(data)
            else:
                data = {
                    'success': False,
                    'error': error
                }
                return JsonResponse(data)
        else:
            if request.is_ajax():
                return JsonResponse(parametro.errors, status=400)
    else:
        parametro = ParametrosFacturacionForms(instance=parametro)
        conexion = ConexionFacturacionForms()

    return render(request, 'configuracion/editar_configuracion.html', {
        'name': name,
        'title': title,
        'subtitle': subtitle,
        'href': href,
        'parametros': parametro,
        'conexion': conexion,
        'id': pk,

    })

@csrf_exempt
def recupera_data_parametros(request, pk):

    lista_detalle = list()
    context = {}
    error = ""

    try:
        conexion = ConexionFacturacion.objects.filter(parametro_facturacion_id=pk)

        for a in conexion:
            data ={
                'id_detalle' : a.id,
                'codigo_contexto': a.codigo_contexto,
                'host': a.host,
                'url': a.url,
                'puerto': a.puerto
            }
            lista_detalle.append(data)
    except Exception as e:
        error = str(e)


    context={
        'lista_detalle':lista_detalle,
        'error':error
    }

    return JsonResponse(context)

@login_required
@csrf_exempt
def eliminar_configuracion(request):
    context = {}
    error = ''

    try:
        id_parametro = request.POST.get('id_parametro')

        parametro   = ParametrosFacturacion.objects.filter(id=id_parametro)
        conexion    = ConexionFacturacion.objects.filter(parametro_facturacion_id=id_parametro)

        conexion.delete()
        parametro.delete()

        context = {
            'success'   :False,
            'error'     : error
        }
    except Exception as e:
        error = str(e)
        context = {
            'success'   : False,
            'error'     : error
        }

    return JsonResponse(context)


def prueba_xml(request):

    name = ['Nuevo']
    title = 'Facturación'
    subtitle = 'Parametros de Configuración'
    href = '/facturacion/configuracion/visualizar/'


    # kwargs = {}

    #kwargs = recupera_data_dte(100)

    #respuesta = envio_documento_tributario_electronico(request, **kwargs)

    # conn = ConnectionHandler(settings.DATABASES)
    # new = conn['default']
    #
    # new.autocommit = False
    #
    # conn = new.cursor()
    # sql = "UPDATE facturacion_foliosdocumentoselectronicos set folio_actual = folio_actual WHERE tipo_dte = %s AND operativo = TRUE"
    # conn.execute(sql, (tipo_documento,))
    #
    # sql = "SELECT folio_actual from facturacion_foliosdocumentoselectronicos where tipo_dte = %s AND operativo=TRUE "
    # conn.execute(sql, (tipo_documento,))
    # folio_documento = conn.fetchone()[0]
    #
    # sql = "UPDATE facturacion_foliosdocumentoselectronicos set folio_actual = folio_actual + 1 WHERE tipo_dte = %s AND operativo = TRUE"
    # conn.execute(sql, (tipo_documento,))
    #
    # new.rollback()
    # # connection.commit()
    # connection.close()

    # connect = psycopg2.connect("dbname='asgard' user='asgard' host='localhost'  password='asgard2016'")
    # connect.autocommit = False
    #
    # conn = connect.cursor()
    # sql = "UPDATE facturacion_foliosdocumentoselectronicos set folio_actual = folio_actual WHERE tipo_dte = %s AND operativo = TRUE"
    # conn.execute(sql, (tipo_documento,))
    #
    # sql = "SELECT folio_actual from facturacion_foliosdocumentoselectronicos where tipo_dte = %s AND operativo=TRUE "
    # conn.execute(sql, (tipo_documento,))
    # folio_documento = conn.fetchone()[0]
    #
    # sql = "UPDATE facturacion_foliosdocumentoselectronicos set folio_actual = folio_actual + 1 WHERE tipo_dte = %s AND operativo = TRUE"
    # conn.execute(sql, (tipo_documento,))
    #
    # connect.rollback()
    # connect.close()





    tipo_documento = 33

    respuesta = obtener_documento_xml_pdf(tipo_documento,19067,'ljk')

    # transaction.set_autocommit(False)
    #
    # update = FoliosDocumentosElectronicos.objects.get(tipo_dte=tipo_documento, operativo=True)
    # update.folio_actual = update.folio_actual
    # update.save()
    #
    # folio = FoliosDocumentosElectronicos.objects.get(tipo_dte=tipo_documento, operativo=True).folio_actual
    #
    # update_2 = FoliosDocumentosElectronicos.objects.get(tipo_dte=tipo_documento, operativo=True)
    # update_2.folio_actual = update.folio_actual + 1
    # update_2.save()
    #
    #
    # #transaction.rollback()
    # transaction.commit()


    #respuesta = consulta_estado_libro_compras_ventas_sii('2016072')
    # #kwargs = prueba_control_folio()
    # #kwargs=pruebas_libro_venta()
    #
    # #kwargs = prueba_libro_compra()
    #
    # #ola = envio_libro_compras_electronico(request, **kwargs)
    #
    #
    # semaforo = threading.Semaphore(2)



    # idte = Element('IDTE_DOC')
    #
    # #General
    # general = Element('General')
    # idte.append(general)
    #
    # #Add hijos general
    #
    # tipo_dte = SubElement(general, 'tipo_dte')
    # tipo_dte.text = '33'
    #
    # folio = SubElement(general, 'folio_dte')
    # folio.text = '15240'
    #
    # id1_erp = SubElement(general, 'ID1_ERP')
    # # id1_erp.text = '0'
    #
    # id2_erp = SubElement(general, 'ID2_ERP')
    # # id2_erp.text = '0'
    #
    # id3_erp = SubElement(general, 'ID3_ERP')
    # # id3_erp.text = '0'
    #
    # id4_erp = SubElement(general, 'ID4_ERP')
    # # id4_erp.text = '0'
    #
    # email_pdf = SubElement(general, 'emails_PDF')
    # email_pdf.text = 'cmunoz@informat.cl'
    #
    # email_xml = SubElement(general, 'emails_XML')
    # email_xml.text = 'cmunoz@informat.cl'
    #
    #
    #
    # #Encabezado
    #
    # cabecera = Element('Cabecera')
    # idte.append(cabecera)
    #
    #
    # #Add hijos cabeceza
    #
    # fch_emis = SubElement(cabecera, 'FchEmis')
    # fch_emis.text = '2016-07-18'
    #
    # indNoRebaja = SubElement(cabecera, 'IndNoRebaja')
    # indNoRebaja.text = '0'
    #
    # tipo_despacho = SubElement(cabecera, 'TipoDespacho')
    # tipo_despacho.text = '0'
    #
    # indicador_traslado = SubElement(cabecera, 'IndTraslado')
    # indicador_traslado.text = '0'
    #
    # tipo_impresion = SubElement(cabecera, 'TpoImpresion')
    # tipo_impresion.text = '0'
    #
    # indicador_servicio = SubElement(cabecera, 'IndServicio')
    # indicador_servicio.text = '0'
    #
    # monto_bruto = SubElement(cabecera, 'MntBruto')
    # monto_bruto.text = '0'
    #
    # forma_pago = SubElement(cabecera, 'FmaPago')
    # forma_pago.text = '1'
    #
    # forma_pago_exp = SubElement(cabecera, 'FmaPagExp')
    # forma_pago_exp.text = '0'
    #
    # fecha_cancel = SubElement(cabecera, 'FchCancel')
    #
    # monto_cancel = SubElement(cabecera, 'MntCancel')
    # monto_cancel.text = '0'
    #
    # saldo_insol = SubElement(cabecera, 'SaldoInsol')
    # saldo_insol.text = '0'
    #
    # periodo_desde = SubElement(cabecera, 'PeriodoDesde')
    #
    # periodo_hasta = SubElement(cabecera, 'PeriodoHasta')
    #
    # medio_pago = SubElement(cabecera, 'MedioPago')
    # medio_pago.text = 'EF'
    #
    # tipo_cta_pago = SubElement(cabecera, 'TipoCtaPago')
    #
    # numero_cta_pago = SubElement(cabecera, 'NumCtaPago')
    #
    # banco_pago = SubElement(cabecera, 'BcoPago')
    #
    # termino_pago_codigo = SubElement(cabecera, 'TermPagoCdg')
    #
    # temino_pago_glosa = SubElement(cabecera, 'TermPagoGlosa')
    #
    # termino_pago_dias = SubElement(cabecera, 'TermPagoDias')
    #
    # fecha_vencimiento = SubElement(cabecera, 'FchVenc')
    # fecha_vencimiento.text = '2013-07-30'
    #
    # rut_mandante = SubElement(cabecera, 'RUTMandante')
    #
    # rut_solicitante = SubElement(cabecera, 'RUTSolicita')
    #
    #
    # indicador_monto_neto = SubElement(cabecera, 'IndMntNeto')
    # indicador_monto_neto.text = '0'
    #
    #
    # #Emisor
    #
    # emisor = Element('Emisor')
    # idte.append(emisor)
    #
    # #add hijos emisor
    #
    # rut_emisor = SubElement(emisor, 'RUTEmisor')
    # rut_emisor.text = '94836000-4'
    #
    # razon_social_emisor = SubElement(emisor, 'RznSoc')
    # razon_social_emisor.text = 'COMERCIAL LO ESPEJO MAQUINARIAS Y EQUIPOS S A'
    #
    # giro_emisor = SubElement(emisor, 'GiroEmis')
    # giro_emisor.text = 'IMPORTAC Y COMERCIAL. DE MAQUINARIA, EQUIPOS , REPUESTOS , CAMIONES'
    #
    # telefono_emisor = SubElement(emisor, 'Telefono')
    # telefono_emisor.text = '0228354536'
    #
    # correo_emisor = SubElement(emisor, 'CorreoEmisor')
    # # correo_emisor.text = 'prueba@example.com'
    #
    # acteco = SubElement(emisor, 'Acteco')
    # acteco.text = '512210'
    #
    # codigo_emisor_traslado = SubElement(emisor, 'CdgTraslado')
    # codigo_emisor_traslado.text = '0'
    #
    # folio_autorizado = SubElement(emisor, 'FolioAut')
    # folio_autorizado.text = '0'
    #
    # fecha_autorizacion = SubElement(emisor, 'FchAut')
    # fecha_autorizacion.text = '0'
    #
    # sucursal = SubElement(emisor, 'Sucursal')
    # # sucursal.text = '0'
    #
    # cod_sii_sucursal = SubElement(emisor, 'CdgSIISucur')
    # cod_sii_sucursal.text = '0'
    #
    # codigo_adicional_suc = SubElement(emisor, 'CodAdicSucur')
    #
    #
    # dir_emisor = SubElement(emisor, 'DirOrigen')
    # dir_emisor.text = 'SAN ANTONIO 220 OF 709'
    #
    # comuna_origen = SubElement(emisor, 'CmnaOrigen')
    # comuna_origen.text = 'SANTIAGO'
    #
    # ciudad_origen = SubElement(emisor, 'CiudadOrigen')
    # # ciudad_origen.text = 'Las Condes'
    #
    # codigo_vendedor = SubElement(emisor, 'CdgVendedor')
    # # codigo_vendedor.text = '869'
    #
    # identificador_adicional_emisor = SubElement(emisor, 'IdAdicEmisor')
    # # identificador_adicional_emisor.text = '0'
    #
    #
    #
    #
    #
    # #Receptor
    # receptor = Element('Receptor')
    # idte.append(receptor)
    #
    # #Add hijos receptor
    #
    # rut_receptor = SubElement(receptor, 'RUTRecep')
    # rut_receptor.text = '76032099-4'
    #
    # codigo_interno_receptor = SubElement(receptor, 'CdgIntRecep')
    # codigo_interno_receptor.text = '76032099-4'
    #
    # razon_receptor = SubElement(receptor, 'RznSocRecep')
    # razon_receptor.text = 'GRAVO S.A.'
    #
    # num_identificador_extranjero = SubElement(receptor, 'NumId')
    #
    # nacionalidad = SubElement(receptor, 'Nacionalidad')
    #
    # identificador_adicional_receptor = SubElement(receptor, 'IdAdicRecep')
    #
    # giro_receptor = SubElement(receptor, 'GiroRecep')
    # giro_receptor.text = 'VENTA AL POR MAYOR DE MATERIAS PRIMAS AG'
    #
    # contacto = SubElement(receptor, 'Contacto')
    #
    #
    # correo_receptor = SubElement(receptor, 'CorreoRecep')
    # # correo_receptor.text = 'bebeto@example.com'
    #
    # dir_receptor = SubElement(receptor, 'DirRecep')
    # dir_receptor.text = 'SAN ANTONIO 220 OF 709'
    #
    # comuna_receptor = SubElement(receptor, 'CmnaRecep')
    # comuna_receptor.text = 'SANTIAGO'
    #
    # cuidad_receptor = SubElement(receptor, 'CiudadRecep')
    # cuidad_receptor.text = 'SANTIAGO'
    #
    # direccion_postal = SubElement(receptor, 'DirPostal')
    #
    # comuna_postal = SubElement(receptor, 'CmnaPostal')
    #
    # cuidad_postal = SubElement(receptor, 'CiudadPostal')
    #
    #
    #
    # #Detalle
    #
    # detalle = Element('Detalle')
    # idte.append(detalle)
    #
    # #detalles del documento
    # registro_detalle = SubElement(detalle, 'reg_Detalle')
    #
    # #Add hijos de los detalles
    # nro_linea = SubElement(registro_detalle, 'NroLinDet')
    # nro_linea.text = '1'
    #
    # tipo_documento_liq = SubElement(registro_detalle, 'TpoDocLiq')
    #
    # indicador_exencion = SubElement(registro_detalle, 'IndExe')
    # indicador_exencion.text = '0'
    #
    # nombre_item = SubElement(registro_detalle, 'NmbItem')
    # nombre_item.text = 'CRIMSON SEEDLESS Uva de Mesa CRIMSON SEEDLESS'
    #
    # descripcion_item = SubElement(registro_detalle, 'DescItem')
    # descripcion_item = 'UVA DE MESA CRIMSON SEEDLESS'
    #
    # cantidad_referencia = SubElement(registro_detalle, 'QtyRef')
    # cantidad_referencia.text = '19710'
    #
    # unidad_referencia = SubElement(registro_detalle, 'UnmdRef')
    # # unidad_referencia.text = '1'
    #
    # precio_referencia = SubElement(registro_detalle, 'PrcRef')
    # precio_referencia.text = '2700.4000'
    #
    # cantidad = SubElement(registro_detalle, 'QtyItem')
    # cantidad.text = '19710'
    #
    # fecha_elaboracion = SubElement(registro_detalle, 'FchaElabor')
    #
    # fecha_vencimiento_prod = SubElement(registro_detalle, 'FchVencim')
    #
    # unidad_medida = SubElement(registro_detalle, 'UnmdItem')
    # # unidad_medida.text = '1'
    #
    # precio_unitario = SubElement(registro_detalle, 'PrcItem')
    # precio_unitario.text = '2700.4000'
    #
    # descuento_porcentaje = SubElement(registro_detalle, 'DescuentoPct')
    # descuento_porcentaje.text = '0'
    #
    # descuento_monto = SubElement(registro_detalle, 'DescuentoMonto')
    # descuento_monto.text = '0'
    #
    # recargo_porcentaje = SubElement(registro_detalle, 'RecargoPct')
    # recargo_porcentaje.text = '0'
    #
    # recargo_monto = SubElement(registro_detalle, 'RecargoMonto')
    # recargo_monto.text = '0'
    #
    # impuesto_adicional1 = SubElement(registro_detalle, 'CodImpAdic1')
    # impuesto_adicional1.text = '0'
    #
    # impuesto_adicional2 = SubElement(registro_detalle, 'CodImpAdic2')
    # impuesto_adicional2.text = '0'
    #
    # monto_item = SubElement(registro_detalle, 'MontoItem')
    # monto_item.text = '53224884'
    #
    # item_espectaculo = SubElement(registro_detalle, 'ItemEspectaculo')
    # rut_mandante_b = SubElement(registro_detalle, 'RUTMandanteB')
    #
    #
    # # # hijo Otra Moneda
    # #
    # # otra_moneda = SubElement(registro_detalle, 'OtrMnda')
    # #
    # # #Subhijos otra moneda
    # #
    # # precio_otra_moneda = SubElement(otra_moneda, 'PrcOtrMon')
    # # precio_otra_moneda.text = '2500'
    # #
    # # moneda = SubElement(otra_moneda, 'Moneda')
    # # moneda.text = 'USD'
    # #
    # # factor_conversion = SubElement(otra_moneda, 'FctConv')
    # # factor_conversion.text = '3'
    # #
    # # descuento_otra_moneda = SubElement(otra_moneda, 'DctoOtrMnda')
    # # descuento_otra_moneda.text = '5'
    # #
    # # recargo_otra_moneda= SubElement(otra_moneda, 'RecargoOtrMnda')
    # # recargo_otra_moneda.text = '0'
    # #
    # # monto_item_otra = SubElement(otra_moneda, 'MontoItemOtrMnd')
    # # monto_item_otra.text = '2500'
    #
    # # # hijo Retenedor
    # #
    # # otra_moneda = SubElement(registro_detalle, 'Retenedor')
    # #
    # # #Subhijos otra moneda
    # #
    # # indicador_agente = SubElement(otra_moneda, 'IndAgente')
    # # indicador_agente.text = '9'
    # #
    # # monto_base_faena = SubElement(otra_moneda, 'MntBaseFaena')
    # # monto_base_faena.text = '10'
    # #
    # # monto_margen_comercial = SubElement(otra_moneda, 'MntMargComer')
    # # monto_margen_comercial.text = '20'
    # #
    # # precio_consumidor_final = SubElement(otra_moneda, 'PrcConsFinal')
    # # precio_consumidor_final.text = '80'
    #
    #
    #
    # #Totales
    #
    # totales = Element('Totales')
    # idte.append(totales)
    #
    # #Add hijos totales
    #
    # tipo_moneda = SubElement(totales, 'TpoMoneda')
    #
    # monto_neto = SubElement(totales, 'MntNeto')
    # monto_neto.text = '53224884'
    #
    # monto_exento = SubElement(totales, 'MntExe')
    # monto_exento.text = '0'
    #
    # monto_base = SubElement(totales, 'MntBase')
    # monto_base.text = '0'
    #
    # monto_margen_comercializacion = SubElement(totales, 'MntMargenCom')
    # monto_margen_comercializacion.text = '0'
    #
    # tasa_iva = SubElement(totales, 'TasaIVA')
    # tasa_iva.text = '19'
    #
    # iva = SubElement(totales, 'IVA')
    # iva.text = '10112728'
    #
    # iva_propio = SubElement(totales, 'IVAProp')
    # iva_propio.text = '0'
    #
    # iva_terceros = SubElement(totales, 'IVATerc')
    # iva_terceros.text = '0'
    #
    # iva_no_retenido = SubElement(totales, 'IVANoRet')
    # iva_no_retenido.text = '0'
    #
    # credito_especial_constructuras = SubElement(totales, 'CredEC')
    # credito_especial_constructuras.text = '0'
    #
    # garantia_deposi_env_embal = SubElement(totales, 'GmtDep')
    # garantia_deposi_env_embal.text = '0'
    #
    # valor_comision_neto = SubElement(totales, 'ValComNeto')
    # valor_comision_neto.text = '0'
    #
    # valor_comision_exento = SubElement(totales, 'ValComExe')
    # valor_comision_exento.text = '0'
    #
    # valor_comision_iva = SubElement(totales, 'ValComIVA')
    # valor_comision_iva.text = '0'
    #
    # monto_total = SubElement(totales, 'MntTotal')
    # monto_total.text = '63337612'
    #
    # monto_no_facturable = SubElement(totales, 'MontoNF')
    # monto_no_facturable.text = '0'
    #
    # monto_periodo = SubElement(totales, 'MontoPeriodo')
    # monto_periodo.text = '0'
    #
    # saldo_anterior = SubElement(totales, 'SaldoAnterior')
    # saldo_anterior.text = '0'
    #
    # valor_pagar = SubElement(totales, 'VlrPagar')
    # valor_pagar.text = '0'
    #
    # # #comision
    # # comision = Element('Comisiones')
    # # idte.append(comision)
    # #
    # # #Add hijos
    # #
    # # registros_comisiones = SubElement(comision, 'reg_Comisiones')
    # #
    # # #Add subhijos
    # #
    # # numero_linea_comision = SubElement(registros_comisiones, 'NroLinCom')
    # # numero_linea_comision.text = '1'
    # #
    # # tipo_movimiento = SubElement(registros_comisiones, 'TipoMovim')
    # # tipo_movimiento.text = 'C'
    # #
    # # glosa_comision = SubElement(registros_comisiones, 'Glosa')
    # # glosa_comision.text = 'text'
    # #
    # # tasa_comision = SubElement(registros_comisiones, 'TasaComision')
    # # tasa_comision.text = '0'
    # #
    # # valor_neto_comision = SubElement(registros_comisiones, 'ValorComNeto')
    # # valor_neto_comision.text = '0'
    # #
    # # valor_exento_comision = SubElement(registros_comisiones, 'ValorComExe')
    # # valor_exento_comision.text = '0'
    # #
    # # valor_neto_comision = SubElement(registros_comisiones, 'ValorComIVA')
    # # valor_neto_comision.text = '0'
    #
    #
    #
    #
    # # #Descripcion recargos globales
    # #
    # # descrip_recar_globales = Element('DescRcgGlobal')
    # # idte.append(descrip_recar_globales)
    # #
    # # #Add hijos de descripcion recargos globales
    # #
    # # registro_descr_recarg_global = SubElement(descrip_recar_globales, 'reg_DescRcgGlobal')
    #
    #
    #
    # # # Impuestos retenidos
    # # impuesto_retenido = SubElement(totales, 'ImptoReten')
    # #
    # # #detalles impuestos retenidos
    # #
    # # registro_imp_retenido = SubElement(impuesto_retenido, 'reg_ImpReten')
    # #
    # # #Add sub-hijos impuesto retenido
    # #
    # # id_impuesto_retenido = SubElement(registro_imp_retenido, 'IdImptoReten')
    # # id_impuesto_retenido.text = '1'
    # #
    # # tipo_impuesto = SubElement(registro_imp_retenido, 'TipoImp')
    # # tipo_impuesto.text = 'ww'
    # #
    # # tasa_impuesto = SubElement(registro_imp_retenido, 'TasaImp')
    # # tasa_impuesto.text = '12'
    # #
    # # monto_impuesto = SubElement(registro_imp_retenido, 'MontoImp')
    # # monto_impuesto.text = '3345'
    #
    #
    #
    # # #Descripcion recargos globales
    # #
    # # descrip_recar_globales = Element('DescRcgGlobal')
    # # idte.append(descrip_recar_globales)
    # #
    # # #Add hijos de descripcion recargos globales
    # #
    # # registro_descr_recarg_global = SubElement(descrip_recar_globales, 'reg_DescRcgGlobal')
    # #
    # # #Sub-hijos de descripcion recargos globales
    # #
    # # numero_linea = SubElement(registro_descr_recarg_global, 'NroLinDR')
    # # numero_linea.text = '1'
    # #
    # # tipo_movimiento = SubElement(registro_descr_recarg_global, 'TpoMov')
    # # tipo_movimiento.text = 'D'
    # #
    # # glosa_descrip_recargo = SubElement(registro_descr_recarg_global, 'GlosaDR')
    # # glosa_descrip_recargo.text = 'sdfsdfsd'
    # #
    # # tipo_valor_descrip_recargo = SubElement(registro_descr_recarg_global, 'TpoValor')
    # # tipo_valor_descrip_recargo.text = '$'
    # #
    # # valor_descrip_recargo = SubElement(registro_descr_recarg_global, 'ValorDR')
    # # valor_descrip_recargo.text = '345'
    # #
    # # valor_descrip_recargo_otra_moneda = SubElement(registro_descr_recarg_global, 'ValorDROtrMnda')
    # # valor_descrip_recargo_otra_moneda.text = '0'
    # #
    # # indicador_facturacion_exenta = SubElement(registro_descr_recarg_global, 'IndExeDR')
    # # indicador_facturacion_exenta.text = '5567'
    #
    #
    # # #Referecias
    # # referencias = Element('Referencias')
    # # idte.append(referencias)
    # #
    # # #Add hijos referencias
    # #
    # # registro_referencia = SubElement(referencias, 'reg_Referencias')
    # #
    # # #Sub-hijos de registros de referencias
    # #
    # # numero_linea_referencia = SubElement(registro_referencia, 'NroLinRef')
    # # numero_linea_referencia.text = '1'
    # #
    # # tipo_doc_referencia = SubElement(registro_referencia, 'TpoDocRef')
    # # tipo_doc_referencia.text = '33'
    # #
    # # Indicador_ref_global = SubElement(registro_referencia, 'IndGlobal')
    # # # Indicador_ref_global.text = '79'
    # #
    # # folio_referencia = SubElement(registro_referencia,'FolioRef')
    # # folio_referencia.text = '79'
    # #
    # # rut_otro_contribuyente = SubElement(registro_referencia, 'RUTOtr')
    # #
    # # indicador_adicional_otro_contribuyente = SubElement(registro_referencia, 'IdAdicOtr')
    # # indicador_adicional_otro_contribuyente = '0'
    # #
    # # fecha_referencia = SubElement(registro_referencia, 'FchRef')
    # # fecha_referencia.text = '2010-07-31'
    # #
    # # codigo_referencia = SubElement(registro_referencia, 'CodRef')
    # # codigo_referencia.text = '1'
    # #
    # # razon_referencia = SubElement(registro_referencia, 'RazonRef')
    # # # razon_referencia.text = 'pepito'
    #
    #
    #
    # # #Otra Moneda
    # # otra_moneda_item = Element('OtraMoneda')
    # # idte.append(otra_moneda_item)
    # #
    # # #Add hijo otra moneda
    # #
    # # tipo_otra_moneda = SubElement(otra_moneda_item, 'TipoMoneda')
    # # tipo_otra_moneda.text = 'USD'
    # #
    # # tipo_cambio = SubElement(otra_moneda_item, 'TpoCambio')
    # # tipo_cambio.text = '5'
    # #
    # # monto_neto_otra_moneda = SubElement(otra_moneda_item, 'MntNetoOtrMnda')
    # # monto_neto_otra_moneda.text = '67'
    # #
    # # monto_exenta_otra_moneda = SubElement(otra_moneda_item, 'MntExeOtrMnda')
    # # monto_exenta_otra_moneda.text = '7878'
    # #
    # # monto_faena_carne_otra_moneda = SubElement(otra_moneda_item, 'MntFaeCarneOtrMnda')
    # # monto_faena_carne_otra_moneda.text = '0'
    # #
    # # monto_margen_otra_moneda = SubElement(otra_moneda_item, 'MntMargComOtrMnda')
    # # monto_margen_otra_moneda.text = '98979'
    # #
    # # iva_otra_moneda = SubElement(otra_moneda_item, 'IVAOtrMnda')
    # # iva_otra_moneda.text = '78978'
    # #
    # # iva_no_retenido_otra_moneda = SubElement(otra_moneda_item, 'IVANoRetOtrMnd')
    # # iva_no_retenido_otra_moneda.text = '0'
    # #
    # # monto_total_otra_moneda = SubElement(otra_moneda_item, 'MntTotOtrMnda')
    # # monto_total_otra_moneda.text = '966969'
    #
    #
    # # #Impuesto retencion Otra Moneda
    # #
    # # impuesto_retenido_otra_moneda = SubElement(otra_moneda_item, 'ImpRetOtrMnda')
    # #
    # # #registro de impuesto retencion otra moneda
    # #
    # # registro_imp_retenido_otra_moneda = SubElement(impuesto_retenido_otra_moneda, 'reg_ImpRetOtrMnda')
    # #
    # # #Subhijo de impuesto retencion otra moneda
    # #
    # # id_imp_retenido_otra_moneda = SubElement(registro_imp_retenido_otra_moneda, 'IdImpRetOtrMnda')
    # # id_imp_retenido_otra_moneda.text = '1'
    # #
    # # tipo_imp_otra_moneda = SubElement(registro_imp_retenido_otra_moneda, 'TipoImpOtrMnda')
    # # tipo_imp_otra_moneda.text = 'aaa'
    # #
    # # tasa_imp_otra_moneda = SubElement(registro_imp_retenido_otra_moneda, 'TasaImpOtrMnda')
    # # tasa_imp_otra_moneda.text = '0'
    # #
    # # valor_imp_otra_moneda = SubElement(registro_imp_retenido_otra_moneda, 'VlrImpOtrMnda')
    # # valor_imp_otra_moneda.text = '65586'
    #
    #
    #
    # # #Sub total información
    # # sub_total_info = Element('SubTotInfo')
    # # idte.append(sub_total_info)
    # #
    # # #Add hijo sub total información
    # # registro_sub_total_info = SubElement(sub_total_info, 'reg_SubTotInfo')
    # #
    # # #Subhijos subtotal informacion
    # #
    # # numero_subtotalinfo = SubElement(registro_sub_total_info, 'NroSTI')
    # # numero_subtotalinfo.text = '1'
    # #
    # # glosa_subtotalinfo = SubElement(registro_sub_total_info, 'GlosaSTI')
    # # glosa_subtotalinfo.text = 'UVA DE MESA CRIMSON SEEDLESS'
    # #
    # # orden_subtotalinfo = SubElement(registro_sub_total_info, 'OrdenSTI')
    # # orden_subtotalinfo.text = '0'
    # #
    # # sub_total_neto_subtotalinfo = SubElement(registro_sub_total_info, 'SubTotNetoSTI')
    # # sub_total_neto_subtotalinfo.text = '0'
    # #
    # # sub_total_iva_subtotalinfo = SubElement(registro_sub_total_info, 'SubTotIVASTI')
    # # sub_total_iva_subtotalinfo.text = '0'
    # #
    # # sub_total_adici_subtotalinfo = SubElement(registro_sub_total_info, 'SubTotAdicSTI')
    # # sub_total_adici_subtotalinfo.text = '0'
    # #
    # # sub_total_exe_subtotalinfo = SubElement(registro_sub_total_info, 'SubTotExeSTI')
    # # sub_total_exe_subtotalinfo.text = '0'
    # #
    # # valor_subtotal_subtotalinfo = SubElement(registro_sub_total_info, 'ValSubtotSTI')
    # # valor_subtotal_subtotalinfo.text = '0'
    # #
    # # lineas_detalles = SubElement(registro_sub_total_info, 'lineasDeta')
    # #
    # # registro_linea_detalle = SubElement(lineas_detalles, 'reg_lineasDeta')
    # #
    # # numero_linea_detalle = SubElement(registro_linea_detalle, 'num_linea_detalle')
    # # numero_linea_detalle.text = '0'
    #
    #
    #
    # # #Transporte
    # # transporte = Element('Transporte')
    # # idte.append(transporte)
    # #
    # # #Add hijo transporte
    # # patente = SubElement(transporte, 'Patente')
    # # patente.text = 'NF0152'
    # #
    # # rut_transportista = SubElement(transporte, 'RUTTrans')
    # # rut_transportista.text = '12345678-8'
    # #
    # # nombre_chofer = SubElement(transporte, 'NombreChofer')
    # # nombre_chofer.text = 'prueba'
    # #
    # # dir_destino = SubElement(transporte, 'DirDest')
    # # dir_destino.text = 'direccion prueba'
    #
    #
    # # #Extra
    # # extras = Element('Extras')
    # # idte.append(extras)
    # #
    # # #Add Hijos
    # #
    # # registro_extras = SubElement(extras, 'reg_Extras')
    # #
    # # #Add Subhijos
    # #
    # # concepto = SubElement(registro_extras, 'concepto')
    # # concepto.text = 'Observaciones'
    # #
    # # valor_extra = SubElement(registro_extras, 'valor')
    #
    # # tree = ElementTree(idte)
    #
    # xml = etree.tostring(idte, short_empty_elements=False,  method='xml')
    #
    # print(xml.decode())
    #
    #
    # kwargs['codigo_contexto'] = 'org_tempuri_servDTE'
    # kwargs['host'] = '192.168.231.111'
    # kwargs['url'] = 'wsDTE'
    # kwargs['puerto'] = 80
    # kwargs={}
    #
    # kwargs['codigo_contexto'] = 'org_tempuri_servMixto'
    # kwargs['host'] = '192.168.231.111'
    # kwargs['url'] = 'wsMIXTO'
    # kwargs['puerto'] = 80
    #
    # print('arma url')
    #
    # error, url_conexion = url_web_service(**kwargs)
    # print('url service ' + url_conexion)
    #
    # error, client = call_service(url_conexion)
    # print(client)
    # id_idte_empresa = 'MOLINERA-96540970-6274974030-20140929'
    # tipo_documento = 33
    # folio = 15238
    # accion = 1
    # traza = 2
    # formato = 2
    # #
    #
    #
    # # borrar = borrar_cola(client, id_idte_empresa, tipo_documento, folio, traza)
    # # print(borrar)
    #
    # estado = get_estado_documento(client, id_idte_empresa, tipo_documento, folio, traza)
    #
    # print(estado)

    # contenido_caf = '<?xml version="1.0"?><AUTORIZACION><CAF version="1.0"><DA><RE>96540970-K</RE><RS>IMPORTADORA Y DISTRIB. DE ARTICULOS ELEC</RS><TD>33</TD><RNG><D>1</D><H>1000</H></RNG><FA>2016-06-21</FA><RSAPK><M>z8RdLh30CG4/lLFfrE6E+z6d+hmLbCKGvuFiwXZ/mxucG7pKEjcJbRA7hWnPSzJX3J0cPWOnTbld4WRgtpb/vQ==</M><E>Aw==</E></RSAPK><IDK>100</IDK></DA><FRMA algoritmo="SHA1withRSA">oPRian0l2UTvuA1DVPwur+f1EAxeAaGHmYdvBNJ8RVH++7XU5cEE/dxedQU3chTk9FovKexSosciKe4Ihf5nwg==</FRMA></CAF><RSASK>-----BEGIN RSA PRIVATE KEY-----MIIBOwIBAAJBAM/EXS4d9AhuP5SxX6xOhPs+nfoZi2wihr7hYsF2f5sbnBu6ShI3CW0QO4Vpz0syV9ydHD1jp025XeFkYLaW/70CAQMCQQCKgujJaU1a9CpjIOpy3wNSKb6mu7JIFwR/QOyA+apnZonl7rTJXihFxg2d1Vi/bM/m7QJvZ06tV5CGuBKjsbHTAiEA6BI0Izs5MsQfuwEG6TtNuOM4IPRQKiuuTN4BLEDgv5MCIQDlMKAXqPCaQEdsF6Lg8MFnHwF3ofiHHge4OU8YgCu1bwIhAJq2zWzSJiHYFSdWBJt83ntCJWtNisbHyYiUAMgrQH+3AiEAmMsVZRtLEYAvnWUXQKCA72oA+mv7BL6v0CY0uwAdI58CIQDifIx4+tXQp0P1oElawLG5z6zVCBs+K153NQ/YCDlvEA==-----END RSA PRIVATE KEY-----</RSASK><RSAPUBK>-----BEGIN PUBLIC KEY-----MFowDQYJKoZIhvcNAQEBBQADSQAwRgJBAM/EXS4d9AhuP5SxX6xOhPs+nfoZi2wihr7hYsF2f5sbnBu6ShI3CW0QO4Vpz0syV9ydHD1jp025XeFkYLaW/70CAQM=-----END PUBLIC KEY-----</RSAPUBK></AUTORIZACION>'
    # caf = importar_caf(client, id_idte_empresa, contenido_caf, traza)
    # print(caf)

    # xml = get_procesar_dte_xml(client, id_idte_empresa, tipo_documento, folio, accion, traza, xml.decode())
    #
    # print(xml)

    # archivo = get_archivo_documento(client, id_idte_empresa, tipo_documento, folio, formato, traza)
    #
    #
    # return archivo

    return render(request, 'prueba_xml/prueba_xml.html', {
        'name': name,
        'title': title,
        'subtitle': subtitle,
        'href': href,
        'error':respuesta
    })

##------------------------------- MANEJO DE FOLIOS CAF  ----------------------------------------------------------------

@csrf_exempt
@login_required
def carga_folios_electronicos(request):
    """
        función que permite realizar la carga de folio (CAF) en IDTE de acuerdo al tipo de documento electronico
    :param request: archivo XML
    :return: retorna un objeto con estado del proceso y el error en caso de existir.
    """
    # TODO revizar la funcion secuencia en duro y decode archivo leido

    name = 'Carga CAF'
    title = 'Facturacion'
    subtitle = 'Lista de Folios Electronicos'
    href = '/folios_electronicos/visualizar/'

    rut_empresa = ''
    flag = 0

    if request.method == 'POST':
            try:
                rut_empresa = Empresa.objects.get(id=request.user.pk).empresa.rut
                #rut_empresa = '76244316-3'

                tempfile = request.FILES.get('file')

                archivo = etree.fromstring(tempfile.read())
                xml = etree.tostring(archivo, method='xml', encoding='UTF-8', )
                decode_xml = xml.decode('UTF-8').replace('\n','')
                decode2_xml = decode_xml.replace('\t','')
                xml_creado ='<?xml version="1.0"?>'+decode2_xml.strip()

                #root = archivo.getroot()
                autorizacion = archivo.tag

                if autorizacion != 'AUTORIZACION':
                    flag = 9
                    data = {
                        'success': False,
                        'error': 'El formato del CAF es Incorrecto'
                    }
                    return JsonResponse(data)
                else:
                    for caf in archivo.findall('CAF'):
                        for a in caf.findall('DA'):
                            rut_emisor = a.find('RE').text
                            if rut_emisor != rut_empresa:
                                flag = 9
                                data = {
                                    'success': False,
                                    'error': 'CAF NO Corresponde a este Emisor Electrónico'
                                }
                                return JsonResponse(data)
                            if a.find('TD').text:
                                tipo_dte = int(a.find('TD').text)

                            for b in a.findall('RNG'):

                                if b.find('D').text:
                                    folio_desde = int(b.find('D').text)
                                if b.find('H').text:
                                    folio_hasta = int(b.find('H').text)
                            if a.find('FA').text:
                                fecha_autorizacion = a.find('FA').text

                    if flag == 0:
                        folios = FoliosDocumentosElectronicos.objects.filter(tipo_dte=tipo_dte,
                                                                             folio_actual__gte=folio_desde,
                                                                             folio_actual__lte=folio_hasta)
                        if not folios:
                            encontro = 0
                        else:
                            for fo in folios:
                                if fo.folio_actual <= fo.rango_final:
                                    encontro = 1
                                    fecha_caf = fo.fecha_ingreso_caf

                        if encontro == 0:
                            # Buscar el ultimo numero de secuencia del tipo de dte
                            secuencia = FoliosDocumentosElectronicos.objects.filter(tipo_dte=tipo_dte).values('secuencia_caf').last()
                            if secuencia:
                                secuencia_folio = secuencia['secuencia_caf'] +1
                            else:
                                secuencia_folio = 1

                            nuevo_folios = FoliosDocumentosElectronicos()
                            nuevo_folios.tipo_dte = tipo_dte
                            nuevo_folios.secuencia_caf = secuencia_folio
                            nuevo_folios.rango_inicial = folio_desde
                            nuevo_folios.rango_final = folio_hasta
                            nuevo_folios.folio_actual = folio_desde
                            nuevo_folios.xml_caf = xml_creado
                            nuevo_folios.fecha_ingreso_caf = datetime.datetime.now()
                            nuevo_folios.usuario_creacion_id = request.user.pk
                            nuevo_folios.save()

                            data = {
                                'success': True,
                                'error': " "
                            }
                            return JsonResponse(data)

                        else:
                            data = {
                                'success': False,
                                'error': " Folios ya ingresados el " + fecha_caf.strftime('%Y-%m-%d')
                            }
                            return JsonResponse(data)
            except Exception as e:
                data = {
                    'success': False,
                    'error': 'Usuario no se encuentra asociado a una empresa.'
                }
                return data
         # else:
         #    return JsonResponse(carga_idte_folios)
    else:
        pass

    return render(request, 'carga_caf/carga_folios_caf.html', {
        'name': name,
        'title': title,
        'subtitle': subtitle,
        'href': href,
        'error': ""
    })

@csrf_exempt
@login_required
def visualizar_folios_electronicos(request):

    folios = FoliosDocumentosElectronicos.objects.all()

    name = 'Lista'
    title = 'Facturación'
    subtitle = 'Folios Electrónicos'
    href = '/folios_electronicos/visualizar'

    error = ""
    filtro_folios = FiltroFoliosDocumentosForm()

    return render(request, 'carga_caf/visualizar_caf.html', {
        'name': name,
        'title': title,
        'subtitle': subtitle,
        'href': href,
        'folios' : folios,
        'filtro_folios':filtro_folios,
        'errores': error,
    })

def cargar_folios_idte(contenido_caf):

    """
        Función que realiza la carga de folios (CAF) a IDTE atraves del Web Service SERVDTE, metodo importar_CAF
    :param request: archivo xml
    :return: retorna un objeto con el estado del proceso, además de el mensaje de error si es que existe.
    """

    nievel_traza = 2  # Nivel completo de traza
    id_dte_empresa = ''

    datos_conexion = {}
    error, conexion = obtener_datos_conexion('wsMIXTO')

    if not error:

        datos_conexion['codigo_contexto'] = conexion.codigo_contexto
        datos_conexion['host'] = conexion.host
        datos_conexion['url'] = conexion.url
        datos_conexion['puerto'] = conexion.puerto

        id_dte_empresa = conexion.parametro_facturacion.codigo_conexion

        ## Armar URL de conexión a Web Service--------------------------------------------------------------------------

        error_url ,url_conexion = url_web_service(**datos_conexion)

        if not error_url:

            ## Conectarse a Web Service de IDTE-------------------------------------------------------------------------
            error, client = call_service(url_conexion)

            if not error:
                try:

                    ##Consultar estado Documento -----------------------------------------------------------------------
                    carga_caf = importar_caf(client, id_dte_empresa, contenido_caf, nievel_traza)

                    if carga_caf.valor == "ERROR":
                        data = {
                            'success': False,
                            'funcion': 'importar_caf',
                            'error'  : carga_caf.msg,
                        }
                        return data
                    else:
                        data = {
                            'success': True,
                            'funcion': 'importar_caf',
                            'error'  : '',
                        }
                        return data
                except suds.WebFault as e:
                    error = e.args[0].decode("utf-8")
                    data = {
                        'success': False,
                        'funcion': 'importar_caf',
                        'error': error,
                    }
                    return data
            else:
                data = {
                    'success': False,
                    'error': error,
                    'funcion': 'call_service',

                }
                return data
        else:
            data = {
                'success': False,
                'error': error_url,
                'funcion': 'url_web_service',

            }
            return data
    else:
        data = {
            'success': False,
            'error': error,
            'funcion': 'obtener_datos_conexion',
        }
        return data

@csrf_exempt
@login_required
def autorizar_folios_electronicos(request):

    autorizar_folios = request.POST.get('folio_seleccionado')
    respuesta = {}

    if int(autorizar_folios) == 0:
        data ={
            'success': False,
            'error': "Debe seleccionar uno."
        }
        return  JsonResponse(data)
    else:

        try:

            folio = FoliosDocumentosElectronicos.objects.get(id=autorizar_folios)
            if folio.operativo == False and (folio.tipo_dte != 0 and folio.secuencia_caf !=0):

                try:
                    pepito = FoliosDocumentosElectronicos.objects.get(tipo_dte=folio.tipo_dte, operativo=True)
                    fol_hasta   = pepito.rango_final
                    fol_activo  = pepito.folio_actual

                except Exception as a:
                    fol_hasta  = 0
                    fol_activo = 0

                if fol_activo > fol_hasta or (fol_activo == 0 and fol_hasta == 0):

                    po = etree.fromstring(folio.xml_caf)
                    xml = etree.tostring(po, short_empty_elements=False, method='xml', encoding='utf-8')

                    respuesta = cargar_folios_idte(xml.decode())

                    if respuesta['success'] == False:
                        return JsonResponse(respuesta)
                    else:
                        update_folio = FoliosDocumentosElectronicos.objects.get(id=autorizar_folios)
                        update_folio.operativo = True
                        update_folio.save()

                        return JsonResponse(respuesta)
            else:
                if folio.operativo == True:
                    data = {
                        'success': False,
                        'error': "Este Folio ya esta Operativo."
                    }
                    return JsonResponse(data)

        except FoliosDocumentosElectronicos.DoesNotExist:
            error = "No se encuentra en la base de datos el CAF a autorizar."
        except Exception as e:
            error = str(e)
        data = {
            'success': False,
            'error': error
        }
        return  JsonResponse(data)



##------------------------------ MANEJO DE DOCUMENTOS TRIBUTARIOS ELECTRONICOS DTE -------------------------------------

def envio_documento_tributario_electronico(**kwargs):


    """
        Función que permite generar el archivo xml y realizar el envio de los documentos tributarios electronicos al
        sistema IDTE el cuál a su vez sera enviado al servicio impuestos internos.
        Si el proceso fue exitoso, este incluira en el objeto retornado la url del documento (Factura, nota de credito,
         nota de debito, etc..) en formato pdf.

    :param kwargs: diccionario con los datos del documento. (En la carpeta esquemas se encuentra la estructura del
                    diccionario que debera recibir por parametro la función. "estructura_diccionario_DTE").
    :return: retorna un objeto el cual contiene la siguiente estructura:

        data = {
            'success': True,                -- estado del proceso
            'error': '',                    -- error originado en el envio del documento
            'estado_sii': '',               -- estado del documento en el servicio impuestos internos
            'msg_sii': '',                  -- mensaje retornado por el s.i.i. para el documento enviado
            'tipo_error': '',               -- tipo de error originado en la función.
            'funcion_error': '',            -- nombre de la función donde se origino el error
            'ruta_archivo': archivo.valor,  -- url del archivo PDF del documento generado
        }
    """

    ##Variables --------------------------------------------------------------------------------------------------------
    tipo_documento      = kwargs['tipo_documento']
    aplicacion          = kwargs['aplicacion']
    nievel_traza        = 2  # Nivel completo de traza de error
    formato_documento   = 2  # PDF
    id_dte_empresa      = ''
    accion              = 1  # Procesar y enviar
    datos_conexion      = {}


    error_exi_folio = validar_existencia_folio(tipo_documento)

    if not error_exi_folio:

        ##Obtengo el folio disponible
        error_folio, folio_documento = obtener_folio(tipo_documento)

        if not error_folio:

            ##Validar el folio a procesar ----------------------------------------------------------------------------------
            error_folio = validar_folios_procesar(tipo_documento, folio_documento)

            if not error_folio:

                kwargs['folio'] = str(folio_documento)

                ##Creacion de xml-------------------------------------------------------------------------------------------
                error_creacion, xml = crear_xml_documento(**kwargs)
                print(xml)

                if not error_creacion:
                    ##Obtener datos de conexion IDTE -----------------------------------------------------------------------
                    error, conexion = obtener_datos_conexion('wsDTE')

                    if not error:
                        datos_conexion['codigo_contexto'] = conexion.codigo_contexto
                        datos_conexion['host'] = conexion.host
                        datos_conexion['url'] = conexion.url
                        datos_conexion['puerto'] = conexion.puerto

                        id_dte_empresa = conexion.parametro_facturacion.codigo_conexion

                        #Armar URL de conexion del Web Services ------------------------------------------------------------
                        error_url, url_conexion = url_web_service(**datos_conexion)

                        if not error_url:

                            ## Conectarse a Web Service de IDTE-------------------------------------------------------------

                            error, client = call_service(url_conexion)

                            if not error:

                                ##Consultar estado documento ---------------------------------------------------------------
                                try:
                                    estado = get_estado_documento(client, id_dte_empresa, tipo_documento, folio_documento,
                                                                  nievel_traza)

                                    if estado.valor == "ERROR":

                                        try:
                                            ##Borrar documento de la cola de DTE--------------------------------------------
                                            borrar_documento = borrar_cola(client, id_dte_empresa,tipo_documento, folio_documento,
                                                                           nievel_traza)

                                            if borrar_documento.dio_error == False:

                                                try:
                                                    ##Envio de documento a procesar a IDTE----------------------------------
                                                    procesar = get_procesar_dte_xml(client, id_dte_empresa, tipo_documento,
                                                                                    folio_documento, accion, nievel_traza, xml)

                                                    if procesar.dio_error == False:

                                                        try:
                                                            ##Consultar estado Documento -------------------------------

                                                            estado = get_estado_documento(client, id_dte_empresa,
                                                                                          tipo_documento, folio_documento,
                                                                                          nievel_traza)

                                                            if estado.valor != "Error":

                                                                ##Actualizacion del folio en la base de datos ----------
                                                                transaction.commit()
                                                                transaction.connections.close_all()
                                                                #-------------------------------------------------------

                                                                datos_estado = estado.valor.split('|')
                                                                estado_sii = datos_estado[15]
                                                                msg_sii = datos_estado[16]

                                                                if int(estado_sii) == 1:
                                                                    ##Obtener archivo PDF de la factura---------------------
                                                                    archivo = get_archivo_documento(client, id_dte_empresa,
                                                                                                    tipo_documento,folio_documento,
                                                                                                    formato_documento, nievel_traza)

                                                                    if archivo.dio_error == False:
                                                                        data = {
                                                                            'success': True,
                                                                            'folio' : folio_documento,
                                                                            'error': '',
                                                                            'estado_sii': '',
                                                                            'msg_sii': '',
                                                                            'tipo_error': '',
                                                                            'funcion_error': '',
                                                                            'ruta_archivo': archivo.valor,
                                                                        }
                                                                        return data
                                                                    else:
                                                                        data = {
                                                                            'success': False,
                                                                            'error': archivo.msg,
                                                                            'estado_sii': estado_sii,
                                                                            'msg_sii': msg_sii,
                                                                            'tipo_error': archivo.tipo_error,
                                                                            'funcion_error': 'get_archivo_documento',
                                                                            'ruta_archivo': '',
                                                                        }
                                                                        return data
                                                                else:
                                                                    data = {
                                                                        'success': False,
                                                                        'error': estado.msg,
                                                                        'estado_sii': '',
                                                                        'msg_sii': '',
                                                                        'tipo_error': '',
                                                                        'funcion_error': 'get_estado_documento',
                                                                        'ruta_archivo': '',
                                                                    }
                                                                    return data
                                                            else:
                                                                data = {
                                                                    'success': False,
                                                                    'error': estado.msg,
                                                                    'estado_sii': '',
                                                                    'msg_sii': '',
                                                                    'tipo_error': '',
                                                                    'funcion_error': 'get_estado_documento',
                                                                    'ruta_archivo': '',
                                                                }
                                                                return data
                                                        except suds.WebFault as w:
                                                            error = w.args[0].decode("utf-8")
                                                            data = {
                                                                'success': False,
                                                                'error': error,
                                                                'estado_sii': '',
                                                                'msg_sii': '',
                                                                'tipo_error': 'Excepción de Try Except',
                                                                'funcion_error': 'get_estado_documento',
                                                                'ruta_archivo': '',
                                                            }
                                                            return data
                                                    else:
                                                        ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                                                        # connection.rollback()
                                                        transaction.rollback()
                                                        transaction.connections.close_all()
                                                        ##------------------------------------------------------------------
                                                        data = {
                                                            'success': False,
                                                            'error': procesar.msg,
                                                            'estado_sii': '',
                                                            'msg_sii': '',
                                                            'tipo_error': procesar.tipo_error,
                                                            'funcion_error': 'get_procesar_dte_xml',
                                                            'ruta_archivo': '',
                                                        }
                                                        return data
                                                except suds.WebFault as w:
                                                    ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla----
                                                    transaction.rollback()
                                                    transaction.connections.close_all()
                                                    ##----------------------------------------------------------------------
                                                    error = w.args[0].decode("utf-8")
                                                    data = {
                                                        'success': False,
                                                        'error': error,
                                                        'estado_sii': '',
                                                        'msg_sii': '',
                                                        'tipo_error': 'Excepción de Try Except',
                                                        'funcion_error': 'get_procesar_dte_xml',
                                                        'ruta_archivo': '',
                                                    }
                                                    return data
                                            else:
                                                ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                                                transaction.rollback()
                                                transaction.connections.close_all()
                                                ##------------------------------------------------------------------
                                                data = {
                                                    'success': False,
                                                    'error': borrar_documento.msg,
                                                    'estado_sii': '',
                                                    'msg_sii': '',
                                                    'tipo_error': borrar_documento.tipo_error,
                                                    'funcion_error': 'borrar_cola',
                                                    'ruta_archivo': '',
                                                }
                                                return data
                                        except suds.WebFault as w:
                                            ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                                            transaction.rollback()
                                            transaction.connections.close_all()
                                            ##------------------------------------------------------------------
                                            error = w.args[0].decode("utf-8")
                                            data = {
                                                'success': False,
                                                'error': error,
                                                'estado_sii': '',
                                                'msg_sii': '',
                                                'tipo_error': 'Excepción de Try Except',
                                                'funcion_error': 'borrar_cola',
                                                'ruta_archivo': '',
                                            }

                                            return data
                                    else:

                                        ##Actualizacion del folio en la base de datos --------------------------------------
                                        transaction.commit()
                                        transaction.connections.close_all()
                                        # ----------------------------------------------------------------------------------

                                        datos_estado = estado.valor.split('|')
                                        estado_sii   = datos_estado[15]
                                        msg_sii      = datos_estado[16]

                                        if int(estado_sii) == 1:
                                            error = "Documento pendiente de envío"
                                        elif int(estado_sii) == 2:
                                            error = "Boleta registrada"
                                        elif int(estado_sii) == 3:
                                            error = "Documento enviado al S.I.I. sin estado"
                                        elif int(estado_sii) == 4:
                                            error = "Documento anulado"
                                        elif int(estado_sii) == 5:
                                            error = "Documento aceptado"
                                        elif int(estado_sii) == 6:
                                            error = "Documento Rechazado"
                                        else:
                                            error = "Estado desconocido"

                                        data = {
                                            'success': False,
                                            'error': error,
                                            'estado_sii': estado_sii,
                                            'msg_sii':msg_sii,
                                            'tipo_error': '',
                                            'funcion_error': 'get_estado_documento',
                                            'ruta_archivo': '',
                                        }
                                        return data
                                except suds.WebFault as w:
                                    ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                                    transaction.rollback()
                                    transaction.connections.close_all()
                                    ##------------------------------------------------------------------
                                    error = w.args[0].decode("utf-8")
                                    data = {
                                        'success': False,
                                        'error': error,
                                        'estado_sii':'',
                                        'msg_sii': '',
                                        'tipo_error': 'Excepción de Try Except',
                                        'funcion_error': 'get_estado_documento',
                                        'ruta_archivo': '',
                                    }

                                    return data
                            else:
                                ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                                transaction.rollback()
                                transaction.connections.close_all()
                                ##------------------------------------------------------------------
                                data = {
                                    'success': False,
                                    'error': error,
                                    'estado_sii':'',
                                    'msg_sii': '',
                                    'tipo_error': 'Conexión Servidor',
                                    'funcion_error': 'call_service',
                                    'ruta_archivo': '',
                                }

                                return data
                        else:
                            ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                            transaction.rollback()
                            transaction.connections.close_all()
                            ##------------------------------------------------------------------
                            data = {
                                'success': False,
                                'error': error_url,
                                'estado_sii': '',
                                'msg_sii': '',
                                'tipo_error': 'Armado URL',
                                'funcion_error': 'url_web_service',
                                'ruta_archivo': '',
                            }

                            return data
                    else:
                        ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                        transaction.rollback()
                        transaction.connections.close_all()
                        ##------------------------------------------------------------------
                        data = {
                            'success': False,
                            'error': error,
                            'estado_sii': '',
                            'msg_sii': '',
                            'tipo_error': 'Obtención Datos',
                            'funcion_error': 'obtener_datos_conexion',
                            'ruta_archivo': '',
                        }

                        return data
                else:
                    ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                    transaction.rollback()
                    transaction.connections.close_all()
                    ##------------------------------------------------------------------
                    data = {
                        'success': False,
                        'error': error_creacion,
                        'estado_sii': '',
                        'msg_sii': '',
                        'tipo_error': 'Lectura Diccionario',
                        'funcion_error': 'crear_xml_documento',
                        'ruta_archivo': '',
                    }
                    return data
            else:
                ##ROLLBACK a la tabla de folios para no realizar cambios en la tabla
                transaction.rollback()
                transaction.connections.close_all()
                ##------------------------------------------------------------------
                data = {
                    'success': False,
                    'error': error_folio,
                    'estado_sii': '',
                    'msg_sii': '',
                    'tipo_error': 'Validar folio',
                    'funcion_error': 'validar_folios_procesar',
                    'ruta_archivo': '',
                }
                return data
        else:
            data = {
                'success': False,
                'error': error_folio,
                'estado_sii': '',
                'msg_sii': '',
                'tipo_error': 'Obtención de folio',
                'funcion_error': 'obtener_folio',
                'ruta_archivo': '',
            }
            return data
    else:
        data = {
            'success': False,
            'error': error_exi_folio,
            'estado_sii': '',
            'msg_sii': '',
            'tipo_error': 'Existencia Folios Operativos',
            'funcion_error': 'validar_existencia_folio',
            'ruta_archivo': '',
        }
        return data


def actualizar_estados_documentos_sii_lease():

    #TODO el tipo de documento SII esta en duro cambiar por el tipo de documento que corresponda de forma dinamica.

    """
        función que permite realizar la actualización de estados del S.I.I. esta funcion realiza la actualizacion de
        documentos en el siguiente orden:

                Lease                       FechaBusqueda
        ----------------------------------------------------------------------------------------------------------------
            1) Enviado         fecha_creacion >= fecha_actual - 30
            2) Error Envio     fecha_creacion >= fecha_actual - 30


        esta se utiliza con crontab cada 1 hora se debe ejecutar.

    :return: retorna objeto con success true o false y error en caso de existir.
    """
    nievel_traza        = 2  # Nivel completo de traza
    id_dte_empresa      = ''
    date_busqueda       = ''
    datos_conexion      = {}
    list_error          = list()



    error, conexion     = obtener_datos_conexion('wsDTE')

    if not error:

        datos_conexion['codigo_contexto']   = conexion.codigo_contexto
        datos_conexion['host']              = conexion.host
        datos_conexion['url']               = conexion.url
        datos_conexion['puerto']            = conexion.puerto

        id_dte_empresa          = conexion.parametro_facturacion.codigo_conexion
        error_url, url_conexion = url_web_service(**datos_conexion)

        if not error_url:

            ## Conectarse a Web Service de IDTE-------------------------------------------------------------------------

            error, client = call_service(url_conexion)
            date_busqueda = datetime.datetime.now() - timedelta(days=30)

            if not error:

                ## IDTE estado_sii -------------------------------------------------------------------------------------
                # 1 Pendiente
                # 2 Registrado (Boletas)
                # 3 Enviado al SII sin estado
                # 4 Anulado
                # 5 Aceptado
                # 6 Rechazado

                ## Estados Facturas Lease (procesos_factura_estado)-----------------------------------------------------
                #1 Propuesta
                #2 Enviada
                #3 Error Envio
                #4 Aceptada
                #5 Rechazada
                #6 Error Inesperado
                #7 Error Envío

                #Actualizacion de documentos estado --------------------------------------------------------------------

                facturas   = Factura.objects.filter(estado_id__in=[2, 3],
                                                    creado_en__gte=date_busqueda,
                                                    motor_emision_id=2
                                                    )

                for a in facturas:

                    try:
                        ##Consultar estado Documento -------------------------------------------------------------------

                        estado = get_estado_documento(client, id_dte_empresa, a.numero_documento, a.numero_pedido, nievel_traza)

                        if estado.valor != "ERROR":

                            datos_estado        = estado.valor.split('|')
                            estado_sii          = datos_estado[15]
                            msg_sii             = datos_estado[16]
                            receptor            = datos_estado[22]
                            total_dte           = datos_estado[9]

                            if estado_sii == 1:
                                respuesta_estado = 2
                            elif estado_sii == 2 or estado_sii == 5:
                                respuesta_estado = 4
                            elif estado_sii == 3:
                                respuesta_estado = 7
                            elif estado_sii == 6:
                                respuesta_estado = 5
                            else:
                                respuesta_estado =6

                            update_estado_sii = Factura.objects.get(numero_documento=a.numero_documento, id= a.id, motor_emision_id=2)
                            update_estado_sii.estado_id = respuesta_estado
                            update_estado_sii.save()

                    except suds.WebFault as w:
                        error = w.args[0].decode("utf-8")
                        list_error.append({
                            'success'       : False,
                            'error'         : error,
                            'estado_sii'    : '',
                            'msg_sii'       : '',
                            'tipo_error'    : 'Obtención Datos',
                            'funcion_error' : 'get_estado_documento'
                        })

                        return list_error
            else:
                list_error.append({
                    'success'       : False,
                    'error'         : error,
                    'estado_sii'    : '',
                    'msg_sii'       : '',
                    'tipo_error'    : 'Obtención Datos',
                    'funcion_error' : 'url_web_service'
                })

                return list_error
        else:
            list_error.append({
                'success'       : False,
                'error'         : error_url,
                'estado_sii'    : '',
                'msg_sii'       : '',
                'tipo_error'    : 'Armado URL',
                'funcion_error' : 'url_web_service'
            })
            return list_error
    else:
        list_error.append({
            'success'       : False,
            'error'         : error,
            'estado_sii'    : '',
            'msg_sii'       : '',
            'tipo_error'    : 'Obtención Datos',
            'funcion_error' : 'obtener_datos_conexion'
        })
        return list_error

def consulta_estado_documento_sii(tipo_documento, folio_documento):

    """
        Función que permite consultar el estado en el S.I.I. del documento especifico.
        Esta retorna un objeto que contiene la siguiente estructura:

        data = {
            'success': True,
            'error': '',
            'funcion': '',
            'estado_sii': estado_sii,
            'msg_sii': msg_sii,
        }
    :param tipo_documento: tipo de documento electronico del S.I.I. Este debe ser numerico
    :param folio_documento: folio del documento. Este dato debe ser númerico
    :return: retorna un objeto con los errores si es que existieran, estado del documento, mensaje de error del s.i.i en
    caso de rechazo, nombre la función de ocurrio algún error, estado del proceso.
    """
    nievel_traza    = 2  # Nivel completo de traza
    id_dte_empresa  = ''
    datos_conexion  = {}
    error, conexion = obtener_datos_conexion('wsDTE')

    if not error:

        datos_conexion['codigo_contexto']   = conexion.codigo_contexto
        datos_conexion['host']              = conexion.host
        datos_conexion['url']               = conexion.url
        datos_conexion['puerto']            = conexion.puerto

        id_dte_empresa = conexion.parametro_facturacion.codigo_conexion

        ## Armar URL de conexión a Web Service--------------------------------------------------------------------------

        error_url, url_conexion = url_web_service(**datos_conexion)

        if not error_url:
            ## Conectarse a Web Service de IDTE-------------------------------------------------------------------------

            error, client = call_service(url_conexion)

            if not error:

                try:
                    ##Consultar estado Documento -----------------------------------------------------------------------
                    estado_documento = get_estado_documento(client, id_dte_empresa, tipo_documento, folio_documento,
                                                            nievel_traza)

                    if estado_documento.valor != "ERROR":
                        datos_estado    = estado_documento.valor.split('|')
                        estado_sii      = datos_estado[15]
                        msg_sii         = datos_estado[16]

                        data = {
                            'success'   : True,
                            'error'     : '',
                            'funcion'   : '',
                            'estado_sii': estado_sii,
                            'msg_sii'   : msg_sii,
                        }

                        return data
                    else:
                        data = {
                            'success'   : False,
                            'error'     : estado_documento.msg,
                            'funcion'   : 'get_estado_documento',
                            'estado_sii': '',
                            'msg_sii'   : '',
                        }
                        return data
                except suds.WebFault as e:

                    error = e.args[0].decode("utf-8")
                    data = {
                        'success'   : False,
                        'error'     : error,
                        'funcion'   :'Excepción función get_estado_documento',
                        'estado_sii': '',
                        'msg_sii'   : '',
                    }
                    return data
            else:
                data = {
                    'success'   : False,
                    'error'     : error,
                    'funcion'   : 'call_service',
                    'estado_sii': '',
                    'msg_sii'   : '',
                }
                return data
        else:
            data = {
                'success'   : False,
                'error'     : error_url,
                'funcion'   : 'url_web_service',
                'estado_sii': '',
                'msg_sii'   : '',
            }
            return data
    else:
        data = {
            'success'   : False,
            'error'     : error,
            'funcion'   : 'obtener_datos_conexion',
            'estado_sii': '',
            'msg_sii'   : '',
        }
        return data

def obtener_documento_xml_pdf(tipo_documento, folio_documento, formato_documento):

    """

    :param tipo_documento: tipo de documento electronico del S.I.I. Este debe ser numerico
    :param folio_documento: folio del documento. Este dato debe ser númerico
    :param formato_documento: formato del documento PDF o XML cedible que desea obtener.
    :return: retorna un objeto el cual contiene la url del archivo xml o pdf, estado del proceso, error si es que se encuentra
            uno, y el nombre de la función donde ocurrio el error.

        data = {
            'success': False,
            'error': error,
            'funcion': 'call_service',
            'ruta_archivo':archivo.valor
        }
    """
    nievel_traza = 2  # Nivel completo de traza
    id_dte_empresa = ''
    datos_conexion = {}
    error, conexion = obtener_datos_conexion('wsDTE')

    if not error:

        datos_conexion['codigo_contexto'] = conexion.codigo_contexto
        datos_conexion['host'] = conexion.host
        datos_conexion['url'] = conexion.url
        datos_conexion['puerto'] = conexion.puerto

        id_dte_empresa = conexion.parametro_facturacion.codigo_conexion

        ## Armar URL de conexión a Web Service--------------------------------------------------------------------------

        error_url, url_conexion = url_web_service(**datos_conexion)

        if not error_url:
            ## Conectarse a Web Service de IDTE-------------------------------------------------------------------------

            error, client = call_service(url_conexion)

            if not error:
                ##Obtención de XML o PDF cedible del documento ---------------------------------------------------------
                if str(formato_documento).lower() == 'pdf' or str(formato_documento).upper() == 'PDF':
                    formato = 2
                elif str(formato_documento).lower() == 'xml' or str(formato_documento).upper() == 'XML':
                    formato = 4
                else:
                    data = {
                        'success': False,
                        'error': 'Formato enviado, desconocido.',
                        'funcion': '',
                        'ruta_archivo': ''

                    }
                    return data

                try:
                    ##Obtener archivo PDF o XML de la factura-----------------------------------------------------------
                    archivo = get_archivo_documento(client, id_dte_empresa,tipo_documento, folio_documento, formato,
                                                    nievel_traza)

                    if archivo.dio_error == False:
                        data = {
                            'success': False,
                            'error': error,
                            'funcion': 'call_service',
                            'ruta_archivo':archivo.valor

                        }
                        return data
                    else:
                        data = {
                            'success': False,
                            'error': archivo.msg,
                            'funcion': 'get_archivo_documento',
                            'ruta_archivo': ''
                        }
                        return data
                except suds.WebFault as e:

                    error = e.args[0].decode("utf-8")
                    data = {
                        'success': False,
                        'error': error,
                        'funcion': 'Excepción función get_estado_documento',
                        'ruta_archivo': ''
                    }
                    return data
            else:
                data = {
                    'success': False,
                    'error': error,
                    'funcion': 'call_service',
                    'ruta_archivo': ''
                }
                return data
        else:
            data = {
                'success': False,
                'error': error_url,
                'funcion': 'url_web_service',
                'ruta_archivo': ''
            }
            return data
    else:
        data = {
            'success': False,
            'error': error,
            'funcion': 'obtener_datos_conexion',
            'ruta_archivo': ''
        }
        return data


## ---------------------------- MANEJO DE LIBROS ELECTRONICOS COMPRAS/VENTAS -------------------------------------------

def prueba_libro_compra():

    kwargs = {}
    lista_libro = list()
    lista_impuestos = list()

    kwargs['id_hist_lcv'] = '20160726'
    kwargs['periodo_libro'] ='2016-07'
    kwargs['rectificatoria'] ='0'
    kwargs['cod_rectificatoria'] ='0'
    kwargs['notificacion'] ='0'
    kwargs['num_notificacion'] ='0'
    kwargs['factor_Proporcional_iva']='0'

    for a in range(1):
        data_libro = {
            'tipo_documento':'30',
            'folio_documento':'6',
            'rut_proveedor':'12345678-9',
            'razon_social_prov':'Proveedor A',
            'folio_interno':'456',
            'codigo_sucursal':'0',
            'anulado':'0',
            'tasa_iva':'19',
            'fecha_emision':'2016-07-18',
            'afecto':'575639',
            'exento':'0',
            'iva_recuperable':'36252',
            'total':'9658669',
            'iva_activo_fijo':'0',
            'monto_activo_fijo':'0',
            'iva_no_recup_1':'0',
            'iva_no_recup_2':'0',
            'iva_no_recup_3':'0',
            'iva_no_recup_4':'0',
            'iva_no_recup_9':'0',
            'iva_uso_comun':'0',
            'imp_sin_derecho_credito':'0',
            'iva_retenido':'0',
            'iva_no_retenido':'0',
            'imp_tabaco_puros':'0',
            'imp_tabaco_cig':'0',
            'imp_tabaco_elab':'0',
            'impu_vehiculo':'0',
            'imp_adicional':'0',
        }
        lista_libro.append(data_libro)

    kwargs['libro_compra'] =lista_libro


    for b in range (1):
        data_impuestos ={
            'tipo_doc_ir':'30',
            'folio_doc_ir':'6',
            'rut_provedor_ir':'12345678-9',
            'iva_margen_comerc':'0',
            'iva_retenido_total':'0',
            'iva_anticipado_faenamiento':'0',
            'iva_anticipado_carne':'0',
            'iva_anticipado_harina':'0',
            'iva_retenido_legumbre':'0',
            'iva_retenido_silvestres':'5555',
            'iva_retenido_ganado':'0',
            'iva_retenido_madera':'0',
            'iva_retenido_trigo':'4444',
            'iva_retenido_arroz':'0',
            'iva_retenido_hidrobiolo':'0',
            'tipo_cta_pago':'0',
            'iva_retenido_chatarra':'0',
            'iva_retenido_construccion':'0',
            'impuesto_adicional_art_37_abc':'0',
            'impuesto_adicional_art_37_ehil':'0',
            'impuesto_adicional_art_37_j':'0',
            'impuesto_art_42_letra_b':'0',
            'impuesto_art_42_letra_c_1':'0',
            'impuesto_art_42_letra_c_2':'0',
            'impuesto_art_42_letra_a':'0',
            'impuesto_art_42_letra_a_2':'0',
            'impuesto_especifico_diesel':'0',
            'recuperacion_imp_diesel_transp':'0',
            'impuesto_especifico_gasolina':'0',
            'iva_retenido_cartones':'0',
            'iva_retenido_frambuesas_pasas':'0',
            'indicador_monto_neto':'0',
            'iva_margen_comer_instru_prepago':'0',
            'impuesto_gas_natural':'0',
            'impuesto_gas_licuado':'0',
            'impuesto_retenido_suplementeros':'0',
            'impuesto_retenido_fact_inicio':'0',
        }
        lista_impuestos.append(data_impuestos)



    kwargs['impuesto_retenido_lc'] =lista_impuestos

    return kwargs

def pruebas_libro_venta():

    kwargs = {}
    lista_libro = list()
    lista_impuestos = list()
    lista_liquidacion = list()
    lista_boletas = list()

    kwargs['id_hist_lcv'] = '20160727'
    kwargs['tipo_libro'] = 'V'
    kwargs['periodo_libro'] ='2016-07'
    kwargs['rectificatoria'] ='0'
    kwargs['cod_rectificatoria'] ='0'
    kwargs['notificacion'] ='0'
    kwargs['num_notificacion'] ='0'

    for c in range(1):

        datos_venta = {
            'tipo_documento_lv':'33',
            'folio_documento':'100',
            'anulado_lv':'0',
            'tasa_iva':'19',
            'fecha_emision':'2016-07-26',
            'rut_cliente':'12345678-9',
            'razon_social':'Cliente x',
            'exento_lv':'0',
            'afecto_lv':'1000',
            'iva_recuperable':'190',
            'total_lv':'1190',
            'folio_interno':'6',
            'ind_serv_periodo':'0',
            'ind_venta_sin_costo':'0',
            'cod_sucursal':'0',
            'iva_fuera_plazo':'0',
            'iva_retenido_total':'0',
            'iva_retenido_parcial':'0',
            'cred_especial_construc':'0',
            'depositos_envases':'0',
            'pasajes_nacional':'0',
            'pasajes_internacional':'0',
            'iva_propio':'0',
            'iva_tercero':'0',
            'art17dl825':'0',
            'rut_emisor_liq':'',
            'val_comision_neto':'0',
            'val_comision_exento':'0',
            'val_comision_iva':'0',
            'ley18211':'0',
        }
        lista_libro.append(datos_venta)


    kwargs['libro_venta'] = lista_libro


    for m in range(1):
        datos_imp = {
            'tipo_doc_ir':'33',
            'folio_doc_ir':'100',
            'iva_margen_comerc':'0',
            'iva_retenido_total':'2000',
            'iva_anticipado_faenamiento':'800',
            'iva_anticipado_carne':'0',
            'iva_anticipado_harina':'0',
            'iva_retenido_legumbre':'0',
            'iva_retenido_silvestres':'0',
            'iva_retenido_ganado':'0',
            'iva_retenido_madera':'0',
            'iva_retenido_trigo':'0',
            'iva_retenido_arroz':'0',
            'iva_retenido_hidrobiolo':'0',
            'tipo_cta_pago':'0',
            'iva_retenido_chatarra':'0',
            'iva_retenido_construccion':'0',
            'impuesto_adicional_art_37_abc':'0',
            'impuesto_adicional_art_37_ehil':'0',
            'impuesto_adicional_art_37_j':'0',
            'impuesto_art_42_letra_b':'0',
            'impuesto_art_42_letra_c_1':'0',
            'impuesto_art_42_letra_c_2':'0',
            'impuesto_art_42_letra_a':'0',
            'impuesto_art_42_letra_a_2':'0',
            'impuesto_especifico_diesel':'0',
            'recuperacion_imp_diesel_transp':'0',
            'impuesto_especifico_gasolina':'0',
            'iva_retenido_cartones':'0',
            'iva_retenido_frambuesas_pasas':'0',
            'indicador_monto_neto':'0',
            'iva_margen_comer_instru_prepago':'0',
            'impuesto_gas_natural':'0',
            'impuesto_gas_licuado':'0',
            'impuesto_retenido_suplementeros':'0',
            'impuesto_retenido_fact_inicio':'0',
        }
        lista_impuestos.append(datos_imp)


    kwargs['impuesto_retenido_lv'] = lista_impuestos


    for b in range(1):
        datos_liq = {
            'tipo_doc_liq':'43',
            'folio_doc_liq':'100',
            'rut_emisor_liq':'12345678-9',
            'anulado_liq':'0',
            'tasa_iva_liq':'19',
            'fecha_emision_liq':'2016-07-25',
            'rut_cliente_liq':'12345678-9',
            'razon_social_cliente_liq':'Cliente x',
            'exento_liq':'0',
            'afecto_liq':'1000',
            'iva_recup_liq':'190',
            'total_liq':'1190',
            'folio_interno_liq':'6',
            'ind_venta_period_liq':'0',
            'ind_venta_sin_costo_liq':'0',
            'iva_reten_total_liq':'0',
            'folio_doc_ir':'0',
            'iva_no_reten_liq':'0',
            'cred_parcial_constr_liq':'0',
            'desposito_envases_liq':'0',
            'pasaje_nacional_liq':'0',
            'pasaje_internacional_liq':'0',
            'iva_propio_liq':'0',
            'iva_tercero_liq':'0',
            'Art17DL825_liq':'0',
            'val_comi_neto_liq':'0',
            'val_comi_exento_liq':'0',
            'val_comi_iva_liq':'0',
            'Ley18211_liq':'0',
            'iva_margen_comerc_liq':'0',
            'iva_retenido_total_liq':'0',
            'iva_anticipado_faenamiento_liq':'2000',
            'iva_anticipado_carne_liq':'0',
            'iva_anticipado_harina_liq':'800',
            'iva_retenido_legumbre_liq':'0',
            'iva_retenido_silvestres_liq':'0',
            'iva_retenido_ganado_liq':'0',
            'iva_retenido_madera_liq':'0',
            'iva_retenido_trigo_liq':'0',
            'iva_retenido_arroz_liq':'0',
            'iva_retenido_hidrobiolo_liq':'0',
            'tipo_cta_pago_liq':'0',
            'iva_retenido_chatarra_liq':'0',
            'iva_retenido_construccion_liq':'0',
            'impuesto_adicional_art_37_abc_liq':'0',
            'impuesto_adicional_art_37_ehil_liq':'0',
            'impuesto_adicional_art_37_j_liq':'0',
            'impuesto_art_42_letra_b_liq':'0',
            'impuesto_art_42_letra_c_1_liq':'0',
            'impuesto_art_42_letra_c_2_liq':'0',
            'impuesto_art_42_letra_a_liq':'0',
            'impuesto_art_42_letra_a_2_liq':'0',
            'impuesto_especifico_diesel_liq':'0',
            'recuperacion_imp_diesel_transp_liq':'0',
            'impuesto_especifico_gasolina_liq':'0',
            'iva_retenido_cartones_liq':'0',
            'iva_retenido_frambuesas_pasas_liq':'0',
            'indicador_monto_neto_liq':'0',
            'iva_margen_comer_instru_prepago_liq':'0',
            'impuesto_gas_natural_liq':'0',
            'impuesto_gas_licuado_liq':'0',
            'impuesto_retenido_suplementeros_liq':'0',
            'impuesto_retenido_fact_inicio_liq':'0',
        }

        lista_liquidacion.append(datos_liq)

    kwargs['liquidacion_factura'] = lista_liquidacion


    for a in range(1):
        datos_boletas = {
            'tipo_doc_bol':'39',
            'cantidad_bol':'1000',
            'cant_anulado_bol':'34',
            'total_afecto_bol':'1000000',
            'total_exento_bol':'0',
            'total_iva_recup_bol':'19000',
            'total_monto_bol':'11900000',
            'total_iva_fuera_plazo_bol':'0',
            'total_iva_rete_total_bol':'0',
            'total_iva_rete_parcial_bol':'0',
            'total_cred_espe_constr_bol':'0',
            'total_despo_envase_bol':'0',
            'total_iva_no_rete_bol':'0',
            'total_pasaje_naci_bol':'0',
            'total_pasaje_intern_bol':'0',
            'total_iva_propio_bol':'0',
            'total_iva_terce_bol':'0',
            'total_val_com_neto_bol':'0',
            'total_val_com_exento_bol':'0',
            'total_val_com_iva_bol':'0',
            'total_ley18211_bol':'0',
        }
        lista_boletas.append(datos_boletas)

    kwargs['boletas'] = lista_boletas

    respuesta = envio_libro_compras_ventas_electronico(**kwargs)

def envio_libro_compras_ventas_electronico(**kwargs):

    """
        función que permite realiza el envio del libros de compras o ventas a S.I.I. atraves de IDTE, esta función recibe un
        diccionario con los datos a enviar, y retorna un objeto con el estado del proceso, errores, estado del SII,
        mensaje del SII, nombre de la función donde ocurrio el error y el tipo de error.
    :param request:
    :param kwargs: diccionario con la data del libro de compras o ventas.
    :return: retorna un objeto con el estado del proceso y mensajes de error, etc.
    """

    ##Variables --------------------------------------------------------------------------------------------------------

    nievel_traza    = 2  # Nivel completo de traza de Error
    id_dte_empresa  = ''
    id_hist_lcv     = kwargs['id_hist_lcv']    #datetime.datetime.now().strftime('%Y-%m-%d').replace('-','')
    accion          = 1  # Procesar y enviar libro
    datos_conexion  = {}
    tipo_libro      = str(kwargs['tipo_libro']) #Tipo de libro compras o ventas

    ##Creacion de xml---------------------------------------------------------------------------------------------------
    if tipo_libro.upper() == 'C':
        error_creacion, xml_libro = crear_xml_libro_compra(**kwargs)
    elif tipo_libro.upper() == 'V':
        error_creacion, xml_libro = crear_xml_libro_venta(**kwargs)
    else:
        error = "El tipo de libro enviado es erroneo."
        data = {
            'success'           : False,
            'error'             : error,
            'estado_sii'        : '',
            'descripcion_estado': '',
            'msg_sii'           : '',
            'tipo_error'        : '',
            'funcion_error'     : '',
        }
        return data


    if not error_creacion:
        ##Obtener datos de conexion IDTE -------------------------------------------------------------------------------
        error, conexion = obtener_datos_conexion('wsLCV')

        if not error:
            datos_conexion['codigo_contexto']   = conexion.codigo_contexto
            datos_conexion['host']              = conexion.host
            datos_conexion['url']               = conexion.url
            datos_conexion['puerto']            = conexion.puerto

            id_dte_empresa          = conexion.parametro_facturacion.codigo_conexion
            error_url, url_conexion = url_web_service(**datos_conexion)

            if not error_url:

                ## Conectarse a Web Service de IDTE---------------------------------------------------------------------

                error, client = call_service(url_conexion)

                if not error:

                    ##Consultar estado libro compra --------------------------------------------------------------------

                    try:

                        estado_libro = get_estado_lcv(client, id_dte_empresa, id_hist_lcv, nievel_traza)

                        if estado_libro.valor == "ERROR":

                            ##Envio de libro de compras a procesar a IDTE---------------------------------------------------

                            try:
                                procesar_libro_compra = procesar_lcv_xml(client, id_dte_empresa, tipo_libro, id_hist_lcv,
                                                                         accion, nievel_traza, xml_libro)

                                if procesar_libro_compra.dio_error == False:

                                    ##Consultar estado Libro ---------------------------------------------------------------
                                    try:
                                        estado_libro_enviado = get_estado_lcv(client, id_dte_empresa, id_hist_lcv,
                                                                              nievel_traza)

                                        if estado_libro_enviado.valor != "Error":
                                            datos_estado    = estado_libro_enviado.valor.split('|')
                                            estado_sii      = datos_estado[6]
                                            msg_sii         = datos_estado[7]

                                            if int(estado_sii) == 1:
                                                error = "Libro no enviado"
                                            elif int(estado_sii) == 3:
                                                error = "Libro enviado sin estado"
                                            elif int(estado_sii) == 5:
                                                error = "Libro aceptado"
                                            elif int(estado_sii) == 6:
                                                error = "Libro Rechazado"
                                            else:
                                                error = "Estado desconocido"

                                            data = {
                                                'success'           : True,
                                                'error'             : '',
                                                'estado_sii'        : estado_sii,
                                                'descripcion_estado': error,
                                                'msg_sii'           : msg_sii,
                                                'tipo_error'        : '',
                                                'funcion_error'     : 'get_estado_lcv',
                                            }
                                            return data
                                        else:
                                            data = {
                                                'success'           : False,
                                                'error'             : estado_libro_enviado.msg,
                                                'estado_sii'        : '',
                                                'descripcion_estado': '',
                                                'msg_sii'           : '',
                                                'tipo_error'        : '',
                                                'funcion_error'     : 'get_estado_lcv',
                                            }
                                            return data
                                    except suds.WebFault as b:
                                        error = b.args[0].decode("utf-8")
                                        data = {
                                            'success'           : False,
                                            'error'             : error,
                                            'estado_sii'        : '',
                                            'descripcion_estado': '',
                                            'msg_sii'           : '',
                                            'tipo_error'        : 'Error de Excepción Try Except',
                                            'funcion_error'     : 'get_estado_lcv',
                                        }
                                        return data
                                else:
                                    data = {
                                        'success'           : False,
                                        'error'             : procesar_libro_compra.msg,
                                        'estado_sii'        : '',
                                        'descripcion_estado': '',
                                        'msg_sii'           : '',
                                        'tipo_error'        : procesar_libro_compra.tipo_error,
                                        'funcion_error'     : 'procesar_lcv_xml',
                                    }
                                    return data
                            except suds.WebFault as e:
                                error = e.args[0].decode("utf-8")
                                data = {
                                    'success'           : False,
                                    'error'             : error,
                                    'estado_sii'        : '',
                                    'descripcion_estado': '',
                                    'msg_sii'           : '',
                                    'tipo_error'        : 'Error de Excepción Try Except',
                                    'funcion_error'     : 'procesar_lcv_xml',
                                }
                            return data
                        else:
                            datos_estado = estado_libro.valor.split('|')
                            estado_sii   = datos_estado[6]
                            msg_sii      = datos_estado[7]

                            if int(estado_sii) == 1:
                                error = "Libro no enviado"
                            elif int(estado_sii) == 3:
                                error = "Libro enviado sin estado"
                            elif int(estado_sii) == 5:
                                error = "Libro aceptado"
                            elif int(estado_sii) == 6:
                                error = "Libro Rechazado"
                            else:
                                error = "Estado desconocido"

                            data = {
                                'success'           : False,
                                'error'             : error,
                                'estado_sii'        : estado_sii,
                                'descripcion_estado': '',
                                'msg_sii'           :msg_sii,
                                'tipo_error'        : '',
                                'funcion_error'     : 'get_estado_lcv',
                            }
                            return data
                    except suds.WebFault as a:
                        error = a.args[0].decode("utf-8")
                        data = {
                            'success'           : False,
                            'error'             : error,
                            'estado_sii'        : '',
                            'descripcion_estado': '',
                            'msg_sii'           : '',
                            'tipo_error'        : 'Error de Excepción Try Except',
                            'funcion_error'     : 'get_estado_lcv',
                        }
                        return data
                else:
                    data = {
                        'success'           : False,
                        'error'             : error,
                        'estado_sii'        :'',
                        'descripcion_estado': '',
                        'msg_sii'           : '',
                        'tipo_error'        : 'Conexión Servidor',
                        'funcion_error'     : 'call_service',
                    }

                    return data
            else:
                data = {
                    'success'           : False,
                    'error'             : error_url,
                    'estado_sii'        : '',
                    'descripcion_estado': '',
                    'msg_sii'           : '',
                    'tipo_error'        : 'Armado URL',
                    'funcion_error'     : 'url_web_service',
                }

                return data
        else:
            data = {
                'success'           : False,
                'error'             : error,
                'estado_sii'        : '',
                'descripcion_estado': '',
                'msg_sii'           : '',
                'tipo_error'        : 'Obtención Datos',
                'funcion_error'     : 'obtener_datos_conexion',
            }

            return data
    else:
        data = {
            'success'           : False,
            'error'             : error_creacion,
            'estado_sii'        : '',
            'descripcion_estado': '',
            'msg_sii'           : '',
            'tipo_error'        : 'Error Lectura',
            'funcion_error'     : 'crear_xml_libro_compra',
        }
        return data

def consulta_estado_libro_compras_ventas_sii(id_hist_lcv):

    """
        Función que permite realiza la consulta del estado del libro de compra enviado, para esto debe realizar el envio
        del id_hist_lcv el cual es el identificado o clave con la cual será identificado el envio en el sistema de IDTE.

        Esta retorna un objeto en donde se puede obtener el estado del proceso, el error, el nombre de la funcion de
        ocurrio el error, estado del s.i.i. y mensaje del s.i.i.

        objeto = {
            'success': False,
            'error':estado_libro.msg,
            'funcion': 'get_estado_lcv',
            'estado_sii': '',
            'msg_sii': ''
        }

    :param id_hist_lcv: clave o llave con la cual fue realizado el almacenamiento del libro electronico en IDTE.
    :return: retorna un objeto con el estado del libro enviado, y lo errores en caso de existir.
    """
    ##Variables --------------------------------------------------------------------------------------------------------
    nievel_traza    = 2  # Nivel completo de traza de Error
    id_dte_empresa  = ''
    datos_conexion  = {}

    ##Obtener datos de conexion IDTE -------------------------------------------------------------------------------
    error, conexion = obtener_datos_conexion('wsLCV')

    if not error:
        datos_conexion['codigo_contexto']   = conexion.codigo_contexto
        datos_conexion['host']              = conexion.host
        datos_conexion['url']               = conexion.url
        datos_conexion['puerto']            = conexion.puerto

        id_dte_empresa          = conexion.parametro_facturacion.codigo_conexion
        error_url, url_conexion = url_web_service(**datos_conexion)

        if not error_url:

            ## Conectarse a Web Service de IDTE---------------------------------------------------------------------

            error, client = call_service(url_conexion)

            if not error:

                ##Consultar estado libro compra --------------------------------------------------------------------
                try:
                    estado_libro = get_estado_lcv(client, id_dte_empresa, id_hist_lcv, nievel_traza)

                    if estado_libro.valor == "ERROR":

                        data = {
                            'success'       : False,
                            'error'         : estado_libro.msg,
                            'funcion'       : 'get_estado_lcv',
                            'estado_sii'    : '',
                            'msg_sii'       : '',
                            'tipo_error'    : '',
                            'funcion_error' : 'get_estado_lcv',
                        }
                        return data
                    else:
                        datos_estado = estado_libro.valor.split('|')
                        estado_sii   = datos_estado[6]
                        msg_sii      = datos_estado[7]

                        if int(estado_sii) == 1:
                            error = "Libro no enviado"
                        elif int(estado_sii) == 3:
                            error = "Libro enviado sin estado"
                        elif int(estado_sii) == 5:
                            error = "Libro aceptado"
                        elif int(estado_sii) == 6:
                            error = "Libro Rechazado"
                        else:
                            error = "Estado desconocido"

                        data = {
                            'success'           : True,
                            'error'             : '',
                            'estado_sii'        : estado_sii,
                            'descripcion_estado': error,
                            'msg_sii'           : msg_sii,
                            'tipo_error'        : '',
                            'funcion_error'     : 'get_estado_lcv',
                        }
                        return data
                except suds.WebFault as e:
                    error = e.args[0].decode("utf-8")
                    data = {
                        'success'           : False,
                        'error'             : error,
                        'estado_sii'        : '',
                        'descripcion_estado': '',
                        'msg_sii'           : '',
                        'tipo_error'        : 'Error de Excepción Try Except',
                        'funcion_error'     : 'get_estado_lcv',
                    }
                    return data
            else:
                data = {
                    'success'           : False,
                    'error'             : error,
                    'estado_sii'        :'',
                    'descripcion_estado': '',
                    'msg_sii'           : '',
                    'tipo_error'        : 'Conexión Servidor',
                    'funcion_error'     : 'call_service',
                }

                return data
        else:
            data = {
                'success'           : False,
                'error'             : error_url,
                'estado_sii'        : '',
                'descripcion_estado': '',
                'msg_sii'           : '',
                'tipo_error'        : 'Armado URL',
                'funcion_error'     : 'url_web_service',
                'ruta_archivo'      : '',
            }

            return data
    else:
        data = {
            'success'           : False,
            'error'             : error,
            'estado_sii'        : '',
            'descripcion_estado': '',
            'msg_sii'           : '',
            'tipo_error'        : 'Obtención Datos',
            'funcion_error'     : 'obtener_datos_conexion',
        }

        return data

def consulta_mensaje_rechazo_libro_compras_ventas_sii(id_hist_lcv):
    """
        función que permite realizar la consulta del mensaje de rechazo entregado por el S.I.I. sobre el libro enviado.
        esta funcion retorna un objeto con el estado del proceso, mensaje del sii, nombre de la función, y error con
         los valores erroneos encontrado en el libro

        data = {
            'success': True,
            'error': mensaje.valor,
            'funcion': 'get_msg_rechazo_sii_lcv',
            'msg_sii': mensaje_rechazo.msg,
        }

    :param id_hist_lcv: Clave primario o llave con la cual fue almacenado el libro electronico en el sistema de IDTE
    :return: retorna un objeto que contiene en su estructura el mensaje indicado por el S.I.I.
    """

    ##Variables --------------------------------------------------------------------------------------------------------

    nievel_traza = 2  # Nivel completo de traza de Error
    id_dte_empresa = ''
    datos_conexion = {}

    ##Obtener datos de conexion IDTE -----------------------------------------------------------------------------------
    error, conexion = obtener_datos_conexion('wsLCV')

    if not error:
        datos_conexion['codigo_contexto']   = conexion.codigo_contexto
        datos_conexion['host']              = conexion.host
        datos_conexion['url']               = conexion.url
        datos_conexion['puerto']            = conexion.puerto

        id_dte_empresa          = conexion.parametro_facturacion.codigo_conexion
        error_url, url_conexion = url_web_service(**datos_conexion)

        if not error_url:

            ## Conectarse a Web Service de IDTE-------------------------------------------------------------------------

            error, client = call_service(url_conexion)

            if not error:

                ##Consultar mensaje rechazo libro SII-------------------------------------------------------------------

                mensaje_rechazo = get_msg_rechazo_sii_lcv(client, id_dte_empresa, id_hist_lcv, nievel_traza)

                if mensaje_rechazo.dio_error == False:

                    data = {
                        'success'       : True,
                        'error'         : mensaje_rechazo.valor,
                        'funcion'       : 'get_msg_rechazo_sii_lcv',
                        'msg_sii'       : mensaje_rechazo.msg,
                        'funcion_error' : 'get_msg_rechazo_sii_lcv',
                    }
                    return data
                else:
                    data = {
                        'success'       : False,
                        'error'         : mensaje_rechazo.msg,
                        'msg_sii'       : mensaje_rechazo.valor,
                        'funcion_error' : 'get_msg_rechazo_sii_lcv',
                    }
                    return data
            else:
                data = {
                    'success'       : False,
                    'error'         : error,
                    'msg_sii'       : '',
                    'funcion_error' : 'call_service',
                }

                return data
        else:
            data = {
                'success'       : False,
                'error'         : error_url,
                'msg_sii'       : '',
                'funcion_error' : 'url_web_service',
            }

            return data
    else:
        data = {
            'success'       : False,
            'error'         : error,
            'msg_sii'       : '',
            'funcion_error' : 'obtener_datos_conexion',
        }

        return data

def envio_libro_ventas_electronico(**kwargs):
    """

    :param kwargs:
    :return:
    """

    ##Variables --------------------------------------------------------------------------------------------------------

    nievel_traza    = 2  # Nivel completo de traza de Error
    id_dte_empresa  = ''
    id_hist_lcv     = kwargs['id_hist_lcv']  # datetime.datetime.now().strftime('%Y-%m-%d').replace('-','')
    accion          = 1  # Procesar y enviar libro
    datos_conexion  = {}
    tipo_libro      = 'V'  # libro de compra

    ##Creacion de xml---------------------------------------------------------------------------------------------------
    error_creacion, xml_libro = crear_xml_libro_venta(**kwargs)

    if not error_creacion:
        ##Obtener datos de conexion IDTE -------------------------------------------------------------------------------
        error, conexion = obtener_datos_conexion('wsLCV')

        if not error:
            datos_conexion['codigo_contexto']   = conexion.codigo_contexto
            datos_conexion['host']              = conexion.host
            datos_conexion['url']               = conexion.url
            datos_conexion['puerto']            = conexion.puerto

            id_dte_empresa          = conexion.parametro_facturacion.codigo_conexion
            error_url, url_conexion = url_web_service(**datos_conexion)

            if not error_url:

                ## Conectarse a Web Service de IDTE---------------------------------------------------------------------

                error, client = call_service(url_conexion)

                if not error:

                    ##Consultar estado libro ventas --------------------------------------------------------------------

                    estado_libro = get_estado_lcv(client, id_dte_empresa, id_hist_lcv, nievel_traza)

                    if estado_libro.valor == "ERROR":

                        # xml_libro = '<IDTE_LC><General><periodo>2013-06</periodo><rectificatoria>0</rectificatoria><cod_rectificatoria>0</cod_rectificatoria><notificacion>0</notificacion><num_notificacion>0</num_notificacion><factor_Proporcional_iva_LC>0</factor_Proporcional_iva_LC></General><LC><reg_LC><TipoDoc_LC>30</TipoDoc_LC><folioDoc_LC>6</folioDoc_LC><rutproveedor>12345678-9</rutproveedor><razonsocial_proveedor>Proveedor A</razonsocial_proveedor><foliointerno_LC>456</foliointerno_LC><cod_sucursal_LC>0</cod_sucursal_LC><anulado_LC>0</anulado_LC><tasa_iva_LC>19</tasa_iva_LC><fecha_emision_LC>2013-06-03</fecha_emision_LC><afecto_LC>576756</afecto_LC><exento_LC>0</exento_LC><iva_recup_LC>109584</iva_recup_LC><total_LC>686340</total_LC><iva_activo_fijo>0</iva_activo_fijo><MntActivoFijo>0</MntActivoFijo><iva_no_recup1>0</iva_no_recup1><iva_no_recup2>0</iva_no_recup2><iva_no_recup3>0</iva_no_recup3><iva_no_recup4>0</iva_no_recup4><iva_no_recup9>0</iva_no_recup9><iva_uso_comun>0</iva_uso_comun><imp_sin_derecho_credit>0</imp_sin_derecho_credit><iva_retenido_LC>0</iva_retenido_LC><iva_no_retenido_LC>0</iva_no_retenido_LC><imp_tabacos_puros>0</imp_tabacos_puros><imp_tabacos_cig>0</imp_tabacos_cig><imp_tabacos_elab>0</imp_tabacos_elab><imp_vehiculos_auto>0</imp_vehiculos_auto><imp_adicionales>0</imp_adicionales></reg_LC><reg_LC><TipoDoc_LC>33</TipoDoc_LC><folioDoc_LC>8</folioDoc_LC><rutproveedor>3333333-3</rutproveedor><razonsocial_proveedor>Proveedor B</razonsocial_proveedor><foliointerno_LC>676</foliointerno_LC><cod_sucursal_LC>0</cod_sucursal_LC><anulado_LC>0</anulado_LC><tasa_iva_LC>19</tasa_iva_LC><fecha_emision_LC>2013-06-20</fecha_emision_LC><afecto_LC>7778</afecto_LC><exento_LC>0</exento_LC><iva_recup_LC>345</iva_recup_LC><total_LC>34545</total_LC><iva_activo_fijo>0</iva_activo_fijo><MntActivoFijo>0</MntActivoFijo><iva_no_recup1>0</iva_no_recup1><iva_no_recup2>0</iva_no_recup2><iva_no_recup3>0</iva_no_recup3><iva_no_recup4>0</iva_no_recup4><iva_no_recup9>0</iva_no_recup9><iva_uso_comun>0</iva_uso_comun><imp_sin_derecho_credit>0</imp_sin_derecho_credit><iva_retenido_LC>0</iva_retenido_LC><iva_no_retenido_LC>0</iva_no_retenido_LC><imp_tabacos_puros>0</imp_tabacos_puros><imp_tabacos_cig>0</imp_tabacos_cig><imp_tabacos_elab>0</imp_tabacos_elab><imp_vehiculos_auto>0</imp_vehiculos_auto><imp_adicionales>0</imp_adicionales></reg_LC><reg_LC><TipoDoc_LC>60</TipoDoc_LC><folioDoc_LC>8</folioDoc_LC><rutproveedor>2222222-2</rutproveedor><razonsocial_proveedor>Proveedor C</razonsocial_proveedor><foliointerno_LC>777</foliointerno_LC><cod_sucursal_LC>0</cod_sucursal_LC><anulado_LC>0</anulado_LC><tasa_iva_LC>19</tasa_iva_LC><fecha_emision_LC>2013-06-10</fecha_emision_LC><afecto_LC>678768</afecto_LC><exento_LC>0</exento_LC><iva_recup_LC>34545</iva_recup_LC><total_LC>5656456</total_LC><iva_activo_fijo>0</iva_activo_fijo><MntActivoFijo>0</MntActivoFijo><iva_no_recup1>0</iva_no_recup1><iva_no_recup2>0</iva_no_recup2><iva_no_recup3>0</iva_no_recup3><iva_no_recup4>0</iva_no_recup4><iva_no_recup9>0</iva_no_recup9><iva_uso_comun>0</iva_uso_comun><imp_sin_derecho_credit>0</imp_sin_derecho_credit><iva_retenido_LC>0</iva_retenido_LC><iva_no_retenido_LC>0</iva_no_retenido_LC><imp_tabacos_puros>0</imp_tabacos_puros><imp_tabacos_cig>0</imp_tabacos_cig><imp_tabacos_elab>0</imp_tabacos_elab><imp_vehiculos_auto>0</imp_vehiculos_auto><imp_adicionales>0</imp_adicionales></reg_LC></LC><IR_LC><reg_IR_LC><TipoDoc_IR_LC>30</TipoDoc_IR_LC><folioDoc_IR_LC>6</folioDoc_IR_LC><rutproveedor_IR_LC>12345678-9</rutproveedor_IR_LC><cod14_IR_LC>0</cod14_IR_LC><cod15_IR_LC>0</cod15_IR_LC><cod17_IR_LC>0</cod17_IR_LC><cod18_IR_LC>0</cod18_IR_LC><cod19_IR_LC>0</cod19_IR_LC><cod30_IR_LC>0</cod30_IR_LC><cod31_IR_LC>55555</cod31_IR_LC><cod32_IR_LC>0</cod32_IR_LC><cod33_IR_LC>0</cod33_IR_LC><cod34_IR_LC>4444</cod34_IR_LC><cod36_IR_LC>0</cod36_IR_LC><cod37_IR_LC>0</cod37_IR_LC><cod38_IR_LC>0</cod38_IR_LC><cod39_IR_LC>0</cod39_IR_LC><cod41_IR_LC>0</cod41_IR_LC><cod23_IR_LC>0</cod23_IR_LC><cod44_IR_LC>0</cod44_IR_LC><cod45_IR_LC>0</cod45_IR_LC><cod24_IR_LC>0</cod24_IR_LC><cod25_IR_LC>0</cod25_IR_LC><cod26_IR_LC>0</cod26_IR_LC><cod27_IR_LC>0</cod27_IR_LC><cod271_IR_LC>0</cod271_IR_LC><cod28_IR_LC>0</cod28_IR_LC><cod29_IR_LC>0</cod29_IR_LC><cod35_IR_LC>0</cod35_IR_LC><cod47_IR_LC>0</cod47_IR_LC><cod48_IR_LC>0</cod48_IR_LC><cod49_IR_LC>0</cod49_IR_LC><cod50_IR_LC>0</cod50_IR_LC><cod51_IR_LC>0</cod51_IR_LC><cod52_IR_LC>0</cod52_IR_LC><cod53_IR_LC>0</cod53_IR_LC><cod60_IR_LC>0</cod60_IR_LC></reg_IR_LC><reg_IR_LC><TipoDoc_IR_LC>60</TipoDoc_IR_LC><folioDoc_IR_LC>8</folioDoc_IR_LC><rutproveedor_IR_LC>2222222-2</rutproveedor_IR_LC><cod14_IR_LC>0</cod14_IR_LC><cod15_IR_LC>0</cod15_IR_LC><cod17_IR_LC>0</cod17_IR_LC><cod18_IR_LC>0</cod18_IR_LC><cod19_IR_LC>0</cod19_IR_LC><cod30_IR_LC>0</cod30_IR_LC><cod31_IR_LC>0</cod31_IR_LC><cod32_IR_LC>0</cod32_IR_LC><cod33_IR_LC>0</cod33_IR_LC><cod34_IR_LC>0</cod34_IR_LC><cod36_IR_LC>7777</cod36_IR_LC><cod37_IR_LC>0</cod37_IR_LC><cod38_IR_LC>0</cod38_IR_LC><cod39_IR_LC>0</cod39_IR_LC><cod41_IR_LC>0</cod41_IR_LC><cod23_IR_LC>0</cod23_IR_LC><cod44_IR_LC>0</cod44_IR_LC><cod45_IR_LC>0</cod45_IR_LC><cod24_IR_LC>0</cod24_IR_LC><cod25_IR_LC>0</cod25_IR_LC><cod26_IR_LC>0</cod26_IR_LC><cod27_IR_LC>0</cod27_IR_LC><cod271_IR_LC>0</cod271_IR_LC><cod28_IR_LC>0</cod28_IR_LC><cod29_IR_LC>0</cod29_IR_LC><cod35_IR_LC>0</cod35_IR_LC><cod47_IR_LC>0</cod47_IR_LC><cod48_IR_LC>0</cod48_IR_LC><cod49_IR_LC>0</cod49_IR_LC><cod50_IR_LC>0</cod50_IR_LC><cod51_IR_LC>0</cod51_IR_LC><cod52_IR_LC>0</cod52_IR_LC><cod53_IR_LC>0</cod53_IR_LC><cod60_IR_LC>0</cod60_IR_LC></reg_IR_LC></IR_LC></IDTE_LC>'
                        ##Envio de libro de compras a procesar a IDTE---------------------------------------------------

                        try:
                            procesar_libro_ventas = procesar_lcv_xml(client, id_dte_empresa, tipo_libro,
                                                                     id_hist_lcv,
                                                                     accion, nievel_traza, xml_libro.decode())

                            if procesar_libro_ventas.dio_error == False:

                                ##Consultar estado Libro ventas---------------------------------------------------------

                                estado_libro_enviado = get_estado_lcv(client, id_dte_empresa, id_hist_lcv,
                                                                      nievel_traza)

                                if estado_libro_enviado.valor != "Error":
                                    datos_estado    = get_estado_lcv.valor.split('|')
                                    estado_sii      = datos_estado[6]
                                    msg_sii         = datos_estado[7]

                                    if int(estado_sii) == 1:
                                        error = "Libro no enviado"
                                    elif int(estado_sii) == 3:
                                        error = "Libro enviado sin estado"
                                    elif int(estado_sii) == 5:
                                        error = "Libro aceptado"
                                    elif int(estado_sii) == 6:
                                        error = "Libro Rechazado"

                                    data = {
                                        'success'           : True,
                                        'error'             : '',
                                        'estado_sii'        : estado_sii,
                                        'descripcion_estado': error,
                                        'msg_sii'           : msg_sii,
                                        'tipo_error'        : '',
                                        'funcion_error'     : 'get_estado_lcv',
                                    }
                                    return data
                                else:
                                    data = {
                                        'success'           : False,
                                        'error'             : estado_libro_enviado.msg,
                                        'estado_sii'        : '',
                                        'descripcion_estado': '',
                                        'msg_sii'           : '',
                                        'tipo_error'        : '',
                                        'funcion_error'     : 'get_estado_lcv',
                                    }
                                    return data
                            else:
                                data = {
                                    'success'           : False,
                                    'error'             : procesar_libro_ventas.msg,
                                    'estado_sii'        : '',
                                    'descripcion_estado': '',
                                    'msg_sii'           : '',
                                    'tipo_error'        : procesar_libro_ventas.tipo_error,
                                    'funcion_error'     : 'procesar_lcv_xml',
                                }
                                return data
                        except suds.WebFault as e:
                            data = {
                                'success'           : False,
                                'error'             : str(e),
                                'estado_sii'        : '',
                                'descripcion_estado': '',
                                'msg_sii'           : '',
                                'tipo_error'        : 'Error de Excepción Try Except',
                                'funcion_error'     : 'procesar_lcv_xml',
                            }
                        return data
                    else:
                        datos_estado    = estado_libro.valor.split('|')
                        estado_sii      = datos_estado[6]
                        msg_sii         = datos_estado[7]

                        if int(estado_sii) == 1:
                            error = "Libro no enviado"
                        elif int(estado_sii) == 3:
                            error = "Libro enviado sin estado"
                        elif int(estado_sii) == 5:
                            error = "Libro aceptado"
                        elif int(estado_sii) == 6:
                            error = "Libro Rechazado"

                        data = {
                            'success'           : False,
                            'error'             : error,
                            'estado_sii'        : estado_sii,
                            'descripcion_estado': '',
                            'msg_sii'           : msg_sii,
                            'tipo_error'        : '',
                            'funcion_error'     : 'get_estado_lcv',
                        }
                        return data
                else:
                    data = {
                        'success'           : False,
                        'error'             : error,
                        'estado_sii'        : '',
                        'descripcion_estado': '',
                        'msg_sii'           : '',
                        'tipo_error'        : 'Conexión Servidor',
                        'funcion_error'     : 'call_service',
                    }

                    return data
            else:
                data = {
                    'success'           : False,
                    'error'             : error_url,
                    'estado_sii'        : '',
                    'descripcion_estado': '',
                    'msg_sii'           : '',
                    'tipo_error'        : 'Armado URL',
                    'funcion_error'     : 'url_web_service',
                    'ruta_archivo'      : '',
                }

                return data
        else:
            data = {
                'success'           : False,
                'error'             : error,
                'estado_sii'        : '',
                'descripcion_estado': '',
                'msg_sii'           : '',
                'tipo_error'        : 'Obtención Datos',
                'funcion_error'     : 'obtener_datos_conexion',
            }

            return data
    else:
        data = {
            'success'           : False,
            'error'             : error_creacion,
            'estado_sii'        : '',
            'descripcion_estado': '',
            'msg_sii'           : '',
            'tipo_error'        : 'Error Lectura',
            'funcion_error'     : 'crear_xml_libro_compra',
        }
        return data


## --------------------------- MANEJO DE CONTROL DE FOLIOS -------------------------------------------------------------

def prueba_control_folio():
    kwargs = {}
    lista_control_folio = list()
    lista_rango_utilizado = list()
    lista_rango_anulado = list()
    kwargs['fecha_emision'] = '2016-07-27'
    kwargs['secuencia'] = 1

    for a in range(1):
        data_control_folio = {
            'tipo_documento_cf':'39',
            'monto_neto_cf':'1000',
            'monto_iva_cf':'190',
            'tasa_iva_cf':'19',
            'monto_exento_cf':'0',
            'monto_total_cf':'1190',
            'folios_emitidos_cf':'334',
            'folios_anulados_cf':'100',
            'folios_utilizados_cf':'434',
        }
        lista_control_folio.append(data_control_folio)

    kwargs['control_folios'] = lista_control_folio


    for b in range(1):
        data_utilizado = {
            'id_rango_utilizado':'1',
            'tipo_doc_rango_util':'39',
            'folio_inicial_rango_util':'1',
            'folio_final_rango_util':'300',
        }
        lista_rango_utilizado.append(data_utilizado)


    kwargs['rango_utilizado'] = lista_rango_utilizado


    for c in range(1):
        data_anulado = {
            'id_rango_anulado':'1',
            'tipo_doc_rango_a':'39',
            'folio_inicial_rango_a':'1',
            'folio_final_rango_a':'50',
        }
        lista_rango_anulado.append(data_anulado)

    kwargs['rango_anulado'] = lista_rango_anulado


    respuesta = envio_control_folios(**kwargs)

def envio_control_folios(**kwargs):
    """
        función que permite realizar el control de folios diario de los documentos emitidos. esta recibe un diccionario
        con la data a procesar. Esta debe incluir la fecha de emision del control de folios y una secuencia que van hacer
        parte de la clave primaria cuando se almacene el registro en las tablas de IDTE.

        Esta funcion retorna un objeto el cual contiene un estado del proceso, el error, el nombre de la funcion donde se
        origino, el tipo de error, estado el s.i.i., descripcion del estado y el mensaje del s.i.i. en caso de rechazar
        el control de folios enviado.

        data = {
            'success': True,
            'error': '',
            'estado_sii': estado_sii,
            'descripcion_estado': error,
            'msg_sii': msg_sii,
            'tipo_error': '',
            'funcion_error': 'get_estado_cf',
        }

    :param kwargs: data del control de folios.
    """
    ##Variables --------------------------------------------------------------------------------------------------------

    nievel_traza    = 2  # Nivel completo de traza de Error
    id_dte_empresa  = ''
    accion          = 1  # Procesar y enviar control de folios
    datos_conexion  = {}
    fecha_emision   = kwargs['fecha_emision'] #fecha emision control de folios
    secuencia       = kwargs['secuencia'] # secuencia de control de folios

    ##Creacion de xml---------------------------------------------------------------------------------------------------
    error_creacion, xml_control_folios = crear_xml_control_folios(**kwargs)

    if not error_creacion:
        ##Obtener datos de conexion IDTE -------------------------------------------------------------------------------
        error, conexion = obtener_datos_conexion('wsMIXTO')

        if not error:
            datos_conexion['codigo_contexto']   = conexion.codigo_contexto
            datos_conexion['host']              = conexion.host
            datos_conexion['url']               = conexion.url
            datos_conexion['puerto']            = conexion.puerto

            id_dte_empresa          = conexion.parametro_facturacion.codigo_conexion
            error_url, url_conexion = url_web_service(**datos_conexion)

            if not error_url:

                ## Conectarse a Web Service de IDTE---------------------------------------------------------------------

                error, client = call_service(url_conexion)

                if not error:

                    ##Consultar estado control de folios ---------------------------------------------------------------
                    try:
                        estado_control_folio = get_estado_cf(client, id_dte_empresa, fecha_emision, secuencia, nievel_traza)
                        print(estado_control_folio)

                        if estado_control_folio.valor == "ERROR":

                            ##Envio de control de folios a IDTE-------------------------------------------------------------

                            try:
                                procesar_control_folio = procesar_cf_xml(client, id_dte_empresa, fecha_emision, secuencia,
                                                                         accion, nievel_traza, xml_control_folios)

                                print(procesar_control_folio)

                                if procesar_control_folio.dio_error == False:

                                    ##Consultar estado control de folios ---------------------------------------------------
                                    try:
                                        estado_control_folio_enviado = get_estado_cf(client, id_dte_empresa, fecha_emision,
                                                                                     secuencia, nievel_traza)

                                        print(estado_control_folio_enviado)

                                        if estado_control_folio_enviado.valor != "Error":
                                            datos_estado    = estado_control_folio_enviado.valor.split('|')
                                            estado_sii      = datos_estado[1]
                                            msg_sii         = datos_estado[3]

                                            if int(estado_sii) == 1:
                                                error = "Control Folios no enviado"
                                            elif int(estado_sii) == 3:
                                                error = "Control Folios enviado sin estado"
                                            elif int(estado_sii) == 5:
                                                error = "Control Folios Aceptado"
                                            elif int(estado_sii) == 6:
                                                error = "Control Folios Rechazado"
                                            else:
                                                error = "Estado desconocido"

                                            data = {
                                                'success'           : True,
                                                'error'             : '',
                                                'estado_sii'        : estado_sii,
                                                'descripcion_estado': error,
                                                'msg_sii'           : msg_sii,
                                                'tipo_error'        : '',
                                                'funcion_error'     : 'get_estado_cf',
                                            }
                                            return data
                                        else:
                                            data = {
                                                'success'           : False,
                                                'error'             : estado_control_folio_enviado.msg,
                                                'estado_sii'        : '',
                                                'descripcion_estado': '',
                                                'msg_sii'           : '',
                                                'tipo_error'        : '',
                                                'funcion_error'     : 'get_estado_cf',
                                            }
                                            return data
                                    except suds.WebFault as a:
                                        error = a.args[0].decode("utf-8")
                                        data = {
                                            'success'           : False,
                                            'error'             : error,
                                            'estado_sii'        : '',
                                            'descripcion_estado': '',
                                            'msg_sii'           : '',
                                            'tipo_error'        : 'Error de Excepción Try Except',
                                            'funcion_error'     : 'get_estado_cf',
                                        }
                                        return data
                                else:
                                    data = {
                                        'success'           : False,
                                        'error'             : procesar_control_folio.msg,
                                        'estado_sii'        : '',
                                        'descripcion_estado': '',
                                        'msg_sii'           : '',
                                        'tipo_error'        : procesar_control_folio.tipo_error,
                                        'funcion_error'     : 'procesar_cf_xml',
                                    }
                                    return data
                            except suds.WebFault as e:
                                error = e.args[0].decode("utf-8")
                                data = {
                                    'success'           : False,
                                    'error'             : error,
                                    'estado_sii'        : '',
                                    'descripcion_estado': '',
                                    'msg_sii'           : '',
                                    'tipo_error'        : 'Error de Excepción Try Except',
                                    'funcion_error'     : 'procesar_cf_xml',
                                }
                            return data
                        else:
                            datos_estado    = estado_control_folio.valor.split('|')
                            estado_sii      = datos_estado[1]
                            msg_sii         = datos_estado[3]

                            if int(estado_sii) == 1:
                                error = "Control Folios no enviado"
                            elif int(estado_sii) == 3:
                                error = "Control Folios enviado sin estado"
                            elif int(estado_sii) == 5:
                                error = "Control Folios Aceptado"
                            elif int(estado_sii) == 6:
                                error = "Control Folios Rechazado"
                            else:
                                error = "Estado desconocido"

                            data = {
                                'success'           : False,
                                'error'             : error,
                                'estado_sii'        : estado_sii,
                                'descripcion_estado': '',
                                'msg_sii'           : msg_sii,
                                'tipo_error'        : '',
                                'funcion_error'     : 'get_estado_cf',
                            }
                            return data
                    except suds.WebFault as e:
                        error = e.args[0].decode("utf-8")
                        data = {
                            'success'           : False,
                            'error'             : error,
                            'estado_sii'        : '',
                            'descripcion_estado': '',
                            'msg_sii'           : '',
                            'tipo_error'        : 'Error de Excepción Try Except',
                            'funcion_error'     : 'get_estado_cf',
                        }
                        return data
                else:
                    data = {
                        'success'           : False,
                        'error'             : error,
                        'estado_sii'        : '',
                        'descripcion_estado': '',
                        'msg_sii'           : '',
                        'tipo_error'        : 'Conexión Servidor',
                        'funcion_error'     : 'call_service',
                    }

                    return data
            else:
                data = {
                    'success'           : False,
                    'error'             : error_url,
                    'estado_sii'        : '',
                    'descripcion_estado': '',
                    'msg_sii'           : '',
                    'tipo_error'        : 'Armado URL',
                    'funcion_error'     : 'url_web_service',
                    'ruta_archivo'      : '',
                }

                return data
        else:
            data = {
                'success'           : False,
                'error'             : error,
                'estado_sii'        : '',
                'descripcion_estado': '',
                'msg_sii'           : '',
                'tipo_error'        : 'Obtención Datos',
                'funcion_error'     : 'obtener_datos_conexion',
            }

            return data
    else:
        data = {
            'success'           : False,
            'error'             : error_creacion,
            'estado_sii'        : '',
            'descripcion_estado': '',
            'msg_sii'           : '',
            'tipo_error'        : 'Error Lectura',
            'funcion_error'     : 'crear_xml_control_folios',
        }
        return data

def consulta_estado_control_folios(fecha_emision, secuencia):
    """
        función que permite realizar la consulta del estado del control de folio según lo indicado por el s.i.i.
        Esta funcion retorna un objeto el cual contiene el estado del proceso realizado, el error en caso de ocurrencia,
        estado del control de folios segun s.i.i., descripcion del estado, mensaje de s.i.i. en caso de ser rechazado
        por el s.i.i el control de folios, el tipo de error y la funcion donde ocurrio dicho error.

        data = {
            'success': False,
            'error': estado_control_folios.msg,
            'funcion': 'get_estado_cf',
            'estado_sii': '',
            'msg_sii': '',
        }

    :param fecha_emision: fecha de emision del control de folios (dato string formato Y-M-D)
    :param secuencia: la secuencia asignada al control de folios. dato numerico
    """
    ##Variables --------------------------------------------------------------------------------------------------------
    nievel_traza    = 2  # Nivel completo de traza de Error
    id_dte_empresa  = ''
    datos_conexion  = {}

    ##Obtener datos de conexion IDTE -----------------------------------------------------------------------------------
    error, conexion = obtener_datos_conexion('wsMIXTO')

    if not error:
        datos_conexion['codigo_contexto']   = conexion.codigo_contexto
        datos_conexion['host']              = conexion.host
        datos_conexion['url']               = conexion.url
        datos_conexion['puerto']            = conexion.puerto

        id_dte_empresa = conexion.parametro_facturacion.codigo_conexion
        error_url, url_conexion = url_web_service(**datos_conexion)

        if not error_url:

            ## Conectarse a Web Service de IDTE-------------------------------------------------------------------------

            error, client = call_service(url_conexion)

            if not error:

                ##Consultar estado Control de folios -------------------------------------------------------------------
                try:
                    estado_control_folios = get_estado_cf(client, id_dte_empresa, fecha_emision, secuencia, nievel_traza)

                    if estado_control_folios.valor == "ERROR":
                        data = {
                            'success'   : False,
                            'error'     : estado_control_folios.msg,
                            'funcion'   : 'get_estado_cf',
                            'estado_sii': '',
                            'msg_sii'   : '',
                        }
                        return data
                    else:
                        datos_estado    = estado_control_folios.valor.split('|')
                        estado_sii      = datos_estado[1]
                        msg_sii         = datos_estado[3]

                        if int(estado_sii) == 1:
                            error = "Control Folios no enviado"
                        elif int(estado_sii) == 3:
                            error = "Control Folios enviado sin estado"
                        elif int(estado_sii) == 5:
                            error = "Control Folios Aceptado"
                        elif int(estado_sii) == 6:
                            error = "Control Folios Rechazado"
                        else:
                            error = "Estado desconocido"

                        data = {
                            'success'               : True,
                            'error'                 : '',
                            'estado_sii'            : estado_sii,
                            'descripcion_estado'    : error,
                            'msg_sii'               : msg_sii,
                            'tipo_error'            : '',
                            'funcion_error'         : 'get_estado_cf',
                        }
                        return data
                except suds.WebFault as e:
                    error = e.args[0].decode("utf-8")
                    data = {
                        'success'               : False,
                        'error'                 : error,
                        'estado_sii'            : '',
                        'descripcion_estado'    : '',
                        'msg_sii'               : '',
                        'tipo_error'            : 'Error de Excepción Try Except',
                        'funcion_error'         : 'get_estado_cf',
                    }
                    return data
            else:
                data = {
                    'success'           : False,
                    'error'             : error,
                    'estado_sii'        : '',
                    'descripcion_estado': '',
                    'msg_sii'           : '',
                    'tipo_error'        : 'Conexión Servidor',
                    'funcion_error'     : 'call_service',
                }

                return data
        else:
            data = {
                'success'           : False,
                'error'             : error_url,
                'estado_sii'        : '',
                'descripcion_estado': '',
                'msg_sii'           : '',
                'tipo_error'        : 'Armado URL',
                'funcion_error'     : 'url_web_service',
                'ruta_archivo'      : '',
            }

            return data
    else:
        data = {
            'success'               : False,
            'error'                 : error,
            'estado_sii'            : '',
            'descripcion_estado'    : '',
            'msg_sii'               : '',
            'tipo_error'            : 'Obtención Datos',
            'funcion_error'         : 'obtener_datos_conexion',
        }

        return data



##---------------------------- MANEJO DE FACTURACION LEASE -------------------------------------------------------------
def envio_factura_inet(request):

    datos_conexion  = {}
    resultado_xml   = armar_xml_inet(request)

    if not resultado_xml[0]:

        ##Obtener datos de conexion IDTE -------------------------------------------------------------------------------
        error, conexion = obtener_datos_conexion_ws_inet('axmldocvtaext')

        if not error:
            datos_conexion['codigo_contexto'] = conexion.codigo_contexto
            datos_conexion['host'] = conexion.host
            datos_conexion['url'] = conexion.url
            datos_conexion['puerto'] = conexion.puerto

            # Armar URL de conexion del Web Services -------------------------------------------------------------------
            resultado_url = url_web_service_inet(**datos_conexion)

            if not resultado_url[0]:

                ## Conectarse a Web Service de IDTE---------------------------------------------------------------------

                resultado_call = call_service_inet(resultado_url[1])

                if not resultado_call[0]:

                    try:
                        response_ws = envio_documento_inet(resultado_call[1], resultado_xml[1])
                        data = {
                            'success': True,
                            'error': '',
                            'respuesta': response_ws
                        }
                        return data


                    except suds.WebFault as w:
                        ##----------------------------------------------------------------------------------------------
                        error = w.args[0].decode("utf-8")
                        data = {
                            'success': False,
                            'error': error,
                        }

                        return data
                else:

                    ##--------------------------------------------------------------------------------------------------
                    data = {
                        'success'   : False,
                        'error'     : resultado_call[0],
                    }

                    return data
            else:

                ##------------------------------------------------------------------------------------------------------
                data = {
                    'success'   : False,
                    'error'     : resultado_url[0],
                }

                return data
        else:

            ##----------------------------------------------------------------------------------------------------------
            data = {
                'success': False,
                'error': error,
            }

            return data
    else:
        ##--------------------------------------------------------------------------------------------------------------
        data = {
            'success'   : False,
            'error'     : resultado_xml[0],
        }
        return data

def armar_dict_documento(request):
    #TODO cambiar giro de empresa

    try:

        ## Declaracion de variables Iniciales
        lista_cabecera      = list()
        lista_emisor        = list()
        lista_receptor      = list()
        lista_detalle       = list()
        lista_total         = list()
        lista_referencias   = list()
        error               = ''

        kwargs              = {}

        var_post    = request.POST.copy()
        factura_xml = Factura.objects.get(id=var_post['id'])

        profile = UserProfile.objects.get(user=request.user)
        empresa = Empresa.objects.get(id=profile.empresa_id)


        lista_cabecera.append({
            'fecha_emision'             : factura_xml.fecha_inicio.strftime('%Y-%m-%d'), ## fecha emision contable
            'ind_no_rebaja'             : str(0), ## Solo nota de credito
            'tipo_despacho'             : str(0), ## Acompaña despacho de productos por vendedor
            'indicador_traslado'        : str(0), ## Solo para guias de despacho
            'tipo_impresion'            : str(0), ## Modalidad de impresion N (Normal) o T (Ticket) Guia
            'indicador_servicio'        : str(0), ## Corresponde a prestación servicio
            'monto_bruto'               : str(0), ## Monto detalle son brutos (1 Si)  (0 No)
            'forma_pago'                : str(1), ## 1-Contado 2- Credito 3- Sin costo
            'forma_pago_exportacion'    : str(0), ## Solo factura exportacion
            'fecha_cancel'              : '',     ## Solo si la factura ha sido cancelada antes de la emisión
            'monto_cancel'              : str(0), ## Solo si la factura ha sido cancelada antes de la emisión
            'saldo_insoluto'            : str(0), ## Solo si la factura ha sido cancelada antes de la emisión
            'periodo_desde'             : '',     ## Fecha facturación servicios periodicos(fecha inicial del servicio)
            'periodo_hasta'             : '',     ## Fecha facturación servicios periodicos (fecha hasta del servicio)
            'medio_pago'                : 'EF',   ## Modalidad de pago CH- cheque CF: cheque fecha LT- letra EF- efectivo PE- pago Cta CTe TC- tarj cred OT- otro
            'tipo_cta_pago'             : '',     ## cuenta CT: cta cte TC: tarj. cred. OT: otra
            'numero_cta_pago'           : '',     ## numero cuenta cte
            'banco_pago'                : '',     ## Banco pago
            'termino_pago_codigo'       : '',     ## codigo acordado empresas, ind terminos de referencia fecha recep factura o fecha entrega mercaderia
            'termino_pago_glosa'        : '',     ## GLosa describe las condiciones de pago
            'termino_pago_dias'         : '',     ## Cant. dias termino pago
            'fecha_vecimiento'          : factura_xml.fecha_termino.strftime('%Y-%m-%d'), ##fecha vencimiento
            'rut_mandante'              : '',
            'rut_solicitante'           : '',
            'indicador_monto_neto'      : '0',
        })


        lista_emisor.append({
            'rut_emisor'                : str(empresa.rut).replace('.', '').upper(),
            'razon_social_emisor'       : str(empresa.nombre).upper(),
            'giro_emisor'               : str(empresa.giro.descripcion), #'ARRIENDO DE INMUEBLES AMOBLADOS O CON EQUIPOS Y MAQUINARIAS',
            'telefono_emisor'           : str(empresa.telefono),
            'correo_emisor'             : str(empresa.email),
            'acteco'                    : str(empresa.giro.codigo),  #'701001'
            'codigo_traslado'           : '0',
            'folio_autorizado'          : '0',
            'fecha_autorizacion'        : '0',
            'sucursal'                  : '',
            'codigo_sii_sucursal'       : '0',
            'codigo_adicional_suc'      : '',
            'direccion_emisor'          : str(empresa.direccion),
            'comuna_origen'             : str(empresa.comuna),
            'ciudad_origen'             : str(empresa.ciudad),
            'codigo_vendedor'           : '',
            'ident_adicional_emisor'    : '',
        })

        lista_receptor.append({
            'rut_receptor'              : str(factura_xml.contrato.cliente.rut).replace('.', '').upper(),
            'codigo_interno_receptor'   : str(factura_xml.contrato.cliente.rut).replace('.', '').upper(),
            'razon_receptor'            : str(factura_xml.contrato.cliente.razon_social).upper(),
            'num_ident_extranjero'      : '',
            'nacionalidad'              : '',
            'ident_adicional_receptor'  : '',
            'giro_receptor'             : str(factura_xml.contrato.cliente.giro).upper(),
            'contacto_receptor'         : '',
            'correo_receptor'           : str(factura_xml.contrato.cliente.email),
            'direccion_receptor'        : str(factura_xml.contrato.cliente.direccion).upper(),
            'comuna_receptor'           : str(factura_xml.contrato.cliente.comuna).upper(),
            'cuidad_receptor'           : str(factura_xml.contrato.cliente.ciudad).upper(),
            'direccion_postal'          : '',
            'comuna_postal'             : '',
            'cuidad_postal'             : '',
        })


        detalle = factura_xml.factura_detalle_set.all()

        linea       = 1
        total_linea = 0

        for d in detalle:

            lista_detalle.append({
                'nro_linea'                 : str(linea),
                'tipo_documento_liq'        : '',
                'ind_exencion'              : '0',
                'nombre_item'               : str(d.concepto.nombre).upper(),
                'descripcion_item'          : str(d.concepto.descripcion).upper(),
                'cantidad_referencia'       : '1',
                'unidad_medida_ref'         : '',#str(d.concepto)
                'precio_referencia'         : formato_numero_sin_miles(d.total),
                'cantidad_item'             : '1',
                'fecha_elaboracion'         : '',
                'fecha_vencimiento_prod'    : '',
                'unidad_medida'             : 'UNI',
                'precio_unitario'           : formato_numero_sin_miles(d.total),
                'descuento_porcentaje'      : '0',
                'descuento_monto'           : '0',
                'recargo_porcentaje'        : '0',
                'recargo_monto'             : '0',
                'cod_imp_adic_1'            : '0',
                'cod_imp_adic_2'            : '0',
                'monto_item'                : formato_numero_sin_miles(d.total),
                'item_espectaculo'          : '',
                'rut_mandante_b'            : '',
                'codigos_items'             : '',  # lista_codigos_items,
                'info_ticket'               : '',  # lista_infoticket
                'otras_monedas_detalle'     : '',  # lista_otra_moneda_detalle
                'retenedor_detalle'         : '',  # lista_retenedor_detalle
                'subdescuentos_detalle'     : '',  # lista_subdescuento,
                'subcantidad_detalle'       : '',  # lista_subcantidad
                'subrecargo_detalle'        : '',  # lista_subrecargo,
            })

            total_linea += d.total
            linea       += 1

        valores = calculo_iva_total_documento(total_linea, 19)

        lista_total.append({
            'tipo_moneda'           : '',           ##Tipo de moneda de los montos
            'monto_neto'            : valores[0],   ## Monto neto
            'monto_exento'          : '0',          ## Monto exento
            'monto_base'            : '0',          ## Monto Informado >0
            'monto_margen_comerc'   : '0',          ## Monto informado
            'tasa_iva'              : '19',         ## Tasa iva
            'iva'                   : valores[1],     ## Monto neto * tasa IVA
            'iva_propio'            : '0',          ## < que IVA
            'iva_terceros'          : '0',          ## < que IVA
            'iva_no_retenido'       : '0',          ## IVA - IVA retenido
            'cred_espec_constr'     : '0',          ## IVA * 0,65
            'garan_deposi_env_embal': '0',          ## Solo empresas usan emvases
            'valor_comision_neto'   : '0',          ## Suma detalles valores comision
            'valor_comision_exento' : '0',          ## Suma detalles valores comisiones y otros cargos no afectos o exentos
            'valor_comision_iva'    : '0',          ## Suma detalle iva valor comision y otros cargos
            'monto_total'           : valores[2], ## Monto total documento
            'monto_no_facturable'   : '0',          ## Suma monto bienes o servicios con indicador facturacion
            'monto_periodo'         : '0',          ## Monto total + monto no facturable
            'saldo_anterior'        : '0',          ## Saldo anterior. * Solo con fines de ilustrar claridad de cobros
            'valor_pagar'           : '0',          ## Valor cobrado
            'impuesto_retenido'     : '',           ## lista_impuesto_retenidos,
        })



        kwargs['tipo_documento']            = factura_xml.numero_documento
        kwargs['aplicacion']                = 'lease'
        kwargs['ID1_ERP']                   = ''
        kwargs['ID2_ERP']                   = ''
        kwargs['ID3_ERP']                   = ''
        kwargs['ID4_ERP']                   = ''
        kwargs['emails_PDF']                = factura_xml.contrato.cliente.email
        kwargs['emails_XML']                = factura_xml.contrato.cliente.email

        kwargs['encabezado']                = lista_cabecera
        kwargs['emisor']                    = lista_emisor
        kwargs['receptor']                  = lista_receptor
        kwargs['detalle']                   = lista_detalle
        kwargs['totales']                   = lista_total
        kwargs['recargos_globales']         = ''  # lista_recargos
        kwargs['referencias_documentos']    = ''  # lista_referencias
        kwargs['referencias_boletas']       = ''  # lista_referencias_boletas
        kwargs['comisiones']                = ''  # lista_comisiones
        kwargs['monto_pagos']               = ''  # lista_monto_pagos
        kwargs['otra_moneda']               = ''  # lista_otra_moneda
        kwargs['subtotales']                = ''  # lista_subtotales
        kwargs['transporte']                = ''  # lista_transporte
        kwargs['extra_documento']           = ''  # lista_extra_documento
        kwargs['error']                     = error


    except Exception as e:
        kwargs['error'] = str(e)

    return kwargs



