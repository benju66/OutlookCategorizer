"""
Scoring engine for email categorization.
Evaluates emails against rules and produces scores.
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional

from config_loader import CategoryRule, Signal
from outlook_client import EmailMessage

logger = logging.getLogger(__name__)


@dataclass
class SignalMatch:
    """A signal that matched in an email."""
    pattern: str
    weight: int
    location: str
    found_in: str  # Where it was actually found
    

@dataclass
class ScoringResult:
    """Result of scoring an email against a category rule."""
    category_name: str
    outlook_category: str
    score: int
    threshold: int
    matches: list[SignalMatch]
    should_apply: bool
    
    def explanation(self) -> str:
        """Human-readable explanation of the scoring decision."""
        lines = [
            f"Category: {self.category_name}",
            f"Score: {self.score} (threshold: {self.threshold})",
            f"Decision: {'APPLY' if self.should_apply else 'SKIP'}",
        ]
        
        if self.matches:
            lines.append("Matching signals:")
            for m in self.matches:
                sign = "+" if m.weight > 0 else ""
                lines.append(f"  {sign}{m.weight}: '{m.pattern}' in {m.found_in}")
        else:
            lines.append("No signals matched")
            
        return "\n".join(lines)


class ScoringEngine:
    """Scores emails against category rules."""
    
    def __init__(self, rules: list[CategoryRule]):
        self.rules = rules
    
    def score_email(self, email: EmailMessage) -> list[ScoringResult]:
        """
        Score an email against all category rules.
        Returns list of ScoringResults (one per category).
        """
        results = []
        
        for rule in self.rules:
            result = self._score_against_rule(email, rule)
            results.append(result)
        
        return results
    
    def _score_against_rule(self, email: EmailMessage, rule: CategoryRule) -> ScoringResult:
        """Score an email against a single category rule."""
        total_score = 0
        matches = []
        
        # Prepare searchable text (lowercase for case-insensitive matching)
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()
        combined_lower = f"{subject_lower} {body_lower}"
        attachments_lower = " ".join(email.attachment_names).lower()
        sender_lower = f"{email.sender_email} {email.sender_name}".lower()
        
        # Process all signal types
        all_signals = (
            rule.strong_signals +
            rule.medium_signals +
            rule.weak_signals +
            rule.negative_signals
        )
        
        for signal in all_signals:
            match = self._check_signal(
                signal, 
                subject_lower, 
                body_lower, 
                combined_lower,
                sender_lower
            )
            if match:
                total_score += signal.weight
                matches.append(match)
        
        # Process attachment signals separately
        for signal in rule.attachment_signals:
            if self._pattern_in_text(signal.pattern.lower(), attachments_lower):
                total_score += signal.weight
                matches.append(SignalMatch(
                    pattern=signal.pattern,
                    weight=signal.weight,
                    location="attachment_name",
                    found_in="attachment"
                ))
        
        return ScoringResult(
            category_name=rule.category_name,
            outlook_category=rule.outlook_category,
            score=total_score,
            threshold=rule.threshold,
            matches=matches,
            should_apply=total_score >= rule.threshold
        )
    
    def _check_signal(
        self, 
        signal: Signal,
        subject: str,
        body: str,
        combined: str,
        sender: str
    ) -> Optional[SignalMatch]:
        """Check if a signal matches and return match details."""
        
        pattern = signal.pattern.lower()
        found_in = None
        
        if signal.location == "subject_contains":
            if self._pattern_in_text(pattern, subject):
                found_in = "subject"
                
        elif signal.location == "body_contains":
            if self._pattern_in_text(pattern, body):
                found_in = "body"
                
        elif signal.location == "anywhere":
            if self._pattern_in_text(pattern, combined):
                found_in = "subject" if self._pattern_in_text(pattern, subject) else "body"
                
        elif signal.location == "sender_contains":
            if self._pattern_in_text(pattern, sender):
                found_in = "sender"
        
        if found_in:
            return SignalMatch(
                pattern=signal.pattern,
                weight=signal.weight,
                location=signal.location,
                found_in=found_in
            )
        
        return None
    
    def _pattern_in_text(self, pattern: str, text: str) -> bool:
        """
        Check if pattern exists in text.
        Uses word boundary matching for short patterns to avoid false positives.
        Special handling for "$" to match dollar amounts.
        """
        # Special case: "$" should match dollar amounts (e.g., "$1925", "$1,000", "$500.00")
        if pattern == "$":
            # Match $ followed by at least one digit (handles formats like $100, $1,000, $500.00)
            return bool(re.search(r'\$\d', text))
        
        if len(pattern) <= 3:
            # For short patterns like "PCO", use word boundaries
            # to avoid matching "COSTCO" when looking for "CO"
            regex = r'\b' + re.escape(pattern) + r'\b'
            return bool(re.search(regex, text, re.IGNORECASE))
        else:
            # For longer patterns, simple substring match is fine
            return pattern in text
