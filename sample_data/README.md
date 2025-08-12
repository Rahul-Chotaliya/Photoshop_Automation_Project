# Sample Data Structure

## Images Folder
Place your product images in supplier subfolders with naming pattern:
{SupplierPartID}{SupplierColor}.png

Examples:
- ABC123Red.png
- ABC124Blue.png
- XYZ456Green.png

## Logos Folder  
Place your logo PDF files with naming pattern:
{DecorationCode}.pdf

Examples:
- LOGO001.pdf
- LOGO002.pdf
- LOGO003.pdf

## Usage
1. Replace sample folders with your actual data
2. Update example_data.csv with your product information (or convert to .xlsx)
3. Run: python main.py example_data.csv sample_data/images sample_data/logos
