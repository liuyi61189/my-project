from django.contrib import admin
from .models import FeatureModule, TestPoint


@admin.register(FeatureModule)
class FeatureModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'created_by', 'created_at']
    list_filter = ['project']
    search_fields = ['name']


@admin.register(TestPoint)
class TestPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'feature_module', 'created_by', 'created_at']
    list_filter = ['feature_module']
    search_fields = ['name']
