import os
import re
import pdfplumber
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.financiero.models import ClasificadorPresupuestario

class Command(BaseCommand):
    help = 'Importa el Clasificador Presupuestario desde un PDF. Uso: python manage.py importar_clasificador <ruta_pdf>'

    def add_arguments(self, parser):
        parser.add_argument('pdf_file', type=str, help='Ruta al archivo PDF')

    def handle(self, *args, **kwargs):
        pdf_path = kwargs['pdf_file']
        
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {pdf_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Analizando PDF: {pdf_path}'))

        # Limpiar tabla antes de importar
        # Primero Presupuesto por on_delete=PROTECT
        from apps.financiero.models import Presupuesto
        Presupuesto.objects.all().delete()
        self.stdout.write(self.style.WARNING('Datos de Presupuesto eliminados por cascada inversa.'))
        
        ClasificadorPresupuestario.objects.all().delete()
        self.stdout.write(self.style.WARNING('Datos de Clasificador eliminados.'))

        # Regex para detectar líneas de código: "1.1.01 Nombre..."
        # El codigo DEBE empezar con un numero.
        code_pattern = re.compile(r'^(\d+(\.\d+)*)\s+(.*)')
        
        # Regex para detectar números de página solos (ej: "8", "22") o con texto irrelevante
        page_number_pattern = re.compile(r'^\d+$')

        batch_data = []
        current_item = None

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                self.stdout.write(f"Procesando página {i+1}/{total_pages}...")
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    
                    # Filtros de basura (encabezados, numero de pagina)
                    if "CLASIFICADOR" in line.upper(): continue
                    if "PÁGINA" in line.upper(): continue
                    if page_number_pattern.match(line): continue
                    
                    match = code_pattern.match(line)
                    if match:
                        # Si hay match, guardamos el item anterior si existe
                        if current_item:
                            batch_data.append(current_item)
                        
                        # Nuevo item
                        raw_code = match.group(1) # Este YA TIENE PUNTOS (1.1.01)
                        name = match.group(3)
                        
                        # Validacion extra: Si el nombre es muy corto o parece basura, ignorar?
                        # Por ahora confiamos en el regex.
                        
                        current_item = {
                            'codigo': raw_code, # Guardamos con puntos
                            'nombre': name,
                            'descripcion': [],
                            'nivel': 0,
                            'padre_code': None
                        }
                    else:
                        # Si no es código, es descripción del item actual (si existe)
                        if current_item:
                            current_item['descripcion'].append(line)

            # Agregar el último
            if current_item:
                batch_data.append(current_item)

        self.stdout.write(self.style.SUCCESS(f'Encontrados {len(batch_data)} ítems. Guardando en BD...'))

        # Procesar Jerarquía y Guardar
        # Ordenamos por longitud de código (esto funciona bien con puntos tb: 1 < 1.1 < 1.1.01)
        batch_data.sort(key=lambda x: len(x['codigo']))
        
        saved_count = 0
        
        with transaction.atomic():
            for item in batch_data:
                code = item['codigo']
                desc = " ".join(item['descripcion']).strip()
                
                # Nivel: Basado en puntos
                # 1 (0 puntos) -> Nivel 1
                # 1.1 (1 punto) -> Nivel 2
                # 1.1.01 (2 puntos) -> Nivel 3
                # 1.1.01.01 (3 puntos) -> Nivel 4? (Ojo estructura MEF)
                
                # Estructura MEF tipica:
                # 1 (Ingresos Corrientes)
                # 1.1 (Impuestos)
                # 1.1.01 (Impuesto a la Renta)
                # 1.1.01.02 (Global)
                
                dots = code.count('.')
                nivel = dots + 1

                # Padre
                padre_obj = None
                if dots > 0:
                    # El padre es todo menos el último segmento
                    last_dot_index = code.rfind('.')
                    parent_code = code[:last_dot_index]
                    
                    if parent_code:
                        try:
                            padre_obj = ClasificadorPresupuestario.objects.get(codigo=parent_code)
                        except ClasificadorPresupuestario.DoesNotExist:
                            pass

                # Tipo (Ingreso/Gasto)
                first_digit = code[0]
                tipo = 'ING' if first_digit in ['1','2','3'] else 'GAS'
                
                # Imputable si es de ultimo nivel (usualmente nivel 4 o 6 digitos formateados)
                # O si no tiene hijos? Dificil saber sin ver todos.
                # Asumimos imputable si tiene 3 puntos (1.1.01.02) o mas? o si nivel >= 4?
                es_imputable = (nivel >= 3) 

                obj, created = ClasificadorPresupuestario.objects.update_or_create(
                    codigo=code,
                    defaults={
                        'nombre': item['nombre'],
                        'descripcion': desc,
                        'nivel': nivel,
                        'padre': padre_obj,
                        'tipo': tipo,
                        'es_imputable': es_imputable
                    }
                )
                saved_count += 1

        self.stdout.write(self.style.SUCCESS(f'Importación finalizada. {saved_count} clasificadores procesados.'))
