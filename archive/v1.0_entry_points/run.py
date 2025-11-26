#!/usr/bin/env python3
"""
Outlook Email Categorization Engine
Entry point - starts the email listener
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from categorizer import EmailCategorizer
from config_loader import load_settings


def setup_logging(log_dir: Path) -> None:
    """Configure logging to file and console."""
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_dir / "categorizer.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point."""
    root_dir = Path(__file__).parent
    
    # Setup logging
    setup_logging(root_dir / "logs")
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Outlook Email Categorization Engine")
    logger.info("=" * 60)
    
    # Load settings
    try:
        settings = load_settings(root_dir / "config" / "settings.yaml")
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        sys.exit(1)
    
    # Show current mode
    if settings.get("dry_run", True):
        logger.info("MODE: Dry-run (will log decisions but NOT apply categories)")
        logger.info("      Set 'dry_run: false' in settings.yaml to enable live mode")
    else:
        logger.info("MODE: LIVE (will apply categories to emails)")
    
    # Initialize and start categorizer
    try:
        categorizer = EmailCategorizer(
            config_dir=root_dir / "config",
            dry_run=settings.get("dry_run", True),
            poll_interval=settings.get("poll_interval_seconds", 60)
        )
        
        logger.info(f"Poll interval: {settings.get('poll_interval_seconds', 60)} seconds")
        logger.info("Starting email monitor... Press Ctrl+C to stop")
        logger.info("-" * 60)
        
        categorizer.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
