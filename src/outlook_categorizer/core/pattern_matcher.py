"""
Unified pattern matching with multiple strategies and performance optimizations.
"""

import re
import logging
from typing import Optional
from .models import PatternType, Signal

logger = logging.getLogger(__name__)


class PatternMatcher:
    """Unified pattern matching with caching and multiple strategies."""
    
    def __init__(self):
        # Compiled regex cache for performance
        self._regex_cache: dict[str, re.Pattern] = {}
    
    def match(self, signal: Signal, text: str) -> bool:
        """
        Match signal pattern against text.
        
        Args:
            signal: Signal to match
            text: Text to search in
            
        Returns:
            True if pattern matches, False otherwise
        """
        if not signal.enabled:
            return False
        
        pattern = signal.pattern.lower()
        text_lower = text.lower()
        
        try:
            if signal.pattern_type == PatternType.REGEX:
                return self._match_regex(pattern, text_lower)
            elif signal.pattern_type == PatternType.WORD_BOUNDARY:
                return self._match_word_boundary(pattern, text_lower)
            elif signal.pattern_type == PatternType.DOLLAR_AMOUNT:
                return self._match_dollar_amount(text_lower)
            else:  # SUBSTRING (default)
                return pattern in text_lower
        except Exception as e:
            logger.warning(f"Error matching pattern '{pattern}': {e}")
            return False
    
    def _match_regex(self, pattern: str, text: str) -> bool:
        """Match using regex with caching."""
        if pattern not in self._regex_cache:
            try:
                self._regex_cache[pattern] = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                logger.error(f"Invalid regex pattern: {pattern} - {e}")
                raise ValueError(f"Invalid regex pattern: {pattern}") from e
        
        return bool(self._regex_cache[pattern].search(text))
    
    def _match_word_boundary(self, pattern: str, text: str) -> bool:
        """Match with word boundaries."""
        regex = r'\b' + re.escape(pattern) + r'\b'
        return bool(re.search(regex, text, re.IGNORECASE))
    
    def _match_dollar_amount(self, text: str) -> bool:
        """
        Match dollar amounts: $100, $1,000, $500.00, etc.
        Improved regex for various formats.
        """
        # Match: $ followed by digits, optional commas, optional decimal
        pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        return bool(re.search(pattern, text))
    
    def find_proximity(
        self, 
        pattern1: str, 
        pattern2: str, 
        text: str, 
        max_words: int = 10
    ) -> bool:
        """
        Check if two patterns appear within N words of each other.
        
        Args:
            pattern1: First pattern to find
            pattern2: Second pattern to find
            text: Text to search in
            max_words: Maximum words apart
            
        Returns:
            True if patterns are within max_words of each other
        """
        words = text.split()
        pattern1_lower = pattern1.lower()
        pattern2_lower = pattern2.lower()
        
        indices1 = [
            i for i, word in enumerate(words) 
            if pattern1_lower in word.lower()
        ]
        indices2 = [
            i for i, word in enumerate(words) 
            if pattern2_lower in word.lower()
        ]
        
        for i1 in indices1:
            for i2 in indices2:
                if abs(i1 - i2) <= max_words:
                    return True
        return False
    
    def clear_cache(self):
        """Clear the regex cache (useful for testing)."""
        self._regex_cache.clear()

