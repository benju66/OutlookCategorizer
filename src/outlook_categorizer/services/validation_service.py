"""
Validation service for configuration and rules.
"""

import logging
from typing import List, Tuple, Optional
from pydantic import ValidationError

from ..core.models import CategoryRule, Signal
from ..adapters.outlook_client import OutlookClient

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating configuration and rules."""
    
    def __init__(self, outlook_client: Optional[OutlookClient] = None):
        """
        Initialize validation service.
        
        Args:
            outlook_client: Optional OutlookClient for category validation
        """
        self.outlook_client = outlook_client
    
    def validate_rule(self, rule: CategoryRule) -> Tuple[bool, List[str]]:
        """
        Validate a category rule.
        
        Args:
            rule: CategoryRule to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Pydantic validation
            rule.model_validate(rule.model_dump())
        except ValidationError as e:
            errors.extend([f"Validation error: {err['msg']}" for err in e.errors()])
            return False, errors
        
        # Custom business logic validation
        if not rule.strong_signals and not rule.medium_signals and not rule.weak_signals:
            errors.append("Rule must have at least one signal")
        
        # Check Outlook category exists
        if self.outlook_client:
            available = self.outlook_client.get_available_categories()
            if rule.outlook_category not in available:
                errors.append(
                    f"Outlook category '{rule.outlook_category}' not found. "
                    f"Available categories: {', '.join(available[:5])}..."
                )
        
        # Check threshold is reasonable
        if rule.threshold < 0 or rule.threshold > 200:
            errors.append("Threshold should be between 0 and 200")
        
        # Check signal weights are reasonable
        for signal in (
            rule.strong_signals + rule.medium_signals + 
            rule.weak_signals + rule.negative_signals + rule.attachment_signals
        ):
            if abs(signal.weight) > 100:
                errors.append(f"Signal weight {signal.weight} is too high (max ±100)")
        
        return len(errors) == 0, errors
    
    def validate_signal(self, signal: Signal) -> Tuple[bool, List[str]]:
        """
        Validate a signal.
        
        Args:
            signal: Signal to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            signal.model_validate(signal.model_dump())
        except ValidationError as e:
            errors.extend([f"Validation error: {err['msg']}" for err in e.errors()])
            return False, errors
        
        # Check pattern is not empty
        if not signal.pattern.strip():
            errors.append("Pattern cannot be empty")
        
        # Check regex pattern is valid if pattern_type is regex
        if signal.pattern_type.value == "regex":
            import re
            try:
                re.compile(signal.pattern)
            except re.error as e:
                errors.append(f"Invalid regex pattern: {e}")
        
        return len(errors) == 0, errors

