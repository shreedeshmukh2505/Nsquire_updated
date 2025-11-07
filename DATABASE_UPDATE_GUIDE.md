# Database Update Guide

## How to Update Cutoff Data Each Year

This guide explains how to update your SQL database with new cutoff data from PDF files.

## Prerequisites

- Python 3.x installed
- PyPDF2 library installed (`pip install PyPDF2`)
- SQLAlchemy library installed (`pip install sqlalchemy`)

## Step-by-Step Process

### 1. Get the New Cutoff PDF

Place your new cutoff PDF file in the project root directory. For example:
```
newapp/
├── cutoff_2025.pdf    # New cutoff file
├── colleges.db        # Your database
├── pdf_to_sql_migrator.py
└── ...
```

### 2. Run the Migration Script

Open a terminal in the project directory and run:

```bash
# Basic usage (assumes cutoff.pdf and year 2024)
python3 pdf_to_sql_migrator.py

# Specify custom PDF file and year
python3 pdf_to_sql_migrator.py cutoff_2025.pdf 2025
```

**Command Format:**
```bash
python3 pdf_to_sql_migrator.py [PDF_FILE_PATH] [YEAR]
```

**Parameters:**
- `PDF_FILE_PATH`: Path to your cutoff PDF file (default: `cutoff.pdf`)
- `YEAR`: Academic year for the cutoff data (default: `2024`)

### 3. Monitor the Migration

The script will display real-time progress:

```
================================================================================
PDF to SQL Migration Tool
================================================================================
PDF File: cutoff_2025.pdf
Year: 2025
================================================================================

2024-11-07 12:30:15 - INFO - Starting migration from cutoff_2025.pdf for year 2025
2024-11-07 12:30:16 - INFO - Found 50 colleges in PDF
2024-11-07 12:30:17 - INFO - Processed college 1/50: VJTI Mumbai
2024-11-07 12:30:18 - INFO - Updated cutoff for Computer Engineering (GOPEN): 100 -> 95
...
================================================================================
Migration completed successfully!
Total colleges processed: 50
Total branches processed: 250
Total cutoffs updated: 2500
================================================================================

✅ Migration completed successfully!
The database has been updated with new cutoff data.
```

## What the Migration Script Does

### Automatic Operations:

1. **Finds Existing Colleges**: If a college already exists in the database, it uses the existing record
2. **Creates New Colleges**: If a college is not found, it creates a new entry
3. **Finds Existing Courses**: If a course exists for a college, it reuses it
4. **Creates New Courses**: If a course doesn't exist, it creates a new one
5. **Updates Cutoffs**:
   - If a cutoff exists for a course/year/category, it **updates** the rank
   - If a cutoff doesn't exist, it **creates** a new entry

### Smart Features:

- ✅ **No Duplicates**: Won't create duplicate colleges or courses
- ✅ **Updates Existing Data**: Automatically updates cutoff ranks if they change
- ✅ **Maintains History**: Keeps historical data by storing cutoffs with year
- ✅ **Error Recovery**: If one college fails, continues with the next
- ✅ **Progress Tracking**: Shows real-time progress and logs all operations

## Available Categories in Database

The system supports the following MHT-CET categories:

| Code | Description |
|------|-------------|
| `GOPEN` | General Open Merit |
| `LOPEN` | Ladies Open Merit |
| `GOBCH` | General - Other Backward Class |
| `LOBCH` | Ladies - Other Backward Class |
| `GSCH` | General - Scheduled Caste |
| `LSCH` | Ladies - Scheduled Caste |
| `GSTH` | General - Scheduled Tribe |
| `GNT1H` | General - Nomadic Tribe 1 |
| `GNT2H` | General - Nomadic Tribe 2 |
| `GNT3H` | General - Nomadic Tribe 3 |
| `GVJH` | General - Vimukta Jati |

## PDF Format Requirements

The migration script expects the PDF to follow this format:

