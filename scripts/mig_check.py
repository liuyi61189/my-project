import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from django.db import connection
c = connection.cursor()
c.execute("SELECT app, name, applied FROM django_migrations WHERE app IN ('projects', 'versions') ORDER BY app, name")
for r in c.fetchall():
    print(r)
print("---")
c.execute("DESCRIBE projects_project")
for r in c.fetchall():
    print(r)
