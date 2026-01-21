from django.core.management.base import BaseCommand
from apps.financiero.models import ClasificadorPresupuestario
import pdfplumber
import re
import os

class Command(BaseCommand):
    help = 'Importar Clasificador Presupuestario desde PDF'

    def add_arguments(self, parser):
        parser.add_argument('pdf_file', type=str, nargs='?', default='docs/Informacion/ClasificadorPresupuestario.pdf', help='Ruta al archivo PDF')

    def handle(self, *args, **options):
        pdf_path = options['pdf_file']
        
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {pdf_path}'))
            return

        self.stdout.write(f'Leyendo: {pdf_path}')
        
        extracted_data = []
        
        # Regex: Start of line, 1-2 digits, followed by (.digits)*
        regex = r'^(\d{1,2}(\.\d{2})*)'
        
        with pdfplumber.open(pdf_path) as pdf:
            current_item = None
            
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                    
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    match = re.match(regex, line)
                    if match:
                        if current_item:
                            extracted_data.append(current_item)
                            
                        visual_code = match.group(0)
                        clean_code = visual_code.replace('.', '')
                        
                        titulo = line[match.end():].strip()
                        
                        current_item = {
                            'code': clean_code,
                            'visual': visual_code,
                            'name': titulo,
                            'desc': ''
                        }
                    else:
                        if current_item:
                            current_item['desc'] += line + '\n'

            if current_item:
                extracted_data.append(current_item)
                
        # Sort by length of clean code to ensure parents are created first
        extracted_data.sort(key=lambda x: len(x['code']))
        
        self.stdout.write(f'Encontrados {len(extracted_data)} items. Procesando...')
        
        count = 0
        for item in extracted_data:
            code = item['code']
            visual = item['visual']
            
            parent = None
            # Parent logic:
            # 1 digit (5) -> Parent None
            # 2 digits (51) -> Parent (5)
            # 4 digits (5101) -> Parent (51)
            # 6 digits (510105) -> Parent (5101)
            if len(code) > 1:
                if len(code) == 2:
                     parent_code = code[0]
                else:
                     parent_code = code[:-2]
                
                try:
                    parent = ClasificadorPresupuestario.objects.get(codigo=parent_code)
                except ClasificadorPresupuestario.DoesNotExist:
                    pass
            
            level = 1
            if parent:
                level = parent.nivel + 1
            elif len(code) == 1: level = 1
            elif len(code) == 2: level = 2
            elif len(code) == 4: level = 3
            elif len(code) == 6: level = 4

            # Infer type based on first digit
            # 1, 2, 3: Ingreso (ING)
            # 5, 6, 7: Gasto (GAS)
            tipo = 'GAS'
            if code.startswith(('1', '2', '3')):
                tipo = 'ING'
            
            ClasificadorPresupuestario.objects.update_or_create(
                codigo=code,
                defaults={
                    'codigo_visual': visual,
                    'nombre': item['name'],
                    'descripcion': item['desc'].strip(),
                    'padre': parent,
                    'nivel': level,
                    'tipo': tipo
                }
            )
            count += 1
            if count % 100 == 0:
                 self.stdout.write(f'Procesados {count}...')

        self.stdout.write('Actualizando es_imputable...')
        # Reset all to True
        ClasificadorPresupuestario.objects.update(es_imputable=True)
        # Set parents to False
        parent_ids = ClasificadorPresupuestario.objects.filter(hijos__isnull=False).values_list('id', flat=True)
        ClasificadorPresupuestario.objects.filter(id__in=parent_ids).update(es_imputable=False)
        
        self.stdout.write(self.style.SUCCESS(f'Importación completa. {count} registros actualizados/creados.'))
