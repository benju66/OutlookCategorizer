# Icon and Assets Organization Plan

## Icon File Location

### Recommended Structure

```
OutlookCategorizer/
├── assets/                    # NEW: All UI assets
│   ├── icons/
│   │   ├── icon.ico          # Main application icon
│   │   ├── app.ico           # Alternative name (if preferred)
│   │   └── favicon.ico       # Web favicon (if needed)
│   ├── images/               # Other images (if needed)
│   └── resources/            # Compiled resources (if using .qrc)
│       └── resources.qrc     # Qt resource file (optional)
│
├── src/
│   └── outlook_categorizer/
│       └── ui/
│           └── resources/    # ALTERNATIVE: UI-specific resources
│               └── icon.ico
```

### Recommended Location: `assets/icons/icon.ico`

**Why This Location**:
- ✅ Standard convention (`assets/` folder)
- ✅ Separates UI assets from code
- ✅ Easy to find and manage
- ✅ Can be excluded from Python imports
- ✅ Works well with PyInstaller (for future .exe)

**Path from code**: `Path(__file__).parent.parent.parent.parent / "assets" / "icons" / "icon.ico"`

**Or use relative path**: `../../../../assets/icons/icon.ico` (from `src/outlook_categorizer/ui/`)

---

## Icon Usage in PyQt6

### Main Application Icon

**Set in `main_window.py` or `run_ui.py`**:
```python
from pathlib import Path
from PyQt6.QtGui import QIcon

# Get icon path
icon_path = Path(__file__).parent.parent.parent / "assets" / "icons" / "icon.ico"

# Set application icon
app.setWindowIcon(QIcon(str(icon_path)))

# Set window icon
window.setWindowIcon(QIcon(str(icon_path)))
```

### Icon File Requirements

**Format**: `.ico` (Windows icon format)
- ✅ Works best on Windows
- ✅ Supports multiple sizes (16x16, 32x32, 48x48, 256x256)
- ✅ PyQt6 handles automatically

**Alternative Formats** (if needed):
- `.png` - Works but less optimal
- `.svg` - Requires QtSvg module

---

## SVG Icons (Lucide) - Recommendation

### Should We Add Now or Later?

**Recommendation: LATER** ⭐

### Why Later?

**Pros of Adding Later**:
- ✅ **Focus on functionality first** - Get core features working
- ✅ **Reduce complexity** - One less thing to manage
- ✅ **Faster development** - No icon decisions to make
- ✅ **Easier iteration** - Can change icons without code changes
- ✅ **Standard PyQt icons work** - QStyle provides standard icons

**Cons of Adding Now**:
- ⚠️ **Additional dependency** - Need QtSvg or convert to PNG
- ⚠️ **More complexity** - Icon management, loading, caching
- ⚠️ **Decision fatigue** - Which icons for which actions?
- ⚠️ **Time investment** - Icon selection and integration

### When to Add SVG Icons

**Add SVG Icons When**:
- ✅ Core functionality is working
- ✅ UI is stable (no major layout changes)
- ✅ User feedback indicates need for better icons
- ✅ Ready for polish phase (Phase 8)

**Timeline**: Add in Phase 8 (Polish & UX) or Phase 9 (Integration)

---

## SVG Icon Implementation (When Ready)

### Option 1: Use QtSvg (Recommended)

**Dependencies**:
```toml
[project.optional-dependencies]
ui = [
    "PyQt6>=6.6.0",
    "PyQt6-Qt6>=6.6.0",
    "PyQt6-QtSvg>=6.6.0",  # For SVG support
]
```

**Usage**:
```python
from PyQt6.QtSvg import QSvgWidget
from PyQt6.QtGui import QIcon

# Load SVG icon
icon = QIcon("assets/icons/add.svg")
button.setIcon(icon)
```

### Option 2: Convert to PNG (Simpler)

**Process**:
1. Convert Lucide SVGs to PNG (using Inkscape, ImageMagick, or online tool)
2. Store in `assets/icons/` as PNG files
3. Use standard QIcon loading

**Pros**:
- ✅ No additional dependencies
- ✅ Faster loading
- ✅ Simpler code

**Cons**:
- ⚠️ Fixed size (need multiple sizes for different DPI)
- ⚠️ Larger file sizes

### Option 3: Use Qt Resource System (.qrc)

**Process**:
1. Create `resources.qrc` file
2. Compile with `pyside6-rcc` or `pyrcc6`
3. Import compiled resources

**Pros**:
- ✅ Icons embedded in executable
- ✅ Fast loading
- ✅ Professional approach

**Cons**:
- ⚠️ More complex setup
- ⚠️ Requires compilation step

---

## Recommended Icon Set (When Ready)

### Essential Icons Needed

