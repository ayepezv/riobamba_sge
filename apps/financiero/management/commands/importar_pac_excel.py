from django.core.management.base import BaseCommand
import pandas as pd
from decimal import Decimal
from django.db import transaction
from apps.financiero.models import PAC, PACLinea, Presupuesto
import os

class Command(BaseCommand):
    help = 'Importa el PAC desde un archivo Excel (.xlsx)'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Ruta al archivo Excel')

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        self.stdout.write(f"Iniciando importación desde Excel: {path}")

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"Archivo no encontrado: {path}"))
            return

        try:
            with transaction.atomic():
                # Paso A: Crear/Buscar Cabecera
                pac, created = PAC.objects.get_or_create(
                    anio=2026,
                    defaults={'descripcion': 'Importación desde Excel'}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Creado PAC 2026: {pac}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Usando PAC 2026 existente: {pac}"))
                    self.stdout.write(self.style.WARNING("Eliminando líneas anteriores para recarga completa..."))
                    pac.lineas.all().delete()

                # Leer Excel
                # Header en fila 0 (por defecto)
                df = pd.read_excel(path, dtype=str)
                df = df.fillna('') # Rellenar NaNs con string vacío

                total_lines = 0
                imported_lines = 0
                warnings = 0

                # Variables para procesar multilinea
                current_partida_full = None
                current_data = {} 
                # current_data will hold: {cpc, tipo, proc, desc, cant, costo, periodo} from the "Digit" row

                for index, row in df.iterrows():
                    # Índices (0-based) basados en columna Excel (A=0, B=1, etc.)
                    # B: Partida (1)
                    # C: CPC (2)
                    # D: Tipo Compra (3)
                    # J: Procedimiento (9)
                    # K: Descripción (10)
                    # L: Cantidad (11)
                    # N: Costo U (13)
                    # P: Periodo (15)

                    raw_partida = str(row.iloc[1]).strip()
                    
                    if not raw_partida:
                        continue

                    # DETECCION TIPO FILA
                    is_start = raw_partida[0].isdigit() # Ej: "53..."
                    is_continuation = raw_partida.startswith('.') # Ej: ".001"

                    if is_start:
                        # Si teniamos uno pendiente, procesarlo antes de arrancar el nuevo?
                        # No, la lógica de Excel parece ser:
                        # Fila 1: 53.05.05 (Datos principales aquí)
                        # Fila 2: .001 (Solo completa la partida)
                        # El ítem se cierra y guarda cuando detectamos el SIGUIENTE inicio o fin de archivo?
                        # O mejor: Acumulamos.
                        
                        # Si ya tenemos un 'current_partida_full', significa que el ANTERIOR ya terminó.
                        # Debemos guardarlo antes de empezar este nuevo.
                        if current_partida_full:
                            self.save_linea(pac, current_partida_full, current_data)
                            imported_lines += 1
                        
                        # Iniciar Nuevo Item
                        current_partida_full = raw_partida
                        current_data = {
                            'cpc': str(row.iloc[2]).strip(),
                            'tipo_compra': str(row.iloc[3]).strip(),
                            'procedimiento': str(row.iloc[9]).strip(),
                            'descripcion': str(row.iloc[10]).strip(),
                            'cantidad': str(row.iloc[11]).strip(),
                            'costo': str(row.iloc[13]).strip(),
                            'periodo': str(row.iloc[15]).strip(),
                        }
                    
                    elif is_continuation:
                        # Es continuación del anterior
                        if current_partida_full:
                            current_partida_full += raw_partida
                        else:
                            self.stdout.write(self.style.WARNING(f"Fila continuación sin padre en línea {index}: {raw_partida}"))

                # Guardar el último pendiente al salir del loop
                if current_partida_full:
                    self.save_linea(pac, current_partida_full, current_data)
                    imported_lines += 1

                self.stdout.write(self.style.SUCCESS(f"Importación Excel Finalizada. Líneas importadas: {imported_lines}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error crítico: {str(e)}"))
            # raise e # Uncomment to see traceback if needed

    def save_linea(self, pac, partida_full, data):
        # 1. Limpieza Partida
        # "53.02.04" + ".001" -> "53.02.04.001"
        # Remove spaces check
        partida_clean = partida_full.replace(' ', '').replace(',', '.')
        
        # 2. Búsqueda Presupuesto (ignoring prefix like 010101.)
        # Intento 1: Endswith (Match exacto del sufijo)
        presupuesto = Presupuesto.objects.filter(partida_concatenada__endswith=partida_clean).first()

        # Intento 2: Contains (Por si acaso)
        if not presupuesto:
             presupuesto = Presupuesto.objects.filter(partida_concatenada__contains=partida_clean).first()
        
        if not presupuesto:
            # Fallback: Root Search (Primeros 3 segmentos: 53.02.04)
            # Must ensure we match .53.02.04 to avoid partial numbers
            segments = partida_clean.split('.')
            if len(segments) >= 3:
                root_code = '.'.join(segments[:3]) # 53.02.04
                # Search for ".53.02.04" to be safe, or just identifier
                presupuesto = Presupuesto.objects.filter(partida_concatenada__contains=f".{root_code}").first()
                if presupuesto:
                    self.stdout.write(f"Match parcial raiz: {partida_clean} -> {presupuesto.partida_concatenada}")
        
        if not presupuesto:
            self.stdout.write(self.style.WARNING(f"Partida NO encontrada: {partida_clean}"))
            # Guardamos sin relacion (NULL) o saltamos?
            # Model tiene on_delete=PROTECT, pero field puede ser null? 
            # models.py: partida = ForeignKey(..., on_delete=models.PROTECT) -> NOT NULL by default.
            # We must skip if not found to avoid integrity error, OR create a dummy?
            # Prompt instructions said: "imprime WARNING y salta".
            return 

        # 3. Datos
        # Costo
        try:
            costo_clean = data['costo'].replace('$', '').replace(',', '').strip()
            costo_unitario = Decimal(costo_clean) if costo_clean else Decimal(0)
        except:
            costo_unitario = Decimal(0)

        # Cantidad
        try:
            cant_clean = data['cantidad'].replace(',', '').strip()
            cantidad = int(float(cant_clean)) if cant_clean else 1
        except:
            cantidad = 1

        # Periodo (Multiple support)
        p_raw = str(data['periodo']).strip()
        # Ensure we catch '1.0' or '1' or '1,2'
        c1 = '1' in p_raw
        c2 = '2' in p_raw
        c3 = '3' in p_raw
        
        # Log if needed
        # print(f"Periodo Raw: {p_raw} -> C1:{c1} C2:{c2} C3:{c3}")
        
        # Default to C1 if empty/unknown and no period detected
        if not (c1 or c2 or c3):
             c1 = True

        # Tipo
        tipo_raw = data['tipo_compra'].upper()
        tipo_compra = 'BIEN'
        if 'SERVICIO' in tipo_raw: tipo_compra = 'SERVICIO'
        elif 'OBRA' in tipo_raw: tipo_compra = 'OBRA'
        elif 'CONSULT' in tipo_raw: tipo_compra = 'CONSULTORIA'

        # Crear
        PACLinea.objects.create(
            pac=pac,
            partida=presupuesto,
            cpc=data['cpc'],
            tipo_compra=tipo_compra,
            detalle=data['descripcion'],
            cantidad=cantidad,
            costo_unitario=costo_unitario,
            c1=c1, c2=c2, c3=c3,
            procedimiento_sugerido=data['procedimiento'],
            codigo_original=partida_full
        )
