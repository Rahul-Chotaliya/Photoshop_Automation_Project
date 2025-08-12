# 🎯 Photoshop Automation Project - Complete User Guide

## 📋 **Project Overview**

This project automates the process of placing logos on apparel images using AI-powered coordinate detection and Photoshop automation. It processes Excel files containing product information and automatically places logos at optimal positions.

## 🚀 **Quick Start Guide**

### Step 1: Install Dependencies

```bash
# Install required Python packages
pip3 install pandas openpyxl opencv-python pillow pdf2image PyMuPDF

# For Windows users (Photoshop automation)
pip3 install pywin32
```

### Step 2: Prepare Your Files

#### A. Excel File Structure
Create an Excel file with these required columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| `Supplier Part ID` | Product identifier | `TSH001` |
| `Supplier Color` | Product color | `Black` |
| `Decoration Code` | Logo identifier | `LOGO001` |
| `Decoration Color` | Logo color | `White` |
| `Decoration Location` | Placement description | `Front` |
| `Final Image Name` | Output filename | `TSH001_Black_Front.jpg` |
| `Location As per Word file` | Placement location | `FULL-FRONT` |
| `Supplier Name` | Folder name | `SupplierA` |

#### B. Folder Structure
Organize your files as follows:

```
input/
├── excel_files/
│   └── your_excel_file.xlsx
└── assets/
    ├── logos/
    │   ├── LOGO001.pdf
    │   ├── LOGO002.png
    │   └── ...
    ├── SupplierA/
    │   ├── TSH001 Black.png
    │   ├── TSH002 White.jpg
    │   └── ...
    ├── SupplierB/
    │   ├── CAP001 Red.png
    │   └── ...
    └── ...
```

#### C. File Naming Conventions

**Product Images:**
- Format: `{Supplier Part ID} {Supplier Color}.{ext}`
- Examples: `TSH001 Black.png`, `CAP001 Red.jpg`
- Supported formats: JPG, JPEG, PNG

**Logo Files:**
- Format: `{Decoration Code}.{ext}`
- Examples: `LOGO001.pdf`, `LOGO002.png`
- Supported formats: PDF (first page), PNG, JPG, JPEG

### Step 3: Run the Application

#### Option A: GUI Interface (Recommended)
```bash
python3 -m gui.interface
```

#### Option B: Command Line
```bash
python3 src/main.py
```

#### Option C: Demo Mode
```bash
python3 demo_simple.py
```

## 🔧 **Configuration**

Edit `config/settings.json` to customize settings:

```json
{
  "input_excel_folder": "./input/excel_files/",
  "input_assets_folder": "./input/assets/",
  "output_folder": "./output/",
  "thumbnail_folder": "./output/thumbnails/",
  "default_logo_width": 150,
  "enable_photoshop_export": false,
  "photoshop_path": "Photoshop",
  "poppler_path": ""
}
```

### Key Settings:

- **`default_logo_width`**: Logo size in pixels (default: 150)
- **`enable_photoshop_export`**: Enable Photoshop automation (Windows only)
- **`photoshop_path`**: Path to Photoshop executable
- **`poppler_path`**: Path to Poppler for PDF conversion

## 📊 **How the System Works**

### Step 1: File Processing
1. **Excel Parsing**: Reads and validates Excel file
2. **Image Discovery**: Finds product images using pattern matching
3. **Logo Loading**: Extracts logos from PDF files or loads image files

### Step 2: AI Coordinate Detection
1. **Human Pose Detection**: Uses MediaPipe to detect body landmarks
2. **Location Analysis**: Analyzes placement location (FULL-FRONT, FULL-BACK, etc.)
3. **Coordinate Calculation**: Determines optimal logo placement position
4. **Fallback Positioning**: Uses heuristic positioning if AI detection fails

### Step 3: Image Processing
1. **Logo Resizing**: Resizes logo to specified width while maintaining aspect ratio
2. **Background Removal**: Removes white backgrounds from logos
3. **Image Merging**: Blends logo onto product image with alpha transparency

### Step 4: Photoshop Automation (Optional)
1. **Document Creation**: Opens new Photoshop document with product image
2. **Logo Placement**: Places logo as separate layer at detected coordinates
3. **File Export**: Saves as PSD and JPG formats
4. **Batch Processing**: Automatically processes next row

## 🎨 **Supported Placement Locations**

