"""
Main application window for Outlook Email Categorizer UI.
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QMenuBar,
    QStatusBar,
    QMessageBox,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QKeySequence

from ..services.category_service import CategoryService
from .presenters.base_presenter import BasePresenter
from .presenters.category_presenter import CategoryPresenter
from .views.category_list import CategoryList

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, category_service: CategoryService, parent=None):
        """
        Initialize main window.
        
        Args:
            category_service: CategoryService instance for data access
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.category_service = category_service
        
        # Initialize presenter
        self.category_presenter = CategoryPresenter(category_service)
        
        # Window properties
        self.setWindowTitle("Outlook Email Categorizer - Rule Manager")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Set application icon
        self._set_window_icon()
        
        # Create UI components
        self._create_menu_bar()
        self._create_status_bar()
        self._create_central_widget()
        
        # Wire up category list
        self._setup_category_list()
        
        # Status bar message
        self.statusBar().showMessage("Ready")
        
        logger.info("Main window initialized")
    
    def _set_window_icon(self):
        """Set the window icon from assets/icons/icon.ico."""
        try:
            # Get icon path relative to project root
            # From src/outlook_categorizer/ui/main_window.py
            # Go up: ui -> outlook_categorizer -> src -> project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            icon_path = project_root / "assets" / "icons" / "icon.ico"
            
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
                logger.debug(f"Set window icon: {icon_path}")
            else:
                logger.warning(f"Icon file not found: {icon_path}")
                logger.debug(f"Looking for icon at: {icon_path.absolute()}")
        except Exception as e:
            logger.warning(f"Could not set window icon: {e}")
    
    def _create_menu_bar(self):
        """Create menu bar with standard menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Category", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.setStatusTip("Create a new category rule")
        new_action.triggered.connect(self._on_new_category)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Category...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.setStatusTip("Open an existing category rule")
        open_action.triggered.connect(self._on_open_category)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.setStatusTip("Save current category")
        save_action.triggered.connect(self._on_save)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Placeholder for future edit actions
        # Will be populated in later phases
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Placeholder for future view actions
        # Will be populated in later phases
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Outlook Email Categorizer")
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        
        help_menu.addSeparator()
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence("F1"))
        shortcuts_action.setStatusTip("Show keyboard shortcuts")
        shortcuts_action.triggered.connect(self._on_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)
    
    def _create_status_bar(self):
        """Create status bar."""
        status_bar = self.statusBar()
        status_bar.showMessage("Ready")
    
    def _create_central_widget(self):
        """Create central widget with splitter layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel (category list) - Phase 2
        self.category_list = CategoryList()
        self.category_list.setMinimumWidth(200)
        self.category_list.setMaximumWidth(400)
        
        # Right panel (category editor) - will be added in Phase 3
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Placeholder label
        placeholder_label2 = QLabel("Category Editor\n(Phase 3)")
        placeholder_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label2.setStyleSheet("color: gray; font-style: italic;")
        right_layout.addWidget(placeholder_label2)
        
        # Add panels to splitter
        splitter.addWidget(self.category_list)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 900])
        
        self.splitter = splitter
        self.right_panel = right_panel
    
    def _setup_category_list(self):
        """Set up category list widget and wire up signals."""
        # Load categories
        categories = self.category_presenter.load_categories()
        self.category_list.load_categories(categories)
        
        # Wire up signals
        self.category_list.category_selected.connect(self._on_category_selected)
        self.category_list.new_category_requested.connect(self._on_new_category_from_list)
        self.category_list.delete_category_requested.connect(self._on_delete_category)
        self.category_list.enable_changed.connect(self._on_enable_changed)
        
        # Set presenter's view
        self.category_presenter.set_view(self.category_list)
        self.category_presenter.initialize()
    
    def _on_category_selected(self, category_name: str):
        """Handle category selection from list."""
        logger.debug(f"Category selected: {category_name}")
        rule = self.category_presenter.load_category(category_name)
        if rule:
            self.statusBar().showMessage(f"Loaded category: {category_name}", 2000)
            # TODO: Load into editor (Phase 3)
        else:
            self.statusBar().showMessage(f"Failed to load category: {category_name}", 3000)
    
    def _on_new_category_from_list(self):
        """Handle New Category request from list."""
        logger.debug("New category requested from list")
        rule = self.category_presenter.create_new_category()
        if rule:
            # Add to list
            self.category_list.load_categories(self.category_presenter.load_categories())
            # Select the new category
            self.category_list.select_category(rule.category_name)
            self.statusBar().showMessage("Created new category - ready to edit", 2000)
            # TODO: Load into editor (Phase 3)
    
    def _on_delete_category(self, category_name: str):
        """Handle delete category request."""
        logger.debug(f"Delete category requested: {category_name}")
        success = self.category_presenter.delete_category(category_name)
        if success:
            # Reload categories
            categories = self.category_presenter.load_categories()
            self.category_list.load_categories(categories)
            self.statusBar().showMessage(f"Deleted category: {category_name}", 2000)
        else:
            self.statusBar().showMessage(f"Failed to delete category: {category_name}", 3000)
    
    def _on_enable_changed(self, category_name: str, enabled: bool):
        """Handle enable/disable category change."""
        logger.debug(f"Enable/disable changed for '{category_name}': {enabled}")
        # Use CategoryService's enable_category method
        success = self.category_service.enable_category(category_name, enabled)
        if success:
            # Reload categories to refresh list
            categories = self.category_presenter.load_categories()
            self.category_list.load_categories(categories)
            # Reselect the category
            self.category_list.select_category(category_name)
            status = "enabled" if enabled else "disabled"
            self.statusBar().showMessage(f"Category '{category_name}' {status}", 2000)
        else:
            self.statusBar().showMessage(f"Failed to update category: {category_name}", 3000)
    
    def _on_new_category(self):
        """Handle New Category menu action."""
        # Trigger new category from list widget
        self.category_list._on_new_category()
    
    def _on_open_category(self):
        """Handle Open Category menu action."""
        self.statusBar().showMessage("Open Category (Phase 2)", 2000)
        # Will be implemented in Phase 2
    
    def _on_save(self):
        """Handle Save menu action."""
        self.statusBar().showMessage("Save (Phase 3)", 2000)
        # Will be implemented in Phase 3
    
    def _on_about(self):
        """Show About dialog."""
        QMessageBox.about(
            self,
            "About Outlook Email Categorizer",
            "<h2>Outlook Email Categorizer</h2>"
            "<p>Version 2.0</p>"
            "<p>Rule-based email categorization for Outlook</p>"
            "<p>Manage categorization rules with an intuitive interface.</p>"
        )
    
    def _on_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """
        <h3>Keyboard Shortcuts</h3>
        <table>
        <tr><td><b>Ctrl+N</b></td><td>New Category</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open Category</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save</td></tr>
        <tr><td><b>F1</b></td><td>Help / Keyboard Shortcuts</td></tr>
        <tr><td><b>Alt+F4</b></td><td>Exit</td></tr>
        </table>
        <p><i>More shortcuts will be added as features are implemented.</i></p>
        """
        QMessageBox.information(
            self,
            "Keyboard Shortcuts",
            shortcuts_text
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # TODO: Check for unsaved changes in Phase 3
        # For now, just close
        event.accept()

