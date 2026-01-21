from django.db import models

class FuenteFinanciamiento(models.Model):
    codigo = models.CharField(max_length=3, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")

    class Meta:
        db_table = 'pr_fuente'
        verbose_name = 'Fuente de Financiamiento'
        verbose_name_plural = 'Fuentes de Financiamiento'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class ClasificadorPresupuestario(models.Model):
    TIPO_CHOICES = (
        ('ING', 'Ingreso'),
        ('GAS', 'Gasto'),
    )
    codigo = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="Código")
    codigo_visual = models.CharField(max_length=30, blank=True, null=True, verbose_name="Código Visual")
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción Legal", blank=True, null=True)
    nivel = models.IntegerField(default=1, verbose_name="Nivel")
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='hijos', verbose_name="Padre")
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, default='GAS', verbose_name="Tipo")
    es_imputable = models.BooleanField(default=False, verbose_name="Es Imputable")
    agrupador = models.BooleanField(default=False, verbose_name="Agrupador") 

    class Meta:
        db_table = 'pr_clasificador'
        verbose_name = 'Clasificador Presupuestario'
        verbose_name_plural = 'Clasificadores Presupuestarios'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Presupuesto(models.Model):
    anio = models.IntegerField(default=2026, verbose_name="Año")
    partida_concatenada = models.CharField(max_length=100, unique=True, verbose_name="Partida Concatenada")
    
    fuente = models.ForeignKey(FuenteFinanciamiento, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fuente")
    # Reference to Unidad in apps.planificacion
    unidad = models.ForeignKey('planificacion.Unidad', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad")
    clasificador = models.ForeignKey(ClasificadorPresupuestario, on_delete=models.PROTECT, verbose_name="Clasificador")
    
    asignacion_inicial = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Asignación Inicial")
    reformas = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Reformas")
    devengado = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Devengado")
    
    # State fields
    certificado = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Certificado")
    comprometido = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Comprometido")

    class Meta:
        db_table = 'pr_presupuesto'
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Registros Presupuestarios'

    def __str__(self):
        return f"{self.partida_concatenada} - {self.clasificador.nombre}"

    @property
    def codificado(self):
        return self.asignacion_inicial + self.reformas

    @property
    def saldo_disponible(self):
        return self.codificado - self.certificado 
