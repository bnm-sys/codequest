# sandbox/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import SandboxSession
from .docker_service import DockerSandboxService
from .evaluator import OutputEvaluator
from .serializers import (
    SandboxSessionSerializer,
    CommandExecuteSerializer,
    CommandResponseSerializer
)
from courses.models import Challenge, Enrollment, UserChallengeAttempt
from accounts.models import Profile


def _calculate_progress(enrollment):
    """Recalculate completion percentage for an enrollment"""
    modules = enrollment.course.modules.all()
    total_modules = modules.count()
    if total_modules == 0:
        return 0

    completed = 0
    for module in modules:
        total_challenges = module.challenges.count()
        if total_challenges == 0:
            continue
        solved = UserChallengeAttempt.objects.filter(
            user=enrollment.user,
            challenge__module=module,
            is_correct=True
        ).values('challenge').distinct().count()
        if solved >= total_challenges:
            completed += 1

    return int((completed / total_modules) * 100)
from gamification.irt_engine import IRTEngine


class SandboxSessionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing sandbox sessions"""
    serializer_class = SandboxSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SandboxSession.objects.filter(user=self.request.user)
    
    def create(self, request):
        """Create a new sandbox session"""
        challenge_id = request.data.get('challenge_id')
        challenge = None
        if challenge_id:
            challenge = get_object_or_404(Challenge, id=challenge_id)
        
        service = DockerSandboxService()
        session = service.get_or_create_session(request.user, challenge)
        
        if not session:
            return Response(
                {'error': 'Failed to create sandbox session. Is Docker running?'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a command in the sandbox container"""
        session = self.get_object()
        
        if not session.is_active or session.is_expired():
            return Response(
                {'error': 'Session expired or inactive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CommandExecuteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        command = serializer.validated_data['command']
        service = DockerSandboxService()
        result = service.execute_command(session.container_id, command)
        
        response_serializer = CommandResponseSerializer(result)
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'])
    def evaluate(self, request, pk=None):
        """Evaluate command output against challenge expectations"""
        session = self.get_object()
        
        if not session.challenge:
            return Response(
                {'error': 'No challenge associated with this session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_output = request.data.get('output', '')
        command_ran = request.data.get('command', '').strip()
        challenge = session.challenge
        response_payload = {
            'is_correct': False,
            'feedback': '',
            'expected_output': challenge.expected_output,
            'xp_awarded': 0,
            'progress': None,
            'streak': None,
            'course_completed': False,
        }
        
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=challenge.module.course
        ).select_related('course').first()
        if not enrollment:
            return Response(
                {'error': 'You must enroll in this course before attempting challenges.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        evaluator = OutputEvaluator()
        is_correct, feedback = evaluator.evaluate_challenge(user_output, challenge, command_executed=command_ran)
        response_payload['is_correct'] = is_correct
        response_payload['feedback'] = feedback
        
        # Record attempt
        prev_attempts = UserChallengeAttempt.objects.filter(
            user=request.user,
            challenge=challenge
        ).count()
        attempt = UserChallengeAttempt.objects.create(
            user=request.user,
            challenge=challenge,
            is_correct=is_correct,
            attempt_no=prev_attempts + 1,
            time_seconds=int(request.data.get('time_seconds', 0) or 0),
        )
        
        # Update IRT skill mastery
        if session.challenge.module.skill_tags:
            skill_tags = session.challenge.module.skill_tags
            if isinstance(skill_tags, dict):
                for skill_tag in skill_tags.keys():
                    difficulty_map = {'easy': -1.0, 'medium': 0.0, 'hard': 1.0, 'expert': 2.0}
                    challenge_difficulty = difficulty_map.get(challenge.difficulty.lower(), 0.0)
                    
                    IRTEngine.update_skill_mastery(
                        user=request.user,
                        skill_tag=skill_tag,
                        is_correct=is_correct,
                        challenge_difficulty=challenge_difficulty,
                        challenge_discrimination=1.0
                    )
        
        if is_correct:
            earned_xp = challenge.module.points
            enrollment.xp = (enrollment.xp or 0) + earned_xp
            enrollment.streak = (enrollment.streak or 0) + 1
            enrollment.progress = _calculate_progress(enrollment)
            enrollment.save()
            
            try:
                profile = request.user.profile
                profile.xp = (profile.xp or 0) + earned_xp
                profile.current_streak = max(profile.current_streak or 0, enrollment.streak)
                # Only increment completed challenge count if this is the first correct attempt
                if not UserChallengeAttempt.objects.filter(
                    user=request.user,
                    challenge=challenge,
                    is_correct=True
                ).exclude(id=attempt.id).exists():
                    profile.completed_challenges = (profile.completed_challenges or 0) + 1
                profile.save()
            except Profile.DoesNotExist:
                pass
            
            response_payload['xp_awarded'] = earned_xp
            response_payload['progress'] = enrollment.progress
            response_payload['streak'] = enrollment.streak
            response_payload['course_completed'] = enrollment.progress >= 100
        else:
            enrollment.streak = 0
            enrollment.save(update_fields=['streak'])
            response_payload['streak'] = 0
            response_payload['progress'] = _calculate_progress(enrollment)
        
        return Response(response_payload)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop and cleanup a sandbox session"""
        session = self.get_object()
        service = DockerSandboxService()
        
        if session.container_id:
            service.stop_container(session.container_id)
        
        session.is_active = False
        session.save()
        
        return Response({'message': 'Session stopped'})
