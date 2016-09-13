from django.db import transaction
from suds.client import Client
from xml.etree.ElementTree import *
from facturacion.models import FoliosDocumentosElectronicos, ConexionFacturacion

import xml.etree.ElementTree as etree
import sys
import os
import suds



suds_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(suds_path)


def obtener_datos_conexion(url):
    """
        función que permite realizar la obtención de los parametros de conexión para un web service
        determinado de IDTE
    :param url: recibe la url
    :return: retorna un objeto con los datos de conexión
    """
    error = ''
    conexion = ''

    try:
        conexion = ConexionFacturacion.objects.get(url__iexact=url)
    except Exception as e:
        error = "No existen datos de conexión "+str(url)+" del servidor de IDTE."

    return error, conexion

def call_service(url):
    """
        esta funcion realiza la conexión con el servidor que contiene los Web Services de IDTE.
    :param url: url de conexión del WSDL
    :return: retorna el client con la conexion y una variable de error.
    """
    error = ''
    client = ''

    try:
        client = Client(url, timeout=5)
    except suds.WebFault as detail:
        error = str(detail.fault)
    except Exception as e:
        error = "No se pudo realizar la conexion con el servidor de IDTE, por favor verifique los datos."

    return error, client

def crear_xml_documento(**kwargs):

    """
        función que permite realizar el armado del xml a enviar al web service de procesar_dte_xml de IDTE.
    :param kwargs: recibe un diccionario con la data a incorporar al xml
    :return: retorna el xml parseado en string
    """
    xml     = ''
    error   = ''
    idte    = Element('IDTE_DOC')

    # General-----------------------------------------------------------------------------------------------------------
    general = Element('General')
    idte.append(general)


    # Add hijos general
    try:
        tipo_dte    = SubElement(general, 'tipo_dte').text   = kwargs['tipo_documento']
        folio       = SubElement(general, 'folio_dte').text  = kwargs['folio']
        id1_erp     = SubElement(general, 'ID1_ERP').text    = kwargs['ID1_ERP']
        id2_erp     = SubElement(general, 'ID2_ERP').text    = kwargs['ID2_ERP']
        id3_erp     = SubElement(general, 'ID3_ERP').text    = kwargs['ID3_ERP']
        id4_erp     = SubElement(general, 'ID4_ERP').text    = kwargs['ID4_ERP']
        email_pdf   = SubElement(general, 'emails_PDF').text = kwargs['emails_PDF']
        email_xml   = SubElement(general, 'emails_XML').text = kwargs['emails_XML']
    except Exception as e:
        error ="General: no se encuentra dato " +str(e.args[0]).strip()+" en el diccionario enviado."
        return error, xml

    # Encabezado--------------------------------------------------------------------------------------------------------
    try:
        encabezado = kwargs['encabezado']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if encabezado:
        cabecera = Element('Cabecera')
        idte.append(cabecera)

        # Add hijos cabeceza

        for a in encabezado:
            try:
                fecha_emision       = SubElement(cabecera, 'FchEmis').text          = a['fecha_emision']
                indNoRebaja         = SubElement(cabecera, 'IndNoRebaja').text      = a['ind_no_rebaja']
                tipo_despacho       = SubElement(cabecera, 'TipoDespacho').text     = a['tipo_despacho']
                indicador_traslado  = SubElement(cabecera, 'IndTraslado').text      = a['indicador_traslado']
                tipo_impresion      = SubElement(cabecera, 'TpoImpresion').text     = a['tipo_impresion']
                indicador_servicio  = SubElement(cabecera, 'IndServicio').text      = a['indicador_servicio']
                monto_bruto         = SubElement(cabecera, 'MntBruto').text         = a['monto_bruto']
                forma_pago          = SubElement(cabecera, 'FmaPago').text          = a['forma_pago']
                forma_pago_exp      = SubElement(cabecera, 'FmaPagExp').text        = a['forma_pago_exportacion']
                fecha_cancel        = SubElement(cabecera, 'FchCancel').text        = a['fecha_cancel']
                monto_cancel        = SubElement(cabecera, 'MntCancel').text        = a['monto_cancel']
                saldo_insol         = SubElement(cabecera, 'SaldoInsol').text       = a['saldo_insoluto']
                periodo_desde       = SubElement(cabecera, 'PeriodoDesde').text     = a['periodo_desde']
                periodo_hasta       = SubElement(cabecera, 'PeriodoHasta').text     = a['periodo_hasta']
                medio_pago          = SubElement(cabecera, 'MedioPago').text        = a['medio_pago']
                tipo_cta_pago       = SubElement(cabecera, 'TipoCtaPago').text      = a['tipo_cta_pago']
                numero_cta_pago     = SubElement(cabecera, 'NumCtaPago').text       = a['numero_cta_pago']
                banco_pago          = SubElement(cabecera, 'BcoPago').text          = a['banco_pago']
                termino_pago_codigo = SubElement(cabecera, 'TermPagoCdg').text      = a['termino_pago_codigo']
                temino_pago_glosa   = SubElement(cabecera, 'TermPagoGlosa').text    = a['termino_pago_glosa']
                termino_pago_dias   = SubElement(cabecera, 'TermPagoDias').text     = a['termino_pago_dias']
                fecha_vencimiento   = SubElement(cabecera, 'FchVenc').text          = a['fecha_vecimiento']
                rut_mandante        = SubElement(cabecera, 'RUTMandante').text      = a['rut_mandante']
                rut_solicitante     = SubElement(cabecera, 'RUTSolicita').text      = a['rut_solicitante']
                indicador_monto_neto = SubElement(cabecera, 'IndMntNeto').text      = a['indicador_monto_neto']
            except Exception as e:
                error ="Cabeceza: no se encuentra dato " +str(e.args[0]).strip()+" en el diccionario enviado."
                return error, xml

    # Emisor------------------------------------------------------------------------------------------------------------

    try:
        emisor_datos = kwargs['emisor']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if emisor_datos:
        emisor = Element('Emisor')
        idte.append(emisor)

        # add hijos emisor

        for b in emisor_datos:
            try:
                rut_emisor              = SubElement(emisor, 'RUTEmisor').text      = b['rut_emisor']
                razon_social_emisor     = SubElement(emisor, 'RznSoc').text         = b['razon_social_emisor']
                giro_emisor             = SubElement(emisor, 'GiroEmis').text       = b['giro_emisor']
                telefono_emisor         = SubElement(emisor, 'Telefono').text       = b['telefono_emisor']
                correo_emisor           = SubElement(emisor, 'CorreoEmisor').text   = b['correo_emisor']
                acteco                  = SubElement(emisor, 'Acteco').text         = b['acteco']
                codigo_emisor_traslado  = SubElement(emisor, 'CdgTraslado').text    = b['codigo_traslado']
                folio_autorizado        = SubElement(emisor, 'FolioAut').text       = b['folio_autorizado']
                fecha_autorizacion      = SubElement(emisor, 'FchAut').text         = b['fecha_autorizacion']
                sucursal                = SubElement(emisor, 'Sucursal').text       = b['sucursal']
                cod_sii_sucursal        = SubElement(emisor, 'CdgSIISucur').text    = b['codigo_sii_sucursal']
                codigo_adicional_suc    = SubElement(emisor, 'CodAdicSucur').text   = b['codigo_adicional_suc']
                dir_emisor              = SubElement(emisor, 'DirOrigen').text      = b['direccion_emisor']
                comuna_origen           = SubElement(emisor, 'CmnaOrigen').text     = b['comuna_origen']
                ciudad_origen           = SubElement(emisor, 'CiudadOrigen').text   = b['ciudad_origen']
                codigo_vendedor         = SubElement(emisor, 'CdgVendedor').text    = b['codigo_vendedor']
                ident_adicional_emisor  = SubElement(emisor, 'IdAdicEmisor').text   = b['ident_adicional_emisor']
            except Exception as e:
                error = "Emisor: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                return error, xml


    # Receptor----------------------------------------------------------------------------------------------------------

    try:
        receptor_datos = kwargs['receptor']
    except Exception as e:
        error = "No se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if receptor_datos:
        receptor = Element('Receptor')
        idte.append(receptor)

        # Add hijos receptor

        for c in receptor_datos:
            try:
                rut_receptor                = SubElement(receptor, 'RUTRecep').text     = c['rut_receptor']
                codigo_interno_receptor     = SubElement(receptor, 'CdgIntRecep').text  = c['codigo_interno_receptor']
                razon_receptor              = SubElement(receptor, 'RznSocRecep').text  = c['razon_receptor']
                num_ident_extranjero        = SubElement(receptor, 'NumId').text        = c['num_ident_extranjero']
                nacionalidad                = SubElement(receptor, 'Nacionalidad').text = c['nacionalidad']
                ident_adicional_receptor    = SubElement(receptor, 'IdAdicRecep').text  = c['ident_adicional_receptor']
                giro_receptor               = SubElement(receptor, 'GiroRecep').text    = c['giro_receptor']
                contacto_receptor           = SubElement(receptor, 'Contacto').text     = c['contacto_receptor']
                correo_receptor             = SubElement(receptor, 'CorreoRecep').text  = c['correo_receptor']
                dir_receptor                = SubElement(receptor, 'DirRecep').text     = c['direccion_receptor']
                comuna_receptor             = SubElement(receptor, 'CmnaRecep').text    = c['comuna_receptor']
                cuidad_receptor             = SubElement(receptor, 'CiudadRecep').text  = c['cuidad_receptor']
                direccion_postal            = SubElement(receptor, 'DirPostal').text    = c['direccion_postal']
                comuna_postal               = SubElement(receptor, 'CmnaPostal').text   = c['comuna_postal']
                cuidad_postal               = SubElement(receptor, 'CiudadPostal').text = c['cuidad_postal']
            except Exception as e:
                error = "Receptor: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                return error, xml


    # Detalle-----------------------------------------------------------------------------------------------------------

    try:
        datos_detalle = kwargs['detalle']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if datos_detalle:
        detalle = Element('Detalle')
        idte.append(detalle)
        count_detalles = 0

        for d in datos_detalle:
            if count_detalles < 60:
                # detalles del documento---------------------------------------------------------
                registro_detalle = SubElement(detalle, 'reg_Detalle')

                # Add hijos de los detalles------------------------------------------------------
                try:
                    nro_linea               = SubElement(registro_detalle, 'NroLinDet').text        = d['nro_linea']
                    tipo_documento_liq      = SubElement(registro_detalle, 'TpoDocLiq').text        = d['tipo_documento_liq']
                    indicador_exencion      = SubElement(registro_detalle, 'IndExe').text           = d['ind_exencion']
                    nombre_item             = SubElement(registro_detalle, 'NmbItem').text          = d['nombre_item']
                    descripcion_item        = SubElement(registro_detalle, 'DescItem').text          = d['descripcion_item']
                    cantidad_referencia     = SubElement(registro_detalle, 'QtyRef').text           = d['cantidad_referencia']
                    unidad_referencia       = SubElement(registro_detalle, 'UnmdRef').text          = d['unidad_medida_ref']
                    precio_referencia       = SubElement(registro_detalle, 'PrcRef').text           = d['precio_referencia']
                    cantidad                = SubElement(registro_detalle, 'QtyItem').text          = d['cantidad_item']
                    fecha_elaboracion       = SubElement(registro_detalle, 'FchaElabor').text        = d['fecha_elaboracion']
                    fecha_vencimiento_prod  = SubElement(registro_detalle, 'FchVencim').text        = d['fecha_vencimiento_prod']
                    unidad_medida           = SubElement(registro_detalle, 'UnmdItem').text         = d['unidad_medida']
                    precio_unitario         = SubElement(registro_detalle, 'PrcItem').text          = d['precio_unitario']
                    descuento_porcentaje    = SubElement(registro_detalle, 'DescuentoPct').text     = d['descuento_porcentaje']
                    descuento_monto         = SubElement(registro_detalle, 'DescuentoMonto').text   = d['descuento_monto']
                    recargo_porcentaje      = SubElement(registro_detalle, 'RecargoPct').text       = d['recargo_porcentaje']
                    recargo_monto           = SubElement(registro_detalle, 'RecargoMonto').text     = d['recargo_monto']
                    impuesto_adicional1     = SubElement(registro_detalle, 'CodImpAdic1').text      = d['cod_imp_adic_1']
                    impuesto_adicional2     = SubElement(registro_detalle, 'CodImpAdic2').text      = d['cod_imp_adic_2']
                    monto_item              = SubElement(registro_detalle, 'MontoItem').text        = d['monto_item']
                    item_espectaculo        = SubElement(registro_detalle, 'ItemEspectaculo').text  = d['item_espectaculo']
                    rut_mandante_b          = SubElement(registro_detalle, 'RUTMandanteB').text     = d['rut_mandante_b']

                    datos_item          = d['codigos_items']
                    datos_ticket        = d['info_ticket']
                    datos_otra_moneda   = d['otras_monedas_detalle']
                    datos_retenedor     = d['retenedor_detalle']
                    datos_subdescuento  = d['subdescuentos_detalle']
                    datos_subcantidad   = d['subcantidad_detalle']
                    datos_subrecargo    = d['subrecargo_detalle']

                except Exception as e:
                    error = "Detalle: no se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
                    return error, xml

                #Códigos de Items Detalles------------------------------------------------------------------------------

                if datos_item:
                    codigo_items_detalle    = SubElement(registro_detalle, 'CodItem')
                    count_item              = 1
                    for f in datos_item:
                        if count_item < 6: ##Se permiten 5 repeticiones de pares de códigos de items.

                            #Subhijos de códigos de Items---------------------------------------------------------------
                            registro_items      = SubElement(codigo_items_detalle, 'reg_CodItem')
                            try:
                                tipo_codigo_item    = SubElement(registro_items, 'TpoCodigo').text = f['tipo_codigo_item']
                                valor_codigo_item   = SubElement(registro_items, 'VlrCodigo').text = f['valor_codigo_item']
                            except Exception as e:
                                error = "Detalle-Codigo Items: no se encuentra dato " +str(e.args[0]).strip()+ \
                                        " en el diccionario enviado."
                                return error, xml

                            count_item +=1

                # Info Ticket Detalles----------------------------------------------------------------------------------
                if datos_ticket:
                    info_ticket_detalle = SubElement(registro_detalle, 'InfoTicket')

                    count_ticket   = 1
                    for t in datos_ticket:
                        if count_ticket <2:
                            try:
                                folio_ticket        = SubElement(info_ticket_detalle, 'FolioTicket').text       = t['folio_ticket']
                                fecha_genera        = SubElement(info_ticket_detalle, 'FchGenera').text         = t['fecha_genera']
                                numero_evento       = SubElement(info_ticket_detalle, 'NmbEvento').text         = t['numero_evento']
                                tipo_ticket         = SubElement(info_ticket_detalle, 'TpoTiket').text          = t['tipo_ticket']
                                codigo_evento       = SubElement(info_ticket_detalle, 'CdgEvento').text         = t['codigo_evento']
                                fecha_evento        = SubElement(info_ticket_detalle, 'FchEvento').text         = t['fecha_evento']
                                lugar_evento        = SubElement(info_ticket_detalle, 'LugarEvento').text       = t['lugar_evento']
                                ubicacion_evento    = SubElement(info_ticket_detalle, 'UbicEvento').text        = t['ubicacion_evento']
                                fila_ubic_evento    = SubElement(info_ticket_detalle, 'FilaUbicEvento').text    = t['fila_ubic_evento']
                                asiento_ubic_evento = SubElement(info_ticket_detalle, 'AsntoUbicEvento').text   = t['asiento_ubic_evento']
                            except Exception as b:
                                error ="Detalle-Info Ticket: no se encuentra dato " +str(b.args[0]).strip()+ " en el diccionario enviado."
                                return error, xml
                            count_ticket +=1


                # Otra Moneda Detalles--------------------------------------------------------------------------------------

                if datos_otra_moneda:
                    otra_moneda         = SubElement(registro_detalle, 'OtrMnda')
                    count_otra_moneda   = 1

                    for m in datos_otra_moneda:
                        if count_otra_moneda <3: ##Se permite solo 2 repeticiones de otras moneda en detalles

                            #Subhijos otra Moneda---------------------------------------------------------------------------

                            registro_otra_moneda_detalle = SubElement(otra_moneda, 'reg_OtrMnda')

                            try:
                                precio_otra_moneda      = SubElement(otra_moneda, 'PrcOtrMon').text         = m['precio_otra_moneda']
                                moneda                  = SubElement(otra_moneda, 'Moneda').text            = m['moneda']
                                factor_conversion       = SubElement(otra_moneda, 'FctConv').text           = m['factor_conversion']
                                descuento_otra_moneda   = SubElement(otra_moneda, 'DctoOtrMnda').text       = m['descuento_otra_moneda']
                                recargo_otra_moneda     = SubElement(otra_moneda, 'RecargoOtrMnda').text    = m['recarg_otra_moneda']
                                monto_item_otra         = SubElement(otra_moneda, 'MontoItemOtrMnd').text   = m['monto_item_otra_moneda']
                            except Exception as e:
                                error = "Detalle-Otra moneda: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                                return error, xml

                            count_otra_moneda +=1


                # Retenedor Detalles----------------------------------------------------------------------------------------

                if datos_retenedor:

                    retenedor = SubElement(registro_detalle, 'Retenedor')
                    count_retenedor = 1

                    for r in datos_retenedor:
                        if count_retenedor <2: #Se permite solo 1 repeticion de retenedor de detalles

                            #Subhijos retenedor-----------------------------------------------------------------------------
                            try:
                                indicador_agente        = SubElement(retenedor, 'IndAgente').text     = r['indicador_agente']
                                monto_base_faena        = SubElement(retenedor, 'MntBaseFaena').text  = r['monto_base_faena']
                                monto_margen_comercial  = SubElement(retenedor, 'MntMargComer').text  = r['monto_margen_comercial']
                                precio_consumidor_final = SubElement(retenedor, 'PrcConsFinal').text  = r['precio_consumidor_final']
                            except Exception as e:
                                error = "Detalle-Retenedor: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                                return error, xml

                            count_retenedor +=1


                # SubDescuento Detalles---------------------------------------------------------------------------------

                if datos_subdescuento:

                    subdescuento_detalle    = SubElement(registro_detalle, 'SubDscto')
                    count_subdscto          = 1
                    for f in datos_subdescuento:
                        if count_subdscto < 6: ##Se permiten 5 repeticiones de pares de SubDscto.

                            #Subhijos de subdescuento ------------------------------------------------------------------
                            registro_subdscto      = SubElement(subdescuento_detalle, 'reg_SubDscto')
                            try:
                                id_subdscto  = SubElement(registro_subdscto, 'IdSubDscto').text = f['id_dscto']
                                tipo_dscto   = SubElement(registro_subdscto, 'TipoDscto').text  = f['tipo_dscto']
                                valor_dscto  = SubElement(registro_subdscto, 'ValorDscto').text = f['valor_dscto']
                            except Exception as e:
                                error = "Detalle- SubDescuento: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                                return error, xml

                            count_subdscto +=1

                # SubCantidad Detalles---------------------------------------------------------------------------------

                if datos_subcantidad:

                    subcantidad_detalle = SubElement(registro_detalle, 'Subcantidad')
                    count_subcantidad = 1
                    for c in datos_subcantidad:
                        if count_subcantidad < 6:  ##Se permiten 5 repeticiones de pares de SubCantidad.

                            # Subhijos de subcantidad ------------------------------------------------------------------
                            registro_subcantidad = SubElement(subcantidad_detalle, 'reg_Subcantidad')
                            try:
                                id_subcantidad          = SubElement(registro_subcantidad, 'idSubcantidad').text    = c['id_subcantidad']
                                subcantidad             = SubElement(registro_subcantidad, 'SubQty').text           = c['subcantidad']
                                subcodigo               = SubElement(registro_subcantidad, 'Subcod').text           = c['subcodigo']
                                tipo_cod_subcantidad    = SubElement(registro_subcantidad, 'TipCodSubQty').text     = c['tipo_cod_subcantidad']
                            except Exception as a:
                                error = "Detalle- SubCantidad: no se encuentra dato " + str(a.args[0]).strip() + \
                                        " en el diccionario enviado."
                                return error, xml

                            count_subcantidad += 1


                # SubRecargo Detalles-----------------------------------------------------------------------------------

                if datos_subrecargo:

                    subrecargo_detalle = SubElement(registro_detalle, 'SubRecargo')
                    count_subrecargo = 1
                    for g in datos_subrecargo:
                        if count_subrecargo < 6:  ##Se permiten 5 repeticiones de pares de SubRecargo.

                            # Subhijos de subrecargo--------------------------------------------------------------------
                            registro_subrecargo = SubElement(subrecargo_detalle, 'reg_SubRecargo')
                            try:
                                id_subrecargo   = SubElement(registro_subrecargo, 'IdSubRecargo').text  = g['id_subrecargo']
                                tipo_recargo    = SubElement(registro_subrecargo, 'TipoRecargo').text   = g['tipo_recargo']
                                valor_recargo   = SubElement(registro_subrecargo, 'ValorRecargo').text  = g['valor_recargo']
                            except Exception as r:
                                error = "Detalle- SubRecargo: no se encuentra dato " + str(r.args[0]).strip() + \
                                        " en el diccionario enviado."
                                return error, xml

                            count_subrecargo += 1



                ##Contador de cantidad de detalles permitidos
                count_detalles += 1

    # Totales-----------------------------------------------------------------------------------------------------------

    try:
        datos_total = kwargs['totales']
    except Exception as e:
        error = "No se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if datos_total:
        totales = Element('Totales')
        idte.append(totales)

        # Add hijos totales

        for e in datos_total:
            try:
                tipo_moneda                     = SubElement(totales, 'TpoMoneda').text     = e['tipo_moneda']
                monto_neto                      = SubElement(totales, 'MntNeto').text       = e['monto_neto']
                monto_exento                    = SubElement(totales, 'MntExe').text        = e['monto_exento']
                monto_base                      = SubElement(totales, 'MntBase').text       = e['monto_base']
                monto_margen_comerc             = SubElement(totales, 'MntMargenCom').text  = e['monto_margen_comerc']
                tasa_iva                        = SubElement(totales, 'TasaIVA').text       = e['tasa_iva']
                iva                             = SubElement(totales, 'IVA').text           = e['iva']
                iva_propio                      = SubElement(totales, 'IVAProp').text       = e['iva_propio']
                iva_terceros                    = SubElement(totales, 'IVATerc').text       = e['iva_terceros']
                iva_no_retenido                 = SubElement(totales, 'IVANoRet').text      = e['iva_no_retenido']
                credito_especial_constructuras  = SubElement(totales, 'CredEC').text        = e['cred_espec_constr']
                garantia_deposi_env_embal       = SubElement(totales, 'GmtDep').text        = e['garan_deposi_env_embal']
                valor_comision_neto             = SubElement(totales, 'ValComNeto').text    = e['valor_comision_neto']
                valor_comision_exento           = SubElement(totales, 'ValComExe').text     = e['valor_comision_exento']
                valor_comision_iva              = SubElement(totales, 'ValComIVA').text     = e['valor_comision_iva']
                monto_total                     = SubElement(totales, 'MntTotal').text      = e['monto_total']
                monto_no_facturable             = SubElement(totales, 'MontoNF').text       = e['monto_no_facturable']
                monto_periodo                   = SubElement(totales, 'MontoPeriodo').text  = e['monto_periodo']
                saldo_anterior                  = SubElement(totales, 'SaldoAnterior').text = e['saldo_anterior']
                valor_pagar                     = SubElement(totales, 'VlrPagar').text      = e['valor_pagar']

                datos_impuesto = e['impuesto_retenido']

            except Exception as e:
                error = "Totales: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                return error, xml


            # Impuestos retenidos-------------------------------------------------------------------------------------------

            if datos_impuesto:

                impuesto_retenido               = SubElement(totales, 'ImptoReten')
                count_impuesto = 0

                for i in datos_impuesto:

                    if count_impuesto <20: ##Se permiten 20 repeticiones de tipos de impuestos.
                        #Subhijos impuesto retenido-------------------------------------------------------------------------
                        registro_imp_retenido = SubElement(impuesto_retenido, 'reg_ImpReten')
                        try:
                            id_impuesto_retenido    = SubElement(registro_imp_retenido, 'IdImptoReten').text    = i['id_impuesto']
                            tipo_impuesto           = SubElement(registro_imp_retenido, 'TipoImp').text         = i['tipo_impuesto']
                            tasa_impuesto           = SubElement(registro_imp_retenido, 'TasaImp').text         = i['tasa_impuesto']
                            monto_impuesto          = SubElement(registro_imp_retenido, 'MontoImp').text        = i['monto_impuesto']
                        except Exception as e:
                            error = "Total - Impuestos: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                            return error, xml

                        count_impuesto +=1


    #Descripcion recargos globales documento ---------------------------------------------------------------------------

    try:
        recargos_globales = kwargs['recargos_globales']
    except Exception as e:
        error = "No se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if recargos_globales:

        descrip_recar_globales = Element('DscRcgGlobal')
        idte.append(descrip_recar_globales)

        count_recargo_global = 0

        for a in recargos_globales:

            #Add hijos de descripcion recargos globales
            if count_recargo_global <20: ##Se permite hasta 20 lineas de recargos

                reg_descr_recarg_global = SubElement(descrip_recar_globales, 'reg_DscRcgGlobal')
                try:
                    numero_linea_sec            = SubElement(reg_descr_recarg_global, 'NroLinDR').text          = a['nro_linea_recargo']
                    tipo_mov_recargo            = SubElement(reg_descr_recarg_global, 'TpoMov').text            = a['tipo_mov_recargo']
                    glosa_recargo               = SubElement(reg_descr_recarg_global, 'GlosaDR').text           = a['glosa_recargo']
                    tipo_valor_recarg           = SubElement(reg_descr_recarg_global, 'TpoValor').text          = a['tipo_valor_recargo']
                    valor_recargo               = SubElement(reg_descr_recarg_global, 'ValorDR').text           = a['valor_recargo']
                    valor_otra_moneda_recarg    = SubElement(reg_descr_recarg_global, 'ValorDROtrMnda').text    = a['valor_otr_recargo']
                    indicador_exencion_recarg   = SubElement(reg_descr_recarg_global, 'IndExeDR').text          = a['ind_exe_recargo']
                except Exception as e:
                    error = "RecargoGlobal: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                    return error, xml

                count_recargo_global +=1


    #Referecias documentos ---------------------------------------------------------------------------------------------

    try:
        referencias_datos = kwargs['referencias_documentos']
    except Exception as e:
        error = "No se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if referencias_datos:

        referencias = Element('Referencias')
        idte.append(referencias)

        count_referencias = 0

        for c in referencias_datos:

            #Add hijos referencias--------------------------------------------------------------------------------------
            if count_referencias <40: ##Se permiten hasta 40 repeticiones

                registro_referencia = SubElement(referencias, 'reg_Referencias')

                #Sub-hijos de registros de referencias------------------------------------------------------------------
                try:
                    numero_linea_referencia = SubElement(registro_referencia, 'NroLinRef').text = c['nro_linea_referencia']
                    tipo_doc_referencia     = SubElement(registro_referencia, 'TpoDocRef').text = c['tipo_doc_referencia']
                    Indicador_ref_global    = SubElement(registro_referencia, 'IndGlobal').text = c['indicador_referencia']
                    folio_referencia        = SubElement(registro_referencia, 'FolioRef').text  = c['folio_referencia']
                    rut_otro_contribuyente  = SubElement(registro_referencia, 'RUTOtr').text    = c['rut_otro_contribuyente']
                    ind_adic_otro_contri    = SubElement(registro_referencia, 'IdAdicOtr').text = c['indicador_adic_otr_contribuyente']
                    fecha_referencia        = SubElement(registro_referencia, 'FchRef').text    = c['fecha_referencia']
                    codigo_referencia       = SubElement(registro_referencia, 'CodRef').text    = c['codigo_referencia']
                    razon_referencia        = SubElement(registro_referencia, 'RazonRef').text  = c['razon_referencia']
                except Exception as e:
                    error = "Referencias: no se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
                    return error, xml

                count_referencias += 1

    # Referecias boletas -----------------------------------------------------------------------------------------------

    try:
        referencias_boleta_datos = kwargs['referencias_boletas']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if referencias_boleta_datos:

        referencias_bol = Element('RefBoletas')
        idte.append(referencias_bol)

        count_ref_boleta = 0

        for b in referencias_boleta_datos:

            # Add hijos referencias--------------------------------------------------------------------------------------
            if count_ref_boleta < 40: ##Se permiten hasta 40 repeticiones

                reg_ref_boleta = SubElement(referencias_bol, 'reg_RefBoletas')

                # Sub-hijos de registros de referencias de boletas -----------------------------------------------------
                try:
                    num_linea_ref_boleta    = SubElement(reg_ref_boleta, 'NroLinRefB').text = b['nro_linea_ref_boleta']
                    cod_ref_boleta          = SubElement(reg_ref_boleta, 'CodRefB').text    = b['cod_ref_boleta']
                    razon_ref_boleta        = SubElement(reg_ref_boleta, 'RazonRefB').text  = b['razon_ref_boleta']
                    cod_vendedor            = SubElement(reg_ref_boleta, 'CodVndor').text   = b['cod_vendedor']
                    cod_caja_bol            = SubElement(reg_ref_boleta, 'CodCaja').text    = b['cod_caja_boleta']

                except Exception as e:
                    error = "Referencias Boletas: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
                    return error, xml

                count_ref_boleta += 1

    # Comisiones -------------------------------------------------------------------------------------------------------

    try:
        comisiones = kwargs['comisiones']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if comisiones:

        comisiones_documento = Element('Comisiones')
        idte.append(comisiones_documento)

        count_comisiones = 0

        for y in comisiones:

            # Add hijos referencias-------------------------------------------------------------------------------------
            if count_comisiones < 20: ##Se permiten hasta 20 repeticiones

                reg_comision = SubElement(comisiones_documento, 'reg_Comisiones')

                # Sub-hijos de registros de comisiones -----------------------------------------------------------------
                try:
                    num_linea_comision  = SubElement(reg_comision, 'NroLinCom').text    = y['nro_linea_comision']
                    tipo_mov_comision   = SubElement(reg_comision, 'TipoMovim').text    = y['tipo_mov_comision']
                    glosa_comision      = SubElement(reg_comision, 'Glosa').text        = y['glosa_comision']
                    tasa_comision       = SubElement(reg_comision, 'TasaComision').text = y['tasa_comision']
                    valor_comi_neto     = SubElement(reg_comision, 'ValComNeto').text   = y['valor_comi_neto']
                    valor_comi_exento   = SubElement(reg_comision, 'ValComExe').text    = y['valor_comi_exento']
                    valor_comi_iva      = SubElement(reg_comision, 'ValComIVA').text    = y['valor_comi_iva']

                except Exception as e:
                    error = "Comisiones: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
                    return error, xml

                count_comisiones += 1

    # Monto Pagos Documentos -------------------------------------------------------------------------------------------

    try:
        monto_pagos = kwargs['monto_pagos']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if monto_pagos:

        monto_pago_documento = Element('MntPagos')
        idte.append(monto_pago_documento)

        count_monto_pagos = 0

        for p in monto_pagos:

            # Add hijos monto de pagos----------------------------------------------------------------------------------
            if count_monto_pagos < 30: ##Se permiten hasta 30 repeticiones

                reg_comision = SubElement(monto_pago_documento, 'reg_MntPagos')

                # Sub-hijos de registros de monto pagos ----------------------------------------------------------------
                try:
                    id_monto_pago   = SubElement(reg_comision, 'IDMntPagos').text   = p['id_monto_pago']
                    fecha_pago      = SubElement(reg_comision, 'FchPago').text      = p['fecha_pago']
                    monto_pago      = SubElement(reg_comision, 'MntPago').text      = p['monto_pago']
                    glosa_pago      = SubElement(reg_comision, 'GlosaPagos').text   = p['glosa_pago']

                except Exception as e:
                    error = "Monto Pagos: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
                    return error, xml

                count_monto_pagos += 1

    # Otra Moneda Documentos -------------------------------------------------------------------------------------------

    try:
        otra_moneda_documento = kwargs['otra_moneda']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if otra_moneda_documento:

        otra_moneda_doc = Element('OtraMoneda')
        idte.append(otra_moneda_doc)



        for o in otra_moneda_documento:

            # Add hijos Otra moneda ------------------------------------------------------------------------------------
            try:
                tipo_otr_moneda             = SubElement(otra_moneda_doc, 'TipoMoneda').text            = o['tipo_otr_moneda']
                tipo_cambio                 = SubElement(otra_moneda_doc, 'TpoCambio').text             = o['tipo_cambio']
                mnt_neto_otra_moneda        = SubElement(otra_moneda_doc, 'MntNetoOtrMnda').text        = o['mnt_neto_otra_moneda']
                mnt_exento_otra_moneda      = SubElement(otra_moneda_doc, 'MntExeOtrMnda').text         = o['mnt_exento_otra_moneda']
                mnt_fae_carne_otr_moneda    = SubElement(otra_moneda_doc, 'MntFaeCarneOtrMnda').text    = o['mnt_fae_carne_otr_moneda']
                mnt_margen_otra_moneda      = SubElement(otra_moneda_doc, 'MntMargComOtrMnda').text     = o['mnt_margen_otra_moneda']
                iva_otra_moneda             = SubElement(otra_moneda_doc, 'IVAOtrMnda').text            = o['iva_otra_moneda']
                iva_no_ret_otr_moneda       = SubElement(otra_moneda_doc, 'IVANoRetOtrMnd').text        = o['iva_no_ret_otr_moneda']
                mnt_total_otr_moneda        = SubElement(otra_moneda_doc, 'MntTotOtrMnda').text         = o['mnt_total_otr_moneda']

                impuesto_otr_moneda         = o['imp_otra_moneda']

            except Exception as e:
                error = "Montos Otra Moneda: no se encuentra dato " + str(e.args[0]).strip() + \
                        " en el diccionario enviado."
                return error, xml


            if impuesto_otr_moneda:

                # Add SubHijos Impuestos Otra moneda -------------------------------------------------------------------
                imp_otr_moneda  = SubElement(otra_moneda_doc, 'ImpRetOtrMnda')
                count_imp_otr_m = 0

                for l in impuesto_otr_moneda:

                    if count_imp_otr_m < 20:  ##Se permiten hasta 20 repeticiones

                        reg_imp_otr_mnda = SubElement(imp_otr_moneda, 'reg_ImpRetOtrMnda')

                        # Sub-hijos de registros impuestos de otra moneda ----------------------------------------------
                        try:
                            id_imp_otr_m    = SubElement(reg_imp_otr_mnda, 'IdImpRetOtrMnda').text  = l['id_imp_otr_m']
                            tipo_imp_otr_m  = SubElement(reg_imp_otr_mnda, 'TipoImpOtrMnda').text   = l['tipo_imp_otr_m']
                            tasa_imp_otr_m  = SubElement(reg_imp_otr_mnda, 'TasaImpOtrMnda').text   = l['tasa_imp_otr_m']
                            valor_imp_otr_m = SubElement(reg_imp_otr_mnda, 'VlrImpOtrMnda').text    = l['valor_imp_otr_m']

                        except Exception as e:
                            error = "Montos Otra Moneda - impuestos: no se encuentra dato " + str(e.args[0]).strip() + \
                                    " en el diccionario enviado."
                            return error, xml

                        count_imp_otr_m += 1


    #Subtotal información documento-------------------------------------------------------------------------------------------------

    try:
        subtotal_datos = kwargs['subtotales']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if subtotal_datos:

        sub_total_info = Element('SubTotInfo')
        idte.append(sub_total_info)

        count_subtotal = 0

        for s in subtotal_datos:

            if count_subtotal <20: ##Se permiten hasta 20 repeticiones

                #Add hijo sub total información-------------------------------------------------------------------------
                registro_sub_total_info = SubElement(sub_total_info, 'reg_SubTotInfo')

                #Subhijos subtotal informacion--------------------------------------------------------------------------
                try:
                    numero_subtotalinfo             = SubElement(registro_sub_total_info, 'NroSTI').text        = s['numero_subtotal']
                    glosa_subtotalinfo              = SubElement(registro_sub_total_info, 'GlosaSTI').text      = s['glosa_subtotal']
                    orden_subtotalinfo              = SubElement(registro_sub_total_info, 'OrdenSTI').text      = s['orden_subtotal']
                    sub_total_neto_subtotalinfo     = SubElement(registro_sub_total_info, 'SubTotNetoSTI').text = s['neto_subtotal']
                    sub_total_iva_subtotalinfo      = SubElement(registro_sub_total_info, 'SubTotIVASTI').text  = s['iva_subtotal']
                    sub_total_adici_subtotalinfo    = SubElement(registro_sub_total_info, 'SubTotAdicSTI').text = s['adici_subtotal']
                    sub_total_exe_subtotalinfo      = SubElement(registro_sub_total_info, 'SubTotExeSTI').text  = s['exento_subtotal']
                    valor_subtotal_subtotalinfo     = SubElement(registro_sub_total_info, 'ValSubtotSTI').text  = s['subtotal']

                    subtotal_linea_datos = s['subtotales_lineas_detalles']
                except Exception as e:
                    error = "Subtotal: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                    return error, xml


                lineas_detalles                 = SubElement(registro_sub_total_info, 'lineasDeta')

                count_linea_subtotal = 0
                for a in subtotal_linea_datos:
                    if count_linea_subtotal <60: #Se aceptan solo 60 repeticiones

                        registro_linea_detalle = SubElement(lineas_detalles, 'reg_lineasDeta')
                        try:
                            numero_linea_detalle = SubElement(registro_linea_detalle, 'num_linea_detalle').text = a['linea_detalle_subtotal']
                        except Exception as e:
                            error = "Subtotal - Lineas detalle: no se encuentra dato " + str(e.args[0]).strip()+ \
                                    " en el diccionario enviado."
                            return error, xml

                        count_linea_subtotal += 1

                count_subtotal +=1

    # Transporte Documentos -------------------------------------------------------------------------------------------

    try:
        transporte = kwargs['transporte']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if transporte:

        transporte_documento = Element('Transporte')
        idte.append(transporte_documento)

        count_transporte = 0

        for t in transporte:

            if count_transporte <1:

                try:
                    patente             = SubElement(transporte_documento, 'Patente').text      = t['patente']
                    rut_transportista   = SubElement(transporte_documento, 'RUTTrans').text     = t['rut_transp']
                    rut_chofer          = SubElement(transporte_documento, 'RUTChofer').text    = t['rut_chofer']
                    nombre_chofer       = SubElement(transporte_documento, 'NombreChofer').text = t['nombre_chofer']
                    direccion_destino   = SubElement(transporte_documento, 'DirDest').text      = t['direccion_destino']
                    comuna_destino      = SubElement(transporte_documento, 'CmnaDest').text     = t['comuna_destino']
                    cuidad_destino      = SubElement(transporte_documento, 'CiudadDest').text   = t['cuidad_destino']

                    aduanas             = t['aduanas']

                except Exception as e:
                    error = "Transporte: no se encuentra dato " + str(
                        e.args[0]).strip() + " en el diccionario enviado."

                    return error, xml

                # Add hijos de aduana----------------------------------------------------------------------------------

                if aduanas:
                    aduana          = SubElement(transporte_documento, 'Aduana')
                    count_aduana    = 0

                    for a in aduanas:
                        if count_aduana < 1:

                            try:
                                modalidad_venta         = SubElement(aduana, 'CodModVenta').text      = a['modalidad_venta']
                                cod_clausula_venta      = SubElement(aduana, 'CodClauVenta').text     = a['cod_clausula_venta']
                                total_clau_venta        = SubElement(aduana, 'TotClauVenta').text     = a['total_clau_venta']
                                cod_via_transp          = SubElement(aduana, 'CodViaTransp').text     = a['cod_via_transp']
                                nombre_transporte       = SubElement(aduana, 'NombreTransp').text     = a['nombre_transporte']
                                rut_cia_transp          = SubElement(aduana, 'RUTCiaTransp').text     = a['rut_cia_transp']
                                nombre_cia_transp       = SubElement(aduana, 'NomCiaTransp').text     = a['nombre_cia_transp']
                                id_adic_transporte      = SubElement(aduana, 'IdAdicTransp').text     = a['id_adic_transporte']
                                booking                 = SubElement(aduana, 'Booking').text          = a['booking']
                                operador                = SubElement(aduana, 'Operador').text         = a['operador']
                                cod_pto_embarque        = SubElement(aduana, 'CodPtoEmbarque').text   = a['cod_pto_embarque']
                                id_adic_pto_embarq      = SubElement(aduana, 'IdAdicPtoEmb').text     = a['id_adic_pto_embarq']
                                cod_pto_desembarque     = SubElement(aduana, 'CodPtoDesemb').text     = a['cod_pto_desembarque']
                                id_adic_pto_desemb      = SubElement(aduana, 'IdAdicPtoDesemb').text  = a['id_adic_pto_desemb']
                                tara                    = SubElement(aduana, 'Tara').text             = a['tara']
                                cod_unid_medida_tara    = SubElement(aduana, 'CodUnidMedTara').text   = a['cod_unid_medida_tara']
                                peso_bruto              = SubElement(aduana, 'PesoBruto').text        = a['peso_bruto']
                                cod_unid_peso_bruto     = SubElement(aduana, 'CodUnidPesoBruto').text = a['cod_unid_peso_bruto']
                                peso_neto               = SubElement(aduana, 'PesoNeto').text         = a['peso_neto']
                                cod_unid_peso_neto      = SubElement(aduana, 'CodUnidPesoNeto').text  = a['cod_unid_peso_neto']
                                total_item              = SubElement(aduana, 'TotItems').text         = a['total_item']
                                total_bulto             = SubElement(aduana, 'TotBultos').text        = a['total_bulto']
                                monto_flete             = SubElement(aduana, 'MntFlete').text         = a['monto_flete']
                                monto_seguro            = SubElement(aduana, 'MntSeguro').text        = a['monto_seguro']
                                cod_pais_recep          = SubElement(aduana, 'CodPaisRecep').text     = a['cod_pais_recep']
                                cod_pais_destino        = SubElement(aduana, 'CodPaisDestin').text    = a['cod_pais_destino']


                                tipo_bulto              = a['tipo_bulto']


                                if tipo_bulto:

                                    # Add hijos de Tipo de bultos ------------------------------------------------------

                                    bultos = SubElement(aduana, 'TipoBultos')
                                    count_tipo_bultos = 0

                                    for b in tipo_bulto:

                                        if count_tipo_bultos < 10: #Se aceptan solo 10 repeticiones

                                            reg_tipo_bulto = SubElement(bultos, 'reg_TipoBultos')
                                            try:
                                                id_tipo_bulto       = SubElement(reg_tipo_bulto, 'IDTipoBultos').text   = b['cod_unid_peso_neto']
                                                total_item          = SubElement(reg_tipo_bulto, 'CodTpoBultos').text   = b['total_item']
                                                total_bulto         = SubElement(reg_tipo_bulto, 'CantBultos').text     = b['total_bulto']
                                                monto_flete         = SubElement(reg_tipo_bulto, 'Marcas').text         = b['monto_flete']
                                                monto_seguro        = SubElement(reg_tipo_bulto, 'IdContainer').text    = b['monto_seguro']
                                                cod_pais_recep      = SubElement(reg_tipo_bulto, 'Sello').text          = b['cod_pais_recep']
                                                cod_pais_destino    = SubElement(reg_tipo_bulto, 'EmisorSello').text    = b['cod_pais_destino']
                                            except Exception as n:
                                                error = "Transporte- Aduanas - Tipo Bultos: no se encuentra dato " + str(
                                                    n.args[0]).strip() + " en el diccionario enviado."

                                                return error, xml

                                            count_tipo_bultos +=1

                            except Exception as e:
                                error = "Transporte- Aduanas: no se encuentra dato " + str(
                                    e.args[0]).strip() + " en el diccionario enviado."

                                return error, xml

                            count_aduana += 1

                count_transporte +=1

    # Extra Documentos -------------------------------------------------------------------------------------------------

    try:
        extra_documento = kwargs['extra_documento']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if extra_documento:

        extras = Element('Extras')
        idte.append(extras)

        count_extras = 0

        for e in extra_documento:

            # Add hijos extra ------------------------------------------------------------------------------------------
            if count_extras < 10:  ##No esta definido un maximo, por seguridad se dejará con maximo 10

                reg_extra = SubElement(extras, 'reg_Extras')

                # Sub-hijos de registros de monto pagos ----------------------------------------------------------------
                try:
                    concepto_extra  = SubElement(reg_extra, 'concepto').text = e['concepto_extra']
                    valor_extra     = SubElement(reg_extra, 'valor').text    = e['valor_extra']

                except Exception as k:
                    error = "Extras: no se encuentra dato " + str(
                        k.args[0]).strip() + " en el diccionario enviado."

                    return error, xml

                count_extras += 1


    xml = etree.tostring(idte, short_empty_elements=False,  method='xml')

    return error, xml.decode()

