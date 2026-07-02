import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from django.db import connection
from datetime import datetime

with connection.cursor() as c:
    # Check what's in django_migrations for projects and versions
    c.execute("SELECT app, name FROM django_migrations WHERE app IN ('projects', 'versions') ORDER BY app, name")
    print("=== Current migration records ===")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # Fake-apply projects.0005
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        c.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('projects', '0005_project_owner_alter_project_description_and_more', %s)",
            [now]
        )
        connection.commit()
        print(f"\n✓ Faked projects.0005 at {now}")
    except Exception as e:
        print(f"\n✗ Failed to fake projects.0005: {e}")

    # Fake-apply users.0002
    try:
        c.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('users', '0002_alter_user_groups', %s)",
            [now]
        )
        connection.commit()
        print(f"✓ Faked users.0002 at {now}")
    except Exception as e:
        print(f"✗ Failed to fake users.0002: {e}")

print("\nDone.")
