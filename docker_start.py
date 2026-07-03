import subprocess
import sys
import time
import os

def wait_for_mysql(host, port, user, password, db, max_retries=30):
    """等待MySQL就绪"""
    import pymysql
    print(f"Waiting for MySQL at {host}:{port}...")
    for i in range(max_retries):
        try:
            conn = pymysql.connect(host=host, port=int(port), user=user, password=password, db=db)
            conn.close()
            print("MySQL is ready!")
            return True
        except Exception as e:
            print(f"  Attempt {i+1}/{max_retries}: {e}")
            time.sleep(2)
    return False

if __name__ == "__main__":
    from decouple import config

    host = config('DB_HOST', default='127.0.0.1')
    port = config('DB_PORT', default='3306')
    user = config('DB_USER', default='root')
    password = config('DB_PASSWORD', default='')
    db = config('DB_NAME', default='testhub')

    if not wait_for_mysql(host, port, user, password, db):
        print("ERROR: MySQL did not become ready in time.")
        sys.exit(1)

    print("Making migrations...")
    subprocess.run([sys.executable, "manage.py", "makemigrations", "--no-input"], check=False)

    print("Running migrations...")
    subprocess.run([sys.executable, "manage.py", "migrate", "--no-input"], check=False)

    print("Initializing locator strategies...")
    try:
        subprocess.run([sys.executable, "manage.py", "init_locator_strategies"], check=False)
    except Exception as e:
        print(f"init_locator_strategies skipped: {e}")

    print("Creating superuser if not exists...")
    create_su_script = """
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@testhub.local', 'Admin@123456')
    print('Superuser created: admin / Admin@123456')
else:
    print('Superuser already exists')
"""
    subprocess.run([sys.executable, "-c", create_su_script], check=True)

    print("==> Starting Django server on 0.0.0.0:8000 ...")
    os.execvp(sys.executable, [sys.executable, "manage.py", "runserver", "0.0.0.0:8000"])