def url_web_service(**kwargs):
    """
        función que permite realizar el armado de la url a conectarse al web services en especifico
    :param kwargs: datos de conexión del web service
    :return: url de conexión
    """
    error = ''
    url_conexion = ''
    try:
        codigo = kwargs['codigo_contexto']
        host = kwargs['host']
        url  = kwargs['url']
        puerto = kwargs['puerto']

        contexto = codigo.split('_')


        url_conexion = 'http://'+str(host).strip()+':'+str(puerto).strip()+'/'+ str(url).strip()+'/'+str(contexto[2]).strip()+'.svc?wsdl'
                        # inf-srv-des01.infodesarrollo.cl/wsDTE/servDTE.svc?wsdl'
    except Exception as e:
        error ="Error al realizar el armado de la URL de conexión del Web Services, por favor verifique los datos de conexión."
    return error, url_conexion

def validar_folios_procesar(tipo_documento,folio_actual):
    """
        Función que permite realizar la validacion del folio a utilizar en un determinado tipo de documento,
    :param tipo_documento: tipo de documento electronico
    :param folio_actual: folio o caf a utilizar
    :return: retorna una valiable con el error si es que se encuentra uno determinado en la validaciones.
    """
    error=''
    try:
        folio = FoliosDocumentosElectronicos.objects.filter(tipo_dte=tipo_documento, operativo=True).get()

        if folio_actual > folio.rango_final or folio_actual == 0:
            error = "No hay folios disponible, revise o ingrese nuevo CAF"

            if folio_actual > folio.rango_final:
                update_folio = FoliosDocumentosElectronicos.objects.get(tipo_dte=tipo_documento, operativo=True)
                update_folio.operativo = False
                update_folio.save()

    except FoliosDocumentosElectronicos.DoesNotExist:
        error = "No Exiten folios operativos para el tipo de documento."

    return error

