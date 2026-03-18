#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'msusuarios.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
# Para PostgreSQL, resetear la secuencia
cursor.execute('ALTER SEQUENCE products_producto_id_seq RESTART WITH 1')
print("ID sequence reset successfully. Next ID will start from 1.")