```
01002 - College Name
  0100219110 - Branch Name (e.g., Computer Engineering)
    Status: Government/Private
    State Level
    GOPEN    LOPEN    GOBCH    GSCH    ...
    I        123      456      789     ...
             (95.2)   (92.1)   (89.5)  ...
```

### Key Elements:
- College code: 5-digit number (e.g., `01002`)
- Branch code: 10-digit number (e.g., `0100219110`)
- Categories: 4-6 character codes (e.g., `GOPEN`, `GOBCH`)
- Ranks: 4-6 digit numbers
- Percentages: Numbers in parentheses (optional)

## Troubleshooting

### Issue: "Could not extract text from PDF"
**Solution**: Make sure the PDF is not encrypted or corrupted. Try opening it manually first.

### Issue: "No colleges found in PDF"
**Solution**: The PDF format may be different. Check that it follows the expected format (see above).

### Issue: Categories showing 0 results
**Solution**:
1. Check if the category exists in the database:
   ```python
   from models import get_session, Cutoff
   session = get_session()
   categories = session.query(Cutoff.category).distinct().all()
   print([c[0] for c in categories])
   ```
2. Make sure the category code matches exactly (case-sensitive)

### Issue: Migration fails midway
**Solution**: The script commits after each college, so partial progress is saved. Simply run it again - it will skip existing data and continue.

## Verifying the Update

After migration, verify the data:

```python
from models import get_session, College, Course, Cutoff

session = get_session()

# Check total cutoffs
total_cutoffs = session.query(Cutoff).count()
print(f"Total cutoffs in database: {total_cutoffs}")

# Check cutoffs for a specific year
cutoffs_2025 = session.query(Cutoff).filter(Cutoff.year == 2025).count()
print(f"Cutoffs for 2025: {cutoffs_2025}")

# Check available categories
categories = session.query(Cutoff.category).distinct().all()
print(f"Available categories: {[c[0] for c in categories]}")

session.close()
```

## Backup Before Updating

**IMPORTANT**: Always backup your database before running migrations!

```bash
# Create a backup of the database
cp colleges.db colleges_backup_$(date +%Y%m%d).db

# Restore if needed
cp colleges_backup_20241107.db colleges.db
```

## Comparing Old vs New Cutoffs

To see what changed after migration:

```python
from models import get_session, Cutoff

session = get_session()

# Compare cutoffs for same course between years
old_cutoff = session.query(Cutoff).filter(
    Cutoff.year == 2024,
    Cutoff.category == 'GOPEN',
    Cutoff.course_id == 1
).first()

new_cutoff = session.query(Cutoff).filter(
    Cutoff.year == 2025,
    Cutoff.category == 'GOPEN',
    Cutoff.course_id == 1
).first()

if old_cutoff and new_cutoff:
    change = new_cutoff.cutoff_rank - old_cutoff.cutoff_rank
    print(f"Cutoff change: {old_cutoff.cutoff_rank} → {new_cutoff.cutoff_rank} ({change:+d})")

session.close()
```

## Annual Workflow

1. **Backup Database** (before any changes)
   ```bash
   cp colleges.db colleges_backup_$(date +%Y%m%d).db
   ```

2. **Download New Cutoff PDF** (from official source)

3. **Run Migration**
   ```bash
   python3 pdf_to_sql_migrator.py cutoff_2025.pdf 2025
   ```

4. **Verify Data**
   - Check college count
   - Check cutoff counts for new year
   - Test with frontend

5. **Update Frontend** (if needed)
   - Update default year in components
   - Update any year-specific references

6. **Test Application**
   - Test chatbot queries
   - Test rank predictor
   - Test compare colleges

## Support

If you encounter issues:

1. Check the log messages - they provide detailed error information
2. Verify your PDF follows the expected format
3. Check database permissions
4. Ensure all required libraries are installed

For persistent issues, check the logs in the terminal output for specific error messages.