**Category Management**:
- Add category: `plus.svg` or `folder-plus.svg`
- Delete category: `trash.svg` or `x.svg`
- Edit category: `edit.svg` or `pencil.svg`
- Save: `save.svg` or `check.svg`
- Cancel: `x.svg` or `arrow-left.svg`

**Signal Management**:
- Add signal: `plus.svg`
- Delete signal: `trash.svg`
- Edit signal: `edit.svg`
- Duplicate signal: `copy.svg`
- Move signal: `arrow-right.svg` or `move.svg`

**Navigation**:
- Category list: `list.svg` or `menu.svg`
- Settings: `settings.svg` or `gear.svg`
- Help: `help-circle.svg` or `question-mark.svg`
- Test: `play.svg` or `test-tube.svg`

**Status Indicators**:
- Enabled: `check-circle.svg` (green)
- Disabled: `x-circle.svg` (gray)
- Warning: `alert-triangle.svg` (yellow)
- Error: `alert-circle.svg` (red)

**Tier Indicators** (Optional):
- Strong: `zap.svg` or `star.svg`
- Medium: `circle.svg` or `dot.svg`
- Weak: `minus.svg` or `dash.svg`
- Negative: `x.svg` or `minus-circle.svg`

---

## Implementation Plan

### Phase 1-7: Use Standard PyQt Icons

**Use QStyle Standard Icons**:
```python
from PyQt6.QtWidgets import QStyle

# Standard icons available
style = self.style()
add_icon = style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
delete_icon = style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
save_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
```

**Available Standard Icons**:
- `SP_FileDialogNewFolder` - Add/New
- `SP_TrashIcon` - Delete
- `SP_DialogSaveButton` - Save
- `SP_DialogCancelButton` - Cancel
- `SP_DialogHelpButton` - Help
- `SP_FileDialogListView` - List
- `SP_FileDialogDetailedView` - Details
- And many more...

**Pros**:
- ✅ No additional files needed
- ✅ Native look and feel
- ✅ Works immediately
- ✅ No dependencies

**Cons**:
- ⚠️ Limited customization
- ⚠️ May not match desired aesthetic

### Phase 8-9: Add Custom Icons (Optional)

**If adding Lucide icons**:
1. Download Lucide SVG icons
2. Store in `assets/icons/lucide/`
3. Create icon loader utility
4. Replace standard icons with custom ones
5. Test on different DPI settings

---

## File Structure Recommendation

```
OutlookCategorizer/
├── assets/                          # NEW: UI assets folder
│   ├── icons/
│   │   ├── icon.ico                # Main app icon (ADD THIS NOW)
│   │   └── lucide/                 # SVG icons (ADD LATER)
│   │       ├── plus.svg
│   │       ├── trash.svg
│   │       ├── edit.svg
│   │       └── ...
│   └── images/                     # Other images (if needed)
│
├── src/
│   └── outlook_categorizer/
│       └── ui/
│           └── utils/
│               └── icon_loader.py  # Icon loading utility (ADD LATER)
```

---

## Summary & Recommendations

### Icon File Location

**✅ RECOMMENDED**: `assets/icons/icon.ico`

**Why**:
- Standard convention
- Separates assets from code
- Easy to manage
- Works with PyInstaller

**Implementation**:
```python
# In run_ui.py or main_window.py
from pathlib import Path
from PyQt6.QtGui import QIcon

icon_path = Path(__file__).parent / "assets" / "icons" / "icon.ico"
app.setWindowIcon(QIcon(str(icon_path)))
```

### SVG Icons (Lucide)

**✅ RECOMMENDATION: ADD LATER**

**Timeline**: Phase 8 (Polish) or Phase 9 (Integration)

**Reasoning**:
- Focus on functionality first
- Standard PyQt icons work fine
- Can add as polish/enhancement
- Reduces initial complexity

**When Ready**:
- Use QtSvg for SVG support
- Or convert to PNG for simplicity
- Store in `assets/icons/lucide/`

---

## Action Items

### Now (Before Implementation)
- [ ] Create `assets/icons/` folder
- [ ] Add `icon.ico` to `assets/icons/`
- [ ] Update `.gitignore` if needed (icons should be tracked)
- [ ] Test icon loading in minimal prototype

### Later (Phase 8-9)
- [ ] Evaluate need for custom icons
- [ ] Download Lucide SVG icons (if needed)
- [ ] Create icon loader utility
- [ ] Replace standard icons with custom ones
- [ ] Test on different DPI settings

---

## Confidence Impact

**Adding icon.ico now**: +1% confidence
- ✅ Validates asset loading
- ✅ Professional appearance
- ✅ Small but important detail

**Adding SVG icons now**: -2% confidence
- ⚠️ Adds complexity
- ⚠️ More decisions to make
- ⚠️ Can defer without impact

**Recommendation**: Add `icon.ico` now, defer SVG icons to Phase 8.

