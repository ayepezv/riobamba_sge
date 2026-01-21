from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'usuario', 'accion', 'ruta', 'metodo', 'duracion_fmt', 'ip_address')
    list_filter = ('accion', 'metodo', 'timestamp', 'usuario')
    search_fields = ('ruta', 'usuario__username', 'detalle_cambios')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    
    def duracion_fmt(self, obj):
        color = 'green'
        if obj.duracion > 1.0: color = 'orange'
        if obj.duracion > 3.0: color = 'red'
        from django.utils.html import format_html
        return format_html('<span style="color: {}; font-weight: bold;">{}s</span>', color, obj.duracion)
    duracion_fmt.short_description = "Duración"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
