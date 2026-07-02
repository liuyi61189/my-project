import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Apps that need 0001_initial + 0002_initial (no migration files on disk at all)
empty_apps = ['assistant', 'core', 'reports', 'testsuites', 'ui_automation']

# Apps that need 0001_initial only
single_apps = ['versions']

# Apps that need 0002_initial (have 0001 but missing 0002)
need_0002 = ['reviews', 'api_testing', 'projects', 'requirement_analysis', 'users']

base = '/app/apps'

for app in empty_apps:
    d = f'{base}/{app}/migrations'
    with open(f'{d}/0001_initial.py', 'w') as f:
        f.write('''from django.db import migrations

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = []
''')
    with open(f'{d}/0002_initial.py', 'w') as f:
        f.write(f'''from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('{app}', '0001_initial'),
    ]
    operations = []
''')
    print(f'Created 0001 + 0002 for {app}')

for app in single_apps:
    d = f'{base}/{app}/migrations'
    with open(f'{d}/0001_initial.py', 'w') as f:
        f.write('''from django.db import migrations

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = []
''')
    print(f'Created 0001 for {app}')

for app in need_0002:
    d = f'{base}/{app}/migrations'
    with open(f'{d}/0002_initial.py', 'w') as f:
        f.write(f'''from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('{app}', '0001_initial'),
    ]
    operations = []
''')
    print(f'Created 0002 for {app}')

# Fix dependency chains for apps that have 0001_add_performance_indexes depending on 0001_initial
for app in ['reviews', 'api_testing']:
    filepath = f'{base}/{app}/migrations/0001_add_performance_indexes.py'
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        content = content.replace(f"('{app}', '0001_initial')", f"('{app}', '0002_initial')")
        with open(filepath, 'w') as f:
            f.write(content)
        print(f'Fixed dependency for {app}/0001_add_performance_indexes')

# Fix projects 0006 and 0007
proj_0006 = f'{base}/projects/migrations/0006_add_performance_indexes.py'
if os.path.exists(proj_0006):
    with open(proj_0006, 'r') as f:
        content = f.read()
    # Check if it depends on 0005 or something else
    if "'projects', '0005_" in content or "'projects', '0005'" in content:
        print('projects/0006 dependency OK')
    else:
        print(f'projects/0006 content check needed')

# Check if projects has 0007
proj_0007 = f'{base}/projects/migrations/0007_remove_project_idx_project_owner_and_more.py'
if not os.path.exists(proj_0007):
    # Database has it, need to create
    with open(proj_0007, 'w') as f:
        f.write('''from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0006_add_performance_indexes'),
    ]
    operations = []
''')
    print('Created projects/0007')

# Fix requirement_analysis - check if 0002_initial is needed between 0001 and 0002_alter
ra_0002 = f'{base}/requirement_analysis/migrations/0002_initial.py'
if not os.path.exists(ra_0002):
    with open(ra_0002, 'w') as f:
        f.write('''from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('requirement_analysis', '0001_initial'),
    ]
    operations = []
''')
    print('Created requirement_analysis/0002_initial')

# Fix users 0002
users_0002 = f'{base}/users/migrations/0002_initial.py'
if not os.path.exists(users_0002):
    # But database has 0002_alter_user_groups, not 0002_initial
    # Check what the db actually has
    cursor.execute("SELECT name FROM django_migrations WHERE app='users' ORDER BY id")
    rows = [r[0] for r in cursor.fetchall()]
    print(f'users migrations in db: {rows}')
    # If db has 0002_alter_user_groups, we need to check if the file exists
    users_0002_alter = f'{base}/users/migrations/0002_alter_user_groups.py'
    if not os.path.exists(users_0002_alter):
        with open(users_0002_alter, 'w') as f:
            f.write('''from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]
    operations = []
''')
        print('Created users/0002_alter_user_groups')

print('\nDone!')