The system recognizes these placement locations:

| Location | Description | Position |
|----------|-------------|----------|
| `FULL-FRONT` | Front center | Upper center of apparel |
| `FULL-BACK` | Back center | Center back area |
| `LEFT-CHEST` | Left chest | Left upper chest |
| `RIGHT-CHEST` | Right chest | Right upper chest |
| `LEFT-SLEEVE` | Left sleeve | Left sleeve area |
| `RIGHT-SLEEVE` | Right sleeve | Right sleeve area |

## 🛠️ **Troubleshooting**

### Common Issues and Solutions

#### 1. "Image not found" Error
**Problem**: System can't find product images
**Solution**: 
- Check image filename matches: `{Supplier Part ID} {Supplier Color}.{ext}`
- Verify supplier folder exists in `input/assets/`
- Ensure image file extension is supported (JPG, JPEG, PNG)

#### 2. "Logo file not found" Error
**Problem**: System can't find logo files
**Solution**:
- Ensure logo filename matches: `{Decoration Code}.pdf` or `{Decoration Code}.{ext}`
- Check logo is in `input/assets/logos/` folder
- Verify logo file format is supported

#### 3. Photoshop Automation Fails
**Problem**: Photoshop integration doesn't work
**Solution**:
- Verify Photoshop 2020 is installed and in PATH
- Set `enable_photoshop_export: true` in settings.json
- Windows only: Ensure pywin32 is installed
- Check Photoshop executable path in settings

#### 4. PDF Logo Conversion Issues
**Problem**: PDF logos don't load properly
**Solution**:
- Install Poppler for better PDF support
- Set `poppler_path` in settings.json
- System automatically falls back to PyMuPDF if needed

#### 5. Poor Logo Placement
**Problem**: Logos are placed in wrong positions
**Solution**:
- Check `Location As per Word file` column values
- Ensure product images contain human figures for AI detection
- System falls back to heuristic positioning if AI fails

### Error Logging

All errors are logged to `logs/error_log.txt`. Check this file for detailed error information:

```bash
tail -f logs/error_log.txt
```

## 📁 **Output Structure**

After processing, you'll find:

```
output/
├── TSH001_Black_Front.jpg
├── TSH002_White_Back.jpg
├── CAP001_Red_Front.jpg
├── BAG001_Blue_Side.jpg
└── thumbnails/
    ├── TSH001_Black_Front.jpg
    ├── TSH002_White_Back.jpg
    ├── CAP001_Red_Front.jpg
    └── BAG001_Blue_Side.jpg
```

## 🔄 **Batch Processing**

The system automatically processes all rows in your Excel file:

1. **Sequential Processing**: Processes one row at a time
2. **Error Handling**: Continues processing even if one job fails
3. **Progress Tracking**: Shows real-time progress updates
4. **Logging**: Records all operations and errors

## 🎯 **Advanced Features**

### Custom Logo Sizing
Modify `default_logo_width` in settings.json to change logo size:

```json
{
  "default_logo_width": 200
}
```

### Multiple Export Formats
The system can export in multiple formats:
- **JPG**: Final output images
- **PSD**: Photoshop files (when Photoshop export is enabled)
- **Thumbnails**: Preview images

### Background Removal
The system automatically removes white backgrounds from logos for better blending.

### Alpha Channel Support
Supports logos with transparency (PNG with alpha channel).

## 📞 **Getting Help**

### 1. Check Logs
```bash
cat logs/error_log.txt
```

### 2. Test Setup
```bash
python3 test_project.py
```

### 3. Run Demo
```bash
python3 demo_simple.py
```

### 4. Verify Files
- Check Excel file format and column names
- Verify image and logo file naming
- Ensure all required folders exist

## 🚀 **Performance Tips**

1. **Image Optimization**: Use appropriately sized images (1200x1800px recommended)
2. **Batch Size**: Process Excel files with 50-100 rows for optimal performance
3. **File Formats**: Use PNG for logos with transparency, JPG for photos
4. **Storage**: Ensure sufficient disk space for output files

## 🔒 **Security Notes**

- The system only reads files from specified input folders
- No data is sent to external servers
- All processing happens locally on your machine
- Log files may contain file paths - review before sharing

---

**Note**: This project requires Photoshop 2020 for full automation. Without Photoshop, it will still generate images using OpenCV but won't create PSD files.