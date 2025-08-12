# Photoshop Automation Project

🚀 **Automate logo placement on apparel images using AI (MediaPipe + OpenCV) with Photoshop integration**

This project automates the process of placing logos on apparel images by:
1. Reading product data from Excel files
2. Finding corresponding images and logos
3. Using AI to calculate optimal logo placement coordinates
4. Automating Photoshop to create final images

## 🎯 Features

- **AI-Powered Positioning**: Uses MediaPipe for human pose detection
- **Photoshop Automation**: Integrates with Photoshop 2020 (crack version supported)
- **Batch Processing**: Process multiple products automatically
- **Smart Fallback**: Heuristic positioning when AI detection fails
- **GUI Interface**: User-friendly interface for easy operation
- **Comprehensive Logging**: Detailed error tracking and reporting

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Photoshop 2020 (crack version works)
- Windows/Linux/macOS

### Excel File Format
Your Excel file must contain these columns:
- **Supplier Part ID**: Product identifier
- **Supplier Color**: Color variant
- **Decoration Code**: Logo identifier (matches PDF filename)
- **Decoration Color**: Logo color
- **Decoration Location**: Placement description
- **Final Image Name**: Output filename
- **Location As per Word file**: Placement location (e.g., "RIGHT-CHEST", "FULL-BACK")
- **Supplier Name**: Folder name containing images

## 🚀 Quick Start

### 1. Automated Setup
```bash
# Run the setup script
python3 setup.py
```

### 2. Manual Setup
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Prepare Your Files

#### Folder Structure
```
input/
├── excel_files/
│   └── your_products.xlsx
└── assets/
    ├── logos/
    │   ├── LOGO001.pdf
    │   └── LOGO002.pdf
    ├── SUPPLIER_A/
    │   ├── TSHIRT001_BLACK.png
    │   └── TSHIRT001_WHITE.png
    └── SUPPLIER_B/
        └── TSHIRT002_BLACK.png
```

#### Naming Rules
- **Images**: `[Supplier Part ID]_[Supplier Color].png`
- **Logos**: `[Decoration Code].pdf`
- **Supplier Folders**: Must match "Supplier Name" column exactly

### 4. Run the Application

#### GUI Interface (Recommended)
```bash
python -m gui.interface
```

#### Command Line
```bash
python -m src.main
```

## 📖 Documentation

- **[PROJECT_GUIDE.md](PROJECT_GUIDE.md)**: Complete project overview and features
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)**: Detailed setup instructions and troubleshooting

## 🔧 Configuration

Edit `config/settings.json` to customize:
- Photoshop export settings
- Logo sizes and positioning
- Export resolutions
- File paths

## 🎨 Supported Locations

The system supports various apparel locations:
- **RIGHT-CHEST**, **LEFT-CHEST**: Chest areas
- **FULL-BACK**, **FULL-FRONT**: Full body areas
- **RIGHT-SLEEVE**, **LEFT-SLEEVE**: Sleeve areas
- **RIGHT-BICEP**, **LEFT-BICEP**: Bicep areas
- **RIGHT-HIP**, **LEFT-HIP**: Hip areas
- **RIGHT-CUFF**, **LEFT-CUFF**: Cuff areas
- **RIGHT-COLLAR**, **LEFT-COLLAR**: Collar areas
- And many more...

## 🛠️ Troubleshooting

### Common Issues
1. **Photoshop not found**: Ensure Photoshop is in PATH or specify full path in settings
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Image not found**: Check folder structure and naming conventions
4. **Excel parsing failed**: Verify all required columns are present

### Error Logs
Check `logs/error_log.txt` for detailed error information.

## 📝 Notes

- Photoshop export is enabled by default. Set `enable_photoshop_export: false` in `config/settings.json` to disable.
- PDF logo conversion uses `pdf2image` (Poppler) first, falls back to PyMuPDF if not available.
- The tool places logos using human landmarks; falls back to heuristic positions if AI detection fails.
- Supports crack versions of Photoshop 2020.

## 🤝 Support

- Check the guides in this repository
- Review error logs for troubleshooting
- Test with small batches first
- Ensure all file paths and naming conventions are correct
