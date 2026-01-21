from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Creación'),
        ('UPDATE', 'Edición'),
        ('DELETE', 'Eliminación'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('VIEW', 'Vista'),
        ('OTHER', 'Otro'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario")
    accion = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Acción")
    ruta = models.CharField(max_length=255, verbose_name="Ruta / URL")
    metodo = models.CharField(max_length=10, verbose_name="Método HTTP")
    
    # Generic Relations for specific objects
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    detalle_cambios = models.JSONField(null=True, blank=True, verbose_name="Detalle de Cambios (JSON)")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    
    # Traceability metrics
    duracion = models.FloatField(help_text="Duración de la operación en segundos", verbose_name="Duración (s)")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    class Meta:
        db_table = 'au_audit_log'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']

    def __str__(self):
        user = self.usuario.username if self.usuario else 'Anónimo'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {user} - {self.accion} ({self.duracion}s)"
