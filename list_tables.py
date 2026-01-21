import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with connection.cursor() as cursor:
    print(connection.introspection.table_names())
