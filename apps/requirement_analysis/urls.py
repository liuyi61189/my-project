from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RequirementDocumentViewSet,
    RequirementAnalysisViewSet,
    BusinessRequirementViewSet,
    GeneratedTestCaseViewSet,
    AnalysisTaskViewSet,
    AIModelConfigViewSet,
    PromptConfigViewSet,
    GenerationConfigViewSet,
    TestCaseGenerationTaskViewSet,
    ConfigStatusViewSet,
    GeneratedRequirementDocViewSet,
    RequirementAnalysisResultViewSet,
    ClarificationQuestionViewSet,
    upload_and_analyze,
    analyze_text,
    generate_requirement_doc,
    get_requirement_template,
    generate_knowledge_base,
    deep_question,
    refine_analysis,
)

# 创建DRF路由器
router = DefaultRouter()
router.register(r'documents', RequirementDocumentViewSet, basename='requirementdocument')
router.register(r'analyses', RequirementAnalysisViewSet, basename='requirementanalysis')
router.register(r'requirements', BusinessRequirementViewSet, basename='businessrequirement')
router.register(r'test-cases', GeneratedTestCaseViewSet, basename='generatedtestcase')
router.register(r'tasks', AnalysisTaskViewSet, basename='analysistask')
router.register(r'ai-models', AIModelConfigViewSet, basename='aimodelconfig')
router.register(r'prompts', PromptConfigViewSet, basename='promptconfig')
router.register(r'generation-config', GenerationConfigViewSet, basename='generationconfig')
router.register(r'testcase-generation', TestCaseGenerationTaskViewSet, basename='testcasegenerationtask')
router.register(r'config', ConfigStatusViewSet, basename='configstatus')
router.register(r'req-docs', GeneratedRequirementDocViewSet, basename='generatedrequirementdoc')
router.register(r'analysis-results', RequirementAnalysisResultViewSet, basename='requirementanalysisresult')
router.register(r'clarifications', ClarificationQuestionViewSet, basename='clarificationquestion')

app_name = 'requirement_analysis'

urlpatterns = [
    # DRF路由
    path('api/', include(router.urls)),

    # 特殊API端点
    path('api/upload-and-analyze/', upload_and_analyze, name='upload-and-analyze'),
    path('api/analyze-text/', analyze_text, name='analyze-text'),
    path('api/generate-req-doc/', generate_requirement_doc, name='generate-req-doc'),
    path('api/req-doc-template/', get_requirement_template, name='req-doc-template'),
    path('api/generate-knowledge-base/', generate_knowledge_base, name='generate-knowledge-base'),
    path('api/deep-question/', deep_question, name='deep-question'),
    path('api/refine-analysis/', refine_analysis, name='refine-analysis'),
]