def validar_existencia_folio(tipo_documento):

    """
        Función que permite realiza la validación de la existencia de folios operativos para el tipo de documento
        determinado
    :param tipo_documento: tipo de documento electronico
    :return: retorna una variable la cual contiene o no un mensaje de error.
    """
    error = ''
    try:
        folio = FoliosDocumentosElectronicos.objects.filter(tipo_dte=tipo_documento, operativo=True).get()
    except FoliosDocumentosElectronicos.DoesNotExist:
        error = "No existen folios operativos para el tipo de documento"
    return error

def obtener_folio(tipo_documento):

    """
        Función que permite realizar la obtención del folio o caf determinado a utilizar para el tipo de documento
        enviado en los parametros
    :param tipo_documento: tipo de documento electronico
    :return: retorna una variable de error si es que no se pudo obtener el folio y ademas a el folio a utilizar para el
            documento determinado.
    """


    ##Obtener Folio Actual Tabla de Folios -------------------------------------------------------------
    # transaction.set_autocommit(False)
    #
    # conn = connection.cursor()
    # sql = "UPDATE facturacion_foliosdocumentoselectronicos set folio_actual = folio_actual WHERE tipo_dte = %s AND operativo = TRUE"
    # conn.execute(sql, (tipo_documento,))
    #
    # sql = "SELECT folio_actual from facturacion_foliosdocumentoselectronicos where tipo_dte = %s AND operativo=TRUE "
    # conn.execute(sql, (tipo_documento,))
    # folio_documento = conn.fetchone()[0]
    #
    # sql = "UPDATE facturacion_foliosdocumentoselectronicos set folio_actual = folio_actual + 1 WHERE tipo_dte = %s AND operativo = TRUE"
    # conn.execute(sql, (tipo_documento,))

    folio_documento = 0
    error           = ''
    try:

        transaction.set_autocommit(False)

        update = FoliosDocumentosElectronicos.objects.get(tipo_dte=tipo_documento, operativo=True)
        update.folio_actual = update.folio_actual
        update.save()

        folio_documento = FoliosDocumentosElectronicos.objects.get(tipo_dte=tipo_documento, operativo=True).folio_actual

        update_2 = FoliosDocumentosElectronicos.objects.get(tipo_dte=tipo_documento, operativo=True)
        update_2.folio_actual = update.folio_actual + 1
        update_2.save()
    except Exception:
        error = "Error en la obtención del folio."


    return error, folio_documento

