import datetime
from django.db import models
from django.core.exceptions import ValidationError

class Certificacion(models.Model):
    ESTADO_CHOICES = (
        ('BOR', 'Borrador'),
        ('SOL', 'Solicitado'),
        ('APR', 'Aprobado'),
        ('CAN', 'Cancelado'),
        ('LIQ', 'Liquidado'),
    )
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código", editable=False) # Auto-generated
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha") # Default hoy
    descripcion = models.TextField(verbose_name="Descripción")
    estado = models.CharField(max_length=3, choices=ESTADO_CHOICES, default='BOR', verbose_name="Estado")
    
    # Reference to Unidad in Planificación
    unidad = models.ForeignKey('planificacion.Unidad', on_delete=models.PROTECT, verbose_name="Unidad Solicitante")
    
    monto_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Monto Total", editable=False)
    pdf_respaldo = models.FileField(upload_to='certificaciones/', blank=True, null=True, verbose_name="PDF Respaldo")

    class Meta:
        db_table = 'fi_certificacion'
        verbose_name = 'Certificación Presupuestaria'
        verbose_name_plural = 'Certificaciones Presupuestarias'
        ordering = ['-codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:50]}"

    def save(self, *args, **kwargs):
        from django.db import transaction
        if not self.codigo:
            # Atomic transaction to prevents race conditions
            with transaction.atomic():
                # Lock the table (or rows) to ensure sequential generation
                # We filter by a dummy condition or simply lock the last record to serialize access
                # For high contention, a separate Sequence model is better, but here we lock based on prefix.
                
                year = datetime.date.today().year
                prefix = f"CP-{year}-"
                
                # select_for_update() locks the selected rows until the transaction ends.
                # We look for the last created code with this prefix.
                # Note: If no rows exist yet, select_for_update won't lock anything. 
                # So we might need a more robust approach if massive concurrency is expected from 0.
                # For this specific legacy-style logic:
                last_qs = Certificacion.objects.filter(codigo__startswith=prefix).order_by('codigo').select_for_update()
                last = last_qs.last()

                if last:
                    try:
                        seq = int(last.codigo.split('-')[-1]) + 1
                    except ValueError:
                        seq = 1
                else:
                    seq = 1
                
                self.codigo = f"{prefix}{seq:03d}"
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class CertificacionDetalle(models.Model):
    certificacion = models.ForeignKey(Certificacion, on_delete=models.CASCADE, related_name='detalles', verbose_name="Certificación")
    # Reference to Presupuesto in Presupuestos
    partida = models.ForeignKey('presupuestos.Presupuesto', on_delete=models.PROTECT, verbose_name="Partida")
    monto = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Monto")

    class Meta:
        db_table = 'fi_certificacion_detalle'
        verbose_name = 'Detalle de Certificación'
        verbose_name_plural = 'Detalles de Certificación'

    def __str__(self):
        return f"{self.certificacion.codigo} - {self.partida}"

    def clean(self):
        # Validacion Critica: Saldo Disponible >= Monto
        if self.monto and self.partida:
             if self.monto > self.partida.saldo_disponible: 
                 raise ValidationError(f"Saldo insuficiente en partida {self.partida}. Disponible: {self.partida.saldo_disponible}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Recalcular total de la certificación
        # Importante: Esto asume que se llama después de guardar el detalle.
        # Si esto falla por recursión, mover a señal post_save.
        # Por simplicidad ahora, actualizamos directamente el padre.