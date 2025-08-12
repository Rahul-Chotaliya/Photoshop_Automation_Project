import pandas as pd
import os

# Create sample data
sample_data = {
    'Supplier Part ID': ['TSH001', 'TSH002', 'CAP001', 'BAG001'],
    'Supplier Color': ['Black', 'White', 'Red', 'Blue'],
    'Decoration Code': ['LOGO001', 'LOGO002', 'LOGO003', 'LOGO004'],
    'Decoration Color': ['White', 'Black', 'White', 'Red'],
    'Decoration Location': ['Front', 'Back', 'Front', 'Side'],
    'Final Image Name': ['TSH001_Black_Front.jpg', 'TSH002_White_Back.jpg', 'CAP001_Red_Front.jpg', 'BAG001_Blue_Side.jpg'],
    'Location As per Word file': ['FULL-FRONT', 'FULL-BACK', 'FULL-FRONT', 'FULL-FRONT'],
    'Supplier Name': ['SupplierA', 'SupplierB', 'SupplierC', 'SupplierD']
}

# Create DataFrame
df = pd.DataFrame(sample_data)

# Create directory if it doesn't exist
os.makedirs('input/excel_files', exist_ok=True)

# Save to Excel
excel_path = 'input/excel_files/sample.xlsx'
df.to_excel(excel_path, index=False)
print(f"Sample Excel file created: {excel_path}")
print("Sample data:")
print(df.to_string())