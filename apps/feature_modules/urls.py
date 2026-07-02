from django.urls import path
from . import views

urlpatterns = [
    # 功能模块
    path('', views.FeatureModuleListCreateView.as_view(), name='featuremodule-list'),
    path('<int:pk>/', views.FeatureModuleDetailView.as_view(), name='featuremodule-detail'),
    path('projects/<int:project_id>/modules/', views.get_project_feature_modules, name='project-featuremodules'),
    # 测试点
    path('test-points/', views.TestPointListCreateView.as_view(), name='testpoint-list'),
    path('test-points/<int:pk>/', views.TestPointDetailView.as_view(), name='testpoint-detail'),
    path('modules/<int:module_id>/test-points/', views.get_module_test_points, name='module-testpoints'),
]
