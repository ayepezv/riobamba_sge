from django.db import models

# --- Estructura Orgánica ---

class Proceso(models.Model):
    codigo = models.CharField(max_length=2, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=200, verbose_name="Nombre")

    class Meta:
        db_table = 'pl_proceso'
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
        db_table = 'pl_direccion'
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
        db_table = 'pl_unidad'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

# --- PAC (Plan Anual de Contratación) ---

class PAC(models.Model):
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('APROBADO', 'Aprobado'),
        ('REFORMADO', 'Reformado'),
    ]

    anio = models.IntegerField(default=2026, verbose_name="Año Fiscal")
    descripcion = models.CharField(max_length=255, verbose_name="Descripción del Plan")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BORRADOR')
    fecha_aprobacion = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pl_pac'
        verbose_name = "Plan Anual de Contratación (PAC)"
        verbose_name_plural = "Planes Anuales (PAC)"

    def __str__(self):
        return f"PAC {self.anio} - {self.estado}"


class PACLinea(models.Model):
    TIPO_COMPRA_CHOICES = [
        ('BIEN', 'Bien'),
        ('SERVICIO', 'Servicio'),
        ('OBRA', 'Obra'),
        ('CONSULTORIA', 'Consultoría'),
    ]
    
    pac = models.ForeignKey(PAC, on_delete=models.CASCADE, related_name='lineas')
    # ForeignKey to Presupuesto is Lazy because Presupuesto will be in apps.presupuestos
    partida = models.ForeignKey('presupuestos.Presupuesto', on_delete=models.PROTECT, verbose_name="Partida Presupuestaria")
    cpc = models.CharField(max_length=20, verbose_name="Código CPC (SERCOP)")
    tipo_compra = models.CharField(max_length=20, choices=TIPO_COMPRA_CHOICES)
    detalle = models.TextField(verbose_name="Detalle del producto/servicio")
    
    cantidad = models.IntegerField(default=1)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    # Cuatrimestres (Multiple Selection)
    c1 = models.BooleanField(default=False, verbose_name="C1")
    c2 = models.BooleanField(default=False, verbose_name="C2")
    c3 = models.BooleanField(default=False, verbose_name="C3")
    
    procedimiento_sugerido = models.CharField(max_length=100, blank=True, null=True)
    codigo_original = models.CharField(max_length=100, blank=True, null=True, verbose_name="Código Original PDF")

    class Meta:
        db_table = 'pl_pac_linea'
        verbose_name = "Línea de PAC"
        verbose_name_plural = "Líneas de PAC"

    def save(self, *args, **kwargs):
        # Lógica automática: Calcular total antes de guardar
        self.monto_total = self.cantidad * self.costo_unitario
        super(PACLinea, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.cpc} - {self.detalle[:30]}..."
