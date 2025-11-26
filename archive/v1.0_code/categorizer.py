"""
Email Categorizer - Main orchestration module.
Coordinates Outlook client, scoring engine, and rules.
"""

import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from outlook_client import OutlookClient, EmailMessage
from scoring_engine import ScoringEngine, ScoringResult
from config_loader import load_settings, load_category_rules

logger = logging.getLogger(__name__)


class EmailCategorizer:
    """Main categorization engine."""
    
    def __init__(
        self, 
        config_dir: Path,
        dry_run: bool = True,
        poll_interval: int = 60
    ):
        self.config_dir = config_dir
        self.dry_run = dry_run
        self.poll_interval = poll_interval
        
        self.outlook = OutlookClient()
        self.scoring_engine = None
        self.last_run_time = None
        self.deploy_marker_file = config_dir.parent / "data" / "deployed_at.txt"
        
        # Load rules
        self._load_rules()
    
    def _load_rules(self):
        """Load category rules from config directory."""
        rules_dir = self.config_dir / "rules"
        rules = load_category_rules(rules_dir)
        self.scoring_engine = ScoringEngine(rules)
        logger.info(f"Loaded {len(rules)} category rule(s): {[r.category_name for r in rules]}")
    
    def _get_start_time(self) -> datetime:
        """
        Determine the starting point for email processing.
        On first run, creates a deployment marker.
        """
        # Ensure data directory exists
        self.deploy_marker_file.parent.mkdir(exist_ok=True)
        
        if self.deploy_marker_file.exists():
            # Use saved deployment time
            with open(self.deploy_marker_file, 'r') as f:
                timestamp = f.read().strip()
                return datetime.fromisoformat(timestamp)
        else:
            # First run - mark deployment time as NOW
            now = datetime.now()
            with open(self.deploy_marker_file, 'w') as f:
                f.write(now.isoformat())
            logger.info(f"First run - will only process emails received after {now}")
            return now
    
    def start(self):
        """Start the categorization polling loop."""
        # Connect to Outlook
        if not self.outlook.connect():
            raise RuntimeError("Could not connect to Outlook")
        
        # Verify categories exist
        available_categories = self.outlook.get_available_categories()
        logger.info(f"Available Outlook categories: {available_categories}")
        
        # Get starting point
        start_time = self._get_start_time()
        self.last_run_time = start_time
        
        # Main loop
        while True:
            try:
                self._process_new_emails()
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                # Wait a bit longer on error before retry
                time.sleep(self.poll_interval * 2)
    
    def _process_new_emails(self):
        """Process any emails received since last run."""
        # Check Outlook connection
        if not self.outlook.is_connected():
            logger.warning("Lost connection to Outlook, reconnecting...")
            if not self.outlook.connect():
                logger.error("Failed to reconnect to Outlook")
                return
        
        # Get new emails
        emails = self.outlook.get_emails_since(self.last_run_time)
        
        if emails:
            logger.info(f"Processing {len(emails)} new email(s)...")
            
            for email in emails:
                self._categorize_email(email)
        
        # Update last run time
        self.last_run_time = datetime.now()
    
    def _categorize_email(self, email: EmailMessage):
        """Score and categorize a single email."""
        # DEBUG: See what we're actually reading
        print(f"SUBJECT: {email.subject}")
        print(f"BODY LENGTH: {len(email.body)} chars")
        print(f"BODY PREVIEW: {email.body[:200]}")
        print("-" * 40)
        
        # Score against all rules
        results = self.scoring_engine.score_email(email)
        
        # Find categories to apply
        categories_to_apply = []
        for result in results:
            if result.should_apply:
                # Check if already has this category
                if result.outlook_category in email.categories:
                    logger.debug(
                        f"Skipping '{result.outlook_category}' - already assigned: "
                        f"{email.subject[:40]}..."
                    )
                    continue
                categories_to_apply.append(result)
        
        # Log decisions
        if categories_to_apply:
            self._log_categorization(email, categories_to_apply)
            
            # Apply categories (unless dry run)
            if not self.dry_run:
                for result in categories_to_apply:
                    self.outlook.apply_category(email, result.outlook_category)
            else:
                cats = [r.outlook_category for r in categories_to_apply]
                logger.info(f"[DRY RUN] Would apply: {cats}")
        else:
            # Log that nothing matched (debug level)
            logger.debug(f"No categories matched: {email.subject[:50]}...")
    
    def _log_categorization(self, email: EmailMessage, results: list[ScoringResult]):
        """Log a categorization decision."""
        subject_preview = email.subject[:50] + "..." if len(email.subject) > 50 else email.subject
        
        for result in results:
            logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Match: {result.outlook_category}")
            logger.info(f"  Subject: {subject_preview}")
            logger.info(f"  Score: {result.score} (threshold: {result.threshold})")
            logger.info(f"  Signals: {len(result.matches)} matched")
            
            # Show top contributing signals
            if result.matches:
                sorted_matches = sorted(result.matches, key=lambda m: m.weight, reverse=True)
                for match in sorted_matches[:3]:  # Top 3
                    sign = "+" if match.weight > 0 else ""
                    logger.info(f"    {sign}{match.weight}: '{match.pattern}' in {match.found_in}")
    
    def run_once(self):
        """Run categorization once (for testing)."""
        if not self.outlook.connect():
            raise RuntimeError("Could not connect to Outlook")
        
        start_time = self._get_start_time()
        self.last_run_time = start_time
        self._process_new_emails()
    
    def test_email_text(self, subject: str, body: str) -> list[ScoringResult]:
        """
        Test scoring against provided text (no Outlook needed).
        Useful for testing rules without actual emails.
        """
        from outlook_client import EmailMessage
        
        test_email = EmailMessage(
            entry_id="TEST",
            subject=subject,
            body=body,
            sender_email="test@example.com",
            sender_name="Test Sender",
            received_time=datetime.now(),
            attachment_names=[],
            categories=[],
            conversation_id="TEST",
            _outlook_item=None
        )
        
        return self.scoring_engine.score_email(test_email)
