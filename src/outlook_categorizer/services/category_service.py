"""
Category service - business logic for category management.
"""

import logging
from pathlib import Path
from typing import List, Optional

from ..core.models import CategoryRule
from .rule_manager import RuleManager

logger = logging.getLogger(__name__)


class CategoryService:
    """Service for managing categories."""
    
    def __init__(self, rule_manager: RuleManager):
        """
        Initialize category service.
        
        Args:
            rule_manager: RuleManager instance
        """
        self.rule_manager = rule_manager
    
    def get_all_categories(self) -> List[CategoryRule]:
        """Get all categories."""
        return self.rule_manager.load_all_rules()
    
    def get_category(self, category_name: str) -> Optional[CategoryRule]:
        """
        Get a specific category by name.
        
        Args:
            category_name: Name of category
            
        Returns:
            CategoryRule or None if not found
        """
        rules = self.rule_manager.load_all_rules()
        for rule in rules:
            if rule.category_name == category_name:
                return rule
        return None
    
    def create_category(self, rule: CategoryRule) -> Path:
        """
        Create a new category.
        
        Args:
            rule: CategoryRule to create
            
        Returns:
            Path to created rule file
        """
        return self.rule_manager.save_rule(rule)
    
    def update_category(self, rule: CategoryRule, rule_file: Optional[Path] = None) -> Path:
        """
        Update an existing category.
        
        Args:
            rule: Updated CategoryRule
            rule_file: Optional path to rule file
            
        Returns:
            Path to updated rule file
        """
        return self.rule_manager.save_rule(rule, rule_file)
    
    def delete_category(self, category_name: str) -> bool:
        """
        Delete a category.
        
        Args:
            category_name: Name of category to delete
            
        Returns:
            True if deleted, False otherwise
        """
        rule = self.get_category(category_name)
        if rule:
            # Find the file
            safe_name = category_name.lower().replace(' ', '_').replace('/', '_')
            rule_file = self.rule_manager.rules_dir / f"{safe_name}.yaml"
            return self.rule_manager.delete_rule(rule_file)
        return False
    
    def enable_category(self, category_name: str, enabled: bool = True) -> bool:
        """
        Enable or disable a category.
        
        Args:
            category_name: Name of category
            enabled: True to enable, False to disable
            
        Returns:
            True if updated, False if category not found
        """
        rule = self.get_category(category_name)
        if rule:
            rule.enabled = enabled
            self.update_category(rule)
            return True
        return False

