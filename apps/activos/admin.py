from django.contrib import admin
from .models import VistaDepreciacionBien
from .reports import exportar_excel_depreciacion, exportar_pdf_depreciacion

@admin.register(VistaDepreciacionBien)
class VistaDepreciacionBienAdmin(admin.ModelAdmin):
    # Definimos columnas estáticas
    list_display = [
        'codigo', 
        'descripcion', 
        'nombre_cuenta', 
        'costo_inicial', 
        'valor_en_libros_actual'
    ]
    
    # Agregamos años dinámicamente
    years = [f'dep_{y}' for y in range(2005, 2027)]
    list_display.extend(years)
    
    search_fields = ('codigo', 'descripcion', 'nombre_cuenta')
    list_filter = ('nombre_cuenta', 'estado')
    
    # Template personalizado
    change_list_template = 'admin/activos/vistadepreciacionbien/change_list.html'

    class Media:
        css = {
            'all': ('admin/css/wide_admin.css',) 
        }

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # 1. Interceptamos parámetros de exportación ANTES de cualquier validación
        if request.GET.get('export') == 'excel':
            cl = self.get_changelist_instance(request)
            queryset = cl.get_queryset(request)
            return exportar_excel_depreciacion(queryset)
        
        if request.GET.get('export') == 'pdf':
            cl = self.get_changelist_instance(request)
            queryset = cl.get_queryset(request)
            return exportar_pdf_depreciacion(queryset)
            
        # 2. LIMPIEZA CLAVE: Eliminamos 'export' del request.GET para evitar 
        # "IncorrectLookupParameters" en el super().changelist_view()
        # Hacemos una copia mutable
        request.GET = request.GET.copy() 
        if 'export' in request.GET:
            del request.GET['export']
            
        return super().changelist_view(request, extra_context=extra_context)
