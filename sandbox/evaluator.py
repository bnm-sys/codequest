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
    def evaluate_challenge(user_output, challenge):
        """
        Evaluate user output against challenge expectations
        
        Args:
            user_output: Output from Docker container
            challenge: Challenge instance with expected_output
            
        Returns:
            Tuple of (is_correct: bool, feedback: str)
        """
        expected = challenge.expected_output.strip()
        
        # Try exact match first
        if OutputEvaluator.exact_match(user_output, expected):
            return True, "Perfect! Output matches exactly."
        
        # Try contains match for partial credit
        if OutputEvaluator.contains_match(user_output, expected):
            return True, "Good! Output contains the expected result."
        
        # Try similarity match (80% threshold)
        if OutputEvaluator.similarity_match(user_output, expected, threshold=0.8):
            return True, "Close! Output is very similar to expected."
        
        # Try regex if expected_output looks like a pattern
        if expected.startswith('^') and expected.endswith('$'):
            if OutputEvaluator.regex_match(user_output, expected):
                return True, "Matches the expected pattern."
        
        # No match found
        return False, f"Output doesn't match expected result. Expected: {expected[:100]}"

