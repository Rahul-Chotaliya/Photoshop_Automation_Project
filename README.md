# Photoshop Automation Project - Logo Placement System

This project automates the process of placing logos on apparel images using AI-powered coordinate detection and Photoshop automation.

## 🎯 **Project Overview**

This system processes Excel files containing product information and automatically:
1. **Finds product images** in supplier-specific folders
2. **Extracts logos** from PDF files (first page) or image files
3. **Detects optimal logo placement coordinates** using MediaPipe + OpenCV
4. **Automates Photoshop** to place logos at precise locations
5. **Generates final images** with proper naming

## 📋 **Required Excel Columns**

Your Excel file must contain these columns:
- `Supplier Part ID` - Product identifier
- `Supplier Color` - Product color
- `Decoration Code` - Logo identifier (matches PDF/image filename)
- `Decoration Color` - Logo color
- `Decoration Location` - Placement location description
- `Final Image Name` - Output filename
- `Location As per Word file` - Placement location (e.g., "FULL-FRONT", "FULL-BACK")
- `Supplier Name` - Folder name containing product images

## 📁 **Folder Structure**

```
input/
├── excel_files/
│   └── your_excel_file.xlsx
└── assets/
    ├── logos/
    │   ├── LOGO001.pdf
    │   ├── LOGO002.pdf
    │   └── ...
    ├── SupplierA/
    │   ├── TSH001 Black.png
    │   └── ...
    ├── SupplierB/
    │   ├── TSH002 White.jpg
    │   └── ...
    └── ...
output/
├── final_images/
└── thumbnails/
```

## 🚀 **Quick Start**

### 1. Install Dependencies
```bash
# Install required packages
pip3 install pandas openpyxl opencv-python mediapipe pillow pdf2image PyMuPDF

# For Windows users (Photoshop automation)
pip3 install pywin32
```

### 2. Prepare Your Files
- **Excel File**: Place in `input/excel_files/`
- **Product Images**: Organize in `input/assets/{SupplierName}/`
- **Logo Files**: Place in `input/assets/logos/` (PDF or image format)

### 3. Run the Application

#### Option A: GUI Interface (Recommended)
```bash
python3 -m gui.interface
```

#### Option B: Command Line
```bash
python3 src/main.py
```

## 🔧 **Configuration**

Edit `config/settings.json` to customize:
- `default_logo_width`: Logo size in pixels
- `enable_photoshop_export`: Enable/disable Photoshop automation
- `photoshop_path`: Path to Photoshop executable
- `poppler_path`: Path to Poppler for PDF conversion

## 📊 **How It Works**

### Step 1: File Processing
- Reads Excel file and validates required columns
- Finds product images using pattern: `{Supplier Part ID} {Supplier Color}.{ext}`
- Locates logo files using pattern: `{Decoration Code}.pdf` or `{Decoration Code}.{ext}`

### Step 2: AI Coordinate Detection
- Uses MediaPipe to detect human pose landmarks in product images
- Analyzes placement location (FULL-FRONT, FULL-BACK, etc.)
- Calculates optimal coordinates for logo placement
- Falls back to heuristic positioning if AI detection fails

### Step 3: Photoshop Automation
- Opens Photoshop 2020
- Creates new document with product image
- Places logo as separate layer at detected coordinates
- Saves as PSD and JPG formats
- Processes next row automatically

## 🎨 **Supported Image Formats**

- **Product Images**: JPG, JPEG, PNG
- **Logo Files**: PDF (first page), PNG, JPG, JPEG
- **Output**: PSD (Photoshop), JPG (Final)

## 🔍 **Logo Placement Locations**

The system supports these placement locations:
- `FULL-FRONT`: Front center of apparel
- `FULL-BACK`: Back center of apparel
- `LEFT-CHEST`: Left chest area
- `RIGHT-CHEST`: Right chest area
- `LEFT-SLEEVE`: Left sleeve
- `RIGHT-SLEEVE`: Right sleeve

## 🛠️ **Troubleshooting**

### Common Issues:

1. **"Image not found" Error**
   - Check image filename matches: `{Supplier Part ID} {Supplier Color}.{ext}`
   - Verify supplier folder exists in `input/assets/`

2. **"Logo file not found" Error**
   - Ensure logo filename matches: `{Decoration Code}.pdf`
   - Check logo is in `input/assets/logos/` folder

3. **Photoshop Automation Fails**
   - Verify Photoshop 2020 is installed and in PATH
   - Set `enable_photoshop_export: true` in settings.json
   - Windows only: Ensure pywin32 is installed

4. **PDF Logo Conversion Issues**
   - Install Poppler for better PDF support
   - Set `poppler_path` in settings.json
   - System falls back to PyMuPDF if needed

## 📝 **Sample Excel Format**

| Supplier Part ID | Supplier Color | Decoration Code | Final Image Name | Location As per Word file | Supplier Name |
|------------------|----------------|-----------------|------------------|---------------------------|---------------|
| TSH001 | Black | LOGO001 | TSH001_Black_Front.jpg | FULL-FRONT | SupplierA |
| TSH002 | White | LOGO002 | TSH002_White_Back.jpg | FULL-BACK | SupplierB |

## 🎯 **Advanced Features**

- **Batch Processing**: Processes all rows in Excel automatically
- **Error Logging**: Comprehensive error tracking in `logs/`
- **Progress Tracking**: Real-time progress updates
- **Thumbnail Generation**: Creates preview thumbnails
- **Multi-format Support**: Handles various image and PDF formats

## 📞 **Support**

For issues or questions:
1. Check the logs in `logs/error_log.txt`
2. Verify file paths and naming conventions
3. Ensure all dependencies are installed
4. Test with sample files first

---

**Note**: This project requires Photoshop 2020 for full automation. Without Photoshop, it will still generate images using OpenCV but won't create PSD files.
