import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.db import connection

with connection.cursor() as c:
    c.execute("SELECT app, name, applied FROM django_migrations WHERE app IN ('projects', 'versions') ORDER BY app, name")
    for r in c.fetchall():
        print(r)

print("---")
# Check if owner column exists
with connection.cursor() as c:
    c.execute("DESCRIBE projects_project")
    for r in c.fetchall():
        print(r)