## ---SERVDTE-----------------------------------------------------------------------------------------------------------

def get_estado_documento(client, id_idte_empresa, tipo_documento, folio, traza):

    """
        Función que permite consultar por el estado de un documento en IDTE.

        EJEMPLO DE RESPUESTAS ------------------------------------------------------------------------------------------
        Calling: get_estado() OK  RESPUESTA
        (RprocWS){
           Clase = "wsDTE"
           ID_trans = "5ced4227-b9ba-48d5-9c97-90c33c07d2af"
           Metodo = "get_estado"
           RutaFull_archivoLOG = "C:\IDTE\Empresas\MOLINERA\LogTRANS\LogDTE-MOLINERA-5ced4227-b9ba-48d5-9c97-90c33c07d2af.txt"
           dio_error = False
           msg = None
           parametros = "33-15237"
           tipo_error = None
           valor = "False| | | | |2016-07-18|53224884|0|10112728|63337612|1|1|1|1|1|1||19/07/2016 13:49:31|1|1|0|19/07/2016 13:49:31|76032099-4"
        }
        REFERENCIA VALOR = anulado|id1_erp_dte|id2_erp_dte|id3_erp_dte|id4_erp_dte|fch_emision_dte|afecto|exento|iva|total|estado_email_pdf|estado_email_xml|estado_RE|estado_RA|estado_RM|estado_SII|msg_error_SII|fch_registro|trasnferido|estado|trackID|fch_envio_SII|rut_cliente|

         Calling: get_estado() ERROR EN RESPUESTA
        (RprocWS){
           Clase = "DTEDAC"
           ID_trans = "3fc9f9f2-aa3a-42b1-8ba9-08480c8e93b1"
           Metodo = "get_estado"
           RutaFull_archivoLOG = "C:\IDTE\Empresas\MOLINERA\LogTRANS\LogDTE-MOLINERA-3fc9f9f2-aa3a-42b1-8ba9-08480c8e93b1.txt"
           dio_error = True
           msg = "No se encontro registros en busqueda info del DTE 33-15238"
           parametros = "33|15238"
           tipo_error = "ERN"
           valor = "ERROR"
        }
    :param client: cliente de conexión con el servidor de IDTE
    :param id_idte_empresa:  identificador de empresa asociado a IDTE
    :param tipo_documento:  tipo de documento electronico del S.I.I. (ej: 33, 39, 41,etc)
    :param folio: folio del documento (Identificador del documento) en IDTE
    :param traza:  nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return: retorna objeto con los elementos.
    """

    result = client.service.get_estado(id_idte_empresa, tipo_documento, folio, traza)

    return result

def get_archivo_documento(client, id_idte_empresa, tipo_documento, folio, formato, traza):

    """
        función que permite realizar la obtención de los archivos de la factura (PDF o XML)

        EJEMPLO DE RESPUESTA
        ----------------------------------------------------------------------------------------------------------------
        Calling: get_archivo()
        (RprocWS){
           Clase = "DTEBC"
           ID_trans = "5fa1b9d2-18a3-420f-acf6-f91382c8ee7e"
           Metodo = "gen_url"
           RutaFull_archivoLOG = "C:\IDTE\Empresas\MOLINERA\LogTRANS\LogDTE-MOLINERA-5fa1b9d2-18a3-420f-acf6-f91382c8ee7e.txt"
           dio_error = False
           msg = "iniciando proceso"
           parametros = "33|15237|2"
           tipo_error = None
           valor = "http://192.168.231.111/verArchivos/bajar.aspx?Tipo=PDFDTE&IDEmp=MOLINERA-96540970-6274974030-20140929&File=DTE_33_15237_C_7f665d31-ea09-4d0a-a875-1b467c648325.PDF"
         }
    :param client: cliente de conexión con el servidor de IDTE
    :param id_idte_empresa: identificador de empresa asociado a IDTE
    :param tipo_documento: tipo de documento electronico del S.I.I. (ej: 33, 39, 41,etc)
    :param folio: folio del documento (Identificador del documento) en IDTE
    :param formato: formato de obtención de archivo donde 1 es para el PDF no cedible, 2 PDF cedible, 3 XML no cedible y 4 XML cedible
    :param traza:nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return:
    """

    archivo = client.service.get_archivo(id_idte_empresa, tipo_documento, folio, formato, traza)

    return archivo
    # if archivo.dio_error:
    #     pass
    # else:
    #     pdf = urllib.request.urlopen(archivo.valor)
    #     response = HttpResponse(pdf.read(), content_type='application/pdf')
    #     response['Content-Disposition'] = 'attachment; filename=DTE-'+str(tipo_documento)+'-'+str(folio)+'.pdf'
    #     pdf.close()
    #
    #     return response

