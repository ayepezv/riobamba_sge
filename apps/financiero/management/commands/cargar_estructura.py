import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
# Models imported inside handle to avoid circular imports during migrations if any


class Command(BaseCommand):
    help = 'Carga la estructura funcional desde un archivo CSV. Uso: python manage.py cargar_estructura <ruta_archivo>'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Ruta al archivo CSV')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {csv_file_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Cargando estructura desde: {csv_file_path}'))

        rows_to_process = []
        with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            if reader.fieldnames:
                reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

            for row in reader:
                raw_codigo = row.get('codigo', '').strip()
                nombre = row.get('nombre', '').strip()
                
                if not raw_codigo:
                    continue
                
                # Normalizar codigo
                longitud = len(raw_codigo)
                if longitud % 2 != 0:
                    longitud += 1
                if longitud < 2: longitud = 2
                
                codigo_norm = raw_codigo.zfill(longitud)
                
                # Nivel implícito por longitud
                rows_to_process.append({
                    'codigo': codigo_norm,
                    'nombre': nombre,
                })

        # Ordenar: primero los cortos (Nivel 1 -> Nivel 2 -> Nivel 3)
        rows_to_process.sort(key=lambda x: len(x['codigo']))

        count_proceso = 0
        count_direccion = 0
        count_unidad = 0

        with transaction.atomic():
            for data in rows_to_process:
                codigo = data['codigo']
                nombre = data['nombre']
                length = len(codigo)

                # Nivel 1: Proceso (2 chars)
                if length == 2:
                    from apps.financiero.models import Proceso
                    Proceso.objects.update_or_create(
                        codigo=codigo,
                        defaults={'nombre': nombre}
                    )
                    count_proceso += 1

                # Nivel 2: Direccion (4 chars)
                elif length == 4:
                    from apps.financiero.models import Direccion, Proceso
                    proceso_code = codigo[:2]
                    try:
                        proceso_obj = Proceso.objects.get(codigo=proceso_code)
                        Direccion.objects.update_or_create(
                            codigo=codigo,
                            defaults={'nombre': nombre, 'proceso': proceso_obj}
                        )
                        count_direccion += 1
                    except Proceso.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Proceso padre no encontrado para Dirección {codigo}"))

                # Nivel 3: Unidad (6 chars)
                elif length == 6:
                    from apps.financiero.models import Unidad, Direccion
                    direccion_code = codigo[:4]
                    try:
                        direccion_obj = Direccion.objects.get(codigo=direccion_code)
                        Unidad.objects.update_or_create(
                            codigo=codigo,
                            defaults={
                                'nombre': nombre, 
                                'direccion': direccion_obj,
                                'es_movimiento': True
                            }
                        )
                        count_unidad += 1
                    except Direccion.DoesNotExist:
                         self.stdout.write(self.style.WARNING(f"Dirección padre no encontrada para Unidad {codigo}"))

        self.stdout.write(self.style.SUCCESS(f'Carga finalizada. Procesos: {count_proceso}, Direcciones: {count_direccion}, Unidades: {count_unidad}.'))
