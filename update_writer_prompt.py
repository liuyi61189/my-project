import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from apps.requirement_analysis.models import PromptConfig
with open('/app/tester_new.md', 'r', encoding='utf-8') as f:
    new_content = f.read()
updated = PromptConfig.objects.filter(prompt_type='writer', is_active=True).update(content=new_content)
print(f'Updated {updated} writer prompts')
if updated == 0:
    PromptConfig.objects.filter(prompt_type='writer').update(is_active=False)
    PromptConfig.objects.create(name='AI用例编写提示词', prompt_type='writer', content=new_content, is_active=True)
    print('Created new writer prompt')
for p in PromptConfig.objects.filter(prompt_type='writer', is_active=True):
    print(f'Active: {p.name}, length: {len(p.content)}')
