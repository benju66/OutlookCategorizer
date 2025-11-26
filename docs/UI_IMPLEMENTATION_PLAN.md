# PyQt UI Implementation Plan

## Executive Summary

**Goal**: Build a user-friendly PyQt6 UI for managing email categorization rules without requiring technical knowledge.

**Estimated Effort**: 6-8 days (enhanced with guidance and help systems)  
**Complexity**: Medium  
**Dependencies**: PyQt6, existing service layer

---

## 1. Architecture Analysis

### Current System Architecture

**Service Layer** (Already Built ✅):
- `RuleManager`: CRUD operations for rules
- `CategoryService`: Business logic wrapper
- `ValidationService`: Rule validation
- `ConfigLoader`: YAML I/O

**Data Models** (Pydantic ✅):
- `CategoryRule`: Complete rule definition
- `Signal`: Individual pattern signal
- `CoOccurrenceBonus`: Signal pair bonuses
- Enums: `PatternType`, `SignalLocation`, `SignalTier`, `ScoringMethod`

**Scoring Engine** (Already Built ✅):
- `ScoringEngine`: Scores emails against rules
- `PatternMatcher`: Pattern matching with caching

### UI Integration Points

**Required Services:**
1. **Rule CRUD**: `RuleManager.load_all_rules()`, `save_rule()`, `load_rule()`
2. **Validation**: `ValidationService.validate_rule()`
3. **Testing**: `ScoringEngine.score_email()` for test panel
4. **Outlook Categories**: `OutlookClient.get_available_categories()` (optional - for dropdown)

**Data Flow:**
```
UI (PyQt) 
  → CategoryService 
    → RuleManager 
      → ConfigLoader (YAML)
```

---

## 2. UI Architecture Design

### Design Pattern: Model-View-Presenter (MVP)

**Why MVP?**
- Separates UI logic from business logic
- Testable (can test presenter without UI)
- Maintainable (clear separation of concerns)
- Reusable (presenter can be used by CLI later)

**Components:**

```
┌─────────────────────────────────────────┐
│           UI Layer (PyQt)               │
│  ┌──────────┐  ┌──────────┐           │
│  │  Views   │  │ Widgets  │           │
│  └────┬─────┘  └────┬─────┘           │
│       │             │                  │
│       └──────┬──────┘                  │
│              │                          │
│         ┌────▼─────┐                   │
│         │ Presenter│                   │
│         └────┬─────┘                   │
└───────────────┼────────────────────────┘
                │
┌───────────────▼────────────────────────┐
│      Service Layer (Existing)          │
│  ┌──────────┐  ┌──────────┐           │
│  │Category  │  │  Rule    │           │
│  │ Service  │  │ Manager  │           │
│  └──────────┘  └──────────┘           │
└────────────────────────────────────────┘
```

### Module Structure

```
src/outlook_categorizer/ui/
├── __init__.py
├── main_window.py          # Main application window
├── presenters/
│   ├── __init__.py
│   ├── category_presenter.py    # Category CRUD logic
│   ├── signal_presenter.py      # Signal management logic
│   └── test_presenter.py         # Test panel logic
├── views/
│   ├── __init__.py
│   ├── category_list.py         # Left sidebar category list
│   ├── category_editor.py       # Main category editor
│   ├── signal_table.py           # Signal table widget
│   └── test_panel.py             # Test panel widget
├── widgets/
│   ├── __init__.py
│   ├── signal_editor_dialog.py   # Add/edit signal dialog
│   ├── co_occurrence_dialog.py   # Co-occurrence bonus dialog
│   └── validation_dialog.py      # Validation error dialog
└── utils/
    ├── __init__.py
    ├── validators.py              # Input validators
    └── formatters.py             # Data formatters
```

---

