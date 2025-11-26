"""
Core data models using Pydantic for validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict, PrivateAttr
from typing import Optional, Literal
from enum import Enum
from datetime import datetime


class PatternType(str, Enum):
    """Pattern matching types."""
    SUBSTRING = "substring"
    REGEX = "regex"
    WORD_BOUNDARY = "word_boundary"
    DOLLAR_AMOUNT = "dollar_amount"


class SignalLocation(str, Enum):
    """Where to search for signals."""
    SUBJECT = "subject_contains"
    BODY = "body_contains"
    ANYWHERE = "anywhere"
    SENDER = "sender_contains"
    ATTACHMENT = "attachment_name"


class SignalTier(str, Enum):
    """Signal strength tiers."""
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"
    NEGATIVE = "negative"
    ATTACHMENT = "attachment"


class ScoringMethod(str, Enum):
    """Scoring calculation methods."""
    ADDITIVE = "additive"      # Current: sum all weights
    TIERED = "tiered"          # Recommended: max(strong) + weighted(medium/weak)
    HYBRID = "hybrid"          # Combination approach


class Signal(BaseModel):
    """A single scoring signal."""
    model_config = ConfigDict(
        frozen=False,  # Allow updates for UI editing
        str_strip_whitespace=True,
        validate_assignment=True,
    )
    
    pattern: str = Field(..., min_length=1, max_length=500, description="Pattern to match")
    weight: int = Field(..., ge=-100, le=100, description="Signal weight")
    location: SignalLocation = Field(default=SignalLocation.ANYWHERE)
    pattern_type: PatternType = Field(default=PatternType.SUBSTRING)
    tier: SignalTier = Field(default=SignalTier.MEDIUM)
    description: str = Field(default="", max_length=500)
    enabled: bool = Field(default=True)
    max_contribution: Optional[int] = Field(default=None, ge=0, le=100)
    
    @field_validator('pattern')
    @classmethod
    def validate_pattern(cls, v: str) -> str:
        """Validate pattern is not empty."""
        if not v.strip():
            raise ValueError("Pattern cannot be empty")
        return v.strip()
    
    @field_validator('pattern_type', mode='before')
    @classmethod
    def auto_detect_pattern_type(cls, v, info) -> PatternType:
        """Auto-detect pattern type for special cases."""
        if isinstance(v, PatternType):
            return v
        if isinstance(v, str) and v == "$":
            return PatternType.DOLLAR_AMOUNT
        if isinstance(v, str):
            try:
                return PatternType(v)
            except ValueError:
                return PatternType.SUBSTRING
        return PatternType.SUBSTRING


class CoOccurrenceBonus(BaseModel):
    """Bonus for signal co-occurrence."""
    model_config = ConfigDict(
        frozen=False,
        str_strip_whitespace=True,
    )
    
    signal_pair: tuple[str, str] = Field(..., description="Two signal patterns that trigger bonus")
    bonus_weight: int = Field(..., ge=0, le=50, description="Bonus weight to add")
    proximity_words: int = Field(default=10, ge=1, le=100, description="Maximum words apart")
    description: str = Field(default="", max_length=500)
    
    @field_validator('signal_pair')
    @classmethod
    def validate_signal_pair(cls, v) -> tuple[str, str]:
        """Ensure signal pair has exactly 2 elements."""
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return tuple(str(s).strip() for s in v)
        raise ValueError("signal_pair must contain exactly 2 signal patterns")


class CategoryRule(BaseModel):
    """Complete rule set for a category."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
    
    category_name: str = Field(..., min_length=1, max_length=100)
    outlook_category: str = Field(..., min_length=1, max_length=100)
    threshold: int = Field(default=40, ge=0, le=200)
    
    # Scoring configuration
    scoring_method: ScoringMethod = Field(default=ScoringMethod.TIERED)
    weak_signal_cap: int = Field(default=15, ge=0, le=50)
    medium_signal_multiplier: float = Field(default=0.9, ge=0.0, le=1.0)
    
    # Signals
    strong_signals: list[Signal] = Field(default_factory=list)
    medium_signals: list[Signal] = Field(default_factory=list)
    weak_signals: list[Signal] = Field(default_factory=list)
    negative_signals: list[Signal] = Field(default_factory=list)
    attachment_signals: list[Signal] = Field(default_factory=list)
    
    # Advanced features
    co_occurrence_bonuses: list[CoOccurrenceBonus] = Field(default_factory=list)
    enabled: bool = Field(default=True)
    
    @field_validator('outlook_category')
    @classmethod
    def validate_outlook_category(cls, v: str) -> str:
        """Validate Outlook category name doesn't contain invalid characters."""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        found = [char for char in invalid_chars if char in v]
        if found:
            raise ValueError(f"Outlook category contains invalid characters: {found}")
        return v
    
    @field_validator('category_name', 'outlook_category')
    @classmethod
    def validate_category_names(cls, v: str) -> str:
        """Ensure category names are not empty after stripping."""
        if not v.strip():
            raise ValueError("Category name cannot be empty")
        return v.strip()


class EmailMessage(BaseModel):
    """Represents an email message with extracted content."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,  # Allow outlook_item
    )
    
    entry_id: str
    subject: str
    body: str
    sender_email: str
    sender_name: str
    received_time: datetime
    attachment_names: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    conversation_id: str = ""
    
    # Reference to original Outlook item (for applying categories)
    # Using PrivateAttr for internal use only (not serialized)
    _outlook_item: Optional[object] = PrivateAttr(default=None)


class SignalMatch(BaseModel):
    """A signal that matched in an email."""
    pattern: str
    weight: int
    location: str
    found_in: str  # Where it was actually found (subject/body/sender/attachment)
    tier: SignalTier = Field(default=SignalTier.MEDIUM)


class ScoringResult(BaseModel):
    """Result of scoring an email against a category rule."""
    category_name: str
    outlook_category: str
    score: int
    threshold: int
    matches: list[SignalMatch] = Field(default_factory=list)
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

