# Image Processing and Logo Placement Automation System

This project automates the process of placing logos on product images using Excel data, OpenCV/MediaPipe for coordinate detection, and Photoshop 2020 for final editing.

## Project Overview

The system processes Excel files containing product information and automatically:
1. Finds product images based on supplier and product details
2. Extracts logos from PDF files
3. Uses AI-powered coordinate detection to find optimal logo placement
4. Automates Photoshop to place logos and save as PSD files

## Requirements

### Software Requirements
- **Windows OS** (required for Photoshop COM automation)
- **Adobe Photoshop 2020** (cracked version as specified)
- **Python 3.8+**

### Python Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### System Dependencies
- **Poppler** (for PDF processing) - Download from: https://poppler.freedesktop.org/
- **Visual C++ Redistributable** (usually included with Windows)

## Project Structure

```
workspace/
├── main.py                 # Main orchestration script
├── requirements.txt        # Python dependencies
├── src/                   # Source modules
│   ├── __init__.py
│   ├── excel_processor.py     # Excel file handling
│   ├── image_finder.py        # Image location logic
│   ├── logo_extractor.py      # PDF logo extraction
│   ├── coordinate_detector.py # AI-powered placement detection
│   └── photoshop_automation.py # Photoshop COM automation
├── output/                # Generated PSD files (created automatically)
└── processing.log         # Application logs
```

## Excel File Format

Your Excel file must contain the following columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| Supplier Part ID | Product identifier | "ABC123" |
| Supplier Color | Product color | "Red" |
| Decoration Code | Logo identifier | "LOGO001" |
| Decoration Location | Placement area | "Chest" |
| Location As per Word | Text description | "Front center" |
| Supplier Name | Supplier folder name | "SupplierABC" |
| Final Image Name | Output PSD filename | "Product_Final" |

## Folder Structure Requirements

### Image Folder Structure
```
images/
├── SupplierABC/
│   ├── ABC123Red.png
│   ├── ABC123Blue.png
│   └── ...
├── SupplierXYZ/
│   ├── XYZ456Green.png
│   └── ...
```

**Image Naming Convention**: `{SupplierPartID}{SupplierColor}.png`

### Logo Folder Structure
```
logos/
├── LOGO001.pdf
├── LOGO002.pdf
└── ...
```

**Logo Naming Convention**: `{DecorationCode}.pdf`

## Usage

### Basic Usage
```bash
python main.py <excel_file> <image_folder> <logo_folder>
```

### Example
```bash
python main.py data.xlsx ./images ./logos
```

### Step-by-Step Process

1. **Prepare your data**:
   - Create Excel file with required columns
   - Organize images in supplier subfolders
   - Place logo PDFs in logos folder

2. **Start Photoshop 2020**:
   - Launch Photoshop before running the script
   - Or let the script launch it automatically

3. **Run the processing script**:
   ```bash
   python main.py your_data.xlsx ./images ./logos
   ```

4. **Monitor progress**:
   - Check console output for real-time progress
   - Review `processing.log` for detailed logs
   - Find output PSD files in `./output/` folder

## Features

### Image Processing
- **Smart Image Finding**: Fuzzy matching for image files
- **Multiple Format Support**: PNG, JPG, BMP, TIFF
- **Supplier Organization**: Automatic navigation to supplier subfolders

### Logo Extraction
- **PDF Processing**: Extracts first page from PDF logos
- **High Quality**: 300 DPI extraction for crisp logos
- **Fallback Methods**: Multiple extraction libraries for reliability

### AI-Powered Placement
- **MediaPipe Integration**: Human pose and feature detection
- **OpenCV Analysis**: Edge detection and visual complexity analysis
- **Location-Based Logic**: Intelligent placement based on text descriptions
- **Placement Options**:
  - Chest placement (pose-aware)
  - Sleeve placement (arm detection)
  - Collar placement
  - Pocket placement
  - Smart placement (complexity-based)

### Photoshop Automation
- **COM Integration**: Direct control of Photoshop 2020
- **Layer Management**: Proper layer creation and naming
- **Coordinate Placement**: Precise positioning
- **PSD Export**: Maintains layers and transparency

## Configuration

### Coordinate Detection Settings
Edit `src/coordinate_detector.py` to adjust:
- Detection confidence levels
- Placement algorithms
- Size scaling factors

### Photoshop Settings
Edit `src/photoshop_automation.py` to modify:
- Output resolution
- Layer blending modes
- Save options

## Troubleshooting

### Common Issues

1. **"Photoshop not found" Error**:
   - Ensure Photoshop 2020 is installed
   - Check Windows COM registration
   - Run as Administrator if needed

2. **"PDF extraction failed" Error**:
   - Install Poppler utilities
   - Check PDF file integrity
   - Verify file permissions

3. **"Image not found" Error**:
   - Check folder structure
   - Verify image naming convention
   - Enable fuzzy search debugging

4. **COM Initialization Error**:
   - Install pywin32: `pip install pywin32`
   - Run: `python Scripts/pywin32_postinstall.py -install`

### Performance Optimization

- **Batch Processing**: Process multiple rows efficiently
- **Memory Management**: Automatic cleanup of temporary files
- **Error Recovery**: Continue processing after individual failures

## Logging

The system provides comprehensive logging:
- **Console Output**: Real-time progress updates
- **File Logging**: Detailed logs in `processing.log`
- **Error Tracking**: Full error traces for debugging

## API Reference

### Main Classes

#### `ImageProcessingPipeline`
Main orchestration class that coordinates all processing steps.

#### `ExcelProcessor`
Handles Excel file reading and validation.

#### `ImageFinder`
Locates product images using various naming patterns.

#### `LogoExtractor`
Extracts logos from PDF files with multiple fallback methods.

#### `CoordinateDetector`
AI-powered logo placement detection using OpenCV and MediaPipe.

#### `PhotoshopAutomation`
Controls Photoshop 2020 via COM for final image processing.

## License

This project is for internal use with your existing Photoshop 2020 installation.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files for detailed error information
3. Ensure all dependencies are properly installed
4. Verify Photoshop 2020 accessibility
