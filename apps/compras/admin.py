from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect
from .models import InformeNecesidad
from .utils import generar_pdf_necesidad
from .services import generar_redaccion_ia

@admin.register(InformeNecesidad)
class InformeNecesidadAdmin(admin.ModelAdmin):
    list_display = ('numero_informe', 'objeto_contratacion_short', 'fecha_solicitud', 'elaborado_por', 'imprimir_button')
    search_fields = ('numero_informe', 'objeto_contratacion')
    list_filter = ('fecha_solicitud',)
    autocomplete_fields = ['pac_linea', 'elaborado_por', 'autorizado_por']
    
    actions = ['imprimir_informe_pdf_action']

    def objeto_contratacion_short(self, obj):
        return obj.objeto_contratacion[:50] + "..." if obj.objeto_contratacion else "-"
    objeto_contratacion_short.short_description = "Objeto Contratación"

    def imprimir_button(self, obj):
        return format_html(
            '<a class="button" href="imprimir/{}/" target="_blank">🖨️ Imprimir PDF</a>',
            obj.pk
        )
    imprimir_button.short_description = "Acciones"
    imprimir_button.allow_tags = True

    @admin.action(description='🖨️ Imprimir Informe PDF')
    def imprimir_informe_pdf_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Por favor seleccione solo un informe para imprimir.", level='ERROR')
            return
        
        informe = queryset.first()
        return generar_pdf_necesidad(informe.pk)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('imprimir/<int:informe_id>/', self.admin_site.admin_view(self.imprimir_view), name='compras_informenecesidad_imprimir'),
        ]
        return custom_urls + urls

    def imprimir_view(self, request, informe_id):
        return generar_pdf_necesidad(informe_id)

    def save_model(self, request, obj, form, change):
        # Auto-generar antecedentes si está vacío y hay una línea PAC seleccionada
        if not obj.antecedentes and obj.pac_linea:
             # Aquí podríamos llamar a la IA, pero lo ideal es hacerlo en el frontend o con un botón "Generar con IA"
             # Por ahora, solo lo sugerimos si está vacío al guardar
             obj.antecedentes = generar_redaccion_ia(obj.pac_linea.detalle)
        
        if not obj.elaborado_por_id:
            obj.elaborado_por = request.user
            
        super().save_model(request, obj, form, change)
