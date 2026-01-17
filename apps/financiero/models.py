from django.db import models

class FuenteFinanciamiento(models.Model):
    codigo = models.CharField(max_length=3, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")

    class Meta:
        db_table = 'fi_fuente'
        verbose_name = 'Fuente de Financiamiento'
        verbose_name_plural = 'Fuentes de Financiamiento'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Proceso(models.Model):
    codigo = models.CharField(max_length=2, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")

    class Meta:
        db_table = 'fi_proceso'
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Direccion(models.Model):
    codigo = models.CharField(max_length=4, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name='direcciones', verbose_name="Proceso Padre")

    class Meta:
        db_table = 'fi_direccion'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class Unidad(models.Model):
    codigo = models.CharField(max_length=6, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE, related_name='unidades', verbose_name="Dirección Padre")
    es_movimiento = models.BooleanField(default=True, verbose_name="Es Movimiento")

    class Meta:
        db_table = 'fi_unidad'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class ClasificadorPresupuestario(models.Model):
    TIPO_CHOICES = (
        ('ING', 'Ingreso'),
        ('GAS', 'Gasto'),
    )
    codigo = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="Código")
    # codigo_formateado removed (redundant, codigo now stores dotted format)
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción Legal", blank=True, null=True)
    nivel = models.IntegerField(default=1, verbose_name="Nivel")
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='hijos', verbose_name="Padre")
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, default='GAS', verbose_name="Tipo")
    es_imputable = models.BooleanField(default=False, verbose_name="Es Imputable")
    agrupador = models.BooleanField(default=False, verbose_name="Agrupador") 

    class Meta:
        db_table = 'fi_clasificador'
        verbose_name = 'Clasificador Presupuestario'
        verbose_name_plural = 'Clasificadores Presupuestarios'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def save(self, *args, **kwargs):
        # Auto-calculate level based on 'clean' code length? or dots?
        # MEF structure usually: 1, 1.1, 1.1.01...
        # Let's rely on the import script to set level/padre, but we can infer imputable.
        # Imputable usually = 6 digits (final level).
        pass
        super().save(*args, **kwargs)

class Presupuesto(models.Model):
    anio = models.IntegerField(default=2026, verbose_name="Año")
    partida_concatenada = models.CharField(max_length=100, unique=True, verbose_name="Partida Concatenada")
    
    fuente = models.ForeignKey(FuenteFinanciamiento, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fuente")
    unidad = models.ForeignKey(Unidad, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad")
    clasificador = models.ForeignKey(ClasificadorPresupuestario, on_delete=models.PROTECT, verbose_name="Clasificador")
    
    asignacion_inicial = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Asignación Inicial")
    reformas = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Reformas")
    devengado = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name="Devengado")

    class Meta:
        db_table = 'fi_presupuesto'
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Registros Presupuestarios'

    def __str__(self):
        return self.partida_concatenada

    @property
    def codificado(self):
        return self.asignacion_inicial + self.reformas
