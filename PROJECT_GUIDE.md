# Photoshop Automation Project - Complete Guide

## Project Overview
This project automates the process of placing logos on apparel images using AI (MediaPipe + OpenCV) with Photoshop integration. It processes Excel files containing product information and automatically places logos at optimal positions on images.

## How It Works (Step by Step)

### Step 1: Input Processing
- **Excel File**: Contains product data with columns like Supplier Part ID, Supplier Color, Decoration Code, etc.
- **Image Folder**: Contains subfolders named after Supplier Names, with images named as "Supplier Part ID + Supplier Color.png"
- **Logo Folder**: Contains PDF logos named as "Decoration Code.pdf"

### Step 2: AI-Powered Logo Positioning
- Uses **MediaPipe** for human pose detection to find optimal logo placement
- Uses **OpenCV** for image processing and coordinate calculation
- Automatically determines the best position for logo placement based on the "Location As per Word file" column

### Step 3: Photoshop Automation
- Opens **Photoshop 2020** (crack version supported)
- Creates new documents for each product
- Places images and logos at calculated coordinates
- Saves final PSD files with names from "Final Image Name" column

## Required Excel Columns

Your Excel file must contain these columns:
- **Supplier Part ID**: Product identifier
- **Supplier Color**: Color variant
- **Decoration Code**: Logo identifier (matches PDF filename)
- **Decoration Color**: Logo color
- **Decoration Location**: Placement description
- **Final Image Name**: Output filename
- **Location As per Word file**: Placement location (e.g., "RIGHT-CHEST", "FULL-BACK")
- **Supplier Name**: Folder name containing images

## Folder Structure

```
project/
├── input/
│   ├── excel_files/          # Put your Excel files here
│   └── assets/
│       ├── logos/            # Put your PDF logos here
│       └── [Supplier Name]/  # Image folders named after suppliers
│           ├── [PartID_Color1].png
│           ├── [PartID_Color2].png
│           └── ...
├── output/                   # Final processed images
├── logs/                     # Error logs
└── templates/                # Location templates
```

## Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Prepare Your Files

#### Excel File Format
Create an Excel file with these columns:
| Supplier Part ID | Supplier Color | Decoration Code | Decoration Color | Decoration Location | Final Image Name | Location As per Word file | Supplier Name |
|------------------|----------------|-----------------|------------------|-------------------|------------------|---------------------------|---------------|
| TSHIRT001 | BLACK | LOGO001 | WHITE | Chest | TSHIRT001_BLACK_LOGO | RIGHT-CHEST | SUPPLIER_A |
| TSHIRT002 | WHITE | LOGO002 | BLACK | Back | TSHIRT002_WHITE_LOGO | FULL-BACK | SUPPLIER_B |

#### Image Organization
```
input/assets/
├── SUPPLIER_A/
│   ├── TSHIRT001_BLACK.png
│   └── TSHIRT001_WHITE.png
└── SUPPLIER_B/
    ├── TSHIRT002_BLACK.png
    └── TSHIRT002_WHITE.png
```

#### Logo Organization
```
input/assets/logos/
├── LOGO001.pdf
└── LOGO002.pdf
```

### 3. Configure Settings

Edit `config/settings.json`:
```json
{
  "enable_photoshop_export": true,
  "photoshop_path": "Photoshop",
  "default_logo_width": 150
}
```

### 4. Run the Application

#### Option A: GUI Interface (Recommended)
```bash
python -m gui.interface
```

#### Option B: Command Line
```bash
python -m src.main
```

## Supported Location Types

The system supports various placement locations:
- **RIGHT-CHEST**: Right chest area
- **LEFT-CHEST**: Left chest area
- **FULL-BACK**: Full back area
- **FULL-FRONT**: Full front area
- **RIGHT-SLEEVE**: Right sleeve
- **LEFT-SLEEVE**: Left sleeve
- **RIGHT-BICEP**: Right bicep
- **LEFT-BICEP**: Left bicep
- **RIGHT-HIP**: Right hip
- **LEFT-HIP**: Left hip
- **RIGHT-CUFF**: Right cuff
- **LEFT-CUFF**: Left cuff
- **RIGHT-COLLAR**: Right collar
- **LEFT-COLLAR**: Left collar
- And many more...

## Features

### AI-Powered Positioning
- **MediaPipe Integration**: Uses human pose detection for accurate logo placement
- **Smart Fallback**: If AI detection fails, uses heuristic positioning
- **Multiple Location Support**: Handles various apparel locations

### Photoshop Automation
- **Batch Processing**: Processes multiple products automatically
- **Coordinate Calculation**: Automatically calculates optimal logo positions
- **PSD Export**: Saves final images as Photoshop files
- **Error Handling**: Continues processing even if individual items fail

### File Management
- **Flexible Input**: Supports various Excel formats and column names
- **Organized Output**: Creates structured output folders
- **Logging**: Comprehensive error logging and tracking

## Troubleshooting

### Common Issues

1. **Photoshop Not Found**
   - Ensure Photoshop is installed and in PATH
   - Check `photoshop_path` in settings.json

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - For PDF processing, install Poppler (optional)

3. **Excel Format Issues**
   - Ensure all required columns are present
   - Check for missing values in key columns

4. **Image Not Found**
   - Verify folder structure matches Supplier Name
   - Check image naming format: "PartID_Color.png"

### Error Logs
Check `logs/error_log.txt` for detailed error information.

## Advanced Configuration

### Custom Logo Sizes
Edit `default_logo_width` in settings.json to adjust logo size.

### Export Resolution
Configure export resolution for different product types:
```json
"export_resolution": {
  "shirt": [1200, 1800],
  "cap": [1200, 1200],
  "bag": [1200, 1200]
}
```

### Template Customization
Add custom location templates to `templates/word_location_templates/` folder.

## Performance Tips

1. **Batch Processing**: Process multiple products at once for efficiency
2. **Image Optimization**: Use appropriately sized images for faster processing
3. **Memory Management**: Close other applications when processing large batches
4. **SSD Storage**: Use SSD for faster file I/O operations

## Support

- Check logs for detailed error information
- Verify file paths and naming conventions
- Ensure all dependencies are properly installed
- Test with a small batch first before processing large datasets