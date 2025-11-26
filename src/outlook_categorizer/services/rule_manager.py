"""
Rule manager service - handles CRUD operations for category rules.
"""

import logging
from pathlib import Path
from typing import List, Optional
from pydantic import ValidationError

from ..core.models import CategoryRule
from ..adapters.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class RuleManager:
    """Manages category rules with validation and persistence."""
    
    def __init__(self, rules_dir: Path):
        """
        Initialize rule manager.
        
        Args:
            rules_dir: Directory containing rule YAML files
        """
        self.rules_dir = Path(rules_dir)
        self.rules_dir.mkdir(parents=True, exist_ok=True)
        self._loader = ConfigLoader()
    
    def load_all_rules(self) -> List[CategoryRule]:
        """
        Load all category rules from directory.
        
        Returns:
            List of CategoryRule objects (only enabled rules)
        """
        rules = []
        seen_names = set()
        
        for rule_file in self.rules_dir.glob("*.yaml"):
            try:
                rule = self.load_rule(rule_file)
                if rule.enabled:
                    # Check for duplicate category names
                    if rule.category_name in seen_names:
                        logger.warning(
                            f"Duplicate category name '{rule.category_name}' "
                            f"found in {rule_file.name}. Skipping duplicate."
                        )
                        continue
                    seen_names.add(rule.category_name)
                    rules.append(rule)
            except Exception as e:
                logger.error(f"Failed to load rule from {rule_file}: {e}")
        return rules
    
    def load_rule(self, rule_file: Path) -> CategoryRule:
        """
        Load a single rule with validation.
        
        Args:
            rule_file: Path to rule YAML file
            
        Returns:
            CategoryRule object
            
        Raises:
            ValidationError: If rule is invalid
            FileNotFoundError: If file doesn't exist
        """
        data = self._loader.load_yaml(rule_file)
        
        # Handle version migration if needed
        version = data.get("version", "1.0")
        if version == "1.0":
            data = self._migrate_v1_to_v2(data)
            # After migration, convert nested to flat
            data = self._convert_v2_to_flat(data)
        elif version == "2.0":
            # New format - convert nested structure to flat
            data = self._convert_v2_to_flat(data)
        
        return CategoryRule.model_validate(data)
    
    def _convert_v2_to_flat(self, data: dict) -> dict:
        """Convert v2.0 nested format to flat format for Pydantic."""
        category = data.get("category", {})
        scoring = data.get("scoring", {})
        signals = data.get("signals", {})
        co_bonuses = data.get("co_occurrence_bonuses", [])
        
        return {
            "category_name": category.get("name", ""),
            "outlook_category": category.get("outlook_category", category.get("name", "")),
            "threshold": category.get("threshold", 40),
            "enabled": category.get("enabled", True),
            "scoring_method": scoring.get("method", "tiered"),
            "weak_signal_cap": scoring.get("weak_signal_cap", 15),
            "medium_signal_multiplier": scoring.get("medium_signal_multiplier", 0.9),
            "strong_signals": signals.get("strong", []),
            "medium_signals": signals.get("medium", []),
            "weak_signals": signals.get("weak", []),
            "negative_signals": signals.get("negative", []),
            "attachment_signals": signals.get("attachment", []),
            "co_occurrence_bonuses": co_bonuses,
        }
    
    def save_rule(self, rule: CategoryRule, rule_file: Optional[Path] = None) -> Path:
        """
        Save rule with validation.
        
        Args:
            rule: CategoryRule to save
            rule_file: Optional path (auto-generated if None)
            
        Returns:
            Path to saved file
            
        Raises:
            ValueError: If rule is invalid
        """
        # Validate before saving
        self.validate_rule(rule)
        
        if rule_file is None:
            # Generate filename from category name
            safe_name = rule.category_name.lower().replace(' ', '_').replace('/', '_')
            rule_file = self.rules_dir / f"{safe_name}.yaml"
        
        # Convert to v2.0 nested format for better readability
        data = {
            "version": "2.0",
            "category": {
                "name": rule.category_name,
                "outlook_category": rule.outlook_category,
                "threshold": rule.threshold,
                "enabled": rule.enabled,
            },
            "scoring": {
                "method": rule.scoring_method.value,
                "weak_signal_cap": rule.weak_signal_cap,
                "medium_signal_multiplier": rule.medium_signal_multiplier,
            },
            "signals": {
                "strong": [s.model_dump(exclude_none=True) for s in rule.strong_signals],
                "medium": [s.model_dump(exclude_none=True) for s in rule.medium_signals],
                "weak": [s.model_dump(exclude_none=True) for s in rule.weak_signals],
                "negative": [s.model_dump(exclude_none=True) for s in rule.negative_signals],
                "attachment": [s.model_dump(exclude_none=True) for s in rule.attachment_signals],
            },
            "co_occurrence_bonuses": [
                b.model_dump(exclude_none=True) for b in rule.co_occurrence_bonuses
            ],
        }
        
        self._loader.save_yaml(rule_file, data)
        logger.info(f"Saved rule to {rule_file}")
        return rule_file
    
    def delete_rule(self, rule_file: Path) -> bool:
        """
        Delete a rule file.
        
        Args:
            rule_file: Path to rule file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if rule_file.exists():
                rule_file.unlink()
                logger.info(f"Deleted rule file: {rule_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete rule file {rule_file}: {e}")
            return False
    
    def validate_rule(self, rule: CategoryRule) -> None:
        """
        Validate rule and raise if invalid.
        
        Args:
            rule: CategoryRule to validate
            
        Raises:
            ValueError: If rule is invalid
        """
        # Pydantic validation happens automatically
        # Add custom business logic validation here
        
        if not rule.strong_signals and not rule.medium_signals and not rule.weak_signals:
            raise ValueError("Rule must have at least one signal")
        
        # Check for duplicate patterns in same tier
        all_patterns = {}
        for tier_name, signals in [
            ("strong", rule.strong_signals),
            ("medium", rule.medium_signals),
            ("weak", rule.weak_signals),
            ("negative", rule.negative_signals),
            ("attachment", rule.attachment_signals),
        ]:
            for signal in signals:
                key = (signal.pattern.lower(), signal.location.value)
                if key in all_patterns:
                    raise ValueError(
                        f"Duplicate pattern '{signal.pattern}' with location '{signal.location.value}' "
                        f"found in {all_patterns[key]} and {tier_name} signals"
                    )
                all_patterns[key] = tier_name
    
    def _migrate_v1_to_v2(self, data: dict) -> dict:
        """
        Migrate v1.0 YAML format to v2.0 format.
        
        Args:
            data: Old format data
            
        Returns:
            New format data
        """
        # Old format has signals at top level
        # New format has them nested under 'signals'
        
        migrated = {
            "version": "2.0",
            "category": {
                "name": data.get("category_name", ""),
                "outlook_category": data.get("outlook_category", data.get("category_name", "")),
                "threshold": data.get("threshold", 40),
                "enabled": True,
            },
            "scoring": {
                "method": "tiered",
                "weak_signal_cap": 15,
                "medium_signal_multiplier": 0.9,
            },
            "signals": {
                "strong": self._migrate_signals(data.get("strong_signals", [])),
                "medium": self._migrate_signals(data.get("medium_signals", [])),
                "weak": self._migrate_signals(data.get("weak_signals", [])),
                "negative": self._migrate_signals(data.get("negative_signals", [])),
                "attachment": self._migrate_signals(data.get("attachment_signals", [])),
            },
        }
        
        return migrated
    
    def _migrate_signals(self, signals: list) -> list:
        """Migrate signal list to new format."""
        migrated = []
        for sig in signals:
            migrated_sig = {
                "pattern": sig.get("pattern", ""),
                "weight": sig.get("weight", 0),
                "location": sig.get("location", "anywhere"),
                "pattern_type": "substring",  # Default
                "tier": sig.get("tier", "medium"),  # Default tier
                "description": sig.get("description", ""),
                "enabled": True,
            }
            # Auto-detect pattern type
            if migrated_sig["pattern"] == "$":
                migrated_sig["pattern_type"] = "dollar_amount"
            elif len(migrated_sig["pattern"]) <= 3:
                migrated_sig["pattern_type"] = "word_boundary"
            
            migrated.append(migrated_sig)
        return migrated

