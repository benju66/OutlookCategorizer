"""
Presenter for category management - handles business logic for categories.
"""

import logging
from typing import Optional, List
from pathlib import Path

from ...core.models import CategoryRule
from ...services.category_service import CategoryService
from .base_presenter import BasePresenter

logger = logging.getLogger(__name__)


class CategoryPresenter(BasePresenter):
    """Presenter for category management."""
    
    def __init__(self, category_service: CategoryService):
        """
        Initialize category presenter.
        
        Args:
            category_service: CategoryService instance for data access
        """
        super().__init__()
        self.category_service = category_service
        self.current_rule: Optional[CategoryRule] = None
        self.has_unsaved_changes = False
    
    def initialize(self):
        """Initialize presenter - called after view is set."""
        self.load_categories()
    
    def load_categories(self) -> List[CategoryRule]:
        """
        Load all categories.
        
        Returns:
            List of all CategoryRule objects
        """
        try:
            categories = self.category_service.get_all_categories()
            logger.info(f"Loaded {len(categories)} categories")
            return categories
        except Exception as e:
            logger.error(f"Failed to load categories: {e}", exc_info=True)
            return []
    
    def load_category(self, category_name: str) -> Optional[CategoryRule]:
        """
        Load a specific category by name.
        
        Args:
            category_name: Name of category to load
            
        Returns:
            CategoryRule or None if not found
        """
        try:
            self.current_rule = self.category_service.get_category(category_name)
            self.has_unsaved_changes = False
            
            if self.current_rule:
                logger.debug(f"Loaded category: {category_name}")
            else:
                logger.warning(f"Category not found: {category_name}")
            
            return self.current_rule
        except Exception as e:
            logger.error(f"Failed to load category '{category_name}': {e}", exc_info=True)
            return None
    
    def create_new_category(self) -> CategoryRule:
        """
        Create a new empty category.
        
        Returns:
            New CategoryRule with default values
        """
        from ...core.models import ScoringMethod
        
        self.current_rule = CategoryRule(
            category_name="New Category",
            outlook_category="New Category",
            threshold=40,
            enabled=True,
            scoring_method=ScoringMethod.TIERED
        )
        self.has_unsaved_changes = True
        logger.debug("Created new category")
        return self.current_rule
    
    def save_category(self, rule: CategoryRule) -> Optional[Path]:
        """
        Save category.
        
        Args:
            rule: CategoryRule to save
            
        Returns:
            Path to saved file, or None if failed
        """
        try:
            if self.current_rule and self.current_rule.category_name == rule.category_name:
                # Update existing
                file_path = self.category_service.update_category(rule)
            else:
                # Create new
                file_path = self.category_service.create_category(rule)
            
            self.current_rule = rule
            self.has_unsaved_changes = False
            logger.info(f"Saved category: {rule.category_name}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save category: {e}", exc_info=True)
            return None
    
    def delete_category(self, category_name: str) -> bool:
        """
        Delete a category.
        
        Args:
            category_name: Name of category to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.category_service.delete_category(category_name)
            if success:
                logger.info(f"Deleted category: {category_name}")
                # Clear current rule if it was deleted
                if self.current_rule and self.current_rule.category_name == category_name:
                    self.current_rule = None
                    self.has_unsaved_changes = False
            return success
        except Exception as e:
            logger.error(f"Failed to delete category '{category_name}': {e}", exc_info=True)
            return False
    
    def get_current_rule(self) -> Optional[CategoryRule]:
        """Get the currently loaded rule."""
        return self.current_rule
    
    def has_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.has_unsaved_changes
    
    def mark_changed(self):
        """Mark that there are unsaved changes."""
        self.has_unsaved_changes = True

