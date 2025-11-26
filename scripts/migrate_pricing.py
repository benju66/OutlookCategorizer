#!/usr/bin/env python3
"""
Migration script to convert pricing.yaml from v1.0 to v2.0 format.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from outlook_categorizer.services.rule_manager import RuleManager


def main():
    """Migrate pricing.yaml to new format."""
    root_dir = Path(__file__).parent.parent
    rules_dir = root_dir / "config" / "rules"
    
    # Backup old file
    old_file = rules_dir / "pricing.yaml"
    if old_file.exists():
        backup_file = rules_dir / "pricing.yaml.backup"
        print(f"Backing up {old_file} to {backup_file}")
        import shutil
        shutil.copy2(old_file, backup_file)
    
    # Load old rule
    rule_manager = RuleManager(rules_dir)
    try:
        rule = rule_manager.load_rule(old_file)
        print(f"Loaded rule: {rule.category_name}")
        
        # Save in new format
        new_file = rules_dir / "pricing.yaml"
        rule_manager.save_rule(rule, new_file)
        print(f"Migrated to new format: {new_file}")
        print("Migration complete!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

