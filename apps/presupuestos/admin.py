from django.contrib import admin
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import FuenteFinanciamiento, ClasificadorPresupuestario, Presupuesto

# --- Filters ---
class ClasificadorNivel2Filter(admin.SimpleListFilter):
    title = _('Clasificador (Grupo)')
    parameter_name = 'clasif_grupo'

    def lookups(self, request, model_admin):
        qs = ClasificadorPresupuestario.objects.filter(nivel=2).values_list('codigo', 'nombre').order_by('codigo')
        return [(c[0], f"{c[0]} - {c[1]}") for c in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clasificador__codigo__startswith=self.value())

class ClasificadorNivel4Filter(admin.SimpleListFilter):
    title = _('Clasificador (Subgrupo)')
    parameter_name = 'clasif_subgrupo'

    def lookups(self, request, model_admin):
        qs = ClasificadorPresupuestario.objects.filter(nivel=3).values_list('codigo', 'nombre').order_by('codigo')
        return [(c[0], f"{c[0]} - {c[1]}") for c in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(clasificador__codigo__startswith=self.value())

class DefaultYearFilter(admin.SimpleListFilter):
    title = _('Año')
    parameter_name = 'anio'

    def lookups(self, request, model_admin):
        years = Presupuesto.objects.values_list('anio', flat=True).distinct().order_by('-anio')
        return [(y, str(y)) for y in years]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(anio=self.value())
        return queryset

    def value(self):
        value = super().value()
        if value is None:
            current_year = timezone.now().year
            return str(current_year) if value is None else value

# --- Admin Models ---

@admin.register(FuenteFinanciamiento)
class FuenteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre')
    search_fields = ('codigo', 'nombre')

@admin.register(ClasificadorPresupuestario)
class ClasificadorAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'nivel', 'padre', 'es_imputable')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo', 'nivel')
    raw_id_fields = ('padre',)

@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    # Template en nueva ubicación
    change_list_template = 'admin/presupuestos/presupuesto/change_list.html'
    
    list_display = ('partida_concatenada', 'get_clasificador_display', 'get_unidad_display', 'asignacion_inicial', 'reformas', 'codificado', 'devengado')
    search_fields = ('partida_concatenada', 'clasificador__codigo', 'clasificador__nombre', 'clasificador__descripcion')
    ordering = ['partida_concatenada']
    
    list_filter = (
        DefaultYearFilter,
        'clasificador__tipo',
        ClasificadorNivel2Filter,
        ClasificadorNivel4Filter,
        'fuente',
        'unidad__direccion__proceso', 
        'unidad__direccion', 
        'unidad',
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
        
        try:
            cl = response.context_data['cl']
            qs = cl.queryset
        except (AttributeError, KeyError):
            return response

        metrics = qs.aggregate(
            total_inicial=Sum('asignacion_inicial'),
            total_reformas=Sum('reformas'),
            total_devengado=Sum('devengado'),
        )
        
        t_inicial = metrics['total_inicial'] or 0
        t_reformas = metrics['total_reformas'] or 0
        metrics['total_codificado'] = t_inicial + t_reformas
        
        response.context_data['summary'] = metrics
        
        return response
