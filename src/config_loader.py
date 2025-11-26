"""
Configuration and rules loading utilities.
"""

import yaml
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


def load_settings(settings_path: Path) -> dict:
    """Load main settings from YAML file."""
    if not settings_path.exists():
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    
    with open(settings_path, 'r') as f:
        return yaml.safe_load(f)


@dataclass
class Signal:
    """A single scoring signal."""
    pattern: str
    weight: int
    location: str = "anywhere"
    description: str = ""


@dataclass 
class CategoryRule:
    """Complete rule set for a category."""
    category_name: str
    outlook_category: str
    threshold: int
    strong_signals: list[Signal] = field(default_factory=list)
    medium_signals: list[Signal] = field(default_factory=list)
    weak_signals: list[Signal] = field(default_factory=list)
    attachment_signals: list[Signal] = field(default_factory=list)
    negative_signals: list[Signal] = field(default_factory=list)


def load_category_rules(rules_dir: Path) -> list[CategoryRule]:
    """Load all category rules from YAML files in rules directory."""
    rules = []
    
    if not rules_dir.exists():
        raise FileNotFoundError(f"Rules directory not found: {rules_dir}")
    
    for rule_file in rules_dir.glob("*.yaml"):
        with open(rule_file, 'r') as f:
            data = yaml.safe_load(f)
        
        rule = CategoryRule(
            category_name=data.get("category_name", rule_file.stem),
            outlook_category=data.get("outlook_category", data.get("category_name", rule_file.stem)),
            threshold=data.get("threshold", 40),
            strong_signals=_parse_signals(data.get("strong_signals", [])),
            medium_signals=_parse_signals(data.get("medium_signals", [])),
            weak_signals=_parse_signals(data.get("weak_signals", [])),
            attachment_signals=_parse_signals(data.get("attachment_signals", []), default_location="attachment_name"),
            negative_signals=_parse_signals(data.get("negative_signals", []), default_location="anywhere"),
        )
        rules.append(rule)
    
    return rules


def _parse_signals(signal_list: list[dict], default_location: str = "anywhere") -> list[Signal]:
    """Parse signal dictionaries into Signal objects."""
    signals = []
    for s in signal_list:
        signals.append(Signal(
            pattern=s.get("pattern", ""),
            weight=s.get("weight", 0),
            location=s.get("location", default_location),
            description=s.get("description", "")
        ))
    return signals
