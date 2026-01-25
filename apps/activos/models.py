from django.db import models

class VistaDepreciacionBien(models.Model):
    idbien = models.IntegerField(primary_key=True)
    codigo = models.CharField(max_length=255)
    codcue = models.CharField(max_length=255)
    nombre_cuenta = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    fecha_adquisicion = models.DateField(null=True, blank=True)
    
    # InspectDB revela FloatField, no DecimalField. Ajustamos para evitar 0.00 erróneos.
    costo_inicial = models.FloatField(null=True, blank=True)
    estado = models.IntegerField(null=True, blank=True)
    valor_en_libros_actual = models.FloatField(null=True, blank=True)

    # Campos de depreciación anual (dinámicos) - Ajustados a FloatField
    dep_2005 = models.FloatField(null=True, blank=True)
    dep_2006 = models.FloatField(null=True, blank=True)
    dep_2007 = models.FloatField(null=True, blank=True)
    dep_2008 = models.FloatField(null=True, blank=True)
    dep_2009 = models.FloatField(null=True, blank=True)
    dep_2010 = models.FloatField(null=True, blank=True)
    dep_2011 = models.FloatField(null=True, blank=True)
    dep_2012 = models.FloatField(null=True, blank=True)
    dep_2013 = models.FloatField(null=True, blank=True)
    dep_2014 = models.FloatField(null=True, blank=True)
    dep_2015 = models.FloatField(null=True, blank=True)
    dep_2016 = models.FloatField(null=True, blank=True)
    dep_2017 = models.FloatField(null=True, blank=True)
    dep_2018 = models.FloatField(null=True, blank=True)
    dep_2019 = models.FloatField(null=True, blank=True)
    dep_2020 = models.FloatField(null=True, blank=True)
    dep_2021 = models.FloatField(null=True, blank=True)
    dep_2022 = models.FloatField(null=True, blank=True)
    dep_2023 = models.FloatField(null=True, blank=True)
    dep_2024 = models.FloatField(null=True, blank=True)
    dep_2025 = models.FloatField(null=True, blank=True)
    dep_2026 = models.FloatField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'vista_depreciacion_anual_bienes'
        verbose_name = 'Depreciación de Bien'
        verbose_name_plural = 'Depreciación de Bienes'

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
