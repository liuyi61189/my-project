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

    # 本项目初始迁移是空占位 0001_initial（表已存在于库中，靠 runserver 直接起来）。
    # 为避免 admin 等内置 app 对 users/versions 的依赖在部分记录被删除后触发
    # InconsistentMigrationHistory，这里直接清空 django_migrations 记录，再由下面的
    # --fake-initial 在空表上按依赖顺序重新“假应用”所有初始迁移，使迁移状态自洽。
    print("Resetting migration records for consistent fake-initial...")
    subprocess.run([sys.executable, "-c",
        "import os, django; "
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings'); "
        "django.setup(); "
        "from django.db import connection; "
        "cur = connection.cursor(); "
        "cur.execute(\"DELETE FROM django_migrations\"); "
        "print('reset migration records')"], check=False)

    # 直接幂等地确保录制坐标列存在（不依赖迁移系统执行，规避迁移图断裂导致漏加列）。
    # 使用三引号多行字符串避免 -c 模式下的复合语句语法错误。
    ensure_script = """
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from django.db import connection
cur = connection.cursor()
created = []
for col in ('center_x', 'center_y'):
    cur.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = 'ui_test_case_steps' AND column_name = %s",
        (col,),
    )
    if not cur.fetchone():
        cur.execute('ALTER TABLE ui_test_case_steps ADD COLUMN ' + col + ' INT NULL')
        created.append(col)
print('ensured columns; newly added:', created)

# 确保 ui_test_case_executions.step_results (JSON) 列存在，用于前端展示每步失败详情
cur.execute(
    "SELECT 1 FROM information_schema.columns "
    "WHERE table_schema = DATABASE() AND table_name = 'ui_test_case_executions' AND column_name = 'step_results'",
)
if not cur.fetchone():
    cur.execute('ALTER TABLE ui_test_case_executions ADD COLUMN step_results JSON NULL')
    print('ensured column step_results on ui_test_case_executions')
else:
    print('step_results already exists')

# 确保需求拆解结果历史表存在（新功能：拆解结果历史记录）
cur.execute('''
CREATE TABLE IF NOT EXISTS requirement_analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    requirement_text LONGTEXT,
    result_content LONGTEXT,
    content_preview LONGTEXT,
    project_id INT NULL,
    created_by_id INT NOT NULL,
    created_at DATETIME NOT NULL
)
''')
print('ensured table requirement_analysis_results')

# 确保深度追问清单表存在（需求拆解结果下的追问项持久化）
cur.execute('''
CREATE TABLE IF NOT EXISTS clarification_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_result_id INT NOT NULL,
    question LONGTEXT,
    answer LONGTEXT,
    category VARCHAR(50) NOT NULL DEFAULT '其他',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    order_idx INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT fk_clarification_result
        FOREIGN KEY (analysis_result_id)
        REFERENCES requirement_analysis_results (id)
        ON DELETE CASCADE
)
''')
print('ensured table clarification_questions')

# 确保需求拆解结果表有 req_doc_id 列（关联需求文档，用于拆解结果持久化关联，刷新后重建）
cur.execute(
    "SELECT 1 FROM information_schema.columns "
    "WHERE table_schema = DATABASE() AND table_name = 'requirement_analysis_results' AND column_name = 'req_doc_id'",
)
if not cur.fetchone():
    cur.execute('ALTER TABLE requirement_analysis_results ADD COLUMN req_doc_id INT NULL')
    print('ensured column req_doc_id on requirement_analysis_results')
else:
    print('req_doc_id already exists')

# 确保测试用例生成任务表有 confirmed_answers 列（存储拆解确认的问答对，用于用例生成上下文注入）
cur.execute(
    "SELECT 1 FROM information_schema.columns "
    "WHERE table_schema = DATABASE() AND table_name = 'testcase_generation_task' AND column_name = 'confirmed_answers'",
)
if not cur.fetchone():
    cur.execute('ALTER TABLE testcase_generation_task ADD COLUMN confirmed_answers TEXT')
    print('ensured column confirmed_answers on testcase_generation_task')
else:
    print('confirmed_answers already exists')
"""
    print("Ensuring center_x/center_y columns exist on ui_test_case_steps...")
    subprocess.run([sys.executable, "-c", ensure_script], check=False)

    # 库实际已完成全部 schema 迁移（本项目初始迁移是空占位，表已存在）。
    # 用 --fake 把所有迁移标记为已应用，不执行任何 SQL，避免对已存在的索引/
    # 表重复执行导致 “Duplicate key/Table already exists”。这让 django_migrations
    # 记录与库的真实状态一致，迁移检查通过、runserver 干净启动。
    print("Running migrations (fake all, no SQL executed)...")
    subprocess.run([sys.executable, "manage.py", "migrate", "--fake", "--no-input"], check=False)

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
