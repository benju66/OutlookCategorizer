#!/usr/bin/env python3
"""
Test the scoring engine without needing Outlook.
Paste email content and see how it would be scored.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config_loader import load_category_rules
from scoring_engine import ScoringEngine
from outlook_client import EmailMessage
from datetime import datetime


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
        status = "✅ WOULD APPLY" if result.should_apply else "❌ Would not apply"
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
    # Load rules
    root_dir = Path(__file__).parent
    rules_dir = root_dir / "config" / "rules"
    rules = load_category_rules(rules_dir)
    
    print(f"Loaded {len(rules)} category rule(s): {[r.category_name for r in rules]}")
    
    scoring_engine = ScoringEngine(rules)
    
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
    
    # Test 8: Edge case - just "price" alone (should NOT match)
    test_email(
        scoring_engine,
        subject="Meeting Tomorrow",
        body="Let's discuss the price of the fixtures tomorrow."
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
