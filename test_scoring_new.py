#!/usr/bin/env python3
"""
Test the scoring engine without needing Outlook.
Paste email content and see how it would be scored.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from outlook_categorizer.core.models import EmailMessage
from outlook_categorizer.core.scoring_engine import ScoringEngine
from outlook_categorizer.services.rule_manager import RuleManager


def test_email(scoring_engine: ScoringEngine, subject: str, body: str, attachments: list[str] = None):
    """Test a single email and print results."""
    
    if attachments is None:
        attachments = []
    
    # Create mock email
    email = EmailMessage(
        entry_id="TEST",
        subject=subject,
        body=body,
        sender_email="test@example.com",
        sender_name="Test Sender",
        received_time=datetime.now(),
        attachment_names=attachments,
        categories=[],
        conversation_id="TEST",
        _outlook_item=None
    )
    
    print("\n" + "=" * 60)
    print(f"SUBJECT: {subject}")
    print(f"BODY: {body[:100]}{'...' if len(body) > 100 else ''}")
    if attachments:
        print(f"ATTACHMENTS: {attachments}")
    print("=" * 60)
    
    results = scoring_engine.score_email(email)
    
    for result in results:
        status = "[APPLY]" if result.should_apply else "[SKIP]"
        print(f"\n{status}: {result.category_name}")
        print(f"Score: {result.score} (threshold: {result.threshold})")
        
        if result.matches:
            print("Signals matched:")
            sorted_matches = sorted(result.matches, key=lambda m: m.weight, reverse=True)
            for match in sorted_matches:
                sign = "+" if match.weight > 0 else ""
                print(f"  {sign}{match.weight}: '{match.pattern}' found in {match.found_in}")
        else:
            print("No signals matched")


def main():
    """Main test function."""
    # Load rules
    root_dir = Path(__file__).parent
    rules_dir = root_dir / "config" / "rules"
    
    rule_manager = RuleManager(rules_dir)
    rules = rule_manager.load_all_rules()
    
    print(f"Loaded {len(rules)} category rule(s): {[r.category_name for r in rules]}")
    
    from outlook_categorizer.core.pattern_matcher import PatternMatcher
    matcher = PatternMatcher()
    scoring_engine = ScoringEngine(rules, matcher)
    
    # Test cases
    print("\n" + "#" * 60)
    print("# RUNNING TEST CASES")
    print("#" * 60)
    
    # Test 1: Clear PCO email (should match)
    test_email(
        scoring_engine,
        subject="PCO #15 - Lobby Tile Upgrade",
        body="Please review the attached PCO for the tile upgrade in the main lobby."
    )
    
    # Test 2: Quote request (should match)
    test_email(
        scoring_engine,
        subject="RE: Millwork Changes",
        body="Please provide pricing for the additional millwork in Unit B2. We need this by Friday."
    )
    
    # Test 3: Cost impact mentioned (should match)
    test_email(
        scoring_engine,
        subject="ASI-23 Review",
        body="This ASI will have a cost impact. Please review and advise on budget implications."
    )
    
    # Test 4: False positive test - "no cost" (should NOT match)
    test_email(
        scoring_engine,
        subject="RE: Door Hardware Change",
        body="We can make this change at no additional cost. Proceed as discussed."
    )
    
    # Test 5: Unrelated email (should NOT match)
    test_email(
        scoring_engine,
        subject="Team Lunch Friday",
        body="Hey team, let's do lunch at noon on Friday. Any preferences on where to go?"
    )
    
    # Test 6: Attachment with PCO (should match)
    test_email(
        scoring_engine,
        subject="Documents for Review",
        body="See attached.",
        attachments=["PCO-015_Tile_Upgrade.pdf", "Schedule.xlsx"]
    )
    
    # Test 7: T&M reference (should match)
    test_email(
        scoring_engine,
        subject="Extra Work Authorization",
        body="Please authorize the following T&M work for the electrical changes."
    )
    
    # Test 8: Dollar amount (should match)
    test_email(
        scoring_engine,
        subject="OP III - Unit Updates",
        body="To add relocate the heat lap switch. ADD $1925. Let us know if this is approved."
    )
    
    print("\n" + "#" * 60)
    print("# INTERACTIVE MODE")
    print("# Enter your own test emails below")
    print("# Type 'quit' to exit")
    print("#" * 60)
    
    while True:
        print("\n")
        subject = input("Subject (or 'quit'): ").strip()
        if subject.lower() == 'quit':
            break
        
        body = input("Body: ").strip()
        attachments_input = input("Attachments (comma-separated, or blank): ").strip()
        attachments = [a.strip() for a in attachments_input.split(",")] if attachments_input else []
        
        test_email(scoring_engine, subject, body, attachments)


if __name__ == "__main__":
    main()

