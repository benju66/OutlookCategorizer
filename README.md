# Outlook Email Categorization Engine

A lightweight, local Python tool that automatically categorizes incoming Outlook emails based on configurable scoring rules.

## Current Status: POC

This proof-of-concept implements the **Pricing** category only. Once validated, additional categories can be added easily.

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test the Scoring Logic (No Outlook Required)

```bash
python test_scoring.py
```

This runs pre-defined test cases and then lets you enter your own email content to see how it would be scored.

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
2. **Scores each email** against category rules using weighted signals
3. **Applies categories** if score meets threshold (supports multiple categories)
4. **Skips** emails that already have the target category

### Scoring Example

An email with subject "PCO #15 - Tile Upgrade" and body mentioning "cost impact":

| Signal | Weight |
|--------|--------|
| "PCO #" in subject | +50 |
| "cost impact" in body | +30 |
| **Total** | **80** |

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

Add or modify signals:

```yaml
strong_signals:
  - pattern: "your keyword"
    location: subject_contains  # or body_contains, anywhere
    weight: 50
```

Signal locations:
- `subject_contains` - Only in subject line
- `body_contains` - Only in email body
- `anywhere` - Subject or body
- `attachment_name` - In attachment filenames
- `sender_contains` - In sender email/name

---

## File Structure

```
email_categorizer/
├── run.py              # Entry point
├── test_scoring.py     # Test without Outlook
├── run.bat             # Windows launcher
├── requirements.txt
│
├── config/
│   ├── settings.yaml   # Main settings
│   └── rules/
│       └── pricing.yaml  # Pricing category rules
│
├── src/
│   ├── categorizer.py      # Main orchestration
│   ├── outlook_client.py   # Outlook COM interface
│   ├── scoring_engine.py   # Scoring logic
│   └── config_loader.py    # YAML parsing
│
├── data/
│   └── deployed_at.txt     # Created on first run
│
└── logs/
    └── categorizer.log     # Activity log
```

---

## Adding New Categories

1. Create `config/rules/your_category.yaml`
2. Follow the `pricing.yaml` structure
3. Restart the app

---

## Troubleshooting

**"Could not connect to Outlook"**
- Make sure Outlook desktop is running
- Run as the same user that owns the Outlook profile

**Category not applying**
- Check the log for scoring details
- Run `test_scoring.py` with your email content
- Adjust weights/thresholds in the YAML

**False positives**
- Add negative signals to reduce score for specific phrases
- Increase threshold

---

## Safety Features

- **Dry-run default**: Won't modify emails until you explicitly enable
- **Deploy marker**: Only processes emails received after first run
- **Additive only**: Adds categories, never removes existing ones
- **Logging**: All decisions logged for review
