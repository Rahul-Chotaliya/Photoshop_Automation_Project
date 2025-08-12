# Setup Guide - Photoshop Automation Project

## Prerequisites

### 1. Python Environment
- Python 3.8 or higher
- pip package manager

### 2. Photoshop 2020 (Crack Version)
- Ensure Photoshop is installed and accessible via command line
- The crack version should work fine with this automation

### 3. System Dependencies (Optional)
- **Poppler** (for better PDF processing): Install via package manager
  - Ubuntu/Debian: `sudo apt install poppler-utils`
  - Windows: Download from http://blog.alivate.com.au/poppler-windows/

## Installation Steps

### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 2: Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 3: Configure Settings
Edit `config/settings.json`:
```json
{
  "enable_photoshop_export": true,
  "photoshop_path": "Photoshop",
  "default_logo_width": 150
}
```

### Step 4: Prepare Your Files

#### A. Excel File
Create an Excel file with these exact columns:
- Supplier Part ID
- Supplier Color  
- Decoration Code
- Decoration Color
- Decoration Location
- Final Image Name
- Location As per Word file
- Supplier Name

**Example:**
| Supplier Part ID | Supplier Color | Decoration Code | Decoration Color | Decoration Location | Final Image Name | Location As per Word file | Supplier Name |
|------------------|----------------|-----------------|------------------|-------------------|------------------|---------------------------|---------------|
| TSHIRT001 | BLACK | LOGO001 | WHITE | Chest | TSHIRT001_BLACK_LOGO | RIGHT-CHEST | SUPPLIER_A |

#### B. Folder Structure
```
input/
├── excel_files/
│   └── your_products.xlsx
└── assets/
    ├── logos/
    │   ├── LOGO001.pdf
    │   ├── LOGO002.pdf
    │   └── ...
    ├── SUPPLIER_A/
    │   ├── TSHIRT001_BLACK.png
    │   ├── TSHIRT001_WHITE.png
    │   └── ...
    ├── SUPPLIER_B/
    │   ├── TSHIRT002_BLACK.png
    │   └── ...
    └── ...
```

**Important Naming Rules:**
- **Images**: Must be named as `[Supplier Part ID]_[Supplier Color].png`
- **Logos**: Must be named as `[Decoration Code].pdf`
- **Supplier Folders**: Must match exactly with "Supplier Name" column

### Step 5: Test the Setup

#### Option A: GUI Interface (Recommended)
```bash
python -m gui.interface
```

#### Option B: Command Line
```bash
python -m src.main
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Photoshop not found" Error
**Solution:**
- Ensure Photoshop is in your system PATH
- Or specify the full path in `config/settings.json`:
```json
"photoshop_path": "C:\\Program Files\\Adobe\\Adobe Photoshop 2020\\Photoshop.exe"
```

#### 2. "Missing dependencies" Error
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# If specific packages fail, install individually:
pip install opencv-python mediapipe pandas openpyxl pdf2image PyMuPDF
```

#### 3. "Image not found" Error
**Solution:**
- Check folder structure matches Supplier Name exactly
- Verify image naming: `PartID_Color.png`
- Ensure file extensions are correct (.png, .jpg, etc.)

#### 4. "PDF processing failed" Error
**Solution:**
- Install Poppler for better PDF support
- Or ensure PyMuPDF is installed: `pip install PyMuPDF`

#### 5. "Excel parsing failed" Error
**Solution:**
- Ensure all required columns are present
- Check for missing values in key columns
- Verify Excel file format (.xlsx or .xls)

### Performance Optimization

#### 1. Memory Management
- Close other applications when processing large batches
- Process in smaller batches if memory issues occur

#### 2. File Organization
- Use SSD storage for faster I/O
- Keep image files reasonably sized (1200x1800 max recommended)

#### 3. Batch Processing
- Process multiple products at once for efficiency
- Use the GUI for better progress tracking

## Quick Test

1. **Copy sample files** to the input folders
2. **Run the GUI**: `python -m gui.interface`
3. **Select your files** and click "Start Processing"
4. **Check output folder** for results
5. **Review logs** if any errors occur

## Support

- Check `logs/error_log.txt` for detailed error information
- Verify all file paths and naming conventions
- Test with a small batch first before processing large datasets
- Ensure Photoshop is properly installed and accessible