# Outlook Email Categorization Engine v2.0

A robust, rule-based Python tool that automatically categorizes incoming Outlook emails using configurable scoring rules with tiered scoring, pattern matching, and validation.

## Features

- **Tiered Scoring System**: Prevents weak signal accumulation with intelligent scoring
- **Multiple Pattern Types**: substring, regex, word_boundary, dollar_amount
- **Co-occurrence Bonuses**: Bonus points when signal pairs appear together
- **Automatic Validation**: Pydantic models ensure data integrity
- **Multi-Category Support**: Add unlimited categories easily
- **Dry-Run Mode**: Test safely before applying categories
- **Comprehensive Logging**: Track all categorization decisions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `pydantic>=2.5.0` - Data validation and models
- `pyyaml>=6.0` - YAML configuration parsing
- `pywin32>=306` - Outlook COM interface (Windows only)

### 2. Test the Scoring Logic (No Outlook Required)

```bash
python test_scoring.py
```

This runs pre-defined test cases and allows interactive testing of email content.

### 3. Run in Dry-Run Mode

Make sure Outlook is open, then:

```bash
python run.py
```

Or double-click `run.bat`

By default, the app runs in **dry-run mode**: it logs what categories it *would* apply but doesn't actually change anything.

### 4. Enable Live Mode

Once you're confident the scoring is accurate, edit `config/settings.yaml`:

```yaml
dry_run: false
```

---

## How It Works

1. **Polls Outlook** every 60 seconds for new emails
2. **Scores each email** against category rules using tiered scoring
3. **Applies categories** if score meets threshold (supports multiple categories)
4. **Skips** emails that already have the target category

### Tiered Scoring System

The v2.0 system uses intelligent tiered scoring:

- **Strong signals**: Maximum weight (or sum)
- **Medium signals**: Weighted sum (0.9x multiplier by default)
- **Weak signals**: Capped sum (max 15 points by default)
- **Negative signals**: Subtract from total
- **Co-occurrence bonuses**: Extra points for signal pairs

This prevents weak signals from accumulating incorrectly.

### Scoring Example

An email with subject "PCO #15 - Tile Upgrade" and body mentioning "cost impact":

| Signal | Weight | Tier |
|--------|--------|------|
| "PCO #" in subject | +50 | Strong |
| "cost impact" in body | +30 | Medium |
| **Total** | **77** | (50 + 30×0.9) |

Threshold is 40, so **Pricing** category is applied.

---

## Configuration

### settings.yaml

```yaml
dry_run: true              # Set false to apply categories
poll_interval_seconds: 60  # How often to check for new emails
default_threshold: 40      # Minimum score to apply category
```

### rules/pricing.yaml

Category rules support v1.0 format (auto-migrates) or v2.0 format:

**v1.0 Format** (auto-migrates):
```yaml
category_name: "Pricing"
outlook_category: "Pricing"
threshold: 40

strong_signals:
  - pattern: "PCO"
    location: subject_contains
    weight: 50
```

**v2.0 Format** (recommended):
```yaml
version: "2.0"

category:
  name: "Pricing"
  outlook_category: "Pricing"
  threshold: 40
  enabled: true

scoring:
  method: "tiered"
  weak_signal_cap: 15
  medium_signal_multiplier: 0.9

signals:
  strong:
    - pattern: "PCO"
      pattern_type: "word_boundary"
      location: "subject_contains"
      weight: 50
      enabled: true
```

### Pattern Types

- `substring` - Simple text match (default)
- `regex` - Regular expression pattern
- `word_boundary` - Match whole words only
- `dollar_amount` - Match dollar amounts ($100, $1,000, etc.)

### Signal Locations

- `subject_contains` - Only in email subject
- `body_contains` - Only in email body
- `anywhere` - Subject or body
- `attachment_name` - In attachment filenames
- `sender_contains` - In sender email/name

---

## Project Structure

```
OutlookCategorizer/
├── run.py              # Entry point
├── test_scoring.py     # Test without Outlook
├── run.bat             # Windows launcher
├── requirements.txt
├── pyproject.toml      # Modern Python packaging
│
├── config/
│   ├── settings.yaml   # Main settings
│   └── rules/
│       └── pricing.yaml  # Category rules (add more here)
│
├── src/
│   └── outlook_categorizer/
│       ├── core/              # Core business logic
│       │   ├── models.py      # Pydantic data models
│       │   ├── scoring_engine.py
│       │   └── pattern_matcher.py
│       ├── adapters/          # External integrations
│       │   ├── outlook_client.py
│       │   └── config_loader.py
│       ├── services/          # Business services
│       │   ├── rule_manager.py
│       │   ├── category_service.py
│       │   └── validation_service.py
│       └── categorizer.py     # Main orchestration
│
├── data/
│   └── deployed_at.txt     # Created on first run
│
├── logs/
│   └── categorizer.log     # Activity log
│
└── archive/
    └── v1.0_code/          # Old code (archived)
```

---

## Adding New Categories

1. Create `config/rules/your_category.yaml`
2. Follow the `pricing.yaml` structure (v1.0 or v2.0 format)
3. Restart the app - it automatically loads all `.yaml` files

The system supports unlimited categories. Each category is independent and can have its own scoring method and signals.

---

## Troubleshooting

**"Could not connect to Outlook"**
- Make sure Outlook desktop is running
- Run as the same user that owns the Outlook profile

**Category not applying**
- Check the log for scoring details
- Run `test_scoring.py` with your email content
- Adjust weights/thresholds in the YAML
- Check that tiered scoring isn't capping your signals

**False positives**
- Add negative signals to reduce score for specific phrases
- Increase threshold
- Adjust weak_signal_cap or medium_signal_multiplier

**Duplicate category warnings**
- Ensure each category has a unique name
- Remove duplicate rule files

---

## Safety Features

- **Dry-run default**: Won't modify emails until you explicitly enable
- **Deploy marker**: Only processes emails received after first run
- **Additive only**: Adds categories, never removes existing ones
- **Logging**: All decisions logged for review
- **Validation**: Pydantic ensures data integrity

---

## Architecture

Built with industry-standard patterns:

- **Pydantic Models**: Type-safe, validated data structures
- **Service Layer**: Business logic separated from UI/adapters
- **Tiered Scoring**: Intelligent scoring prevents signal accumulation issues
- **Pattern Matcher**: Unified interface with regex caching
- **Versioned Config**: Supports migration from v1.0 to v2.0

See `docs/IMPLEMENTATION_SUMMARY.md` for detailed architecture documentation.

---

## Version History

### v2.0 (Current)
- Complete rebuild with Pydantic models
- Tiered scoring system
- Pattern type support (regex, word_boundary, dollar_amount)
- Co-occurrence bonuses
- Service layer architecture
- Automatic v1.0 → v2.0 migration

### v1.0 (Archived)
- Original proof-of-concept
- Simple additive scoring
- Basic pattern matching

---

## License

[Add your license here]
