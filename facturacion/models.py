from django.db import models
from accounts.models import User



class ParametrosFacturacion(models.Model):
    persona             = models.ForeignKey('administrador.Cliente', blank=True,null=True, on_delete=models.PROTECT)
    id_fiscal_persona   = models.CharField(max_length=20, null=True, blank=True)
    nombre_persona      = models.CharField(max_length=100, null=True, blank=True)
    codigo_conexion     = models.CharField(max_length=100)
    motor_emision       = models.ForeignKey('MotorFacturacion', on_delete=models.PROTECT)

    class Meta:
        ordering = ["codigo_conexion"]
        verbose_name_plural = "Parametros de Facturación"


    def __str__(self):
        return '%s' % (self.codigo_conexion)

class ConexionFacturacion(models.Model):
    parametro_facturacion   = models.ForeignKey(ParametrosFacturacion, on_delete=models.PROTECT)
    codigo_contexto         = models.CharField(max_length=50, null=True, blank=True)
    host                    = models.CharField(max_length=20, null=True, blank=True)
    url                     = models.CharField(max_length=30, null=True, blank=True)
    puerto                  = models.IntegerField()

    class Meta:
        ordering = ["codigo_contexto"]
        verbose_name_plural = "Conexión de Facturación"


    def __str__(self):
        return '%s' % (self.codigo_contexto)

class FoliosDocumentosElectronicos(models.Model):
    tipo_dte            = models.IntegerField()
    secuencia_caf       = models.IntegerField()
    rango_inicial       = models.IntegerField()
    rango_final         = models.IntegerField()
    folio_actual        = models.IntegerField()
    xml_caf             = models.TextField()
    fecha_ingreso_caf   = models.DateTimeField()
    operativo           = models.BooleanField(default=False)
    usuario_creacion    = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        ordering = ["tipo_dte"]
        verbose_name_plural = "Folios Documentos Electronicos"

    def __str__(self):
        return '%s' % (self.folio_actual)


class MotorFacturacion(models.Model):

    nombre      = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=250)
    activo      = models.BooleanField(default=False)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Motor de Facturación"

    def __str__(self):
        return '%s' % (self.nombre)

class CodigoConcepto(models.Model):

    codigo      = models.IntegerField()
    nombre      = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=250)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Codigos de Conceptos"

    def __str__(self):
        return '%s' % (self.nombre)

# class DetalleDocumentosEmitidos(models.Model):
#     aplicacion = models.CharField(max_length=20)
#     tipo_documento = models.IntegerField()
#     folio_emitido = models.IntegerField()
#     fecha_emision = models.DateTimeField()
#     usuario_emision = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)
#     fecha_reemision = models.DateTimeField()
#     usuario_reemision = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)
#     folios_documento = models.ForeignKey(FoliosDocumentosElectronicos, blank=True, null=True, on_delete=models.PROTECT)
#
#     class Meta:
#         ordering = ['aplicacion','tipo_documento','folio_emitido']
#         verbose_name_plural = "FDetalle de Documentos Emitidos"
#
#     def __str__(self):
#         return '%s' % (self.folio_emitido)

