# sandbox/admin.py
from django.contrib import admin
from .models import SandboxSession


@admin.register(SandboxSession)
class SandboxSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'container_id', 'challenge', 'created_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('user__username', 'container_id')
    readonly_fields = ('created_at', 'expires_at')