## 3. UI Components Design

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  View  Help                                      │
├──────────┬──────────────────────────────────────────────────┤
│          │ Category: Pricing                    [Enabled] │
│          ├──────────────────────────────────────────────────┤
│ Category │ Basic Info                                        │
│ List     │ ┌────────────────────────────────────────────┐ │
│          │ │ Name:        [Pricing            ]         │ │
│ [Pricing]│ │ Outlook Cat: [Pricing            ]         │ │
│          │ │ Threshold:   [40        ]                   │ │
│ [+ New]  │ │ Method:      [Tiered ▼]                    │ │
│          │ └────────────────────────────────────────────┘ │
│          │                                                  │
│          │ Signals                                          │
│          │ ┌────────────────────────────────────────────┐ │
│          │ │ [Strong] [Medium] [Weak] [Negative]      │ │
│          │ ├────────────────────────────────────────────┤ │
│          │ │ Pattern │ Type │ Location │ Weight │ [✓] │ │
│          │ │ PCO     │ word │ subject  │   50   │ [✓] │ │
│          │ │ pricing │ sub  │ body     │   40   │ [✓] │ │
│          │ │ ...     │ ...  │ ...      │  ...   │ ... │ │
│          │ │ [+ Add Signal]                            │ │
│          │ └────────────────────────────────────────────┘ │
│          │                                                  │
│          │ Co-occurrence Bonuses                           │
│          │ ┌────────────────────────────────────────────┐ │
│          │ │ Signal Pair │ Bonus │ Proximity │ [✓]      │ │
│          │ │ [PCO, $]    │   10  │    10     │ [✓]      │ │
│          │ │ [+ Add Bonus]                                │ │
│          │ └────────────────────────────────────────────┘ │
│          │                                                  │
│          │ [Save] [Cancel] [Test Rule]                     │
│          └──────────────────────────────────────────────────┤
│                                                               │
│ Test Panel                                                    │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Subject: [OP III - Unit Updates              ]         │ │
│ │ Body:    [Here's your pricing to add...      ]         │ │
│ │          [                                    ]         │ │
│ │ [Test] → Score: 72 (Threshold: 40) [APPLY]            │ │
│ │ Matches: pricing (+40), your pricing (+40)              │ │
│ └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Main Window (`main_window.py`)
- **Purpose**: Container for all UI components
- **Features**:
  - Menu bar (File, Edit, View, Help)
  - Status bar
  - Splitter layout (category list | editor | test panel)
  - Keyboard shortcuts
  - Window state persistence

#### 2. Category List (`category_list.py`)
- **Purpose**: Left sidebar showing all categories
- **Features**:
  - List/tree widget with categories
  - Enable/disable toggle per category
  - "+ New Category" button
  - Delete category (with confirmation)
  - Visual indicators (enabled/disabled)
  - Search/filter categories

#### 3. Category Editor (`category_editor.py`)
- **Purpose**: Main editing area for category rules
- **Features**:
  - Basic info form (name, outlook category, threshold, method)
  - **Score Preview Panel** (real-time score calculation):
    - Shows Strong/Medium/Weak/Negative totals
    - Shows final score vs threshold
    - Shows "Would Apply" indicator
    - Updates automatically as signals change
  - Tabbed interface for signals (Strong/Medium/Weak/Negative/Attachment)
  - Signal tables with inline editing
  - Co-occurrence bonuses table
  - Save/Cancel buttons
  - Real-time validation feedback
  - **Undo/Redo** buttons (with keyboard shortcuts)

#### 4. Signal Table (`signal_table.py`)
- **Purpose**: Reusable table widget for signals
- **Features**:
  - Columns: Pattern, Type, Location, Weight, Description, Enabled
  - **Tabbed interface** for each tier (Strong/Medium/Weak/Negative/Attachment)
  - **Per-tier "Add Signal" button** (opens dialog with tier pre-selected)
  - Inline editing (double-click to edit: Pattern, Weight, Description, Enabled)
  - Dialog editing (right-click → Edit: All fields including tier changes)
  - Add/Delete rows (single and multi-select)
  - Sortable columns
  - Context menu (Edit, Delete, Duplicate, Move to Tier, Copy, Paste)
  - **Multi-select support** (Ctrl+Click, Shift+Click for bulk operations)
  - **Bulk operations**: Copy/paste, duplicate multiple, bulk edit weight
  - Validation indicators (color coding by weight, enabled/disabled state)
  - **Search/filter** within tier table

#### 5. Signal Editor Dialog (`signal_editor_dialog.py`)
- **Purpose**: Dialog for adding/editing signals
- **Features**:
  - **Tier pre-selected** when opened from tier tab (can be changed)
  - Pattern input (text field with validation)
  - **Pattern type dropdown** with helper (? button):
    - Substring (default) - Simple text match
    - Word Boundary - Matches whole words only
    - Regex - Advanced pattern matching (with regex validator)
    - Dollar Amount - Matches dollar amounts
    - **Helper tooltip**: When to use each type
  - **Location dropdown** with helper (? button):
    - Subject Contains - Only in email subject
    - Body Contains - Only in email body
    - Anywhere - Subject OR body (most common)
    - Sender Contains - In sender email/name
    - Attachment Name - In attachment filename
    - **Helper tooltip**: When to use each location
  - **Weight spinner (-100 to 100)** with guidance:
    - **Weight guidance panel** showing recommended ranges:
      - Strong: 40-100 points (high confidence)
      - Medium: 20-50 points (good indicators)
      - Weak: 5-20 points (supporting indicators)
      - Negative: -20 to -100 points (prevents false positives)
    - **Real-time validation**: Warn if weight outside typical range for tier
    - **Score impact preview**: Shows how weight affects final score
  - **Tier dropdown** with helper (? button):
    - Strong/Medium/Weak/Negative/Attachment
    - **Tier selection guide**: When to use each tier
    - **Visual indicators**: Color coding by tier
  - Description text area (optional)
  - Enabled checkbox
  - Max contribution spinner (optional, advanced)
  - **Preview/test pattern button**: Test pattern against sample text
  - **Regex validator**: Real-time validation for regex patterns
  - **Validation feedback**: Inline errors, helpful messages

#### 6. Test Panel (`test_panel.py`)
- **Purpose**: Test rules against sample emails
- **Features**:
  - Subject input field
  - Body text area
  - Attachments input (comma-separated)
  - Test button
  - Results display:
    - Score breakdown
    - Threshold comparison
    - Matched signals list
    - Would apply indicator
  - Clear button
  - Load sample emails button

#### 7. Co-occurrence Bonus Dialog (`co_occurrence_dialog.py`)
- **Purpose**: Dialog for adding/editing co-occurrence bonuses
- **Features**:
  - Signal pair selection (two dropdowns or autocomplete)
  - Bonus weight spinner (0-50)
  - Proximity words spinner (1-100)
  - Description text area
  - Validation

---

## 4. User Guidance & Help Content

### Weight Guidance Panel

**Location**: Signal Editor Dialog, sidebar or tooltip

**Content**:
```
Weight Guide:
─────────────
Strong Signals: 40-100 points
  ✅ Very specific patterns (e.g., "PCO #15")
  ✅ High confidence indicators
  ✅ Usually only 1-2 per category
  → Use when: Pattern is definitive

Medium Signals: 20-50 points
  ✅ Common keywords (e.g., "pricing", "quote")
  ✅ Good indicators, often combined
  ✅ Multiplied by 0.9 in tiered scoring
  ✅ Usually 5-15 per category
  → Use when: Pattern is reliable but not definitive

Weak Signals: 5-20 points
  ✅ Supporting words (e.g., "cost", "price")
  ✅ Can accumulate incorrectly
  ✅ Capped at 15 total points
  ✅ Usually 3-10 per category
  → Use when: Pattern is suggestive but not strong

Negative Signals: -20 to -100 points
  ✅ Prevents false positives
  ✅ Subtracts from total score
  → Use when: Pattern indicates NOT this category
```

### Tier Selection Helper

**Location**: Signal Editor Dialog, "?" button next to Tier dropdown

**Content**:
```
[?] Which tier should I use?

Strong (40-100 points):
  ✅ Very specific patterns (e.g., "PCO #15")
  ✅ High confidence indicators
  ✅ Usually only 1-2 per category
  → Use when: Pattern is definitive

Medium (20-50 points):
  ✅ Common keywords (e.g., "pricing", "quote")
  ✅ Good indicators, often combined
  ✅ Usually 5-15 per category
  → Use when: Pattern is reliable but not definitive

Weak (5-20 points):
  ✅ Supporting words (e.g., "cost", "price")
  ✅ Can accumulate incorrectly
  ✅ Usually 3-10 per category
  → Use when: Pattern is suggestive but not strong

Negative (-20 to -100):
  ✅ Prevents false positives
  ✅ Subtracts from score
  → Use when: Pattern indicates NOT this category
```

### Pattern Type Helper

**Location**: Signal Editor Dialog, "?" button next to Pattern Type dropdown

**Content**:
```
[?] Which pattern type?

Substring (default):
  ✅ Simple text match
  ✅ Case-insensitive
  ✅ Example: "pricing" matches "Here's your pricing"
  → Use for: Most keywords

Word Boundary:
  ✅ Matches whole words only
  ✅ Prevents partial matches
  ✅ Example: "PCO" matches "PCO #15" but not "COSTCO"
  → Use for: Short patterns (≤3 chars), acronyms

Regex:
  ✅ Advanced pattern matching
  ✅ Example: "PCO\s*#?\s*\d+" matches "PCO #15", "PCO15"
  → Use for: Complex patterns, variations
  ⚠️ Requires regex knowledge

Dollar Amount:
  ✅ Matches dollar amounts
  ✅ Example: "$" matches "$100", "$1,000", "$500.00"
  → Use for: Price/cost indicators
```

### Location Helper

**Location**: Signal Editor Dialog, "?" button next to Location dropdown

**Content**:
```
[?] Where should I search?

Subject Contains:
  ✅ Only in email subject line
  ✅ More specific, higher confidence
  → Use for: Important keywords in subject

Body Contains:
  ✅ Only in email body text
  ✅ More common, lower confidence
  → Use for: Keywords that appear in body

Anywhere (recommended):
  ✅ Subject OR body
  ✅ Most flexible, common choice
  → Use for: Keywords that could be anywhere

Sender Contains:
  ✅ In sender email address or name
  ✅ Very specific use case
  → Use for: Sender-based rules

Attachment Name:
  ✅ In attachment filename
  ✅ Very specific use case
  → Use for: File-based rules (e.g., "PCO" in filename)
```

### Score Preview Panel

**Location**: Category Editor, always visible sidebar or bottom panel

**Content**:
```
Score Preview:
──────────────
Strong Signals: 50 (max: PCO in subject)
Medium Signals: 72 × 0.9 = 64.8
Weak Signals: 13 (capped at 15)
Negative Signals: 0
──────────────────────────────
Total Score: 127.8
Threshold: 40
Would Apply: ✅ Yes

[Test with Sample Email] → Opens test panel
```

**Visual Representation** (optional):
```
Signal Impact Chart:
────────────────────
Strong:   ████████████████████ 50
Medium:   ████████████████ 36 (40×0.9)
Weak:     ████████ 13 (capped)
────────────────────────────────────
Total:    ████████████████████████████████ 99
Threshold: ████████████ 40
```

### Workflow Guides

**Location**: Help Menu → Workflow Guides

**Content**:

**Creating a New Category**:
1. Click "+ New Category" button
2. Enter category name (e.g., "Pricing")
3. Enter Outlook category name (must match exactly, case-sensitive)
4. Set threshold (default: 40)
5. Select scoring method (default: Tiered)
6. Add signals (see "Adding a Signal" guide)
7. Test with sample emails
8. Click "Save"

**Adding a Signal**:
1. Select tier tab (Strong/Medium/Weak/Negative)
2. Click "+ Add Signal" button in that tab
3. Enter pattern (e.g., "pricing")
4. Select pattern type (usually "substring")
5. Select location (usually "anywhere")
6. Set weight (see weight guide for recommended ranges)
7. Add description (optional but recommended)
8. Click "Save"
9. Signal appears in that tier's table

**Testing a Rule**:
1. Enter sample email subject in test panel
2. Enter sample email body in test panel
3. Optionally enter attachment names
4. Click "Test" button
5. Review score breakdown:
   - See which signals matched
   - See score contribution from each tier
   - See final score vs threshold
   - See if category would apply
6. Adjust weights/threshold as needed
7. Re-test until satisfied
8. Save category

---

## 5. Implementation Phases

### Phase 1: Foundation (Day 1)
**Goal**: Set up UI infrastructure

**Tasks**:
1. Install PyQt6 dependency
2. Create UI module structure
3. Create main window skeleton
4. Set up MVP pattern (presenter base class)
5. Create basic layout (splitter, menus, status bar)
6. Test window opens and displays

**Deliverables**:
- Main window opens
- Basic layout visible
- Menu bar functional

---

### Phase 2: Category List (Day 1-2)
**Goal**: Display and manage category list

**Tasks**:
1. Create `CategoryList` widget
2. Create `CategoryPresenter` (load categories)
3. Wire up to `CategoryService`
4. Display categories in list widget
5. Add "+ New Category" button
6. Add enable/disable toggle
7. Add delete category (with confirmation)
8. Handle category selection (load into editor)

**Deliverables**:
- Category list displays all categories
- Can create new category
- Can enable/disable categories
- Can delete categories
- Selecting category loads it in editor

---

### Phase 3: Category Editor - Basic Info (Day 2)
**Goal**: Edit category basic information

**Tasks**:
1. Create `CategoryEditor` widget
2. Create form fields:
   - Category name (text input)
   - Outlook category (text input + autocomplete from Outlook)
   - Threshold (spinbox, 0-200)
   - Scoring method (dropdown: tiered/additive/hybrid)
   - Weak signal cap (spinbox, 0-50)
   - Medium signal multiplier (double spinbox, 0.0-1.0)
   - Enabled checkbox
3. Wire up to presenter
4. Load category data into form
5. Save category data from form
6. Real-time validation

**Deliverables**:
- Can edit category basic info
- Validation works
- Save button saves to YAML

---

### Phase 4: Signal Tables (Day 3-3.5)
**Goal**: Display and manage signals with comprehensive guidance

**Tasks**:
1. Create `SignalTable` widget (reusable)
2. Create **tabbed interface** for each tier (Strong/Medium/Weak/Negative/Attachment)
3. Display signals in table:
   - Pattern, Type, Location, Weight, Description, Enabled
   - **Color coding** by weight (red=negative, green=positive)
   - **Icons** for pattern types
   - **Visual state** for enabled/disabled
4. Add **"Add Signal" button per tier tab** (opens dialog with tier pre-selected)
5. Create `SignalEditorDialog` with:
   - **Weight guidance panel** (recommended ranges per tier)
   - **Tier selection helper** (when to use each tier)
   - **Pattern type helper** (when to use each type)
   - **Location helper** (when to use each location)
   - **Score impact preview** (real-time score calculation)
   - **Regex validator** (for regex patterns)
   - **Default values** (tier from button, weight based on tier, pattern_type=substring, location=anywhere)
6. Wire up add/edit/delete signals
7. **Inline editing** for simple fields:
   - Pattern (text), Weight (spinbox), Description (text), Enabled (checkbox)
   - Double-click cell to edit inline
8. **Dialog editing** for complex fields:
   - Right-click → Edit opens full dialog
   - Can change tier, pattern type, location
9. Context menu:
   - Edit (full dialog)
   - Delete
   - Duplicate
   - **Move to Tier** (change tier)
   - **Copy** (Ctrl+C)
   - **Paste** (Ctrl+V)
10. **Multi-select support**:
    - Ctrl+Click for individual selection
    - Shift+Click for range selection
    - **Bulk operations**: Delete selected, Duplicate selected, Bulk edit weight
11. **Search/filter** within tier table
12. **Sortable columns** (by weight, pattern, etc.)

**Deliverables**:
- Signal tables display all signals organized by tier
- Can add new signals via per-tier button (tier pre-selected)
- Can edit signals via dialog with comprehensive guidance
- Can edit simple fields inline (double-click)
- Can delete signals (single and bulk)
- Can duplicate signals (single and bulk)
- Can move signals between tiers
- Can copy/paste signals
- Weight guidance helps users assign appropriate weights
- Tier/pattern type/location helpers guide user decisions

---

### Phase 5: Co-occurrence Bonuses (Day 3-4)
**Goal**: Manage co-occurrence bonuses

**Tasks**:
1. Create co-occurrence bonuses table
2. Create `CoOccurrenceDialog`
3. Add/edit/delete bonuses
4. Signal pair selection (autocomplete from existing signals)
5. Validation (signals must exist)

**Deliverables**:
- Co-occurrence bonuses table displays
- Can add/edit/delete bonuses
- Validation works

---

### Phase 6: Test Panel (Day 4)
**Goal**: Test rules against sample emails

**Tasks**:
1. Create `TestPanel` widget
2. Create `TestPresenter` (wires to ScoringEngine)
3. Subject input field
4. Body text area
5. Attachments input
6. Test button
7. Results display:
   - Score vs threshold
   - Matched signals list
   - Would apply indicator
8. Clear button
9. Load sample emails (predefined examples)

**Deliverables**:
- Test panel functional
- Can test rules against sample emails
- Results display correctly
- Shows score breakdown

---

### Phase 7: Validation & Error Handling (Day 4.5-5.5)
**Goal**: Comprehensive validation, error handling, and help system

**Tasks**:
1. Create `ValidationDialog` for error display
2. **Comprehensive validation**:
   - Pattern cannot be empty
   - Weight cannot be 0 (or warn if 0)
   - At least one signal must be enabled
   - Threshold must be > 0
   - At least one signal in at least one tier
   - Pattern type must match pattern (regex validation)
   - Signal pair must reference existing signals
   - Category name must be unique
   - Outlook category name validation (invalid characters)
3. Real-time validation in forms:
   - **Inline validation** (red borders, error messages)
   - **Weight validation**: Warn if outside typical range for tier
   - **Regex validation**: Test regex patterns in real-time
4. Validation on save (show errors if invalid)
5. Prevent saving invalid rules
6. Show validation errors inline
7. Handle Pydantic validation errors
8. User-friendly error messages with suggestions
9. **Help System**:
   - **Context-sensitive help**: "?" buttons next to fields
   - **Help menu**:
     - Getting Started Guide
     - Signal Management Guide
     - Weight Assignment Guide
     - Pattern Types Guide
     - Scoring Method Guide
     - Examples & Templates
     - Keyboard Shortcuts
     - FAQ
   - **Tooltips** for all fields with explanations
   - **"Learn More" links** to documentation
10. **Workflow Guides**:
    - Step-by-step guide for creating new category
    - Step-by-step guide for adding signals
    - Step-by-step guide for testing rules
    - Best practices guide

**Deliverables**:
- Comprehensive validation throughout UI
- Error messages are user-friendly with suggestions
- Can't save invalid rules
- Context-sensitive help available
- Help menu with guides and documentation
- Tooltips explain all fields
- Workflow guides help users complete tasks

---

### Phase 8: Polish & UX (Day 5.5-7)
**Goal**: Improve user experience with advanced features

**Tasks**:
1. **Complete keyboard shortcuts**:
   - Ctrl+N: New Category
   - Ctrl+S: Save Category
   - Ctrl+O: Open Category
   - Ctrl+W: Close Category
   - Ctrl+F: Find Signal
   - Ctrl+D: Duplicate Signal
   - Delete: Delete Signal
   - Ctrl+Z: Undo
   - Ctrl+Y: Redo
   - F5: Refresh
   - F1: Help
   - Esc: Close Dialog
   - Enter: Save (in dialogs)
2. **Undo/Redo functionality**:
   - Track changes in presenter
   - Limit to last 10 actions
   - Visual indicators for undo/redo availability
3. Confirmation dialogs:
   - Unsaved changes warning
   - Delete category confirmation
   - Delete signal confirmation (with count if bulk)
   - Bulk operations confirmation
4. Status bar messages:
   - "Category saved successfully"
   - "Signal added"
   - "X signals selected"
   - Validation status
5. Tooltips for all fields (comprehensive explanations)
6. Icons for buttons (optional, but recommended)
7. Window state persistence:
   - Remember window size/position
   - Remember splitter positions
   - Remember tab selections
8. Recent categories (optional)
9. Search/filter categories
10. **Score Preview Panel**:
    - Real-time score calculation as signals are added/edited
    - Shows: Strong total, Medium total (× multiplier), Weak total (capped), Negative total
    - Shows final score vs threshold
    - Shows "Would Apply" indicator
    - Updates automatically when signals change
11. **Signal Impact Visualization** (optional):
    - Bar chart showing signal contributions
    - Visual representation of tier contributions
    - Threshold line indicator
12. **Auto-save** (optional):
    - Save automatically every 30 seconds
    - Show "Saved" indicator
    - Recover unsaved changes on crash
13. Dark mode support (optional)

**Deliverables**:
- Polished UI with excellent UX
- Complete keyboard shortcuts implemented
- Undo/redo functionality works
- Confirmation dialogs for all destructive actions
- Status bar provides helpful feedback
- Score preview shows real-time calculations
- Visual feedback throughout UI

---

### Phase 9: Integration & Testing (Day 7-8)
**Goal**: Integrate with main application and comprehensive testing

**Tasks**:
1. Create `run_ui.py` entry point
2. Test with real rules (pricing.yaml)
3. Test creating new category
4. Test editing existing category
5. Test deleting category
6. Test all validation scenarios:
   - Empty patterns
   - Invalid weights
   - Invalid regex patterns
   - Missing required fields
   - Duplicate category names
7. Test signal management:
   - Adding signals to each tier
   - Editing signals (inline and dialog)
   - Moving signals between tiers
   - Bulk operations (copy/paste, duplicate, delete)
   - Weight assignment with guidance
8. Test test panel with various emails
9. Test help system:
   - Context-sensitive help (? buttons)
   - Help menu guides
   - Tooltips
   - Workflow guides
10. Test score preview:
    - Real-time updates
    - Accurate calculations
    - Visual feedback
11. Handle edge cases:
    - Invalid YAML files
    - Missing files
    - Permission errors
    - Outlook not available
    - Very long category names
    - Very many signals (performance)
    - Very many categories (performance)
12. Performance testing:
    - Many categories (20+)
    - Many signals per category (50+)
    - Large pattern strings
    - Complex regex patterns
13. User acceptance testing:
    - Non-technical user walkthrough
    - Task completion testing
    - Usability feedback
    - Help system effectiveness

**Deliverables**:
- UI fully integrated
- All features tested and working
- Edge cases handled gracefully
- Performance acceptable
- Help system comprehensive
- Ready for production use

---

## 6. Technical Details

### Dependencies

**Required**:
- `PyQt6>=6.6.0` - UI framework
- `PyQt6-Qt6>=6.6.0` - Qt6 core (usually bundled)

**Optional** (for better UX):
- `PyQt6-tools` - Designer, resource compiler
- `qdarkstyle` - Dark theme support

### PyQt6 Widgets to Use

**Core Widgets**:
- `QMainWindow` - Main window
- `QWidget` - Base widget
- `QVBoxLayout`, `QHBoxLayout`, `QGridLayout` - Layouts
- `QSplitter` - Resizable panels
- `QTabWidget` - Tabbed interface
- `QTableWidget` - Signal tables
- `QLineEdit`, `QTextEdit`, `QSpinBox`, `QDoubleSpinBox` - Input widgets
- `QComboBox` - Dropdowns
- `QPushButton`, `QCheckBox` - Buttons
- `QDialog` - Dialogs
- `QMessageBox` - Confirmation/error dialogs
- `QListWidget` - Category list
- `QMenuBar`, `QStatusBar` - Menu and status

**Advanced Widgets** (if needed):
- `QTreeWidget` - Hierarchical category list (future)
- `QSyntaxHighlighter` - Regex pattern highlighting
- `QValidator` - Input validation

### Data Binding Strategy

**Option 1: Manual Binding** (Recommended for MVP)
- Presenter loads data from service
- Presenter updates UI widgets directly
- UI widgets emit signals on change
- Presenter listens to signals and updates model
- Presenter saves to service

**Option 2: Model-View Framework** (Future enhancement)
- Use `QAbstractItemModel` for tables
- More complex but better for large datasets

**Recommendation**: Start with Option 1, migrate to Option 2 if needed.

### Validation Strategy

**Client-Side** (UI):
- Use `QValidator` for input validation
- Real-time feedback (red borders, error messages)
- Prevent invalid input

**Server-Side** (Service):
- Pydantic validation (already implemented)
- Show validation errors in dialog
- Prevent saving invalid rules

### Error Handling

**Strategy**:
1. Try-catch in presenter methods
2. Show user-friendly error messages
3. Log errors to file
4. Don't crash UI on errors
5. Provide recovery options

**Error Types**:
- Validation errors → Show in validation dialog
- File I/O errors → Show message box
- Service errors → Show message box with details
- Network errors (if Outlook) → Show warning, continue

---

## 7. Code Structure Examples

### Presenter Example

```python
# src/outlook_categorizer/ui/presenters/category_presenter.py

from typing import Optional
from pathlib import Path
from ..core.models import CategoryRule
from ...services.category_service import CategoryService

class CategoryPresenter:
    """Presenter for category management."""
    
    def __init__(self, category_service: CategoryService):
        self.service = category_service
        self.current_rule: Optional[CategoryRule] = None
        self.has_unsaved_changes = False
    
    def load_categories(self) -> list[CategoryRule]:
        """Load all categories."""
        return self.service.get_all_categories()
    
    def load_category(self, category_name: str) -> Optional[CategoryRule]:
        """Load a specific category."""
        self.current_rule = self.service.get_category(category_name)
        self.has_unsaved_changes = False
        return self.current_rule
    
    def create_new_category(self) -> CategoryRule:
        """Create a new empty category."""
        self.current_rule = CategoryRule(
            category_name="New Category",
            outlook_category="New Category",
            threshold=40,
            enabled=True
        )
        self.has_unsaved_changes = True
        return self.current_rule
    
    def save_category(self, rule: CategoryRule) -> Path:
        """Save category."""
        if self.current_rule and self.current_rule.category_name == rule.category_name:
            # Update existing
            return self.service.update_category(rule)
        else:
            # Create new
            return self.service.create_category(rule)
    
    def delete_category(self, category_name: str) -> bool:
        """Delete category."""
        return self.service.delete_category(category_name)
```

### View Example

```python
# src/outlook_categorizer/ui/views/category_editor.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QCheckBox, QPushButton
)
from PyQt6.QtCore import pyqtSignal
from ...core.models import CategoryRule, ScoringMethod

class CategoryEditor(QWidget):
    """Category editor widget."""
    
    # Signals
    save_requested = pyqtSignal()
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Basic info form
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Category Name:", self.name_edit)
        
        self.outlook_edit = QLineEdit()
        form.addRow("Outlook Category:", self.outlook_edit)
        
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(0, 200)
        form.addRow("Threshold:", self.threshold_spin)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([m.value for m in ScoringMethod])
        form.addRow("Scoring Method:", self.method_combo)
        
        self.enabled_check = QCheckBox("Enabled")
        form.addRow("", self.enabled_check)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        self.save_btn.clicked.connect(self.save_requested.emit)
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)
    
    def load_category(self, rule: CategoryRule):
        """Load category into form."""
        self.name_edit.setText(rule.category_name)
        self.outlook_edit.setText(rule.outlook_category)
        self.threshold_spin.setValue(rule.threshold)
        self.method_combo.setCurrentText(rule.scoring_method.value)
        self.enabled_check.setChecked(rule.enabled)
    
    def get_category_data(self) -> dict:
        """Get data from form."""
        return {
            "category_name": self.name_edit.text(),
            "outlook_category": self.outlook_edit.text(),
            "threshold": self.threshold_spin.value(),
            "scoring_method": ScoringMethod(self.method_combo.currentText()),
            "enabled": self.enabled_check.isChecked(),
        }
```

---

## 8. Testing Strategy

### Unit Tests
- Test presenters (mock services)
- Test validators
- Test formatters

### Integration Tests
- Test UI with real services
- Test save/load cycle
- Test validation

### Manual Testing Checklist
- [ ] Create new category
- [ ] Edit existing category
- [ ] Delete category
- [ ] Add/edit/delete signals
- [ ] Add/edit/delete co-occurrence bonuses
- [ ] Test panel works correctly
- [ ] Validation prevents invalid saves
- [ ] Keyboard shortcuts work
- [ ] Confirmation dialogs appear
- [ ] Error handling works

---

## 9. Deployment Considerations

### Entry Point

Create `run_ui.py`:
```python
#!/usr/bin/env python3
"""Launch UI application."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).parent / "src"))

from outlook_categorizer.ui.main_window import MainWindow
from outlook_categorizer.services.rule_manager import RuleManager
from outlook_categorizer.services.category_service import CategoryService

def main():
    app = QApplication(sys.argv)
    
    # Initialize services
    rules_dir = Path(__file__).parent / "config" / "rules"
    rule_manager = RuleManager(rules_dir)
    category_service = CategoryService(rule_manager)
    
    # Create and show main window
    window = MainWindow(category_service)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### Distribution

**Option 1: Source Distribution**
- Users install dependencies: `pip install -r requirements.txt`
- Run: `python run_ui.py`

**Option 2: Executable** (Future)
- Use `PyInstaller` or `cx_Freeze`
- Create standalone `.exe` file
- No Python installation required

---

## 10. Risk Assessment

### Technical Risks

**Risk**: PyQt6 learning curve
- **Mitigation**: Use simple widgets, follow examples
- **Impact**: Low - PyQt6 is well-documented

**Risk**: Performance with many categories/signals
- **Mitigation**: Use pagination/virtual scrolling if needed
- **Impact**: Low - typical use case is <20 categories

**Risk**: Integration with existing services
- **Mitigation**: Services are already well-designed
- **Impact**: Low - clean interfaces exist

### UX Risks

**Risk**: UI too complex for non-technical users
- **Mitigation**: Simple, intuitive design, tooltips, help menu
- **Impact**: Medium - address with good UX design

**Risk**: Users break YAML files
- **Mitigation**: Validation prevents invalid saves, backup before save
- **Impact**: Low - validation is robust

---

## 11. Success Criteria

### Functional Requirements
- ✅ Can create new categories
- ✅ Can edit existing categories
- ✅ Can delete categories
- ✅ Can add/edit/delete signals
- ✅ Can add/edit/delete co-occurrence bonuses
- ✅ Can test rules against sample emails
- ✅ Validation prevents invalid saves
- ✅ All changes persist to YAML files

### Non-Functional Requirements
- ✅ UI is responsive (<100ms for most operations)
- ✅ UI is intuitive (non-technical users can use it)
- ✅ Error handling is robust (doesn't crash)
- ✅ Validation provides clear feedback

---

## 12. Future Enhancements (Post-MVP)

1. **Import/Export**
   - Export category to YAML file
   - Import category from YAML file
   - Bulk import/export

2. **Advanced Features**
   - Rule templates
   - Rule versioning/history
   - Undo/redo
   - Search/filter signals

3. **UX Improvements**
   - Dark mode
   - Customizable themes
   - Keyboard shortcuts customization
   - Toolbar customization

4. **Integration**
   - Sync with Outlook categories (auto-create)
   - Preview emails from Outlook
   - Statistics dashboard (how many emails categorized)

---

## 13. Implementation Timeline

| Phase | Days | Tasks | Dependencies |
|-------|------|-------|--------------|
| 1. Foundation | 1 | UI setup, main window | PyQt6 installed |
| 2. Category List | 1-2 | List widget, CRUD | Phase 1 |
| 3. Basic Editor | 1 | Form fields, save | Phase 2 |
| 4. Signal Tables | 1.5 | Tables, dialogs, guidance | Phase 3 |
| 5. Co-occurrence | 0.5 | Bonus management | Phase 4 |
| 6. Test Panel | 1 | Test functionality | Phase 4 |
| 7. Validation & Help | 1.5 | Error handling, help system | Phase 3-6 |
| 8. Polish & UX | 1.5 | UX improvements, score preview | Phase 7 |
| 9. Integration | 1-2 | Testing, entry point | Phase 8 |
| **Total** | **8-10 days** | | |

**Realistic Estimate**: 6-8 days for enhanced MVP with guidance systems, 8-10 days with full polish

---

## 14. Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Set up development environment** - Install PyQt6
3. **Start Phase 1** - Foundation and main window
4. **Iterate** - Build incrementally, test as you go
5. **User feedback** - Get early feedback on UX

---

## Conclusion

This plan provides a comprehensive roadmap for implementing a PyQt6 UI for the email categorization system. The enhanced MVP can be built in 6-8 days, providing a user-friendly interface with comprehensive guidance and help systems for managing rules without requiring technical knowledge.

**Key Enhancements Included**:
- ✅ Per-tier signal management with pre-selected tiers
- ✅ Weight guidance and score preview
- ✅ Tier/pattern type/location selection helpers
- ✅ Comprehensive help system with context-sensitive help
- ✅ Bulk operations (multi-select, copy/paste)
- ✅ Real-time score calculation preview
- ✅ Undo/redo functionality
- ✅ Workflow guides and tutorials

The architecture is clean, maintainable, and follows best practices. The phased approach allows for incremental development and testing.

**Ready to proceed with implementation when approved.**

