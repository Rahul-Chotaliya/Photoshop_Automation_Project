"""
Excel file processing module for reading product data
"""

import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ExcelProcessor:
    """Handles reading and validation of Excel files"""
    
    REQUIRED_COLUMNS = [
        'Supplier Part ID',
        'Supplier Color', 
        'Decoration Code',
        'Decoration Location',
        'Location As per Word',
        'Supplier Name',
        'Final Image Name'
    ]
    
    def read_excel(self, excel_path: str) -> pd.DataFrame:
        """
        Read Excel file and validate required columns
        
        Args:
            excel_path: Path to the Excel file
            
        Returns:
            DataFrame with validated data
            
        Raises:
            ValueError: If required columns are missing
            FileNotFoundError: If Excel file doesn't exist
        """
        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            logger.info(f"Successfully read Excel file with {len(df)} rows")
            
            # Validate required columns
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Remove rows with missing critical data
            original_count = len(df)
            df = df.dropna(subset=['Supplier Part ID', 'Supplier Color', 'Decoration Code', 'Supplier Name'])
            
            if len(df) < original_count:
                logger.warning(f"Removed {original_count - len(df)} rows with missing critical data")
            
            # Clean string columns
            string_columns = ['Supplier Part ID', 'Supplier Color', 'Decoration Code', 'Supplier Name']
            for col in string_columns:
                df[col] = df[col].astype(str).str.strip()
            
            logger.info(f"Excel validation complete. Processing {len(df)} valid rows")
            return df
            
        except FileNotFoundError:
            logger.error(f"Excel file not found: {excel_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            raise
    
    def validate_row_data(self, row: pd.Series) -> bool:
        """
        Validate individual row data
        
        Args:
            row: Pandas Series representing a row
            
        Returns:
            True if row is valid, False otherwise
        """
        try:
            # Check for empty values in critical fields
            critical_fields = ['Supplier Part ID', 'Supplier Color', 'Decoration Code', 'Supplier Name']
            
            for field in critical_fields:
                if pd.isna(row[field]) or str(row[field]).strip() == '':
                    logger.warning(f"Empty value in critical field '{field}' for row")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating row: {e}")
            return False