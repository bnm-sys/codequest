# gamification/irt_engine.py
"""
Item Response Theory (IRT) implementation for adaptive learning.
Uses the 2-PL (2-Parameter Logistic) IRT model.
"""
import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from django.utils import timezone
from .models import SkillMastery


class IRTEngine:
    """
    2-PL IRT Model: P(theta) = 1 / (1 + exp(-a * (theta - b)))
    where:
    - theta: user ability/skill level
    - a: discrimination parameter (how well the item discriminates between abilities)
    - b: difficulty parameter (item difficulty)
    - P(theta): probability of correct response
    """
    
    @staticmethod
    def logistic_function(theta, a, b):
        """2-PL logistic function"""
        return 1 / (1 + np.exp(-a * (theta - b)))
    
    @staticmethod
    def estimate_ability(responses, difficulties, discriminations, initial_theta=0.0):
        """
        Estimate user ability (theta) using Maximum Likelihood Estimation (MLE)
        
        Args:
            responses: list of binary responses (1=correct, 0=incorrect)
            difficulties: list of difficulty parameters (b) for each item
            discriminations: list of discrimination parameters (a) for each item
            initial_theta: starting value for theta
            
        Returns:
            Estimated theta value
        """
        if not responses:
            return initial_theta
        
        def log_likelihood(theta):
            """Negative log-likelihood to minimize"""
            ll = 0.0
            for i, response in enumerate(responses):
                p = IRTEngine.logistic_function(theta, discriminations[i], difficulties[i])
                # Avoid log(0)
                p = max(1e-10, min(1 - 1e-10, p))
                ll += response * np.log(p) + (1 - response) * np.log(1 - p)
            return -ll  # Negative because we minimize
        
        # Bounds: theta typically ranges from -3 to +3
        result = minimize(log_likelihood, initial_theta, method='L-BFGS-B', bounds=[(-3, 3)])
        return float(result.x[0])
    
    @staticmethod
    def estimate_item_parameters(responses_matrix, initial_a=1.0, initial_b=0.0):
        """
        Estimate item parameters (a, b) from response matrix
        
        Args:
            responses_matrix: 2D array where rows are users, columns are items
            initial_a: initial discrimination parameter
            initial_b: initial difficulty parameter
            
        Returns:
            Tuple of (discriminations, difficulties) arrays
        """
        n_items = responses_matrix.shape[1]
        discriminations = np.ones(n_items) * initial_a
        difficulties = np.zeros(n_items) + initial_b
        
        # Simple estimation: use item mean as difficulty proxy
        item_means = np.mean(responses_matrix, axis=0)
        difficulties = norm.ppf(np.clip(item_means, 0.01, 0.99))
        
        return discriminations, difficulties
    
    @staticmethod
    def update_skill_mastery(user, skill_tag, is_correct, challenge_difficulty=0.0, challenge_discrimination=1.0):
        """
        Update user's skill mastery after attempting a challenge
        
        Args:
            user: User instance
            skill_tag: Skill identifier (e.g., "git-clone")
            is_correct: Whether the attempt was correct
            challenge_difficulty: Difficulty parameter of the challenge
            challenge_discrimination: Discrimination parameter of the challenge
            
        Returns:
            Updated SkillMastery instance
        """
        mastery, created = SkillMastery.objects.get_or_create(
            user=user,
            skill_tag=skill_tag,
            defaults={'theta': 0.0, 'attempts': 0, 'correct_attempts': 0}
        )
        
        mastery.attempts += 1
        if is_correct:
            mastery.correct_attempts += 1
        
        # Get recent challenge attempts for this skill
        from courses.models import UserChallengeAttempt
        from courses.models import Challenge
        
        # Get challenges tagged with this skill
        challenges = Challenge.objects.filter(module__skill_tags__icontains=skill_tag)
        if challenges.exists():
            recent_attempts = UserChallengeAttempt.objects.filter(
                user=user,
                challenge__in=challenges
            ).order_by('-submitted_at')[:10]  # Last 10 attempts
            
            if recent_attempts.exists():
                responses = [1 if attempt.is_correct else 0 for attempt in recent_attempts]
                difficulties = [challenge_difficulty] * len(responses)  # Simplified
                discriminations = [challenge_discrimination] * len(responses)
                
                # Update theta using MLE
                mastery.theta = IRTEngine.estimate_ability(
                    responses,
                    difficulties,
                    discriminations,
                    initial_theta=mastery.theta
                )
        
        mastery.save()
        return mastery
    
    @staticmethod
    def recommend_next_challenge(user, available_challenges, skill_tag=None):
        """
        Recommend the best next challenge using IRT principles.
        Ideal challenge should have difficulty close to user's ability.
        
        Args:
            user: User instance
            available_challenges: QuerySet of available Challenge objects
            skill_tag: Optional skill tag to filter by
            
        Returns:
            Recommended Challenge instance or None
        """
        if not available_challenges.exists():
            return None
        
        # Get or estimate user's ability for the skill
        if skill_tag:
            try:
                mastery = SkillMastery.objects.get(user=user, skill_tag=skill_tag)
                user_theta = mastery.theta
            except SkillMastery.DoesNotExist:
                user_theta = 0.0  # Beginner
        else:
            # Average theta across all skills
            masteries = SkillMastery.objects.filter(user=user)
            if masteries.exists():
                user_theta = np.mean([m.theta for m in masteries])
            else:
                user_theta = 0.0
        
        best_challenge = None
        best_score = float('-inf')
        
        for challenge in available_challenges:
            # Map difficulty string to numeric value
            difficulty_map = {'easy': -1.0, 'medium': 0.0, 'hard': 1.0, 'expert': 2.0}
            challenge_difficulty = difficulty_map.get(challenge.difficulty.lower(), 0.0)
            
            # Information function: I(theta) = a^2 * P(theta) * Q(theta)
            # where P is probability of correct, Q = 1 - P
            # Maximize information at user's current theta
            a = 1.0  # Default discrimination
            p = IRTEngine.logistic_function(user_theta, a, challenge_difficulty)
            q = 1 - p
            information = (a ** 2) * p * q
            
            # Prefer challenges where difficulty is close to ability (not too easy/hard)
            # Also weight by information
            distance_from_ability = abs(challenge_difficulty - user_theta)
            score = information - (distance_from_ability * 0.5)  # Penalize far from ability
            
            if score > best_score:
                best_score = score
                best_challenge = challenge
        
        return best_challenge if best_challenge else available_challenges.first()