def get_procesar_dte_xml(client, id_idte_empresa, tipo_documento, folio, accion, traza, xml):

    """
        Función que permite realizar el procesamiento.

        EJEMPLO DE RESPUESTA
        ----------------------------------------------------------------------------------------------------------------
        Calling: get_procesar_dte_xml() ERROR EN RESPUESTA
        (RprocWS){
           Clase = "DTEDAC"
           ID_trans = "83c31344-f1e2-4134-a51c-c69337c7563f"
           Metodo = "validar_DTE_a_procesar"
           RutaFull_archivoLOG = "C:\IDTE\Empresas\MOLINERA\LogTRANS\LogDTE-MOLINERA-83c31344-f1e2-4134-a51c-c69337c7563f.txt"
           dio_error = True
           msg = "ERN-El DTE ya esta en el Historico"
           parametros = "33|15237"
           tipo_error = "ERN"
           valor = "ERROR"
         }

         Calling: get_procesar_dte_xml() RESPUESTA OK
        (RprocWS){
           Clase = "DTEBC"
           ID_trans = "c6f30e8e-9365-4edd-bb62-ede370aa7dd5"
           Metodo = "grabar_PDF"
           RutaFull_archivoLOG = "C:\IDTE\Empresas\MOLINERA\LogTRANS\LogDTE-MOLINERA-c6f30e8e-9365-4edd-bb62-ede370aa7dd5.txt"
           dio_error = False
           msg = None
           parametros = "largo cedible 53322|largo no cedible 52850|33|15238|c6f30e8e-9365-4edd-bb62-ede370aa7dd5"
           tipo_error = None
           valor = "OK"
         }


    :param client: cliente de conexión con el servidor de IDTE
    :param id_idte_empresa:  identificador de empresa asociado a IDTE
    :param tipo_documento:  tipo de documento electronico del S.I.I. (ej: 33, 39, 41,etc)
    :param folio:  folio del documento (Identificador del documento) en IDTE
    :param accion: indica la operación que se va a ejecutar sobre el web service (1 procesar y enviar, 2 procesar y bloquear,
                    3 anular DTE- folio no se podra usar mas, 4 borrar registro si no esta enviado al sii, 5 desbloquear)
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :param xml: string del xml enviado a procesar
    :return: retorna un objeto con los valores expuestos en los ejemplos
    """

    procesar_dte = client.service.procesar_DTE_XML(id_idte_empresa, tipo_documento, folio, accion, traza, xml)

    return procesar_dte

def importar_caf(client, id_idte_empresa, contenido_caf, traza):

    """
        Función que permite realizar la importación de CAF (Folio) a el sistema de IDTE
    :param client: cliente de conexión con el servidor de IDTE
    :param id_idte_empresa:  identificador de empresa asociado a IDTE
    :param contenido_caf: xml con el contenido de los caf a importar.
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return: retorna un objeto con el estado y los datos del proceso

    EJEMPLO DE RESPUESTA
    --------------------------------------------------------------------------------------------------------------------
    Calling: importar_caf()
    (RprocWS){
       Clase = "CAFBC"
       ID_trans = "bfac79e7-4742-44cd-b3b4-c5b380ccbf70"
       Metodo = "Importar"
       RutaFull_archivoLOG = "C:\IDTE\Empresas\MOLINERA\LogTRANS\LogICAF-MOLINERA-bfac79e7-4742-44cd-b3b4-c5b380ccbf70.txt"
       dio_error = False
       msg = None
       parametros = "largo contenido 1168"
       tipo_error = None
       valor = "OK"
     }
    """
    caf = client.service.Importar_CAF(id_idte_empresa, contenido_caf, traza)

    return caf

def borrar_cola(client, id_dte_empresa, tipo_documento, folio, traza):

    """
        función que permite realizar el borrado del documento de la tabla cola_DTE, la cual contiene los documentos
        que están en espera para realizar el procesamiento o emisión hacia el servicio de facturación de IDTE.

        EJEMPLO RESPUESTA METODO
        ----------------------------------------------------------------------------------------------------------------
        Calling: borrar_cola()
        (RprocWS){
           Clase = "DTEDAC"
           ID_trans = "ed85b866-5863-40a5-93e2-1edde02b5ad5"
           Metodo = "borrar"
           RutaFull_archivoLOG = "C:\IDTE\Empresas\MOLINERA\LogTRANS\LogDTE-MOLINERA-ed85b866-5863-40a5-93e2-1edde02b5ad5.txt"
           dio_error = False
           msg = None
           parametros = "33|15237"
           tipo_error = None
           valor = "OK"
        }
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param tipo_documento: tipo de documento electronico del S.I.I. (ej: 33, 39, 41,etc)
    :param folio: folio del documento (Identificador del documento) en IDTE
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return: retorna un objeto con los valores (si es que dio error el proceso, mensaje de error, metodos utilizado, etc.)
    """

    borrar_documento = client.service.borrar_cola(id_dte_empresa, tipo_documento, folio, traza)

    return borrar_documento


##--- SERVMIXTO --------------------------------------------------------------------------------------------------------

def procesar_ra_xml(client, id_dte_empresa, tipo_documento, folio, rut_proveedor, accion, traza, xml):

    """
        Función que permite realizar el envio a IDTE la respuesta de aceptación de la factura del proveedor.
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa:  identificador de empresa asociado a IDTE
    :param tipo_documento:  tipo de documento electronico del S.I.I. (ej: 33, 39, 41,etc)
    :param folio: folio del documento (Identificador del documento) en IDTE
    :param rut_proveedor: rut del proveedor del producto o servicio
    :param accion: indica que la operación se va a ejecutar sobre el Web Service 1- Procesar y enviar RA, 2-Procesar y bloquear RA
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :param xml: string del xml enviado para la aceptación de la factura.
    :return:
    """
    procesar_ra = client.service.procesar_RA_XML(id_dte_empresa, tipo_documento, folio, rut_proveedor, accion, traza, xml)

    return procesar_ra

def procesar_rm_xml(client, id_dte_empresa, tipo_documento, folio, rut_proveedor, accion, traza, xml):

    """
        función que permite realizar el recibo de la mercancia del proveedor.
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa:  identificador de empresa asociado a IDTE
    :param tipo_documento:  tipo de documento electronico del S.I.I. (ej: 33, 39, 41,etc)
    :param folio:  folio del documento (Identificador del documento) en IDTE
    :param rut_proveedor: rut del proveedor del producto o servicio
    :param accion: indica que operación se va a ejecutar sobre el Web Service.
                    1- procesar y enviar RM, 2- Procesar y bloquear RM, 4- Borrar registro(si no esta enviado al sii) RM
                    5- desbloquear RM
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :param xml: string del xml enviado para lrealizar la recepción de la mercancia
    :return:
    """
    procesar_rm = client.service.procesar_RM_XML(id_dte_empresa, tipo_documento, folio, rut_proveedor, accion, traza, xml)

    return procesar_rm

def procesar_lb_xml(client, id_dte_empresa, id_hist_lb, accion, traza, xml):

    """
        función que permite realizar el envio a IDTE del libro de boletas.
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param id_hist_lb: Clave primaria o identificador con el cual será almacenado en las tablas de IDTE el libro enviado este
                        debe ser añomesdia 20160815
    :param accion: indica que operación se va a ejecutar sobre el Web Service.
                    1- procesar y enviar , 2- Procesar y bloquear , 4- Borrar registro(si no esta enviado al sii)
                    5- desbloquear
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :param xml: string del xml enviado para realizar el envio del libro de boletas
    :return: retorna un objeto el cual contiene los datos del proceso realizado
    """
    procesar_libro_boleta = client.service.procesar_LB_XML(id_dte_empresa, id_hist_lb, accion, traza, xml)

    return  procesar_libro_boleta

def procesar_cesion_xml(client, id_dte_empresa, tipo_documento, folio, accion, traza, xml):


    """
        función que permite procesar una cesion de un documento.
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param tipo_documento: tipo de documento electronico o manual asociado a S.I.I.
    :param folio: folio del documento (Identificador del documento) en IDTE y el S.I.I.
    :param accion: indica que operación se va a ejecutar sobre el Web Service.
                    1- procesar cesion y 4- borrar registro
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :param xml: string del xml enviado para realizar la cesion del documento
    :return: retorna un objeto el cual contiene los datos del proceso realizado
    """
    procesar_cesion = client.service.procesar_CESION_XML(id_dte_empresa, tipo_documento, folio, accion, traza, xml)

    return procesar_cesion

#--Control de folios----------------------------------------------------------------------------------------------------

def procesar_cf_xml(client, id_dte_empresa, fecha_emision, secuencia_envio, accion, traza, xml):

    """
        función que permite realizar el envio a IDTE del libro de control de folios CAF.
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param fecha_emision: fecha de emision del libro de control de folios formato 2016-08-01
    :param secuencia_envio: parametro que forma parte de la clave primaria o identificador en las tablas de IDTE
    :param accion: indica que operación se va a ejecutar sobre el Web Service.
                    1- procesar y enviar , 2- Procesar y bloquear , 4- Borrar registro(si no esta enviado al sii)
                    5- desbloquear
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :param xml: string del xml de control de folios
    :return: retorna un objeto el cual contiene los datos del proceso.
    """
    procesar_control_folios = client.service.procesar_CF_XML(id_dte_empresa, fecha_emision, secuencia_envio, accion, traza, xml)

    return procesar_control_folios

def get_estado_cf(client, id_dte_empresa,fecha_emision, secuencia_envio, traza):

    """
        función que permite obtener el estado del control de folios enviados al S.I.I. de acuerdo a lo determinado por
        este
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param fecha_emision: fecha de emision del libro de control de folios formato 2016-08-01
    :param secuencia_envio: parametro que forma parte de la clave primaria o identificador en las tablas de IDTE
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return: retorna un objeto el cual contiene los datos del proceso.
    """
    estado_control_folios = client.service.get_estado_CF(id_dte_empresa,fecha_emision, secuencia_envio, traza)

    return estado_control_folios

def crear_xml_control_folios(**kwargs):

    """
        Función que permite realizar la creación del xml de Control de folios, el cual se envia al sistema de IDTE
    :param kwargs: diccionario con los datos del control de folios
    :return: retorna variable la cual contiene el string del xml.
    """
    xml= ''
    error = ''
    idte = Element('IDTE_CF')

    #------------------------------------- CONTROL DE FOLIOS -----------------------------------------------------------
    try:
        control_folio = kwargs['control_folios']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if control_folio:
        cabecera = Element('CF')
        idte.append(cabecera)

        # Add hijos control folios

        for a in control_folio:
            try:
                registro_cf             = SubElement(cabecera, 'reg_CF')

                tipo_documento_cf       = SubElement(registro_cf, 'TipoDoc_CF').text        = a['tipo_documento_cf']
                monto_neto_cf           = SubElement(registro_cf, 'MntNeto_CF').text        = a['monto_neto_cf']
                monto_iva_cf            = SubElement(registro_cf, 'MntIVA').text            = a['monto_iva_cf']
                tasa_iva_cf             = SubElement(registro_cf, 'tasa_iva_CF').text       = a['tasa_iva_cf']
                monto_exento_cf         = SubElement(registro_cf, 'MntExe_CF').text         = a['monto_exento_cf']
                monto_total_cf          = SubElement(registro_cf, 'MntTotal_CF').text       = a['monto_total_cf']
                folios_emitidos_cf      = SubElement(registro_cf, 'FoliosEmitidos').text    = a['folios_emitidos_cf']
                folios_anulados_cf      = SubElement(registro_cf, 'FoliosAnulados').text    = a['folios_anulados_cf']
                folios_utilizados_cf    = SubElement(registro_cf, 'FoliosUtilizados').text  = a['folios_utilizados_cf']

            except Exception as e:
                error ="Control folios: no se encuentra dato " +str(e.args[0]).strip()+" en el diccionario enviado."
                return error, xml

    # ------------------------------------- RANGO UTILIZADOS -----------------------------------------------------------

    try:
        rango_utilizado = kwargs['rango_utilizado']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if rango_utilizado:
        rango_u = Element('RangoUtilizados')
        idte.append(rango_u)

        # Add hijos rango utilizados

        for a in rango_utilizado:
            try:
                registro_rango_u = SubElement(rango_u, 'reg_RangoUtilizados')

                id_rango_utilizado          = SubElement(registro_rango_u, 'idRangoUtilizados').text    = a['id_rango_utilizado']
                tipo_doc_rango_util         = SubElement(registro_rango_u, 'TipoDoc_CF').text           = a['tipo_doc_rango_util']
                folio_inicial_rango_util    = SubElement(registro_rango_u, 'Folio_inicial_usado').text  = a['folio_inicial_rango_util']
                folio_final_rango_util      = SubElement(registro_rango_u, 'Folio_final_usado').text    = a['folio_final_rango_util']

            except Exception as e:
                error = "Rango Utilizado: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
                return error, xml

    # ------------------------------------- RANGO ANULADOS -------------------------------------------------------------

    try:
        rango_anulado = kwargs['rango_anulado']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if rango_anulado:
        rango_a = Element('RangoAnulados')
        idte.append(rango_a)

        # Add hijos control folios

        for a in rango_anulado:
            try:
                registro_rango_a = SubElement(rango_a, 'reg_RangoAnulados')

                id_rango_anulado        = SubElement(registro_rango_a, 'idRangoAnulados').text  = a['id_rango_anulado']
                tipo_doc_rango_a        = SubElement(registro_rango_a, 'TipoDoc_CF').text       = a['tipo_doc_rango_a']
                folio_inicial_rango_a   = SubElement(registro_rango_a, 'Folio_inicial').text    = a['folio_inicial_rango_a']
                folio_final_rango_a     = SubElement(registro_rango_a, 'Folio_final').text      = a['folio_final_rango_a']

            except Exception as e:
                error = "Rango Anulado: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
                return error, xml

    xml = etree.tostring(idte, short_empty_elements=False, method='xml')

    return error, xml.decode()

