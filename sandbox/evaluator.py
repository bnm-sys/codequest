# sandbox/evaluator.py
"""
Evaluation processor for analyzing Docker sandbox output and determining correctness
"""
import re
import difflib
from typing import Dict, Tuple


class OutputEvaluator:
    """Evaluates user command output against expected results"""
    
    @staticmethod
    def normalize_output(text):
        """Normalize output for comparison (lowercase, strip whitespace, remove colors)"""
        if not text:
            return ""
        # Remove ANSI color codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.strip().lower()
    
    @staticmethod
    def exact_match(user_output, expected_output):
        """Check if outputs match exactly (after normalization)"""
        user_norm = OutputEvaluator.normalize_output(user_output)
        expected_norm = OutputEvaluator.normalize_output(expected_output)
        return user_norm == expected_norm
    
    @staticmethod
    def contains_match(user_output, expected_output):
        """Check if user output contains expected output"""
        user_norm = OutputEvaluator.normalize_output(user_output)
        expected_norm = OutputEvaluator.normalize_output(expected_output)
        return expected_norm in user_norm
    
    @staticmethod
    def regex_match(user_output, pattern):
        """Check if user output matches a regex pattern"""
        user_norm = OutputEvaluator.normalize_output(user_output)
        return bool(re.search(pattern, user_norm, re.IGNORECASE))
    
    @staticmethod
    def similarity_match(user_output, expected_output, threshold=0.8):
        """Check if outputs are similar using sequence matching"""
        user_norm = OutputEvaluator.normalize_output(user_output)
        expected_norm = OutputEvaluator.normalize_output(expected_output)
        similarity = difflib.SequenceMatcher(None, user_norm, expected_norm).ratio()
        return similarity >= threshold
    
    @staticmethod
    def evaluate_challenge(user_output, challenge, command_executed=None):
        """
        Evaluate user output against challenge expectations
        
        Args:
            user_output: Output from Docker container
            challenge: Challenge instance with expected_output
            command_executed: The command that was executed (optional)
            
        Returns:
            Tuple of (is_correct: bool, feedback: str)
        """
        eval_type = getattr(challenge, 'evaluation_type', 'contains')
        expected = challenge.expected_output.strip()
        
        # Command-based evaluation
        if eval_type == 'command':
            if command_executed and challenge.command_to_practice:
                # Check if the correct command was executed
                user_cmd = command_executed.strip().lower()
                expected_cmd = challenge.command_to_practice.strip().lower()
                if expected_cmd in user_cmd or user_cmd.startswith(expected_cmd.split()[0]):
                    return True, f"Perfect! You executed the correct command: {challenge.command_to_practice}"
                else:
                    return False, f"Try using: {challenge.command_to_practice}"
        
        # File/directory exists evaluation
        if eval_type == 'file_exists':
            # Check if expected file/directory appears in output
            expected_items = [item.strip() for item in expected.split() if item.strip()]
            found_items = []
            for item in expected_items:
                if item.lower() in user_output.lower():
                    found_items.append(item)
            if found_items:
                return True, f"Great! Found: {', '.join(found_items)}"
            else:
                return False, f"Look for: {expected}"
        
        # Exact match
        if eval_type == 'exact':
            if OutputEvaluator.exact_match(user_output, expected):
                return True, "Perfect! Output matches exactly."
            return False, f"Expected exact output: {expected[:100]}"
        
        # Contains match (default)
        if eval_type == 'contains' or not eval_type:
            if OutputEvaluator.contains_match(user_output, expected):
                return True, "Excellent! You found the expected result."
            
            # Try similarity match for partial credit
            if OutputEvaluator.similarity_match(user_output, expected, threshold=0.7):
                return True, "Close! You're on the right track."
        
        # No match found
        return False, f"Keep trying! Look for: {expected[:80]}"

