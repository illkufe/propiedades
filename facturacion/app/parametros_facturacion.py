from facturacion.models import *
from django.db.models import *
from django.db import transaction
from decimal import Decimal
import json


from utilidades.views import formato_numero_sin_miles
from administrador.views import Cliente


@transaction.atomic()
def guarda_parametros_facturacion(**kwargs):

    persona             = kwargs['persona']
    codigo_conexion     = kwargs['codigo_conexion']
    motor_emision       = kwargs['motor_emision']
    detalle_conexion    = kwargs['detalle_conexion']
    id_parametro = 0
    error = ''

    detalle = json.loads(detalle_conexion)

    try:
        datos_persona = Cliente.objects.get(id=persona)

        parametro = ParametrosFacturacion()
        parametro.persona_id            = persona
        parametro.id_fiscal_persona     = datos_persona.rut
        parametro.nombre_persona        = datos_persona.nombre
        parametro.codigo_conexion       = codigo_conexion
        parametro.motor_emision_id      = motor_emision
        parametro.save()

        id_parametro = parametro.id
    except Exception as e:
        error = "Error Parametros " +str(e)


    if id_parametro != 0:
        try:
            for a in detalle:
                conexion = ConexionFacturacion()
                conexion.parametro_facturacion_id = id_parametro
                conexion.codigo_contexto    = a['codigo_contexto']
                conexion.host               = a['host']
                conexion.url                = a['url']
                conexion.puerto             = a['puerto']
                conexion.save()

        except Exception as e:
            error = "Error Conexion " + str(e)

    return error

@transaction.atomic()
def editar_parametros_facturacion(**kwargs):

    persona             = kwargs['persona']
    codigo_conexion     = kwargs['codigo_conexion']
    detalle_conexion    = kwargs['detalle_conexion']
    motor_emision       = kwargs['motor_emision']
    id_parametro        = kwargs['id_parametro']
    error = ''

    detalle = json.loads(detalle_conexion)

    try:
        datos_persona = Cliente.objects.get(id=persona)

        parametro = ParametrosFacturacion.objects.get(id=id_parametro)
        parametro.persona_id        = persona
        parametro.id_fiscal_persona = datos_persona.rut
        parametro.nombre_persona    = datos_persona.nombre
        parametro.codigo_conexion   = codigo_conexion
        parametro.motor_emision_id  = motor_emision
        parametro.save()

    except Exception as e:
        error = "Error Parametros " + str(e)


    if not error:
        try:
            for a in detalle:

                if a['id_detalle'] == '':
                    nuevo_conexion = ConexionFacturacion()
                    nuevo_conexion.parametro_facturacion_id = id_parametro
                    nuevo_conexion.codigo_contexto  = a['codigo_contexto']
                    nuevo_conexion.host             = a['host']
                    nuevo_conexion.url              = a['url']
                    nuevo_conexion.puerto           = a['puerto']
                    nuevo_conexion.save()
                    nuevo_conexion.save()
                else:
                    if a['borrar']:
                        delete_conexion = ConexionFacturacion.objects.get(id=a['id_detalle'])
                        delete_conexion.delete()
                    else:
                        editar_conexion = ConexionFacturacion(id=a['id_detalle'])
                        editar_conexion.parametro_facturacion_id    = id_parametro
                        editar_conexion.codigo_contexto             = a['codigo_contexto']
                        editar_conexion.host                        = a['host']
                        editar_conexion.url                         = a['url']
                        editar_conexion.puerto                      = a['puerto']
                        editar_conexion.save()

        except Exception as e:
            error = "Error Conexion " + str(e)

    return error

def calculo_iva_total_documento(valor_neto, tasa_iva):
    try:
        valor_iva   = valor_neto * Decimal((tasa_iva /100))
        valor_total = valor_neto + valor_iva
    except Exception as a:
        error =a
    valores = [
        valor_neto,
        valor_iva,
        valor_total
    ]

    return valores