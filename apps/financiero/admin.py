from django.contrib import admin
from .models import Certificacion, CertificacionDetalle

class CertificacionDetalleInline(admin.StackedInline):
    model = CertificacionDetalle
    extra = 1
    autocomplete_fields = ['partida']

@admin.register(Certificacion)
class CertificacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'descripcion', 'estado', 'unidad', 'monto_total')
    list_filter = ('estado', 'unidad', 'fecha')
    search_fields = ('codigo', 'descripcion')
    inlines = [CertificacionDetalleInline]
    readonly_fields = ('codigo', 'monto_total')
