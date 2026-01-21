import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM financiero_paclinea LIMIT 0")
    col_names = [desc[0] for desc in cursor.description]
    print(f"Columns in financiero_paclinea: {col_names}")
