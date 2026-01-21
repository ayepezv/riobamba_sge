import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

prefixes = ['fi_', 'pl_', 'pr_', 'financiero_']
tables = connection.introspection.table_names()

relevant_tables = [t for t in tables if any(t.startswith(p) for p in prefixes)]
relevant_tables.sort()

print(f"Found {len(relevant_tables)} relevant tables:")
with connection.cursor() as cursor:
    for t in relevant_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"{t}: {count} rows")
