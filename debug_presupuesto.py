import os
import django
import sys

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.financiero.models import Presupuesto

print("--- DIAGNOSTICO PRESUPUESTO ---")

# 1. Total items
count = Presupuesto.objects.count()
print(f"Total Presupuestos: {count}")

# 2. Search for 53.02.04
term = '53.02.04'
match = Presupuesto.objects.filter(partida_concatenada__contains=term).first()
if match:
    print(f"FOUND match for '{term}': {match.partida_concatenada}")
else:
    print(f"NO match for '{term}'")

# 3. List some 53 items
items53 = list(Presupuesto.objects.filter(partida_concatenada__contains='.53.').values_list('partida_concatenada', flat=True)[:10])
print(f"Sample 53 items: {items53}")

# 4. List some 84 items
items84 = list(Presupuesto.objects.filter(partida_concatenada__contains='.84.').values_list('partida_concatenada', flat=True)[:10])
print(f"Sample 84 items: {items84}")