##--- SERVLCV ----------------------------------------------------------------------------------------------------------

def crear_xml_libro_compra(**kwargs):

    """
        función que permite realizar la creación del xml del libro de compras
    :param kwargs: diccionario de datos del libro de compras
    :return: retorna una variable la cual contiene el xml, ademas de una variable de error si es que ocurrio algún hecho
    que afecto la creacion del xml
    """
    xml= ''
    error = ''
    idte = Element('IDTE_LC')

    #------------------------------------- GENERAL ---------------------------------------------------------------------
    general = Element('General')
    idte.append(general)


    # Add hijos general
    try:

        periodo_libro            = SubElement(general, 'periodo').text                      = kwargs['periodo_libro']
        rectificatoria           = SubElement(general, 'rectificatoria').text               = kwargs['rectificatoria']
        codigo_rectificatoria    = SubElement(general, 'cod_rectificatoria').text           = kwargs['cod_rectificatoria']
        notificacion             = SubElement(general, 'notificacion').text                 = kwargs['notificacion']
        numero_notificacion      = SubElement(general, 'num_notificacion').text             = kwargs['num_notificacion']
        factor_propor_iva_lc     = SubElement(general, 'factor_Proporcional_iva_LC').text   = kwargs['factor_Proporcional_iva']

    except Exception as e:
        error ="General: no se encuentra dato " +str(e.args[0]).strip()+" en el diccionario enviado."
        return error, xml


    #------------------------------------- LIBRO COMPRA ----------------------------------------------------------------
    try:
        libro_compra = kwargs['libro_compra']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if libro_compra:
        cabecera = Element('LC')
        idte.append(cabecera)

        # Add hijos cabeceza

        for a in libro_compra:
            try:
                registro_lc                 = SubElement(cabecera, 'reg_LC')

                tipo_documento_lc           = SubElement(registro_lc, 'TipoDoc_LC').text                = a['tipo_documento']
                folio_documento             = SubElement(registro_lc, 'folioDoc_LC').text               = a['folio_documento']
                rut_proveedor               = SubElement(registro_lc, 'rutproveedor').text              = a['rut_proveedor']
                razon_social_proveedor      = SubElement(registro_lc, 'razonsocial_proveedor').text     = a['razon_social_prov']
                folio_interno               = SubElement(registro_lc, 'foliointerno_LC').text           = a['folio_interno']
                codigo_sucursal             = SubElement(registro_lc, 'cod_sucursal_LC').text           = a['codigo_sucursal']
                anulado_lc                  = SubElement(registro_lc, 'anulado_LC').text                = a['anulado']
                tasa_iva                    = SubElement(registro_lc, 'tasa_iva_LC').text               = a['tasa_iva']
                fecha_emision               = SubElement(registro_lc, 'fecha_emision_LC').text          = a['fecha_emision']
                afecto_lc                   = SubElement(registro_lc, 'afecto_LC').text                 = a['afecto']
                exento_lc                   = SubElement(registro_lc, 'exento_LC').text                 = a['exento']
                iva_recuperable             = SubElement(registro_lc, 'iva_recup_LC').text              = a['iva_recuperable']
                total_lc                    = SubElement(registro_lc, 'total_LC').text                  = a['total']
                iva_activo_fijo             = SubElement(registro_lc, 'iva_activo_fijo').text           = a['iva_activo_fijo']
                monto_activo_fijo           = SubElement(registro_lc, 'MntActivoFijo').text             = a['monto_activo_fijo']
                iva_no_recuperable_1        = SubElement(registro_lc, 'iva_no_recup1').text             = a['iva_no_recup_1']
                iva_no_recuperable_2        = SubElement(registro_lc, 'iva_no_recup2').text             = a['iva_no_recup_2']
                iva_no_recuperable_3        = SubElement(registro_lc, 'iva_no_recup3').text             = a['iva_no_recup_3']
                iva_no_recuperable_4        = SubElement(registro_lc, 'iva_no_recup4').text             = a['iva_no_recup_4']
                iva_no_recuperable_9        = SubElement(registro_lc, 'iva_no_recup9').text             = a['iva_no_recup_9']
                iva_uso_comun               = SubElement(registro_lc, 'iva_uso_comun').text             = a['iva_uso_comun']
                impuesto_sin_derecho_cred   = SubElement(registro_lc, 'imp_sin_derecho_credit').text    = a['imp_sin_derecho_credito']
                iva_retenido                = SubElement(registro_lc, 'iva_retenido_LC').text           = a['iva_retenido']
                iva_no_retenido             = SubElement(registro_lc, 'iva_no_retenido_LC').text        = a['iva_no_retenido']
                impuesto_tabaco_puros       = SubElement(registro_lc, 'imp_tabacos_puros').text         = a['imp_tabaco_puros']
                impuesto_tabaco_cigarros    = SubElement(registro_lc, 'imp_tabacos_cig').text           = a['imp_tabaco_cig']
                impuesto_tabaco_elaborado   = SubElement(registro_lc, 'imp_tabacos_elab').text          = a['imp_tabaco_elab']
                impuesto_vehiculo           = SubElement(registro_lc, 'imp_vehiculos_auto').text        = a['impu_vehiculo']
                impuesto_adicionales        = SubElement(registro_lc, 'imp_adicionales').text           = a['imp_adicional']
            except Exception as e:
                error ="libro compra: no se encuentra dato " +str(e.args[0]).strip()+" en el diccionario enviado."
                return error, xml



    #------------------------------------- IMPUESTOS RETENIDOS LC ------------------------------------------------------
    try:
        impuestos_retenidos = kwargs['impuesto_retenido_lc']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip()+ " en el diccionario enviado."
        return error, xml

    if impuestos_retenidos:
        impuestos = Element('IR_LC')
        idte.append(impuestos)

        # Add hijos impuestos

        for a in impuestos_retenidos:
            try:
                registro_impuestos_lc       = SubElement(impuestos, 'reg_IR_LC')

                tipo_documento_ir_lc                = SubElement(registro_impuestos_lc, 'TipoDoc_IR_LC').text       = a['tipo_doc_ir']
                folio_documento_ir                  = SubElement(registro_impuestos_lc, 'folioDoc_IR_LC').text      = a['folio_doc_ir']
                rut_proveedor_ir                    = SubElement(registro_impuestos_lc, 'rutproveedor_IR_LC').text  = a['rut_provedor_ir']
                iva_margen_comercializacion         = SubElement(registro_impuestos_lc, 'cod14_IR_LC').text         = a['iva_margen_comerc']
                iva_retenido_total                  = SubElement(registro_impuestos_lc, 'cod15_IR_LC').text         = a['iva_retenido_total']
                iva_anticipado_faenamiento_carne    = SubElement(registro_impuestos_lc, 'cod17_IR_LC').text         = a['iva_anticipado_faenamiento']
                iva_anticipado_carne                = SubElement(registro_impuestos_lc, 'cod18_IR_LC').text         = a['iva_anticipado_carne']
                iva_anticipado_harina               = SubElement(registro_impuestos_lc, 'cod19_IR_LC').text         = a['iva_anticipado_harina']
                iva_retenido_legumbres              = SubElement(registro_impuestos_lc, 'cod30_IR_LC').text         = a['iva_retenido_legumbre']
                iva_retenido_silvestres             = SubElement(registro_impuestos_lc, 'cod31_IR_LC').text         = a['iva_retenido_silvestres']
                iva_retenido_ganado                 = SubElement(registro_impuestos_lc, 'cod32_IR_LC').text         = a['iva_retenido_ganado']
                iva_retenido_madera                 = SubElement(registro_impuestos_lc, 'cod33_IR_LC').text         = a['iva_retenido_madera']
                iva_retenido_trigo                  = SubElement(registro_impuestos_lc, 'cod34_IR_LC').text         = a['iva_retenido_trigo']
                iva_retenido_arroz                  = SubElement(registro_impuestos_lc, 'cod36_IR_LC').text         = a['iva_retenido_arroz']
                iva_retenido_hidrobiolo             = SubElement(registro_impuestos_lc, 'cod37_IR_LC').text         = a['iva_retenido_hidrobiolo']
                iva_retenido_chatarra               = SubElement(registro_impuestos_lc, 'cod38_IR_LC').text         = a['tipo_cta_pago']
                iva_retenido_ppa                    = SubElement(registro_impuestos_lc, 'cod39_IR_LC').text         = a['iva_retenido_chatarra']
                iva_retenido_construccion           = SubElement(registro_impuestos_lc, 'cod41_IR_LC').text         = a['iva_retenido_construccion']
                impuesto_adicional_art_37_abc       = SubElement(registro_impuestos_lc, 'cod23_IR_LC').text         = a['impuesto_adicional_art_37_abc']
                impuesto_adicional_art_37_ehil      = SubElement(registro_impuestos_lc, 'cod44_IR_LC').text         = a['impuesto_adicional_art_37_ehil']
                impuesto_adicional_art_37_j         = SubElement(registro_impuestos_lc, 'cod45_IR_LC').text         = a['impuesto_adicional_art_37_j']
                impuesto_art_42_letra_b             = SubElement(registro_impuestos_lc, 'cod24_IR_LC').text         = a['impuesto_art_42_letra_b']
                impuesto_art_42_letra_c_1           = SubElement(registro_impuestos_lc, 'cod25_IR_LC').text         = a['impuesto_art_42_letra_c_1']
                impuesto_art_42_letra_c_2           = SubElement(registro_impuestos_lc, 'cod26_IR_LC').text         = a['impuesto_art_42_letra_c_2']
                impuesto_art_42_letra_a             = SubElement(registro_impuestos_lc, 'cod27_IR_LC').text         = a['impuesto_art_42_letra_a']
                impuesto_art_42_letra_a_2           = SubElement(registro_impuestos_lc, 'cod271_IR_LC').text        = a['impuesto_art_42_letra_a_2']
                impuesto_especifico_diesel          = SubElement(registro_impuestos_lc, 'cod28_IR_LC').text         = a['impuesto_especifico_diesel']
                recuperacion_imp_diesel_transp      = SubElement(registro_impuestos_lc, 'cod29_IR_LC').text         = a['recuperacion_imp_diesel_transp']
                impuesto_especifico_gasolina        = SubElement(registro_impuestos_lc, 'cod35_IR_LC').text         = a['impuesto_especifico_gasolina']
                iva_retenido_cartones               = SubElement(registro_impuestos_lc, 'cod47_IR_LC').text         = a['iva_retenido_cartones']
                iva_retenido_frambuesas_pasas       = SubElement(registro_impuestos_lc, 'cod48_IR_LC').text         = a['iva_retenido_frambuesas_pasas']
                factura_compra_bolsa_prod_chile     = SubElement(registro_impuestos_lc, 'cod49_IR_LC').text         = a['indicador_monto_neto']
                iva_margen_comer_instru_prepago     = SubElement(registro_impuestos_lc, 'cod50_IR_LC').text         = a['iva_margen_comer_instru_prepago']
                impuesto_gas_natural                = SubElement(registro_impuestos_lc, 'cod51_IR_LC').text         = a['impuesto_gas_natural']
                impuesto_gas_licuado                = SubElement(registro_impuestos_lc, 'cod52_IR_LC').text         = a['impuesto_gas_licuado']
                impuesto_retenido_suplementeros     = SubElement(registro_impuestos_lc, 'cod53_IR_LC').text         = a['impuesto_retenido_suplementeros']
                impuesto_retenido_fact_inicio       = SubElement(registro_impuestos_lc, 'cod60_IR_LC').text         = a['impuesto_retenido_fact_inicio']

            except Exception as e:
                error ="impuestos: no se encuentra dato " +str(e.args[0]).strip()+" en el diccionario enviado."
                return error, xml


    xml = etree.tostring(idte, short_empty_elements=False,  method='xml')

    return error, xml.decode()

