# sandbox/serializers.py
from rest_framework import serializers
from sandbox.models import SandboxSession


class SandboxSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SandboxSession
        fields = ['id', 'container_id', 'challenge', 'created_at', 'expires_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'expires_at']


class CommandExecuteSerializer(serializers.Serializer):
    command = serializers.CharField(max_length=1000)
    container_id = serializers.CharField(required=False)


class CommandResponseSerializer(serializers.Serializer):
    output = serializers.CharField()
    error = serializers.CharField()
    exit_code = serializers.IntegerField()

