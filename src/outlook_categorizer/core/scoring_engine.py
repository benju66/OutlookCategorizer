"""
Scoring engine for email categorization with tiered scoring support.
"""

import logging
from typing import List, Optional
from .models import CategoryRule, ScoringResult, EmailMessage, SignalMatch, ScoringMethod
from .pattern_matcher import PatternMatcher

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Scores emails against category rules using tiered scoring."""
    
    def __init__(self, rules: List[CategoryRule], matcher: PatternMatcher = None):
        """
        Initialize scoring engine.
        
        Args:
            rules: List of category rules to score against
            matcher: Pattern matcher instance (creates new if None)
        """
        self.rules = rules
        self.matcher = matcher or PatternMatcher()
    
    def score_email(self, email: EmailMessage) -> List[ScoringResult]:
        """
        Score an email against all category rules.
        
        Args:
            email: Email to score
            
        Returns:
            List of ScoringResults (one per category)
        """
        results = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            result = self._score_against_rule(email, rule)
            results.append(result)
        
        return results
    
    def _score_against_rule(self, email: EmailMessage, rule: CategoryRule) -> ScoringResult:
        """Score an email against a single category rule."""
        if rule.scoring_method == ScoringMethod.TIERED:
            return self._score_tiered(email, rule)
        elif rule.scoring_method == ScoringMethod.ADDITIVE:
            return self._score_additive(email, rule)
        else:  # HYBRID
            return self._score_hybrid(email, rule)
    
    def _score_tiered(self, email: EmailMessage, rule: CategoryRule) -> ScoringResult:
        """
        Tiered scoring: max(strong) + weighted(medium) + capped(weak) + negative.
        This prevents weak signal accumulation issues.
        """
        # Prepare searchable text (lowercase for case-insensitive matching)
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()
        combined_lower = f"{subject_lower} {body_lower}"
        attachments_lower = " ".join(email.attachment_names).lower()
        sender_lower = f"{email.sender_email} {email.sender_name}".lower()
        
        # Score each tier
        strong_scores, strong_matches = self._score_signals(
            email, rule.strong_signals, 
            subject_lower, body_lower, combined_lower, sender_lower
        )
        medium_scores, medium_matches = self._score_signals(
            email, rule.medium_signals,
            subject_lower, body_lower, combined_lower, sender_lower
        )
        weak_scores, weak_matches = self._score_signals(
            email, rule.weak_signals,
            subject_lower, body_lower, combined_lower, sender_lower
        )
        negative_scores, negative_matches = self._score_signals(
            email, rule.negative_signals,
            subject_lower, body_lower, combined_lower, sender_lower
        )
        
        # Score attachment signals separately
        attachment_scores, attachment_matches = self._score_attachment_signals(
            email, rule.attachment_signals, attachments_lower
        )
        
        # Calculate tiered totals
        # Strong: take maximum (or sum if multiple - could be configurable)
        strong_total = max(strong_scores) if strong_scores else 0
        
        # Medium: weighted sum
        medium_total = sum(medium_scores) * rule.medium_signal_multiplier
        
        # Weak: capped sum
        weak_total = min(sum(weak_scores), rule.weak_signal_cap)
        
        # Negative: subtract
        negative_total = sum(negative_scores)
        
        # Attachment: add to strong (or could be separate tier)
        attachment_total = sum(attachment_scores)
        
        # Base score
        base_score = strong_total + medium_total + weak_total + negative_total + attachment_total
        
        # Co-occurrence bonuses
        bonus = self._calculate_co_occurrence_bonuses(email, rule, combined_lower)
        
        total_score = base_score + bonus
        
        # Collect all matches
        all_matches = strong_matches + medium_matches + weak_matches + negative_matches + attachment_matches
        
        return ScoringResult(
            category_name=rule.category_name,
            outlook_category=rule.outlook_category,
            score=int(total_score),
            threshold=rule.threshold,
            matches=all_matches,
            should_apply=total_score >= rule.threshold
        )
    
    def _score_additive(self, email: EmailMessage, rule: CategoryRule) -> ScoringResult:
        """Additive scoring: simple sum of all signal weights (legacy method)."""
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()
        combined_lower = f"{subject_lower} {body_lower}"
        attachments_lower = " ".join(email.attachment_names).lower()
        sender_lower = f"{email.sender_email} {email.sender_name}".lower()
        
        all_signals = (
            rule.strong_signals +
            rule.medium_signals +
            rule.weak_signals +
            rule.negative_signals
        )
        
        total_score = 0
        matches = []
        
        for signal in all_signals:
            match = self._check_signal(
                signal,
                subject_lower, body_lower, combined_lower, sender_lower
            )
            if match:
                total_score += signal.weight
                matches.append(match)
        
        # Attachment signals
        for signal in rule.attachment_signals:
            if self.matcher.match(signal, attachments_lower):
                total_score += signal.weight
                matches.append(SignalMatch(
                    pattern=signal.pattern,
                    weight=signal.weight,
                    location="attachment_name",
                    found_in="attachment",
                    tier=signal.tier
                ))
        
        return ScoringResult(
            category_name=rule.category_name,
            outlook_category=rule.outlook_category,
            score=total_score,
            threshold=rule.threshold,
            matches=matches,
            should_apply=total_score >= rule.threshold
        )
    
    def _score_hybrid(self, email: EmailMessage, rule: CategoryRule) -> ScoringResult:
        """Hybrid scoring: combination of tiered and additive."""
        # Use tiered for strong/medium/weak, additive for everything else
        tiered_result = self._score_tiered(email, rule)
        # Could add additional logic here if needed
        return tiered_result
    
    def _score_signals(
        self,
        email: EmailMessage,
        signals: List,
        subject: str,
        body: str,
        combined: str,
        sender: str
    ) -> tuple[List[int], List[SignalMatch]]:
        """Score a list of signals and return scores and matches."""
        scores = []
        matches = []
        
        for signal in signals:
            match = self._check_signal(signal, subject, body, combined, sender)
            if match:
                weight = signal.weight
                # Apply max_contribution cap if set
                if signal.max_contribution is not None:
                    weight = min(weight, signal.max_contribution)
                scores.append(weight)
                matches.append(match)
        
        return scores, matches
    
    def _score_attachment_signals(
        self,
        email: EmailMessage,
        signals: List,
        attachments_lower: str
    ) -> tuple[List[int], List[SignalMatch]]:
        """Score attachment signals."""
        scores = []
        matches = []
        
        for signal in signals:
            if self.matcher.match(signal, attachments_lower):
                weight = signal.weight
                if signal.max_contribution is not None:
                    weight = min(weight, signal.max_contribution)
                scores.append(weight)
                matches.append(SignalMatch(
                    pattern=signal.pattern,
                    weight=weight,
                    location="attachment_name",
                    found_in="attachment",
                    tier=signal.tier
                ))
        
        return scores, matches
    
    def _check_signal(
        self,
        signal,
        subject: str,
        body: str,
        combined: str,
        sender: str
    ) -> Optional[SignalMatch]:
        """Check if a signal matches and return match details."""
        found_in = None
        text_to_search = None
        
        if signal.location.value == "subject_contains":
            text_to_search = subject
            if self.matcher.match(signal, subject):
                found_in = "subject"
        elif signal.location.value == "body_contains":
            text_to_search = body
            if self.matcher.match(signal, body):
                found_in = "body"
        elif signal.location.value == "anywhere":
            text_to_search = combined
            if self.matcher.match(signal, combined):
                found_in = "subject" if self.matcher.match(signal, subject) else "body"
        elif signal.location.value == "sender_contains":
            text_to_search = sender
            if self.matcher.match(signal, sender):
                found_in = "sender"
        
        if found_in:
            return SignalMatch(
                pattern=signal.pattern,
                weight=signal.weight,
                location=signal.location.value,
                found_in=found_in,
                tier=signal.tier
            )
        
        return None
    
    def _calculate_co_occurrence_bonuses(
        self,
        email: EmailMessage,
        rule: CategoryRule,
        combined_text: str
    ) -> int:
        """Calculate co-occurrence bonuses."""
        bonus_total = 0
        
        for co_bonus in rule.co_occurrence_bonuses:
            pattern1, pattern2 = co_bonus.signal_pair
            
            if self.matcher.find_proximity(
                pattern1,
                pattern2,
                combined_text,
                co_bonus.proximity_words
            ):
                bonus_total += co_bonus.bonus_weight
                logger.debug(
                    f"Co-occurrence bonus: {pattern1} + {pattern2} = +{co_bonus.bonus_weight}"
                )
        
        return bonus_total

