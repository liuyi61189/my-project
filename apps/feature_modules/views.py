from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import models
from .models import FeatureModule, TestPoint
from .serializers import FeatureModuleSerializer, TestPointSerializer
from apps.projects.models import Project
from apps.core.mixins import ProjectScopedMixin, get_accessible_projects_for_user


class FeatureModuleListCreateView(ProjectScopedMixin, generics.ListCreateAPIView):
    """功能模块列表和创建视图"""
    queryset = FeatureModule.objects.all()
    serializer_class = FeatureModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['project', 'name']

    def perform_create(self, serializer):
        user = self.request.user
        project_id = self.request.data.get('project_id')
        project = None
        if project_id:
            try:
                project = self.get_accessible_projects().get(id=project_id)
            except Project.DoesNotExist:
                pass
        serializer.save(created_by=user, project=project)


class FeatureModuleDetailView(ProjectScopedMixin, generics.RetrieveUpdateDestroyAPIView):
    """功能模块详情视图"""
    queryset = FeatureModule.objects.all()
    serializer_class = FeatureModuleSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_project_feature_modules(request, project_id):
    """获取指定项目的功能模块列表"""
    accessible_projects = get_accessible_projects_for_user(request.user)

    if not accessible_projects.filter(id=project_id).exists():
        return Response({'error': '没有权限访问该项目'}, status=status.HTTP_403_FORBIDDEN)

    modules = FeatureModule.objects.filter(project_id=project_id).order_by('name')
    from .serializers import FeatureModuleSerializer
    serializer = FeatureModuleSerializer(modules, many=True)
    return Response(serializer.data)


# ─── TestPoint Views ───

class TestPointListCreateView(ProjectScopedMixin, generics.ListCreateAPIView):
    """测试点列表和创建视图"""
    serializer_class = TestPointSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['feature_module']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['feature_module', 'name']

    def get_queryset(self):
        accessible_projects = self.get_accessible_projects()
        accessible_modules = FeatureModule.objects.filter(project__in=accessible_projects)
        return TestPoint.objects.filter(feature_module__in=accessible_modules)

    def perform_create(self, serializer):
        user = self.request.user
        feature_module_id = self.request.data.get('feature_module_id')
        feature_module = None
        if feature_module_id:
            try:
                accessible_modules = FeatureModule.objects.filter(
                    project__in=self.get_accessible_projects()
                )
                feature_module = accessible_modules.get(id=feature_module_id)
            except FeatureModule.DoesNotExist:
                pass
        serializer.save(created_by=user, feature_module=feature_module)


class TestPointDetailView(ProjectScopedMixin, generics.RetrieveUpdateDestroyAPIView):
    """测试点详情视图"""
    serializer_class = TestPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        accessible_projects = self.get_accessible_projects()
        accessible_modules = FeatureModule.objects.filter(project__in=accessible_projects)
        return TestPoint.objects.filter(feature_module__in=accessible_modules)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_module_test_points(request, module_id):
    """获取指定功能模块下的测试点列表"""
    accessible_projects = get_accessible_projects_for_user(request.user)
    accessible_modules = FeatureModule.objects.filter(project__in=accessible_projects)

    if not accessible_modules.filter(id=module_id).exists():
        return Response({'error': '没有权限访问该功能模块'}, status=status.HTTP_403_FORBIDDEN)

    test_points = TestPoint.objects.filter(feature_module_id=module_id).order_by('name')
    from .serializers import TestPointSerializer
    serializer = TestPointSerializer(test_points, many=True)
    return Response(serializer.data)
