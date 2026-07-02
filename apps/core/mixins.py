"""
公共权限 Mixin —— 消除各 View 中重复的 Q(owner=user) | Q(members=user) 查询。

权限策略：
- superuser（如 admin）：可查看和操作所有项目及资源
- 普通用户：只能看到自己创建（owner）或被邀请加入（members）的项目

三种使用场景：
1. OwnerOrMemberMixin —— 模型本身有 owner/members 字段（如 ApiProject、Project）
2. ProjectScopedMixin  —— 模型通过 project 外键关联到 Project（如 TestCase、ApiCollection）
3. get_accessible_projects_for_user() —— 函数视图（FBV）中复用同一查询逻辑
"""

from django.db import models
from apps.projects.models import Project


def _is_superuser(user):
    """判断用户是否为超级管理员"""
    if user is None or not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser


def get_accessible_projects_for_user(user):
    """
    获取用户有权限访问的项目 queryset。
    - superuser：全部项目
    - 普通用户：自己创建或被邀请加入的项目
    """
    if _is_superuser(user):
        return Project.objects.all()
    return Project.objects.filter(
        models.Q(owner=user) | models.Q(members=user)
    ).distinct()


def filter_by_owner_or_member(queryset, user):
    """
    对任意含 owner (FK) 和 members (M2M) 字段的 queryset 进行权限过滤。
    适用于 ApiProject、UiProject 等与 Project 同构的模型。
    - superuser：全部记录
    - 普通用户：owner 或 member

    用法：
        qs = filter_by_owner_or_member(ApiProject.objects.all(), request.user)
    """
    if _is_superuser(user):
        return queryset.distinct()
    return queryset.filter(
        models.Q(owner=user) | models.Q(members=user)
    ).distinct()


class OwnerOrMemberMixin:
    """
    适用于模型自身包含 owner (FK) 和 members (M2M) 字段的 ViewSet。
    - superuser：全部项目
    - 普通用户：owner 或 member

    用法：
        class ApiProjectViewSet(OwnerOrMemberMixin, viewsets.ModelViewSet):
            queryset = ApiProject.objects.all()
            ...
    """

    def get_queryset(self):
        qs = super().get_queryset()
        if _is_superuser(self.request.user):
            return qs.distinct()
        user = self.request.user
        return qs.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()


class ProjectScopedMixin:
    """
    适用于通过 project 外键关联到 Project 的模型 View。
    - superuser：全部项目下的记录
    - 普通用户：有权访问的项目下的记录

    提供 get_accessible_projects() 方法供 perform_create 等场景复用。

    用法：
        class TestCaseListCreateView(ProjectScopedMixin, generics.ListCreateAPIView):
            queryset = TestCase.objects.all()
            ...
    """

    def get_accessible_projects(self):
        """获取当前用户有权限访问的项目 queryset"""
        return get_accessible_projects_for_user(self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        accessible_projects = self.get_accessible_projects()
        return qs.filter(project__in=accessible_projects)
