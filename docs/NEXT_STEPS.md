# Next Steps - Getting Started with v2.0

## Step 1: Install Dependencies

First, install the new dependencies (Pydantic is required):

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pydantic>=2.5.0 pyyaml>=6.0
```

**Note**: `pywin32` should already be installed if you were using the old version.

## Step 2: Test the New System

Test that the new architecture loads and works:

```bash
python test_scoring_new.py
```

This will:
- Load rules from `config/rules/`
- Run test cases
- Allow interactive testing

## Step 3: Migrate Your Existing Rules

You have two options:

### Option A: Automatic Migration (Recommended)
The system will automatically migrate v1.0 YAML files when loading them. Just use the new system and it will handle migration on-the-fly.

### Option B: Manual Migration
Run the migration script to convert `pricing.yaml` to v2.0 format:

```bash
python scripts/migrate_pricing.py
```

This will:
- Backup your existing `pricing.yaml` to `pricing.yaml.backup`
- Load and validate the rule
- Save in new v2.0 format

## Step 4: Verify Everything Works

### Test Scoring Logic
```bash
python test_scoring_new.py
```

### Test with Outlook (Dry Run)
```bash
python run_new.py
```

Make sure Outlook is running. The system will:
- Connect to Outlook
- Load rules
- Process emails in dry-run mode (won't modify anything)
- Show what categories it would apply

## Step 5: Switch to New System

Once you're confident everything works:

1. **Backup old files** (optional but recommended):
   ```bash
   # Create backup directory
   mkdir backup
   copy src\*.py backup\
   copy run.py backup\
   copy test_scoring.py backup\
   ```

2. **Use the new entry point**:
   - Use `run_new.py` instead of `run.py`
   - Use `test_scoring_new.py` instead of `test_scoring.py`

3. **Migrate pricing.yaml** (if you want v2.0 format):
   ```bash
   python scripts/migrate_pricing.py
   ```

## Step 6: Enable Live Mode (When Ready)

Edit `config/settings.yaml`:
```yaml
dry_run: false  # Change from true to false
```

**Important**: Only do this after testing in dry-run mode!

## Troubleshooting

### "ModuleNotFoundError: No module named 'pydantic'"
- Run: `pip install pydantic>=2.5.0`

### "Failed to load rule"
- Check that YAML files are valid
- Check logs for specific error messages
- Old v1.0 format will auto-migrate

### "Could not connect to Outlook"
- Make sure Outlook desktop is running
- Run as the same user that owns the Outlook profile

## What's Different in v2.0?

### Scoring Changes
- **Tiered scoring** by default (prevents weak signal accumulation)
- Strong signals: max() or sum
- Medium signals: weighted sum (0.9x multiplier)
- Weak signals: capped sum (max 15 points)

### Configuration Changes
- New nested YAML structure (v2.0)
- Pattern types: `substring`, `regex`, `word_boundary`, `dollar_amount`
- Co-occurrence bonuses supported
- Better validation

### Code Changes
- New package structure: `src/outlook_categorizer/`
- Pydantic models instead of dataclasses
- Service layer for business logic
- Better error handling and validation

## Next Development Steps

After verifying everything works:

1. **Add PyQt UI** (if desired)
   - User-friendly rule editor
   - Visual category management
   - Test panel

2. **Add More Categories**
   - Create new YAML files in `config/rules/`
   - Follow the v2.0 schema
   - System automatically loads all `.yaml` files

3. **Write Tests**
   - Unit tests for scoring engine
   - Integration tests for categorizer
   - Test fixtures for sample emails

4. **Documentation**
   - User guide
   - API documentation
   - Category creation guide

## Quick Reference

### File Locations
- **New code**: `src/outlook_categorizer/`
- **Old code**: `src/` (original files, still there)
- **Rules**: `config/rules/*.yaml`
- **Settings**: `config/settings.yaml`
- **Logs**: `logs/categorizer.log`

### Entry Points
- **New runner**: `run_new.py`
- **New tester**: `test_scoring_new.py`
- **Old runner**: `run.py` (still works)
- **Old tester**: `test_scoring.py` (still works)

### Key Classes
- `EmailCategorizer`: Main orchestrator
- `ScoringEngine`: Scoring logic
- `RuleManager`: Rule CRUD operations
- `PatternMatcher`: Pattern matching
- `CategoryRule`: Rule model (Pydantic)
- `Signal`: Signal model (Pydantic)

