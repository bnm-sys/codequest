# sandbox/docker_service.py
"""
Docker container management service for secure sandbox execution
"""
import docker
import logging
import time
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import SandboxSession

logger = logging.getLogger(__name__)


class DockerSandboxService:
    """Service for managing Docker containers for user sandboxes"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.image = settings.DOCKER_IMAGE
            self.timeout = settings.DOCKER_CONTAINER_TIMEOUT
        except docker.errors.DockerException as e:
            logger.error(f"Failed to connect to Docker: {e}")
            self.client = None
    
    def create_container(self, user, challenge=None):
        """
        Create a new Docker container for a user session
        
        Args:
            user: User instance
            challenge: Optional Challenge instance
            
        Returns:
            SandboxSession instance or None if failed
        """
        if not self.client:
            logger.error("Docker client not available")
            return None
        
        try:
            # Create container with limited resources
            container = self.client.containers.create(
                image=self.image,
                command='/bin/bash',  # Keep container running
                stdin_open=True,
                tty=True,
                detach=True,
                mem_limit='512m',  # Limit memory
                cpu_period=100000,
                cpu_quota=50000,  # Limit CPU to 50%
                network_disabled=False,  # Allow network for git clone, etc.
                read_only=False,
                tmpfs={'/tmp': 'size=100m'}  # Temporary filesystem
            )
            
            # Create session record
            expires_at = timezone.now() + timedelta(seconds=self.timeout)
            session = SandboxSession.objects.create(
                user=user,
                container_id=container.id,
                challenge=challenge,
                expires_at=expires_at,
                is_active=True
            )
            
            # Start container
            container.start()
            logger.info(f"Created container {container.id} for user {user.username}")
            
            return session
            
        except docker.errors.ImageNotFound:
            logger.error(f"Docker image {self.image} not found")
            return None
        except Exception as e:
            logger.error(f"Error creating container: {e}")
            return None
    
    def execute_command(self, container_id, command):
        """
        Execute a command in a Docker container
        
        Args:
            container_id: Docker container ID
            command: Command string to execute
            
        Returns:
            Dict with 'output', 'error', 'exit_code'
        """
        if not self.client:
            return {'output': '', 'error': 'Docker client not available', 'exit_code': 1}
        
        try:
            container = self.client.containers.get(container_id)
            
            # Execute command with timeout
            exec_result = container.exec_run(
                command,
                stdout=True,
                stderr=True,
                timeout=30  # 30 second timeout per command
            )
            
            output = exec_result.output.decode('utf-8', errors='replace')
            exit_code = exec_result.exit_code
            
            return {
                'output': output,
                'error': '' if exit_code == 0 else output,
                'exit_code': exit_code
            }
            
        except docker.errors.NotFound:
            return {'output': '', 'error': 'Container not found', 'exit_code': 1}
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {'output': '', 'error': str(e), 'exit_code': 1}
    
    def stop_container(self, container_id):
        """Stop and remove a Docker container"""
        if not self.client:
            return False
        
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            container.remove()
            logger.info(f"Stopped and removed container {container_id}")
            return True
        except docker.errors.NotFound:
            return True  # Already removed
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired sandbox sessions and their containers"""
        expired_sessions = SandboxSession.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now()
        )
        
        cleaned = 0
        for session in expired_sessions:
            if session.container_id:
                self.stop_container(session.container_id)
            session.is_active = False
            session.save()
            cleaned += 1
        
        logger.info(f"Cleaned up {cleaned} expired sessions")
        return cleaned
    
    def get_or_create_session(self, user, challenge=None):
        """Get active session or create a new one"""
        # Check for existing active session
        active_session = SandboxSession.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        
        if active_session:
            return active_session
        
        # Create new session
        return self.create_container(user, challenge)

