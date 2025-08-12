"""
Image finding module for locating product images in supplier folders
"""

import os
import glob
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class ImageFinder:
    """Handles finding product images based on supplier and product information"""
    
    SUPPORTED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
    
    def find_image(self, image_folder: str, supplier_name: str, 
                   supplier_part_id: str, supplier_color: str) -> Optional[str]:
        """
        Find product image based on naming pattern: SupplierPartID + SupplierColor.png
        
        Args:
            image_folder: Root folder containing supplier subfolders
            supplier_name: Name of the supplier (subfolder name)
            supplier_part_id: Product part ID
            supplier_color: Product color
            
        Returns:
            Full path to the image file if found, None otherwise
        """
        try:
            # Construct supplier folder path
            supplier_folder = os.path.join(image_folder, supplier_name)
            
            if not os.path.exists(supplier_folder):
                logger.error(f"Supplier folder not found: {supplier_folder}")
                return None
            
            # Create the expected image name pattern
            image_name_base = f"{supplier_part_id}{supplier_color}"
            
            # Try different variations and extensions
            image_variations = [
                f"{supplier_part_id}{supplier_color}",
                f"{supplier_part_id}_{supplier_color}",
                f"{supplier_part_id}-{supplier_color}",
                f"{supplier_part_id} {supplier_color}",
            ]
            
            # Search for the image file
            for variation in image_variations:
                for extension in self.SUPPORTED_EXTENSIONS:
                    image_path = os.path.join(supplier_folder, f"{variation}{extension}")
                    
                    if os.path.exists(image_path):
                        logger.info(f"Found image: {image_path}")
                        return image_path
            
            # If exact match not found, try fuzzy search
            fuzzy_path = self._fuzzy_search(supplier_folder, supplier_part_id, supplier_color)
            if fuzzy_path:
                return fuzzy_path
            
            logger.error(f"Image not found for {supplier_part_id}{supplier_color} in {supplier_folder}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding image: {e}")
            return None
    
    def _fuzzy_search(self, supplier_folder: str, part_id: str, color: str) -> Optional[str]:
        """
        Perform fuzzy search for image files when exact match fails
        
        Args:
            supplier_folder: Path to supplier folder
            part_id: Product part ID
            color: Product color
            
        Returns:
            Path to best matching image file
        """
        try:
            # Get all image files in the folder
            all_images = []
            for ext in self.SUPPORTED_EXTENSIONS:
                pattern = os.path.join(supplier_folder, f"*{ext}")
                all_images.extend(glob.glob(pattern, recursive=False))
            
            if not all_images:
                return None
            
            # Score images based on similarity to expected pattern
            scored_images = []
            for image_path in all_images:
                filename = os.path.basename(image_path)
                filename_lower = filename.lower()
                part_id_lower = part_id.lower()
                color_lower = color.lower()
                
                score = 0
                if part_id_lower in filename_lower:
                    score += 2
                if color_lower in filename_lower:
                    score += 2
                
                # Bonus for exact concatenation
                if f"{part_id_lower}{color_lower}" in filename_lower:
                    score += 3
                
                if score > 0:
                    scored_images.append((score, image_path))
            
            if scored_images:
                # Return the highest scoring image
                scored_images.sort(reverse=True, key=lambda x: x[0])
                best_match = scored_images[0][1]
                logger.info(f"Fuzzy match found: {best_match}")
                return best_match
            
            return None
            
        except Exception as e:
            logger.error(f"Error in fuzzy search: {e}")
            return None
    
    def list_supplier_folders(self, image_folder: str) -> List[str]:
        """
        List all supplier folders in the image directory
        
        Args:
            image_folder: Root image folder path
            
        Returns:
            List of supplier folder names
        """
        try:
            if not os.path.exists(image_folder):
                return []
            
            folders = [f for f in os.listdir(image_folder) 
                      if os.path.isdir(os.path.join(image_folder, f))]
            
            logger.info(f"Found {len(folders)} supplier folders")
            return folders
            
        except Exception as e:
            logger.error(f"Error listing supplier folders: {e}")
            return []
    
    def validate_image_file(self, image_path: str) -> bool:
        """
        Validate that the image file exists and is readable
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if image is valid, False otherwise
        """
        try:
            if not os.path.exists(image_path):
                return False
            
            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                logger.warning(f"Image file is empty: {image_path}")
                return False
            
            # Check extension
            extension = Path(image_path).suffix.lower()
            if extension not in self.SUPPORTED_EXTENSIONS:
                logger.warning(f"Unsupported image format: {extension}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating image file: {e}")
            return False