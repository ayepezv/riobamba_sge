from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.planificacion.models import PACLinea

class InformeNecesidad(models.Model):
    pac_linea = models.ForeignKey(PACLinea, on_delete=models.CASCADE, verbose_name="Línea del PAC", help_text="Seleccione la línea del PAC para heredar información.")
    numero_informe = models.CharField(max_length=50, unique=True, verbose_name="Número de Informe", help_text="Ej: INF-NEC-2026-001")
    fecha_solicitud = models.DateField(default=timezone.now, verbose_name="Fecha de Solicitud")
    objeto_contratacion = models.TextField(verbose_name="Objeto de Contratación", help_text="Heredado del PAC, pero editable.")
    antecedentes = models.TextField(verbose_name="Antecedentes", help_text="Describa los antecedentes de la necesidad.")
    base_legal = models.TextField(verbose_name="Base Legal", default="Reglamento General de la LOSNCP, Art. 65...", help_text="Fundamentación legal.")
    analisis_necesidad = models.TextField(verbose_name="Análisis de Necesidad", help_text="Justificación de la necesidad.")
    conclusion_recomendacion = models.TextField(verbose_name="Conclusión y Recomendación", help_text="Conclusiones y recomendaciones finales.")
    elaborado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='informes_elaborados', verbose_name="Elaborado Por")
    autorizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='informes_autorizados', verbose_name="Autorizado Por (Jefe de Área)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cp_informe_necesidad'
        verbose_name = "Informe de Necesidad"
        verbose_name_plural = "Informes de Necesidad"

    def save(self, *args, **kwargs):
        if not self.objeto_contratacion and self.pac_linea:
            self.objeto_contratacion = self.pac_linea.detalle
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_informe} - {self.objeto_contratacion[:50]}"
