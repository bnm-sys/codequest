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
            # Try to detect Docker socket location (macOS Docker Desktop)
            import os
            docker_base_url = settings.DOCKER_BASE_URL
            # If default socket doesn't exist, try macOS Docker Desktop location
            if docker_base_url == 'unix://var/run/docker.sock' and not os.path.exists('/var/run/docker.sock'):
                docker_path = os.path.expanduser('~/.docker/run/docker.sock')
                if os.path.exists(docker_path):
                    docker_base_url = f'unix://{docker_path}'
            
            self.client = docker.DockerClient(base_url=docker_base_url)
            # Test connection
            self.client.ping()
            self.image = settings.DOCKER_IMAGE
            self.timeout = settings.DOCKER_CONTAINER_TIMEOUT
            logger.info(f"Docker client connected successfully at {docker_base_url}")
        except docker.errors.DockerException as e:
            logger.error(f"Failed to connect to Docker: {e}")
            self.client = None
        except Exception as e:
            logger.error(f"Error initializing Docker client: {e}")
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
            # Use tail -f /dev/null to keep container running
            container = self.client.containers.create(
                image=self.image,
                command=['tail', '-f', '/dev/null'],  # Keep container running
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
            
            # Start container first
            container.start()
            
            # Verify container is running
            container.reload()
            if container.status != 'running':
                logger.error(f"Container {container.id} failed to start. Status: {container.status}")
                try:
                    container.remove()
                except:
                    pass
                return None
            
            # Set up challenge environment if challenge provided
            if challenge and challenge.setup_commands:
                self._setup_challenge_environment(container, challenge)
            
            # Create session record after successful start
            expires_at = timezone.now() + timedelta(seconds=self.timeout)
            session = SandboxSession.objects.create(
                user=user,
                container_id=container.id,
                challenge=challenge,
                expires_at=expires_at,
                is_active=True
            )
            
            logger.info(f"Created and started container {container.id} for user {user.username}")
            
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
            
            # Always execute via bash -c for proper shell features (pipes, redirections, etc.)
            # If command already includes bash -c, extract it; otherwise wrap it
            if command.startswith('/bin/bash -c'):
                # Remove "/bin/bash -c" prefix and extract the actual command
                cmd_part = command[len('/bin/bash -c'):].strip()
                # Remove quotes if present
                if cmd_part.startswith('"') and cmd_part.endswith('"'):
                    cmd_part = cmd_part[1:-1]
                elif cmd_part.startswith("'") and cmd_part.endswith("'"):
                    cmd_part = cmd_part[1:-1]
                # Execute via bash -c as a list
                exec_command = ['/bin/bash', '-c', cmd_part]
            else:
                # Wrap command in bash -c for shell features
                exec_command = ['/bin/bash', '-c', command]
            
            # Execute command
            exec_result = container.exec_run(
                exec_command,
                stdout=True,
                stderr=True
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
    
    def _setup_challenge_environment(self, container, challenge):
        """Set up the container environment for a specific challenge"""
        if not challenge.setup_commands:
            return
        
        try:
            # Execute each setup command
            setup_commands = [cmd.strip() for cmd in challenge.setup_commands.split('\n') if cmd.strip()]
            for cmd in setup_commands:
                exec_result = container.exec_run(
                    ['/bin/bash', '-c', cmd],
                    stdout=True,
                    stderr=True
                )
                if exec_result.exit_code != 0:
                    logger.warning(f"Setup command failed: {cmd}")
        except Exception as e:
            logger.error(f"Error setting up challenge environment: {e}")
    
    def get_or_create_session(self, user, challenge=None):
        """Get active session or create a new one"""
        # Check for existing active session for this specific challenge
        if challenge:
            active_session = SandboxSession.objects.filter(
                user=user,
                challenge=challenge,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()
            if active_session:
                return active_session
        
        # Create new session
        return self.create_container(user, challenge)

