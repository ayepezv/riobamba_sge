import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.financiero.models import FuenteFinanciamiento, Unidad, ClasificadorPresupuestario, Presupuesto

class Command(BaseCommand):
    help = 'Carga el presupuesto desde un archivo CSV. Uso: python manage.py cargar_presupuesto <ruta_archivo>'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta absoluta o relativa al archivo CSV')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'El archivo no existe: {csv_file_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Iniciando carga desde: {csv_file_path}'))

        with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            # Normalize headers
            if reader.fieldnames:
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            # Mapping de columnas flexibles
            header_map = {
                'PARTIDA': ['PARTIDA', 'CODIGO', 'partida', 'codigo'],
                'NOMBRE': ['NOMBRE PARTIDA', 'NOMBRE DE PARTIDA', 'nombre'],
                'INICIAL': ['ASIGNACION INICIAL', 'INICIAL', 'asignacion_inicial'],
                'REFORMAS': ['REFORMAS', 'reformas'],
                'DEVENGADO': ['DEVENGADO', 'devengado']
            }
            
            def get_col_name(candidates):
                for c in candidates:
                    if c in reader.fieldnames:
                        return c
                return None

            col_partida = get_col_name(header_map['PARTIDA'])
            col_nombre = get_col_name(header_map['NOMBRE'])
            col_inicial = get_col_name(header_map['INICIAL'])
            col_reformas = get_col_name(header_map['REFORMAS'])
            col_devengado = get_col_name(header_map['DEVENGADO'])

            if not col_partida or not col_nombre:
                self.stdout.write(self.style.ERROR(f"Columnas no encontradas. Headers: {reader.fieldnames}"))
                return



            processed_count = 0
            created_count = 0
            updated_count = 0

            with transaction.atomic():
                for row in reader:
                    partida_full = row.get(col_partida, '').strip()
                    if not partida_full:
                        continue
                    
                    # Limpiar caracteres invisibles/espacios
                    partida_full = "".join(partida_full.split()) 

                    parts = partida_full.split('.')
                    
                    unidad_obj = None
                    clasificador_code = ""
                    fuente_code = ""
                    es_ingreso = False

                    # Lógica GASTOS (7 bloques): 040303.61.01.05.000.000.001
                    if len(parts) >= 7:
                        estructura_code = parts[0]
                        clasificador_code = f"{parts[1]}.{parts[2]}.{parts[3]}"
                        fuente_code = parts[6] # Asumimos posición 7 es fuente
                    
                    # Lógica INGRESOS (5 bloques): 13.01.07.01.001 (Clasificador(4) + Fuente(1))
                    elif len(parts) == 5:
                        es_ingreso = True
                        estructura_code = None
                        clasificador_code = f"{parts[0]}.{parts[1]}.{parts[2]}.{parts[3]}"
                        fuente_code = parts[4]
                    
                    else:
                        continue

                    nombre_clasificador = row.get(col_nombre, 'Clasificador Sin Nombre').strip()
                    
                    # Helper para limpiar floats
                    def clean_float(val):
                        if not val: return 0.0
                        return float(val.replace(',', '').replace(' ', ''))

                    asignacion_val = clean_float(row.get(col_inicial))
                    reformas_val = clean_float(row.get(col_reformas)) if col_reformas else 0.0
                    devengado_val = clean_float(row.get(col_devengado)) if col_devengado else 0.0




                    # 1. Estructura Programática -> UNIDAD
                    if estructura_code:
                        try:
                            # Presupuesto se asigna a nivel de UNIDAD (6 dígitos)
                            unidad_obj = Unidad.objects.get(codigo=estructura_code)
                        except Unidad.DoesNotExist:
                             # Warning silencioso o explícito
                             unidad_obj = None
                    
                    # Si es estructura padre (e.g. 2 o 4 dígitos) no se asigna presupuesto directamente en este modelo?
                    # Asumimos que el CSV trae códigos de 6 dígitos para gastos. 
                    # Si trae códigos cortos, no asignamos unidad.


                    # 2. Fuente Financiamiento
                    fuente_obj, _ = FuenteFinanciamiento.objects.get_or_create(
                        codigo=fuente_code,
                        defaults={'nombre': f"Fuente {fuente_code}"}
                    )

                    # 3. Clasificador Presupuestario
                    # El CSV trae formato '61.01.05' (o similar con puntos). 
                    # El modelo ahora usa puntos en 'codigo'.
                    
                    clasificador_obj, _ = ClasificadorPresupuestario.objects.update_or_create(
                        codigo=clasificador_code,
                        defaults={
                            'nombre': nombre_clasificador,
                            'tipo': 'ING' if es_ingreso else 'GAS',
                            'es_imputable': True 
                        }
                    )

                    # 4. Presupuesto
                    presupuesto_obj, created = Presupuesto.objects.update_or_create(
                        partida_concatenada=partida_full,
                        defaults={
                            'anio': 2026,
                            'fuente': fuente_obj,
                            'unidad': unidad_obj,
                            'clasificador': clasificador_obj,
                            'asignacion_inicial': asignacion_val,
                            'reformas': reformas_val,
                            'devengado': devengado_val
                        }
                    )
                    
                    processed_count += 1
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Proceso finalizado. Total Leaf: {processed_count}. Creados: {created_count}. Actualizados: {updated_count}.'))
