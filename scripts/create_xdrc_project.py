import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/app')
django.setup()

from apps.projects.models import Project
from django.contrib.auth import get_user_model
User = get_user_model()

# 取第一个可用用户
user = User.objects.first()
print(f"使用用户：{user}")

# 检查是否已存在
if Project.objects.filter(name='心动日常').exists():
    p = Project.objects.get(name='心动日常')
    p.knowledge_base_path = '/app/knowledge-bases/心动日常/'
    p.save()
    print(f"已更新：ID={p.id}  kb={p.knowledge_base_path}")
else:
    p = Project.objects.create(
        name='心动日常',
        description='心动日常 APP 功能知识库，覆盖聊天通讯、百宝袋工具、宠物猫、365打卡、娱乐天地、会员体系等全功能模块',
        status='active',
        owner=user,
        knowledge_base_path='/app/knowledge-bases/心动日常/',
    )
    print(f"创建成功：ID={p.id}  name={p.name}  kb={p.knowledge_base_path}")
