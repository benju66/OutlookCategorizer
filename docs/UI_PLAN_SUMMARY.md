# UI Implementation Plan - Quick Summary

## Overview

**Goal**: Build PyQt6 UI for managing email categorization rules  
**Effort**: 5-7 days (MVP), 7-9 days (with polish)  
**Architecture**: Model-View-Presenter (MVP) pattern

---

## Key Components

### Main Window
- Menu bar, status bar
- Splitter layout: Category List | Editor | Test Panel

### Category List (Left Sidebar)
- List all categories
- Enable/disable toggle
- Create new category
- Delete category
- Select category to edit

### Category Editor (Main Area)
- Basic info: Name, Outlook category, threshold, scoring method
- Signal tables: Strong/Medium/Weak/Negative/Attachment
- Co-occurrence bonuses table
- Save/Cancel buttons

### Test Panel (Bottom)
- Subject/body input
- Test button
- Score breakdown display
- Matched signals list

---

## Implementation Phases

1. **Foundation** (Day 1) - Main window, layout
2. **Category List** (Day 1-2) - Display and manage categories
3. **Basic Editor** (Day 2) - Edit category info
4. **Signal Tables** (Day 3) - Manage signals
5. **Co-occurrence** (Day 3-4) - Manage bonuses
6. **Test Panel** (Day 4) - Test rules
7. **Validation** (Day 4-5) - Error handling
8. **Polish** (Day 5-6) - UX improvements
9. **Integration** (Day 6-7) - Testing, entry point

---

## Dependencies

- `PyQt6>=6.6.0` (already in pyproject.toml as optional)
- Existing service layer (already built ✅)

---

## Architecture

```
UI (PyQt) → Presenter → Service Layer → YAML Files
```

**MVP Pattern**:
- **Views**: PyQt widgets (UI only)
- **Presenters**: Business logic (no UI)
- **Services**: Data access (already exist)

---

## Key Features

✅ Create/edit/delete categories  
✅ Add/edit/delete signals  
✅ Manage co-occurrence bonuses  
✅ Test rules against sample emails  
✅ Real-time validation  
✅ User-friendly error messages  
✅ Keyboard shortcuts  
✅ Confirmation dialogs  

---

## Entry Point

Create `run_ui.py`:
```python
python run_ui.py  # Launches UI
```

---

## Success Criteria

- Non-technical users can manage rules
- All CRUD operations work
- Validation prevents invalid saves
- Test panel works correctly
- Changes persist to YAML files

---

## Full Plan

See `docs/UI_IMPLEMENTATION_PLAN.md` for complete details.

