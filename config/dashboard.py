from django.utils.translation import gettext_lazy as _
# from unfold.decorators import dashboard_callback # DEPRECADO
from apps.presupuestos.models import Presupuesto
from apps.compras.models import InformeNecesidad
from django.db.models import Sum

def dashboard_callback(request, context):
    # 1. KPIs de Presupuesto
    # 'codificado' es una propiedad, no un campo de base de datos.
    # Debemos sumar asignacion_inicial + reformas manualmente.
    metrics = Presupuesto.objects.aggregate(
        total_inicial=Sum('asignacion_inicial'),
        total_reformas=Sum('reformas'),
        total_devengado=Sum('devengado')
    )
    
    presupuesto_total = (metrics['total_inicial'] or 0) + (metrics['total_reformas'] or 0)
    presupuesto_ejecutado = metrics['total_devengado'] or 0

    porcentaje_ejecucion = 0
    if presupuesto_total > 0:
        porcentaje_ejecucion = (presupuesto_ejecutado / presupuesto_total) * 100

    # 2. KPIs de Compras
    total_tramites = InformeNecesidad.objects.count()
    # tramites_pendientes = InformeNecesidad.objects.filter(aprobado=False).count() # Campo no existe
    
    # 3. Retornar contexto para el Dashboard
    context.update({
        "kpi": [
            {
                "title": _("Presupuesto Codificado 2026"),
                "metric": f"${presupuesto_total:,.2f}",
                "footer": _("Total Institucional"),
                "icon": "account_balance_wallet",
                "color": "primary-600",
            },
            {
                "title": _("Ejecución Presupuestaria"),
                "metric": f"{porcentaje_ejecucion:.1f}%",
                "footer": f"${presupuesto_ejecutado:,.2f} Devengado",
                "icon": "trending_up",
                "color": "green-600",
            },
            {
                "title": _("Informes de Necesidad"),
                "metric": str(total_tramites),
                "footer": _("Total Generados"),
                "icon": "shopping_cart",
                "color": "amber-600",
            },
        ],
        "navigation": [
            {"title": "Planificación", "link": "/admin/planificacion/", "icon": "account_tree"},
            {"title": "Presupuestos", "link": "/admin/presupuestos/presupuesto/", "icon": "monetization_on"},
            {"title": "Compras", "link": "/admin/compras/informenecesidad/", "icon": "shopping_cart"},
        ]
    })
    return context
