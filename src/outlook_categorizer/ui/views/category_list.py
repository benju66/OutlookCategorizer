"""
Category list widget - displays all categories in a list.
"""

import logging
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QCheckBox,
    QMessageBox,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ...core.models import CategoryRule

logger = logging.getLogger(__name__)


class CategoryList(QWidget):
    """Widget displaying list of categories."""
    
    # Signals
    category_selected = pyqtSignal(str)  # Emits category name when selected
    new_category_requested = pyqtSignal()  # Emits when "New Category" clicked
    delete_category_requested = pyqtSignal(str)  # Emits category name when delete requested
    enable_changed = pyqtSignal(str, bool)  # Emits (category_name, enabled) when enable/disable changed
    
    def __init__(self, parent=None):
        """Initialize category list widget."""
        super().__init__(parent)
        self.categories: dict[str, CategoryRule] = {}  # category_name -> CategoryRule
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel("Categories")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Category list
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.new_button = QPushButton("+ New Category")
        self.new_button.clicked.connect(self._on_new_category)
        button_layout.addWidget(self.new_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete_category)
        self.delete_button.setEnabled(False)  # Disabled until category selected
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # Enable/disable checkbox
        self.enable_checkbox = QCheckBox("Enable selected category")
        self.enable_checkbox.setEnabled(False)  # Disabled until category selected
        self.enable_checkbox.stateChanged.connect(self._on_enable_changed)
        layout.addWidget(self.enable_checkbox)
    
    def load_categories(self, categories: list[CategoryRule]):
        """
        Load categories into the list.
        
        Args:
            categories: List of CategoryRule objects to display
        """
        self.list_widget.clear()
        self.categories.clear()
        
        for category in categories:
            self.categories[category.category_name] = category
            self._add_category_item(category)
        
        logger.debug(f"Loaded {len(categories)} categories into list")
    
    def _add_category_item(self, category: CategoryRule):
        """Add a category to the list widget."""
        item = QListWidgetItem(category.category_name)
        item.setData(Qt.ItemDataRole.UserRole, category.category_name)
        
        # Visual indicator for enabled/disabled
        if not category.enabled:
            item.setForeground(Qt.GlobalColor.gray)
            item.setText(f"{category.category_name} (disabled)")
        
        self.list_widget.addItem(item)
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle category item click."""
        category_name = item.data(Qt.ItemDataRole.UserRole)
        if category_name:
            # Enable delete button and checkbox
            self.delete_button.setEnabled(True)
            self.enable_checkbox.setEnabled(True)
            
            # Update checkbox state
            category = self.categories.get(category_name)
            if category:
                self.enable_checkbox.blockSignals(True)
                self.enable_checkbox.setChecked(category.enabled)
                self.enable_checkbox.blockSignals(False)
            
            # Emit signal
            self.category_selected.emit(category_name)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle category item double-click (same as single click for now)."""
        self._on_item_clicked(item)
    
    def _on_new_category(self):
        """Handle New Category button click."""
        self.new_category_requested.emit()
    
    def _on_delete_category(self):
        """Handle Delete Category button click."""
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        
        category_name = current_item.data(Qt.ItemDataRole.UserRole)
        if not category_name:
            return
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Delete Category",
            f"Are you sure you want to delete the category '{category_name}'?\n\n"
            "This will permanently delete the rule file.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Emit signal - main_window will handle via presenter
            self.delete_category_requested.emit(category_name)
    
    def _on_enable_changed(self, state: int):
        """Handle enable/disable checkbox change."""
        current_item = self.list_widget.currentItem()
        if not current_item:
            return
        
        category_name = current_item.data(Qt.ItemDataRole.UserRole)
        if not category_name:
            return
        
        enabled = state == Qt.CheckState.Checked.value
        logger.debug(f"Enable/disable changed for '{category_name}': {enabled}")
        # Emit signal - main_window will handle via presenter
        self.enable_changed.emit(category_name, enabled)
    
    def get_selected_category(self) -> Optional[str]:
        """Get the currently selected category name."""
        current_item = self.list_widget.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def select_category(self, category_name: str):
        """Select a category by name."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == category_name:
                self.list_widget.setCurrentItem(item)
                self._on_item_clicked(item)
                break
    
    def refresh_category(self, category: CategoryRule):
        """Refresh a category in the list (update display)."""
        category_name = category.category_name
        
        # Update internal dict
        self.categories[category_name] = category
        
        # Update list item
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item and item.data(Qt.ItemDataRole.UserRole) == category_name:
                # Update text
                if not category.enabled:
                    item.setForeground(Qt.GlobalColor.gray)
                    item.setText(f"{category_name} (disabled)")
                else:
                    item.setForeground(Qt.GlobalColor.white)  # Default color
                    item.setText(category_name)
                break

