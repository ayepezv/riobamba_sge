import os
import django
from django.conf import settings
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riobamba_sge.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.planificacion.models import PAC, PACLinea
from apps.presupuestos.models import Presupuesto, ClasificadorPresupuestario
from apps.compras.models import InformeNecesidad
from apps.compras.utils import generar_pdf_necesidad

import traceback

def verify():
    print("Verifying InformeNecesidad...")
    User = get_user_model()
    
    # Clean up previous test data
    InformeNecesidad.objects.filter(numero_informe='INF-TEST-001').delete()
    
    # 1. Asegurar usuarios
    user_creator, _ = User.objects.get_or_create(username='test_creator', defaults={'email': 'creator@test.com', 'cedula': '1111111111'})
    user_authorizer, _ = User.objects.get_or_create(username='test_authorizer', defaults={'email': 'auth@test.com', 'cedula': '2222222222'})
    
    # 2. Asegurar Clasificador y Presupuesto
    clasificador, _ = ClasificadorPresupuestario.objects.get_or_create(
        codigo='530804', defaults={'nombre': 'Materiales de Oficina', 'tipo': 'GAS'}
    )
    
    partida, _ = Presupuesto.objects.get_or_create(
        partida_concatenada='2026.1.1.1.530804',
        defaults={
            'anio': 2026, 
            'asignacion_inicial': 1000, 
            'clasificador': clasificador
        }
    )
    
    pac, _ = PAC.objects.get_or_create(anio=2026, defaults={'descripcion': 'PAC Test 2026'})
    
    pac_linea, _ = PACLinea.objects.get_or_create(
        pac=pac,
        partida=partida,
        cpc='123456789',
        tipo_compra='BIEN',
        defaults={
            'detalle': 'Compra de Equipos Informáticos',
            'cantidad': 10,
            'costo_unitario': 500.00
        }
    )
    
    # 3. Crear Informe
    informe = InformeNecesidad(
        pac_linea=pac_linea,
        numero_informe='INF-TEST-001',
        objeto_contratacion='Adquisición de Laptops',
        antecedentes='Antecedentes de prueba...',
        base_legal='Base legal de prueba...',
        analisis_necesidad='Análisis de prueba...',
        conclusion_recomendacion='Conclusión de prueba...',
        elaborado_por=user_creator,
        autorizado_por=user_authorizer
    )
    informe.save()
    print(f"Informe {informe.numero_informe} created successfully.")
    
    # 4. Generar PDF
    print("Generating PDF...")
    try:
        response = generar_pdf_necesidad(informe.pk)
        
        if response.status_code == 200 and response['Content-Type'] == 'application/pdf':
            print("PDF generated successfully.")
            # Guardar localmente para inspección manual si se desea
            with open('test_informe.pdf', 'wb') as f:
                f.write(response.content)
            print("PDF saved to test_informe.pdf")
        else:
            print(f"Failed to generate PDF. Status: {response.status_code}")
            print(response.content[:500])
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    try:
        verify()
    except Exception as e:
        print(f"Verification FAILED: {e}")
        traceback.print_exc()
