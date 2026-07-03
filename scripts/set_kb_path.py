import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from apps.projects.models import Project
for p in Project.objects.all():
    print(f'Project: {p.id} {p.name}')
p = Project.objects.first()
if p:
    p.knowledge_base_path = '/app/knowledge-bases/万年历/'
    p.save()
    print(f'DONE: {p.id} {p.name} -> {p.knowledge_base_path}')
else:
    print('No project found')
