"""Core business logic modules."""

from .models import (
    Signal,
    CategoryRule,
    EmailMessage,
    ScoringResult,
    SignalMatch,
    PatternType,
    SignalLocation,
    SignalTier,
    ScoringMethod,
    CoOccurrenceBonus,
)
from .scoring_engine import ScoringEngine
from .pattern_matcher import PatternMatcher

__all__ = [
    "Signal",
    "CategoryRule",
    "EmailMessage",
    "ScoringResult",
    "SignalMatch",
    "PatternType",
    "SignalLocation",
    "SignalTier",
    "ScoringMethod",
    "CoOccurrenceBonus",
    "ScoringEngine",
    "PatternMatcher",
]

