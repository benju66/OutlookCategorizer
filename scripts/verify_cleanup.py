#!/usr/bin/env python3
"""
Verify that cleanup is complete and no duplicates exist.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from outlook_categorizer.services.rule_manager import RuleManager


def main():
    """Run cleanup verification."""
    print("=" * 60)
    print("CLEANUP VERIFICATION")
    print("=" * 60)
    
    # Check rule files
    rules_dir = Path(__file__).parent.parent / "config" / "rules"
    rule_files = list(rules_dir.glob("*.yaml"))
    
    print(f"\nRule files found: {len(rule_files)}")
    for rf in rule_files:
        print(f"  - {rf.name}")
    
    # Check for duplicate pricing files
    pricing_files = [f for f in rule_files if "pricing" in f.name.lower()]
    if len(pricing_files) > 1:
        print(f"\n[WARNING] Multiple pricing files found: {[f.name for f in pricing_files]}")
    else:
        print(f"\n[OK] Only one pricing file: {pricing_files[0].name if pricing_files else 'None'}")
    
    # Load rules and check for duplicates
    try:
        rule_manager = RuleManager(rules_dir)
        rules = rule_manager.load_all_rules()
        
        print(f"\nRules loaded: {len(rules)}")
        rule_names = [r.category_name for r in rules]
        print(f"Rule names: {rule_names}")
        
        # Check for duplicate category names
        unique_names = set(rule_names)
        if len(rule_names) == len(unique_names):
            print("\n[OK] Duplicate check: PASSED (no duplicate category names)")
        else:
            print(f"\n[WARNING] Duplicate category names found!")
            duplicates = [name for name in rule_names if rule_names.count(name) > 1]
            print(f"   Duplicates: {set(duplicates)}")
        
    except Exception as e:
        print(f"\n[ERROR] Error loading rules: {e}")
        return 1
    
    # Check for old code files
    src_dir = Path(__file__).parent.parent / "src"
    old_files = [
        "categorizer.py",
        "config_loader.py", 
        "outlook_client.py",
        "scoring_engine.py"
    ]
    
    print("\n" + "=" * 60)
    print("OLD CODE FILES CHECK")
    print("=" * 60)
    
    found_old = []
    for old_file in old_files:
        if (src_dir / old_file).exists():
            found_old.append(old_file)
    
    if found_old:
        print(f"\n[WARNING] Old code files found in src/: {found_old}")
    else:
        print("\n[OK] No old code files in src/ (all archived)")
    
    # Check entry points
    root_dir = Path(__file__).parent.parent
    print("\n" + "=" * 60)
    print("ENTRY POINTS CHECK")
    print("=" * 60)
    
    run_py = root_dir / "run.py"
    test_py = root_dir / "test_scoring.py"
    
    if run_py.exists():
        content = run_py.read_text()
        if "outlook_categorizer" in content:
            print("\n[OK] run.py uses new code (outlook_categorizer)")
        else:
            print("\n[WARNING] run.py may be using old imports")
    
    if test_py.exists():
        content = test_py.read_text()
        if "outlook_categorizer" in content:
            print("[OK] test_scoring.py uses new code (outlook_categorizer)")
        else:
            print("[WARNING] test_scoring.py may be using old imports")
    
    # Final summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_clean = (
        len(pricing_files) <= 1 and
        len(rule_names) == len(unique_names) and
        len(found_old) == 0
    )
    
    if all_clean:
        print("\n[SUCCESS] ALL CLEANUP COMPLETE - No duplicates found!")
        return 0
    else:
        print("\n[WARNING] Some issues found - see warnings above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

