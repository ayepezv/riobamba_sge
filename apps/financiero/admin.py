from django.contrib import admin
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from .models import FuenteFinanciamiento, Proceso, Direccion, Unidad, ClasificadorPresupuestario, Presupuesto

# --- Custom Filters ---

class ClasificadorNivel2Filter(admin.SimpleListFilter):
    title = _('Clasificador (Grupo)')
    parameter_name = 'clasif_grupo'

    def lookups(self, request, model_admin):
        # Obtener los primeros 2 dígitos distintos de los clasificadores usados en presupuesto
        # Para optimizar, podríamos hacer esto hardcoded o consultar la tabla Clasificador
        # Consultamos los clasificadores de nivel 2 existentes
        qs = ClasificadorPresupuestario.objects.filter(nivel=2).values_list('codigo', 'nombre').order_by('codigo')
        return [(c[0], f"{c[0]} - {c[1]}") for c in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clasificador__codigo__startswith=self.value())

class ClasificadorNivel4Filter(admin.SimpleListFilter):
    title = _('Clasificador (Subgrupo)')
    parameter_name = 'clasif_subgrupo'

    def lookups(self, request, model_admin):
        # Consultamos los clasificadores de nivel 3 (4 dígitos: 51.01) existentes
        qs = ClasificadorPresupuestario.objects.filter(nivel=3).values_list('codigo', 'nombre').order_by('codigo')
        return [(c[0], f"{c[0]} - {c[1]}") for c in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clasificador__codigo__startswith=self.value())


# --- Admin Models ---

@admin.register(FuenteFinanciamiento)
class FuenteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'proceso')
    search_fields = ('codigo', 'nombre')
    list_filter = ('proceso',)

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'direccion', 'es_movimiento')
    search_fields = ('codigo', 'nombre')
    list_filter = ('direccion__proceso', 'direccion')

@admin.register(ClasificadorPresupuestario)
class ClasificadorAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'nivel', 'padre', 'es_imputable')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo', 'nivel')
    raw_id_fields = ('padre',)

from django.utils import timezone
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, RelatedDropdownFilter, ChoiceDropdownFilter, RelatedOnlyDropdownFilter
)

# ... (Previous Filters)

class DefaultYearFilter(admin.SimpleListFilter):
    title = _('Año')
    parameter_name = 'anio'

    def lookups(self, request, model_admin):
        # Asumimos que existen registros de años en presupuesto o hardcodeamos rango
        # Mejor sacar del queryset
        years = Presupuesto.objects.values_list('anio', flat=True).distinct().order_by('-anio')
        return [(y, str(y)) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(anio=self.value())
        return queryset

    def value(self):
        value = super().value()
        if value is None:
            # Default to current year if exists, otherwise do nothing or 2026?
            # User asked for current year default.
            current_year = timezone.now().year
            # But our data is 2026. Let's force 2026 if current year not found?
            # For this specific project case (2026 budget), maybe default to 2026?
            # Or assume system clock is correct. Let's try 2026 as per user context unless requested otherwise.
            # actually user said "año actual". 
            return str(current_year) if value is None else value

# ... (omitted)

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    change_list_template = 'admin/financiero/presupuesto/change_list.html'
    
    list_display = ('partida_concatenada', 'get_clasificador_display', 'get_unidad_display', 'asignacion_inicial', 'reformas', 'codificado', 'devengado')
    search_fields = ('partida_concatenada', 'clasificador__nombre', 'unidad__nombre', 'clasificador__codigo')
    
    list_filter = (
        DefaultYearFilter,
        ('clasificador__tipo', ChoiceDropdownFilter),
        ClasificadorNivel2Filter,
        ClasificadorNivel4Filter,
        ('fuente', RelatedDropdownFilter), 
        
        # Use RelatedOnlyDropdownFilter for dependent structure
        ('unidad__direccion__proceso', RelatedOnlyDropdownFilter), 
        ('unidad__direccion', RelatedOnlyDropdownFilter), 
        ('unidad', RelatedOnlyDropdownFilter),
    )
    readonly_fields = ('codificado',)

    def get_clasificador_display(self, obj):
        return f"{obj.clasificador.codigo} - {obj.clasificador.nombre}"
    get_clasificador_display.short_description = "Clasificador"

    def get_unidad_display(self, obj):
        if obj.unidad:
            return f"{obj.unidad.codigo} - {obj.unidad.nombre}"
        return "-"
    get_unidad_display.short_description = "Unidad"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        
        # Intentar obtener el queryset filtrado (ChangeList)
        try:
            cl = response.context_data['cl']
            qs = cl.queryset
        except (AttributeError, KeyError):
            return response

        # Calcular totales
        metrics = qs.aggregate(
            total_inicial=Sum('asignacion_inicial'),
            total_reformas=Sum('reformas'),
            total_devengado=Sum('devengado'),
        )
        
        # Calcular codificado (suma de campos puede ser None si no hay registros)
        t_inicial = metrics['total_inicial'] or 0
        t_reformas = metrics['total_reformas'] or 0
        metrics['total_codificado'] = t_inicial + t_reformas
        
        print("DEBUG METRICS:", metrics) # Debugging print
        
        response.context_data['summary'] = metrics
        
        return response
