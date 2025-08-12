# Excel parsing utilities

# Base required columns, allowing synonyms for Supplier Name
REQUIRED_COLUMNS = [
    "Supplier Part ID",
    "Supplier Color",
    "Decoration Code",
    "Decoration Color",
    "Decoration Location",
    "Final Image Name",
    "Location As per Word file",
    "Supplier Name"  # Preferred column name
]

SUPPLIER_NAME_SYNONYMS = [
    "Supplier", "Supplier Folder", "Supplier_Name", "SupplierName"
]

def parse_excel_file(excel_path):
    try:
        try:
            import pandas as pd  # lazy import to avoid hard dependency at module import time
        except ImportError:
            raise RuntimeError("pandas is required to read Excel files. Please install dependencies from requirements.txt")

        df = pd.read_excel(excel_path)

        # Normalize Supplier Name if synonyms exist
        if "Supplier Name" not in df.columns:
            for alt in SUPPLIER_NAME_SYNONYMS:
                if alt in df.columns:
                    df["Supplier Name"] = df[alt]
                    break

        # Validate required columns
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        df = df[REQUIRED_COLUMNS]

        # Drop rows with any crucial missing values
        df.dropna(subset=[
            "Supplier Part ID", "Decoration Code",
            "Final Image Name", "Location As per Word file",
            "Supplier Name"
        ], inplace=True)

        return df.to_dict(orient="records")

    except Exception as e:
        raise RuntimeError(f"Error reading Excel file: {str(e)}")



# # excel_parser.py

# import os
# import pandas as pd

# REQUIRED_COLUMNS = [
#     "Supplier Part ID", "Supplier Color", "Decoration Code",
#     "Decoration Color", "Decoration Location", "Final Image Name",
#     "Location As per Word file"
# ]

# class ExcelParser:
#     def __init__(self, excel_path):
#         self.excel_path = excel_path

#     def read_excel(self):
#         if not os.path.exists(self.excel_path):
#             raise FileNotFoundError(f"Excel file not found: {self.excel_path}")

#         try:
#             df = pd.read_excel(self.excel_path)
#         except Exception as e:
#             raise Exception(f"Failed to read Excel file: {e}")

#         for col in REQUIRED_COLUMNS:
#             if col not in df.columns:
#                 raise ValueError(f"Missing required column: {col}")

#         df = df[REQUIRED_COLUMNS]
#         df.dropna(subset=["Supplier Part ID", "Decoration Code"], inplace=True)

#         return df.to_dict(orient="records")
