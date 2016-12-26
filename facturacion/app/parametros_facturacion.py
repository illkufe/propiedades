from decimal import Decimal

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