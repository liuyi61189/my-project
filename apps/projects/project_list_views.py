from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.core.mixins import get_accessible_projects_for_user

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_projects_list(request):
    """获取用户有权限访问的项目列表，用于下拉选择"""
    projects = get_accessible_projects_for_user(request.user).values('id', 'name', 'status').order_by('name')
    
    return Response({
        'results': list(projects)
    })