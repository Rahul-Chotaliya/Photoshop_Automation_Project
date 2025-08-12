#!/usr/bin/env python3
"""
Image Processing and Logo Placement Automation System

This script processes Excel files containing product information and automates
the placement of logos on product images using OpenCV, MediaPipe, and Photoshop.
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd
from typing import Dict, List, Tuple, Optional

# Import custom modules
from src.excel_processor import ExcelProcessor
from src.image_finder import ImageFinder
from src.logo_extractor import LogoExtractor
from src.coordinate_detector import CoordinateDetector
from src.photoshop_automation import PhotoshopAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ImageProcessingPipeline:
    """Main pipeline for processing images with logo placement"""
    
    def __init__(self, excel_path: str, image_folder: str, logo_folder: str):
        self.excel_path = excel_path
        self.image_folder = image_folder
        self.logo_folder = logo_folder
        
        # Initialize processors
        self.excel_processor = ExcelProcessor()
        self.image_finder = ImageFinder()
        self.logo_extractor = LogoExtractor()
        self.coordinate_detector = CoordinateDetector()
        self.photoshop_automation = PhotoshopAutomation()
        
    def process_all_rows(self):
        """Process all rows in the Excel file"""
        try:
            # Read Excel file
            logger.info(f"Reading Excel file: {self.excel_path}")
            df = self.excel_processor.read_excel(self.excel_path)
            
            total_rows = len(df)
            logger.info(f"Found {total_rows} rows to process")
            
            # Process each row
            for index, row in df.iterrows():
                logger.info(f"Processing row {index + 1}/{total_rows}")
                self.process_single_row(row, index + 1)
                
        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}")
            raise
            
    def process_single_row(self, row: pd.Series, row_number: int):
        """Process a single row from the Excel file"""
        try:
            # Extract data from row
            supplier_part_id = row['Supplier Part ID']
            supplier_color = row['Supplier Color']
            decoration_code = row['Decoration Code']
            decoration_location = row['Decoration Location']
            location_as_per_word = row['Location As per Word']
            supplier_name = row['Supplier Name']
            final_image_name = row['Final Image Name']
            
            logger.info(f"Processing: {supplier_part_id} - {supplier_color}")
            
            # Step 1: Find the product image
            image_path = self.image_finder.find_image(
                self.image_folder, 
                supplier_name, 
                supplier_part_id, 
                supplier_color
            )
            
            if not image_path:
                logger.error(f"Image not found for {supplier_part_id} - {supplier_color}")
                return
                
            # Step 2: Extract logo from PDF
            logo_path = self.logo_extractor.extract_logo(
                self.logo_folder, 
                decoration_code
            )
            
            if not logo_path:
                logger.error(f"Logo not found for decoration code: {decoration_code}")
                return
                
            # Step 3: Detect coordinates for logo placement
            coordinates = self.coordinate_detector.detect_placement_coordinates(
                image_path, 
                logo_path, 
                decoration_location,
                location_as_per_word
            )
            
            if not coordinates:
                logger.error(f"Could not detect coordinates for {supplier_part_id}")
                return
                
            # Step 4: Automate Photoshop to place logo and save
            success = self.photoshop_automation.process_image(
                image_path,
                logo_path,
                coordinates,
                final_image_name
            )
            
            if success:
                logger.info(f"Successfully processed row {row_number}: {final_image_name}")
            else:
                logger.error(f"Failed to process row {row_number}")
                
        except Exception as e:
            logger.error(f"Error processing row {row_number}: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: python main.py <excel_file> <image_folder> <logo_folder>")
        print("Example: python main.py data.xlsx ./images ./logos")
        sys.exit(1)
        
    excel_path = sys.argv[1]
    image_folder = sys.argv[2]
    logo_folder = sys.argv[3]
    
    # Validate paths
    if not os.path.exists(excel_path):
        logger.error(f"Excel file not found: {excel_path}")
        sys.exit(1)
        
    if not os.path.exists(image_folder):
        logger.error(f"Image folder not found: {image_folder}")
        sys.exit(1)
        
    if not os.path.exists(logo_folder):
        logger.error(f"Logo folder not found: {logo_folder}")
        sys.exit(1)
    
    # Create pipeline and process
    pipeline = ImageProcessingPipeline(excel_path, image_folder, logo_folder)
    pipeline.process_all_rows()
    
    logger.info("Processing completed!")


if __name__ == "__main__":
    main()