def crear_xml_libro_venta(**kwargs):
    """
        función que permite realizar la creación del xml del libro de ventas
    :param kwargs: diccionario de datos del libro de ventas
    :return: retorna una variable la cual contiene el xml, ademas de una variable de error si es que ocurrio algún hecho
    que afecto la creacion del xml
    """
    xml = ''
    error = ''
    idte = Element('IDTE_LV')

    # ------------------------------------- GENERAL ---------------------------------------------------------------------
    general = Element('General')
    idte.append(general)

    # Add hijos general
    try:

        periodo_libro           = SubElement(general, 'periodo').text               = kwargs['periodo_libro']
        rectificatoria          = SubElement(general, 'rectificatoria').text        = kwargs['rectificatoria']
        codigo_rectificatoria   = SubElement(general, 'cod_rectificatoria').text    = kwargs['cod_rectificatoria']
        notificacion            = SubElement(general, 'notificacion').text          = kwargs['notificacion']
        numero_notificacion     = SubElement(general, 'num_notificacion').text      = kwargs['num_notificacion']

    except Exception as e:
        error = "General: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    # ------------------------------------- LIBRO VENTA ----------------------------------------------------------------
    try:
        libro_venta = kwargs['libro_venta']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if libro_venta:
        cabecera = Element('LV')
        idte.append(cabecera)

        # Add hijos cabeceza

        for a in libro_venta:
            try:
                registro_lc = SubElement(cabecera, 'reg_LV')

                tipo_documento_lv       = SubElement(registro_lc, 'TipoDoc_LV').text                = a['tipo_documento_lv']
                folio_documento         = SubElement(registro_lc, 'folioDoc_LV').text               = a['folio_documento']
                anulado_lv              = SubElement(registro_lc, 'anulado_LV').text                = a['anulado_lv']
                tasa_iva                = SubElement(registro_lc, 'tasa_iva').text                  = a['tasa_iva']
                fecha_emision           = SubElement(registro_lc, 'fecha_emision').text             = a['fecha_emision']
                rut_cliente             = SubElement(registro_lc, 'rutcliente').text                = a['rut_cliente']
                razon_social            = SubElement(registro_lc, 'razonsocial_cliente').text       = a['razon_social']
                exento_lv               = SubElement(registro_lc, 'exento').text                    = a['exento_lv']
                afecto_lv               = SubElement(registro_lc, 'afecto').text                    = a['afecto_lv']
                iva_recuperable         = SubElement(registro_lc, 'iva_recup').text                 = a['iva_recuperable']
                total_lv                = SubElement(registro_lc, 'total').text                     = a['total_lv']
                folio_interno           = SubElement(registro_lc, 'foliointerno').text              = a['folio_interno']
                ind_serv_periodo        = SubElement(registro_lc, 'ind_serv_period').text           = a['ind_serv_periodo']
                ind_venta_sin_costo     = SubElement(registro_lc, 'ind_venta_sin_costo').text       = a['ind_venta_sin_costo']
                cod_sucursal            = SubElement(registro_lc, 'cod_sucursal').text              = a['cod_sucursal']
                iva_fuera_plazo         = SubElement(registro_lc, 'iva_fuera_plazo').text           = a['iva_fuera_plazo']
                iva_retenido_total      = SubElement(registro_lc, 'iva_retenido_total').text        = a['iva_retenido_total']
                iva_retenido_parcial    = SubElement(registro_lc, 'iva_retenido_parcial').text      = a['iva_retenido_parcial']
                cred_especial_construc  = SubElement(registro_lc, 'credito_especial_construc').text = a['cred_especial_construc']
                depositos_envases       = SubElement(registro_lc, 'deposito_envases').text          = a['depositos_envases']
                pasajes_nacional        = SubElement(registro_lc, 'pasajes_nacional').text          = a['pasajes_nacional']
                pasajes_internacional   = SubElement(registro_lc, 'pasajes_internacional').text     = a['pasajes_internacional']
                iva_propio              = SubElement(registro_lc, 'IVAPropio').text                 = a['iva_propio']
                iva_tercero             = SubElement(registro_lc, 'IVATerceros').text               = a['iva_tercero']
                art17dl825              = SubElement(registro_lc, 'Art17DL825').text                = a['art17dl825']
                rut_emisor_liq          = SubElement(registro_lc, 'RUTEmisorLiq').text              = a['rut_emisor_liq']
                val_comision_neto       = SubElement(registro_lc, 'ValComNeto').text                = a['val_comision_neto']
                val_comision_exento     = SubElement(registro_lc, 'ValComExe').text                 = a['val_comision_exento']
                val_comision_iva        = SubElement(registro_lc, 'ValComIVA').text                 = a['val_comision_iva']
                ley18211                = SubElement(registro_lc, 'Ley18211').text                  = a['ley18211']

            except Exception as e:

                error = "libro venta: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
                return error , xml

    # ------------------------------------- IMPUESTOS RETENIDOS LIBRO VENTA --------------------------------------------
    try:
        impuestos_retenidos = kwargs['impuesto_retenido_lv']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if impuestos_retenidos:
        impuestos = Element('IR_LV')
        idte.append(impuestos)

        # Add hijos impuestos

        for a in impuestos_retenidos:
            try:
                registro_impuestos_lv = SubElement(impuestos, 'reg_IR_LV')
                tipo_documento_ir_lc            = SubElement(registro_impuestos_lv, 'TipoDoc_IR_LV').text   = a['tipo_doc_ir']
                folio_documento_ir              = SubElement(registro_impuestos_lv, 'folioDoc_IR_LV').text  = a['folio_doc_ir']
                iva_margen_comercializacion     = SubElement(registro_impuestos_lv, 'cod14_IR_LV').text     = a['iva_margen_comerc']
                iva_retenido_total              = SubElement(registro_impuestos_lv, 'cod15_IR_LV').text     = a['iva_retenido_total']
                iva_anticipado_faena_carne      = SubElement(registro_impuestos_lv, 'cod17_IR_LV').text     = a['iva_anticipado_faenamiento']
                iva_anticipado_carne            = SubElement(registro_impuestos_lv, 'cod18_IR_LV').text     = a['iva_anticipado_carne']
                iva_anticipado_harina           = SubElement(registro_impuestos_lv, 'cod19_IR_LV').text     = a['iva_anticipado_harina']
                iva_retenido_legumbres          = SubElement(registro_impuestos_lv, 'cod30_IR_LV').text     = a['iva_retenido_legumbre']
                iva_retenido_silvestres         = SubElement(registro_impuestos_lv, 'cod31_IR_LV').text     = a['iva_retenido_silvestres']
                iva_retenido_ganado             = SubElement(registro_impuestos_lv, 'cod32_IR_LV').text     = a['iva_retenido_ganado']
                iva_retenido_madera             = SubElement(registro_impuestos_lv, 'cod33_IR_LV').text     = a['iva_retenido_madera']
                iva_retenido_trigo              = SubElement(registro_impuestos_lv, 'cod34_IR_LV').text     = a['iva_retenido_trigo']
                iva_retenido_arroz              = SubElement(registro_impuestos_lv, 'cod36_IR_LV').text     = a['iva_retenido_arroz']
                iva_retenido_hidrobiolo         = SubElement(registro_impuestos_lv, 'cod37_IR_LV').text     = a['iva_retenido_hidrobiolo']
                iva_retenido_chatarra           = SubElement(registro_impuestos_lv, 'cod38_IR_LV').text     = a['tipo_cta_pago']
                iva_retenido_ppa                = SubElement(registro_impuestos_lv, 'cod39_IR_LV').text     = a['iva_retenido_chatarra']
                iva_retenido_construccion       = SubElement(registro_impuestos_lv, 'cod41_IR_LV').text     = a['iva_retenido_construccion']
                impuesto_adicional_art_37_abc   = SubElement(registro_impuestos_lv, 'cod23_IR_LV').text     = a['impuesto_adicional_art_37_abc']
                impuesto_adicional_art_37_ehil  = SubElement(registro_impuestos_lv, 'cod44_IR_LV').text     = a['impuesto_adicional_art_37_ehil']
                impuesto_adicional_art_37_j     = SubElement(registro_impuestos_lv, 'cod45_IR_LV').text     = a['impuesto_adicional_art_37_j']
                impuesto_art_42_letra_b         = SubElement(registro_impuestos_lv, 'cod24_IR_LV').text     = a['impuesto_art_42_letra_b']
                impuesto_art_42_letra_c_1       = SubElement(registro_impuestos_lv, 'cod25_IR_LV').text     = a['impuesto_art_42_letra_c_1']
                impuesto_art_42_letra_c_2       = SubElement(registro_impuestos_lv, 'cod26_IR_LV').text     = a['impuesto_art_42_letra_c_2']
                impuesto_art_42_letra_a         = SubElement(registro_impuestos_lv, 'cod27_IR_LV').text     = a['impuesto_art_42_letra_a']
                impuesto_art_42_letra_a_2       = SubElement(registro_impuestos_lv, 'cod271_IR_LV').text    = a['impuesto_art_42_letra_a_2']
                impuesto_especifico_diesel      = SubElement(registro_impuestos_lv, 'cod28_IR_LV').text     = a['impuesto_especifico_diesel']
                recuperacion_imp_diesel_transp  = SubElement(registro_impuestos_lv, 'cod29_IR_LV').text     = a['recuperacion_imp_diesel_transp']
                impuesto_especifico_gasolina    = SubElement(registro_impuestos_lv, 'cod35_IR_LV').text     = a['impuesto_especifico_gasolina']
                iva_retenido_cartones           = SubElement(registro_impuestos_lv, 'cod47_IR_LV').text     = a['iva_retenido_cartones']
                iva_retenido_frambuesas_pasas   = SubElement(registro_impuestos_lv, 'cod48_IR_LV').text     = a['iva_retenido_frambuesas_pasas']
                factura_compra_bolsa_prod_chile = SubElement(registro_impuestos_lv, 'cod49_IR_LV').text     = a['indicador_monto_neto']
                iva_margen_comer_instru_prepago = SubElement(registro_impuestos_lv, 'cod50_IR_LV').text     = a['iva_margen_comer_instru_prepago']
                impuesto_gas_natural            = SubElement(registro_impuestos_lv, 'cod51_IR_LV').text     = a['impuesto_gas_natural']
                impuesto_gas_licuado            = SubElement(registro_impuestos_lv, 'cod52_IR_LV').text     = a['impuesto_gas_licuado']
                impuesto_retenido_suplementeros = SubElement(registro_impuestos_lv, 'cod53_IR_LV').text     = a['impuesto_retenido_suplementeros']
                impuesto_retenido_fact_inicio   = SubElement(registro_impuestos_lv, 'cod60_IR_LV').text     = a['impuesto_retenido_fact_inicio']

            except Exception as e:
                error = "impuestos: no se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
                return error, xml


    # ------------------------------------- LIQUIDACION DE FACTURA  ----------------------------------------------------
    try:
        liquidacion_factura = kwargs['liquidacion_factura']
    except Exception as e:
        error = "No se encuentra dato " + str(e.args[0]).strip() + " en el diccionario enviado."
        return error, xml

    if liquidacion_factura:
        liq_factura = Element('LFRecibida')
        idte.append(liq_factura)

        # Add hijos liquidación factura

        for a in liquidacion_factura:
            try:
                registro_liq_factura = SubElement(liq_factura, 'reg_LFRecibida')



                tipo_doc_liq                        = SubElement(registro_liq_factura, 'TipoDoc_LV').text                   = a['tipo_doc_liq']
                folio_doc_liq                       = SubElement(registro_liq_factura, 'folioDoc_LV').text                  = a['folio_doc_liq']
                rut_emisor_liq                      = SubElement(registro_liq_factura, 'RUTEmisorLiq').text                 = a['rut_emisor_liq']
                anulado_liq                         = SubElement(registro_liq_factura, 'anulado_LV').text                   = a['anulado_liq']
                tasa_iva_liq                        = SubElement(registro_liq_factura, 'tasa_iva').text                     = a['tasa_iva_liq']
                fecha_emision_liq                   = SubElement(registro_liq_factura, 'fecha_emision').text                = a['fecha_emision_liq']
                rut_cliente_liq                     = SubElement(registro_liq_factura, 'rutcliente').text                   = a['rut_cliente_liq']
                razon_social_cliente_liq            = SubElement(registro_liq_factura, 'razonsocial_cliente').text          = a['razon_social_cliente_liq']
                exento_liq                          = SubElement(registro_liq_factura, 'exento').text                       = a['exento_liq']
                afecto_liq                          = SubElement(registro_liq_factura, 'afecto').text                       = a['afecto_liq']
                iva_recup_liq                       = SubElement(registro_liq_factura, 'iva_recup').text                    = a['iva_recup_liq']
                total_liq                           = SubElement(registro_liq_factura, 'total').text                        = a['total_liq']
                folio_interno_liq                   = SubElement(registro_liq_factura, 'foliointerno').text                 = a['folio_interno_liq']
                ind_venta_period_liq                = SubElement(registro_liq_factura, 'ind_serv_period').text              = a['ind_venta_period_liq']
                ind_venta_sin_costo_liq             = SubElement(registro_liq_factura, 'ind_venta_sin_costo').text          = a['ind_venta_sin_costo_liq']
                iva_reten_total_liq                 = SubElement(registro_liq_factura, 'iva_retenido_total').text           = a['iva_reten_total_liq']
                iva_reten_parcial_liq               = SubElement(registro_liq_factura, 'iva_retenido_parcial').text         = a['folio_doc_ir']
                iva_no_reten_liq                    = SubElement(registro_liq_factura, 'iva_no_retenido').text              = a['iva_no_reten_liq']
                cred_parcial_constr_liq             = SubElement(registro_liq_factura, 'credito_especial_construc').text    = a['cred_parcial_constr_liq']
                desposito_envases_liq               = SubElement(registro_liq_factura, 'deposito_envases').text             = a['desposito_envases_liq']
                pasaje_nacional_liq                 = SubElement(registro_liq_factura, 'pasajes_nacional').text             = a['pasaje_nacional_liq']
                pasaje_internacional_liq            = SubElement(registro_liq_factura, 'pasajes_internacional').text        = a['pasaje_internacional_liq']
                iva_propio_liq                      = SubElement(registro_liq_factura, 'IVAPropio').text                    = a['iva_propio_liq']
                iva_tercero_liq                     = SubElement(registro_liq_factura, 'IVATerceros').text                  = a['iva_tercero_liq']
                Art17DL825_liq                      = SubElement(registro_liq_factura, 'Art17DL825').text                   = a['Art17DL825_liq']
                val_comi_neto_liq                   = SubElement(registro_liq_factura, 'ValComNeto').text                   = a['val_comi_neto_liq']
                val_comi_exento_liq                 = SubElement(registro_liq_factura, 'ValComExe').text                    = a['val_comi_exento_liq']
                val_comi_iva_liq                    = SubElement(registro_liq_factura, 'ValComIVA').text                    = a['val_comi_iva_liq']
                Ley18211_liq                        = SubElement(registro_liq_factura, 'Ley18211').text                     = a['Ley18211_liq']
                iva_margen_comercializacion_liq     = SubElement(registro_liq_factura, 'cod14_IR_LV').text                  = a['iva_margen_comerc_liq']
                iva_retenido_total_liq              = SubElement(registro_liq_factura, 'cod15_IR_LV').text                  = a['iva_retenido_total_liq']
                iva_anticipado_faena_carne_liq      = SubElement(registro_liq_factura, 'cod17_IR_LV').text                  = a['iva_anticipado_faenamiento_liq']
                iva_anticipado_carne_liq            = SubElement(registro_liq_factura, 'cod18_IR_LV').text                  = a['iva_anticipado_carne_liq']
                iva_anticipado_harina_liq           = SubElement(registro_liq_factura, 'cod19_IR_LV').text                  = a['iva_anticipado_harina_liq']
                iva_retenido_legumbres_liq          = SubElement(registro_liq_factura, 'cod30_IR_LV').text                  = a['iva_retenido_legumbre_liq']
                iva_retenido_silvestres_liq         = SubElement(registro_liq_factura, 'cod31_IR_LV').text                  = a['iva_retenido_silvestres_liq']
                iva_retenido_ganado_liq             = SubElement(registro_liq_factura, 'cod32_IR_LV').text                  = a['iva_retenido_ganado_liq']
                iva_retenido_madera_liq             = SubElement(registro_liq_factura, 'cod33_IR_LV').text                  = a['iva_retenido_madera_liq']
                iva_retenido_trigo_liq              = SubElement(registro_liq_factura, 'cod34_IR_LV').text                  = a['iva_retenido_trigo_liq']
                iva_retenido_arroz_liq              = SubElement(registro_liq_factura, 'cod36_IR_LV').text                  = a['iva_retenido_arroz_liq']
                iva_retenido_hidrobiolo_liq         = SubElement(registro_liq_factura, 'cod37_IR_LV').text                  = a['iva_retenido_hidrobiolo_liq']
                iva_retenido_chatarra_liq           = SubElement(registro_liq_factura, 'cod38_IR_LV').text                  = a['tipo_cta_pago_liq']
                iva_retenido_ppa_liq                = SubElement(registro_liq_factura, 'cod39_IR_LV').text                  = a['iva_retenido_chatarra_liq']
                iva_retenido_construccion_liq       = SubElement(registro_liq_factura, 'cod41_IR_LV').text                  = a['iva_retenido_construccion_liq']
                impuesto_adicional_art_37_abc_liq   = SubElement(registro_liq_factura, 'cod23_IR_LV').text                  = a['impuesto_adicional_art_37_abc_liq']
                impuesto_adicional_art_37_ehil_liq  = SubElement(registro_liq_factura, 'cod44_IR_LV').text                  = a['impuesto_adicional_art_37_ehil_liq']
                impuesto_adicional_art_37_j_liq     = SubElement(registro_liq_factura, 'cod45_IR_LV').text                  = a['impuesto_adicional_art_37_j_liq']
                impuesto_art_42_letra_b_liq         = SubElement(registro_liq_factura, 'cod24_IR_LV').text                  = a['impuesto_art_42_letra_b_liq']
                impuesto_art_42_letra_c_1_liq       = SubElement(registro_liq_factura, 'cod25_IR_LV').text                  = a['impuesto_art_42_letra_c_1_liq']
                impuesto_art_42_letra_c_2_liq       = SubElement(registro_liq_factura, 'cod26_IR_LV').text                  = a['impuesto_art_42_letra_c_2_liq']
                impuesto_art_42_letra_a_liq         = SubElement(registro_liq_factura, 'cod27_IR_LV').text                  = a['impuesto_art_42_letra_a_liq']
                impuesto_art_42_letra_a_2_liq       = SubElement(registro_liq_factura, 'cod271_IR_LV').text                 = a['impuesto_art_42_letra_a_2_liq']
                impuesto_especifico_diesel_liq      = SubElement(registro_liq_factura, 'cod28_IR_LV').text                  = a['impuesto_especifico_diesel_liq']
                recuperacion_imp_diesel_transp_liq  = SubElement(registro_liq_factura, 'cod29_IR_LV').text                  = a['recuperacion_imp_diesel_transp_liq']
                impuesto_especifico_gasolina_liq    = SubElement(registro_liq_factura, 'cod35_IR_LV').text                  = a['impuesto_especifico_gasolina_liq']
                iva_retenido_cartones_liq           = SubElement(registro_liq_factura, 'cod47_IR_LV').text                  = a['iva_retenido_cartones_liq']
                iva_retenido_frambuesas_pasas_liq   = SubElement(registro_liq_factura, 'cod48_IR_LV').text                  = a['iva_retenido_frambuesas_pasas_liq']
                factura_compra_bolsa_prod_chile_liq = SubElement(registro_liq_factura, 'cod49_IR_LV').text                  = a['indicador_monto_neto_liq']
                iva_margen_comer_instru_prepago_liq = SubElement(registro_liq_factura, 'cod50_IR_LV').text                  = a['iva_margen_comer_instru_prepago_liq']
                impuesto_gas_natural_liq            = SubElement(registro_liq_factura, 'cod51_IR_LV').text                  = a['impuesto_gas_natural_liq']
                impuesto_gas_licuado_liq            = SubElement(registro_liq_factura, 'cod52_IR_LV').text                  = a['impuesto_gas_licuado_liq']
                impuesto_retenido_suplementeros_liq = SubElement(registro_liq_factura, 'cod53_IR_LV').text                  = a['impuesto_retenido_suplementeros_liq']
                impuesto_retenido_fact_inicio_liq   = SubElement(registro_liq_factura, 'cod60_IR_LV').text                  = a['impuesto_retenido_fact_inicio_liq']

            except Exception as e:
                error = "liquidacion factura: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                return error, xml


        # ------------------------------------- BOLETAS  ---------------------------------------------------------------

        try:
            boletas = kwargs['boletas']
        except Exception as e:
            error = "No se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
            return error, xml

        if boletas:
            boleta_xml = Element('total_boletas')
            idte.append(boleta_xml)

            # Add hijos boletas

            for a in boletas:
                try:
                    registro_boletas = SubElement(boleta_xml, 'reg_total_boletas')

                    tipo_doc_bol                = SubElement(registro_boletas, 'TipoDoc_totalLV').text                  = a['tipo_doc_bol']
                    cantidad_bol                = SubElement(registro_boletas, 'cant_doc').text                         = a['cantidad_bol']
                    cant_anulado_bol            = SubElement(registro_boletas, 'cant_anulados').text                    = a['cant_anulado_bol']
                    total_afecto_bol            = SubElement(registro_boletas, 'total_afecto').text                     = a['total_afecto_bol']
                    total_exento_bol            = SubElement(registro_boletas, 'total_exento').text                     = a['total_exento_bol']
                    total_iva_recup_bol         = SubElement(registro_boletas, 'total_iva_recup').text                  = a['total_iva_recup_bol']
                    total_monto_bol             = SubElement(registro_boletas, 'total_montos').text                     = a['total_monto_bol']
                    total_iva_fuera_plazo_bol   = SubElement(registro_boletas, 'total_iva_fuera_plazo').text            = a['total_iva_fuera_plazo_bol']
                    total_iva_rete_total_bol    = SubElement(registro_boletas, 'total_iva_retenido_total').text         = a['total_iva_rete_total_bol']
                    total_iva_rete_parcial_bol  = SubElement(registro_boletas, 'total_iva_retenido_parcial').text       = a['total_iva_rete_parcial_bol']
                    total_cred_espe_constr_bol  = SubElement(registro_boletas, 'total_credito_especial_constru').text   = a['total_cred_espe_constr_bol']
                    total_despo_envase_bol      = SubElement(registro_boletas, 'total_deposito_envases').text           = a['total_despo_envase_bol']
                    total_iva_no_rete_bol       = SubElement(registro_boletas, 'total_iva_no_retenido').text            = a['total_iva_no_rete_bol']
                    total_pasaje_naci_bol       = SubElement(registro_boletas, 'total_pasajes_nacional').text           = a['total_pasaje_naci_bol']
                    total_pasaje_intern_bol     = SubElement(registro_boletas, 'total_pasajes_internac').text           = a['total_pasaje_intern_bol']
                    total_iva_propio_bol        = SubElement(registro_boletas, 'total_iva_propio').text                 = a['total_iva_propio_bol']
                    total_iva_terce_bol         = SubElement(registro_boletas, 'total_iva_terceros').text               = a['total_iva_terce_bol']
                    total_val_com_neto_bol      = SubElement(registro_boletas, 'TotValComNeto').text                    = a['total_val_com_neto_bol']
                    total_val_com_exento_bol    = SubElement(registro_boletas, 'TotValComExe').text                     = a['total_val_com_exento_bol']
                    total_val_com_iva_bol       = SubElement(registro_boletas, 'TotValComIVA').text                     = a['total_val_com_iva_bol']
                    total_ley18211_bol          = SubElement(registro_boletas, 'TotLey18211').text                      = a['total_ley18211_bol']

                except Exception as e:
                    error = "boletas: no se encuentra dato " +str(e.args[0]).strip()+ " en el diccionario enviado."
                    return error, xml

    xml = etree.tostring(idte, short_empty_elements=False, method='xml')

    return error, xml.decode()

