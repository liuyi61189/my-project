import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from apps.requirement_analysis.models import AIModelService

class FakeTask:
    project_id = 1

ctx = AIModelService.build_knowledge_context(FakeTask())
print(f"Context length: {len(ctx)} chars")
print("---first 800 chars---")
print(ctx[:800])
