from django.core.management.base import BaseCommand
import pdfplumber
from decimal import Decimal
from django.db import transaction
from apps.planificacion.models import PAC, PACLinea
from apps.presupuestos.models import Presupuesto
import re

class Command(BaseCommand):
    help = 'Importa el PAC desde un archivo PDF'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Ruta al archivo PDF')

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        self.stdout.write(f"Iniciando importación desde: {path}")

        try:
            with transaction.atomic():
                # Paso A: Crear/Buscar Cabecera
                pac, created = PAC.objects.get_or_create(
                    anio=2026,
                    defaults={'descripcion': 'Importación desde PDF'}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Creado PAC 2026: {pac}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Usando PAC 2026 existente: {pac}"))

                # Eliminar lineas anteriores en borrador si se desea reiniciar? 
                # Dejamos que acumule por ahora o advertimos.
                
                # Paso B: Recorrer PDF
                with pdfplumber.open(path) as pdf:
                    total_lines = 0
                    imported_lines = 0
                    warnings = 0

                    for page_num, page in enumerate(pdf.pages):
                        self.stdout.write(f"Procesando página {page_num + 1}...")
                        
                        # Extract table
                        tables = page.extract_tables()

                        for table in tables:
                            for row in table:
                                # Header check
                                if not row or not row[0] or 'Partida' in str(row[0]):
                                    continue
                                
                                # Basic check for valid row structure based on column count
                                if len(row) < 8:
                                    continue

                                # --- EXTRACT RAW DATA ---
                                raw_partida_multiline = row[0]
                                cpc = row[1]
                                tipo_compra_raw = row[2] or ''
                                procedimiento = row[3]
                                descripcion = row[4]
                                cantidad_raw = row[5]
                                costo_raw = row[6]
                                periodo_raw = row[7]

                                if not raw_partida_multiline:
                                    continue

                                total_lines += 1

                                # --- 1. RECONSTRUCCION CODIGO PARTIDA ---
                                # "84.04.02.000\n.000.001" -> "84.04.02.000.000.001"
                                # Eliminar newlines y espacios intermedios
                                partida_full = raw_partida_multiline.replace('\n', '').replace('\r', '').replace(' ', '')
                                
                                # Parseo limpieza puntos/comas
                                # Asumimos formato con puntos o comas
                                partida_clean = partida_full.replace(',', '.')
                                
                                # Si termina en punto, quitarlo? no suele pasar si se concatena bien
                                
                                # --- 2. BUSQUEDA CASCADA ---
                                # Intento 1: Exacto
                                presupuesto = Presupuesto.objects.filter(partida_concatenada=partida_clean).first()

                                if not presupuesto:
                                    # Fallback: Root Search (Primeros 3 segmentos)
                                    # Ej: 84.04.02.000... -> 84.04.02
                                    segments = partida_clean.split('.')
                                    if len(segments) >= 3:
                                        root_code = '.'.join(segments[:3])
                                        presupuesto = Presupuesto.objects.filter(partida_concatenada__startswith=root_code).first()
                                        
                                        if presupuesto:
                                            self.stdout.write(self.style.NOTICE(f"Match parcial: {partida_clean} -> Asignado a {presupuesto.partida_concatenada}"))
                                    
                                if not presupuesto:
                                    self.stdout.write(self.style.WARNING(f"Partida NO encontrada: {raw_partida_multiline} (Clean: {partida_clean}) - SALTA"))
                                    warnings += 1
                                    continue

                                # --- 3. DATOS ADICIONALES ---
                                try:
                                    # Costo: Eliminar $ y ,
                                    if costo_raw:
                                        costo_clean_str = str(costo_raw).replace('$', '').replace(',', '').strip()
                                        costo_unitario = Decimal(costo_clean_str)
                                    else:
                                        costo_unitario = Decimal(0)
                                except Exception as e:
                                    self.stdout.write(self.style.ERROR(f"Error parseando costo '{costo_raw}': {e}"))
                                    continue
                                
                                try:
                                    if cantidad_raw:
                                        cantidad = int(float(str(cantidad_raw).replace(',', '')))
                                    else:
                                        cantidad = 1
                                except:
                                    cantidad = 1

                                # Periodo
                                kw_cuatrimestre = '1'
                                if periodo_raw:
                                    p_str = str(periodo_raw)
                                    if '1' in p_str: kw_cuatrimestre = '1'
                                    elif '2' in p_str: kw_cuatrimestre = '2'
                                    elif '3' in p_str: kw_cuatrimestre = '3'

                                # Tipo Compra
                                tipo_compra = 'BIEN'
                                if tipo_compra_raw:
                                    tipo_upper = tipo_compra_raw.upper()
                                    if 'SERVICIO' in tipo_upper: tipo_compra = 'SERVICIO'
                                    elif 'OBRA' in tipo_upper: tipo_compra = 'OBRA'
                                    elif 'CONSULT' in tipo_upper: tipo_compra = 'CONSULTORIA'

                                # --- GUARDAR ---
                                    # Cuatrimestres
                                    is_c1 = (kw_cuatrimestre == '1')
                                    is_c2 = (kw_cuatrimestre == '2')
                                    is_c3 = (kw_cuatrimestre == '3')

                                    PACLinea.objects.create(
                                        pac=pac,
                                        partida=presupuesto,
                                        cpc=cpc,
                                        tipo_compra=tipo_compra,
                                        detalle=descripcion,
                                        cantidad=cantidad,
                                        costo_unitario=costo_unitario,
                                        c1=is_c1,
                                        c2=is_c2,
                                        c3=is_c3,
                                        procedimiento_sugerido=procedimiento,
                                        codigo_original=partida_full
                                    )
                                imported_lines += 1

                self.stdout.write(self.style.SUCCESS(f"Importación finalizada. Líneas procesadas: {imported_lines}/{total_lines}. Advertencias: {warnings}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error crítico: {str(e)}"))