def procesar_lcv_xml(client, id_dte_empresa, tipo_libro, id_hist_lcv, accion, traza, xml):

    """
        función que permite realizar el envio del xml del libro de compras o ventas a el sistema de IDTE

    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param tipo_libro: tipo de libro a enviar C = compras y V= ventas
    :param id_hist_lcv: identificador o clave primaria de libro en las tablas de IDTE, este debe ser añomesdia 20160815
    :param accion: indica que operación se va a ejecutar sobre el Web Service.
                    1- procesar y enviar , 2- Procesar y bloquear , 4- Borrar registro(si no esta enviado al sii)
                    5- desbloquear
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :param xml: string del xml del libro de compras o ventas
    :return: retorna un objeto el cual contiene los datos del estado del proceso
    """
    procesar_lcv = client.service.procesar_LCV_XML(id_dte_empresa, tipo_libro, id_hist_lcv, accion, traza, xml)

    return procesar_lcv

def get_estado_lcv(client, id_dte_empresa, id_hist_lcv, traza):

    """
        función que permite consultar el estado del libro enviado a el S.I.I.,
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param id_hist_lcv: identificador o clave primaria de libro en las tablas de IDTE, este debe ser añomesdia 20160815
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return: retorna un objeto el cual contiene los datos del estado del proceso
    """
    estado_lcv = client.service.get_estado(id_dte_empresa, id_hist_lcv, traza)

    return estado_lcv

def get_msg_rechazo_sii_lcv(client, id_dte_empresa, id_hist_lcv, traza):

    """
        función que permite realizar la obtencción del mensaje de rechazo del libro de compras o ventas indicado por el
        S.I.I

    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param id_hist_lcv: identificador o clave primaria de libro en las tablas de IDTE, este debe ser añomesdia 20160815
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return: retorna un objeto el cual contiene los datos del estado del proceso
    """
    mensaje_rechazo_lcv_sii = client.service.get_msg_rechazo_SII(id_dte_empresa, id_hist_lcv, traza)

    return  mensaje_rechazo_lcv_sii

def get_log_errores_lcv(client, id_dte_empresa, id_hist_lcv, traza):

    """
        función que permite realiza la obtención del log de error del envio del libro de compras o ventas
    :param client: cliente de conexión con el servidor de IDTE
    :param id_dte_empresa: identificador de empresa asociado a IDTE
    :param id_hist_lcv: identificador o clave primaria de libro en las tablas de IDTE, este debe ser añomesdia 20160815
    :param traza: nivel de detalle de la traza o log donde 1 indica solo registra los errores y valor 2 indica que registra
                  todo.
    :return: retorna un objeto el cual contiene los datos del estado del proceso
    """
    log_errores_lcv = client.service.get_log_errores(id_dte_empresa, id_hist_lcv, traza)

    return log_errores_lcv