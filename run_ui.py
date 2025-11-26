#!/usr/bin/env python3
"""
Launch UI application for Outlook Email Categorizer.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from outlook_categorizer.ui.main_window import MainWindow
from outlook_categorizer.services.rule_manager import RuleManager
from outlook_categorizer.services.category_service import CategoryService


def setup_logging():
    """Configure logging for UI application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(Path(__file__).parent / "logs" / "ui.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for UI application."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Outlook Email Categorizer - UI Application")
    logger.info("=" * 60)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Outlook Email Categorizer")
    app.setOrganizationName("OutlookCategorizer")
    
    # Set application icon
    try:
        icon_path = Path(__file__).parent / "assets" / "icons" / "icon.ico"
        if icon_path.exists():
            from PyQt6.QtGui import QIcon
            app.setWindowIcon(QIcon(str(icon_path)))
            logger.debug(f"Set application icon: {icon_path}")
        else:
            logger.warning(f"Icon file not found: {icon_path.absolute()}")
    except Exception as e:
        logger.warning(f"Could not set application icon: {e}")
    
    # Initialize services
    try:
        config_dir = Path(__file__).parent / "config"
        rules_dir = config_dir / "rules"
        
        rule_manager = RuleManager(rules_dir)
        category_service = CategoryService(rule_manager)
        
        logger.info(f"Initialized services - Rules directory: {rules_dir}")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "Initialization Error",
            f"Failed to initialize application:\n\n{str(e)}\n\nPlease check your configuration."
        )
        sys.exit(1)
    
    # Create and show main window
    try:
        window = MainWindow(category_service)
        window.show()
        
        logger.info("Main window displayed")
        logger.info("Application ready")
        
        # Run event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(
            None,
            "Application Error",
            f"Failed to start application:\n\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

