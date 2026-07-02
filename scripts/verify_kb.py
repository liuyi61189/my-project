import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from apps.projects.views import _resolve_knowledge_path
from apps.projects.models import Project

p = Project.objects.first()
path = _resolve_knowledge_path(p)
print(f'Knowledge path: {path}')

if path:
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = '  ' * level
        folder = os.path.basename(root) or '万年历'
        print(f'{indent}📁 {folder}')
        for f in sorted(files):
            if f.endswith('.md'):
                fpath = os.path.join(root, f)
                size = os.path.getsize(fpath)
                print(f'{indent}  📄 {f} ({size}B)')
        # First 3 lines of last file
        if files:
            fpath = os.path.join(root, sorted(files)[0])
            with open(fpath, encoding='utf-8') as fh:
                first = fh.readline().strip()
            print(f'{indent}  → {first}')
else:
    print('ERROR: No valid knowledge path')
