# Cleanup Plan - Remove Old Code, Keep Only v2.0

## Files to Archive/Remove

### Old Code Files (src/ root)
- `src/categorizer.py` → Archive
- `src/config_loader.py` → Archive  
- `src/outlook_client.py` → Archive
- `src/scoring_engine.py` → Archive
- `src/__init__.py` → Remove (empty/unused)

### Old Entry Points
- `run.py` → Archive, replace with `run_new.py`
- `test_scoring.py` → Archive, replace with `test_scoring_new.py`

### Duplicate Rule Files
- `config/rules/pricing_v2.yaml` → Remove (keep pricing.yaml which auto-migrates)

## Files to Rename

- `run_new.py` → `run.py`
- `test_scoring_new.py` → `test_scoring.py`

## Improvements to Make

1. Add duplicate category name check in RuleManager
2. Update README.md for v2.0
3. Update run.bat
4. Improve .gitignore

