from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import path

from .models import Proceso, Direccion, Unidad, PAC, PACLinea

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

# --- PAC ---

class PACLineaInline(admin.TabularInline):
    model = PACLinea
    extra = 1
    autocomplete_fields = ['partida']
    fields = ('partida', 'partida_popup_link', 'cpc', 'tipo_compra', 'detalle', 'cantidad', 'costo_unitario', 'monto_total', 'c1', 'c2', 'c3')
    readonly_fields = ('monto_total', 'partida_popup_link')
    
    def partida_popup_link(self, obj):
        if obj.partida_id:
            # URL actualizada a presupuestos
            url = f"/admin/presupuestos/presupuesto/{obj.partida_id}/change/?_popup=1"
            return format_html('<a href="#" onclick="return openBudgetModal(\'{}\');" title="Ver Detalle Presupuesto">👁️</a>', url)
        return "-"
    partida_popup_link.short_description = "Ver"

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
        js = ('js/custom_admin.js',)

@admin.register(PAC)
class PACAdmin(admin.ModelAdmin):
    list_display = ('anio', 'descripcion', 'estado', 'fecha_aprobacion', 'total_planificado')
    inlines = [PACLineaInline]
    search_fields = ['anio', 'descripcion']
    list_filter = ['estado', 'anio']
    # Apuntar al template en la nueva ubicación (la moveremos luego)
    change_form_template = 'admin/planificacion/pac/change_form.html'

    def total_planificado(self, obj):
        resultado = obj.lineas.aggregate(Sum('monto_total'))
        return resultado['monto_total__sum'] or 0
    total_planificado.short_description = "Total Planificado ($)"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('<int:object_id>/validate/', self.admin_site.admin_view(self.validate_pac_view), name='planificacion_pac_validate'),
            path('<int:object_id>/validation-report/', self.admin_site.admin_view(self.validation_report_view), name='planificacion_pac_validation_report'),
        ]
        return my_urls + urls

    def validate_pac_view(self, request, object_id):
        pac = get_object_or_404(PAC, pk=object_id)
        
        # Validation Logic
        # Notar que 'partida' ahora está en otro módulo, pero ORM lo maneja igual.
        lineas = pac.lineas.values('partida__id', 'partida__partida_concatenada', 'partida__asignacion_inicial', 'partida__reformas').annotate(total_pac=Sum('monto_total'))
        
        has_errors = False
        for item in lineas:
            inicial = item['partida__asignacion_inicial'] or 0
            reformas = item['partida__reformas'] or 0
            codificado = inicial + reformas
            total_pac = item['total_pac'] or 0
            
            if total_pac > codificado:
                has_errors = True
                break
        
        if has_errors:
            messages.warning(request, "⚠️ Se encontraron inconsistencias presupuestarias. Redirigiendo al reporte detallado...")
            return redirect('admin:planificacion_pac_validation_report', object_id)
        else:
            messages.success(request, f"✅ Validación Exitosa: Todas las partidas del PAC {pac.anio} están dentro del presupuesto.")
            return redirect('admin:planificacion_pac_change', object_id)

    def validation_report_view(self, request, object_id):
        pac = get_object_or_404(PAC, pk=object_id)
        lineas = pac.lineas.values('partida__id', 'partida__partida_concatenada', 'partida__clasificador__nombre', 'partida__asignacion_inicial', 'partida__reformas').annotate(total_pac=Sum('monto_total'))
        
        errors = []
        for item in lineas:
            inicial = item['partida__asignacion_inicial'] or 0
            reformas = item['partida__reformas'] or 0
            codificado = inicial + reformas
            total_pac = item['total_pac'] or 0
            
            if total_pac > codificado:
                diff = total_pac - codificado
                errors.append({
                    'partida': item['partida__partida_concatenada'],
                    'nombre': item['partida__clasificador__nombre'],
                    'codificado': codificado,
                    'total_pac': total_pac,
                    'diferencia': diff,
                    'pac_lines': pac.lineas.filter(partida_id=item['partida__id']) 
                })
        
        context = dict(
            self.admin_site.each_context(request),
            pac=pac,
            errors=errors,
            title=f"Reporte de Validación Presupuestaria - PAC {pac.anio}"
        )
        return render(request, 'admin/planificacion/pac/validation_report.html', context)

    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }
        js = ('js/custom_admin.js',)
