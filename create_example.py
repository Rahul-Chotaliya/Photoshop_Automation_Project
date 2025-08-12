#!/usr/bin/env python3
"""
Create example Excel file without requiring pandas initially installed
"""

def create_example_csv():
    """Create example CSV file that can be opened in Excel"""
    data = [
        ["Supplier Part ID", "Supplier Color", "Decoration Code", "Decoration Location", "Location As per Word", "Supplier Name", "Final Image Name"],
        ["ABC123", "Red", "LOGO001", "Chest", "Front center", "SupplierABC", "Product_ABC123_Red_Final"],
        ["ABC124", "Blue", "LOGO002", "Sleeve", "Left arm", "SupplierABC", "Product_ABC124_Blue_Final"],
        ["XYZ456", "Green", "LOGO001", "Back", "Upper back", "SupplierXYZ", "Product_XYZ456_Green_Final"],
        ["XYZ457", "Black", "LOGO003", "Collar", "Neck area", "SupplierXYZ", "Product_XYZ457_Black_Final"],
        ["DEF789", "White", "LOGO002", "Pocket", "Left chest pocket", "SupplierDEF", "Product_DEF789_White_Final"]
    ]
    
    with open("example_data.csv", "w", newline='') as f:
        for row in data:
            f.write(",".join([f'"{item}"' for item in row]) + "\n")
    
    print("✅ Created example_data.csv")
    print("   You can open this in Excel and save as .xlsx if needed")

def create_directory_structure():
    """Create sample directory structure"""
    import os
    
    directories = [
        "sample_data/images/SupplierABC",
        "sample_data/images/SupplierXYZ", 
        "sample_data/images/SupplierDEF",
        "sample_data/logos",
        "output"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create sample README files
    readme_content = """# Sample Data Structure

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
"""
    
    with open("sample_data/README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created sample_data/README.md")

if __name__ == "__main__":
    print("🚀 Creating example data and structure...")
    create_example_csv()
    create_directory_structure()
    print("\n✅ Setup complete! Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run setup: python setup.py") 
    print("3. Add your images and logos to sample_data folders")
    print("4. Run: python main.py example_data.csv sample_data/images sample_data/logos")