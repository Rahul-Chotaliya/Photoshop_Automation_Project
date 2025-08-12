"""
Photoshop automation module for controlling Photoshop 2020 via COM
"""

import os
import sys
import logging
import time
from typing import Optional, Dict
from pathlib import Path

# Windows-specific COM imports
try:
    import win32com.client
    import pythoncom
except ImportError:
    logging.error("pywin32 not installed. Install with: pip install pywin32")
    win32com = None

logger = logging.getLogger(__name__)


class PhotoshopAutomation:
    """Handles Photoshop automation for logo placement and file operations"""
    
    def __init__(self):
        self.app = None
        self.document = None
        self._initialize_photoshop()
    
    def _initialize_photoshop(self):
        """Initialize Photoshop application connection"""
        try:
            if win32com is None:
                raise Exception("pywin32 not available - Windows COM required")
            
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Try to connect to existing Photoshop instance
            try:
                self.app = win32com.client.GetActiveObject("Photoshop.Application")
                logger.info("Connected to existing Photoshop instance")
            except:
                # Start new Photoshop instance
                self.app = win32com.client.Dispatch("Photoshop.Application")
                logger.info("Started new Photoshop instance")
            
            # Make Photoshop visible
            self.app.Visible = True
            
            # Set basic preferences
            self.app.Preferences.RulerUnits = 1  # Pixels
            
        except Exception as e:
            logger.error(f"Failed to initialize Photoshop: {e}")
            logger.error("Make sure Photoshop 2020 is installed and accessible")
            self.app = None
    
    def process_image(self, image_path: str, logo_path: str, 
                     coordinates: Dict, final_name: str) -> bool:
        """
        Main processing function to open image, place logo, and save PSD
        
        Args:
            image_path: Path to the product image
            logo_path: Path to the logo image
            coordinates: Dictionary with placement coordinates
            final_name: Final output filename for PSD
            
        Returns:
            True if processing successful, False otherwise
        """
        try:
            if not self.app:
                logger.error("Photoshop not initialized")
                return False
            
            # Open the product image
            doc = self._open_image(image_path)
            if not doc:
                return False
            
            # Place the logo
            success = self._place_logo(doc, logo_path, coordinates)
            if not success:
                doc.Close(2)  # Close without saving
                return False
            
            # Save as PSD
            success = self._save_as_psd(doc, final_name)
            
            # Close document
            doc.Close(2)  # Close without saving (already saved)
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            # Try to close any open document
            try:
                if self.app and self.app.Documents.Count > 0:
                    self.app.ActiveDocument.Close(2)
            except:
                pass
            return False
    
    def _open_image(self, image_path: str):
        """
        Open image file in Photoshop
        
        Args:
            image_path: Path to image file
            
        Returns:
            Document object or None
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Convert to absolute path
            abs_path = os.path.abspath(image_path)
            
            # Open the file
            doc = self.app.Open(abs_path)
            logger.info(f"Opened image in Photoshop: {abs_path}")
            
            return doc
            
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            return None
    
    def _place_logo(self, doc, logo_path: str, coordinates: Dict) -> bool:
        """
        Place logo on the image at specified coordinates
        
        Args:
            doc: Photoshop document object
            logo_path: Path to logo image
            coordinates: Placement coordinates dictionary
            
        Returns:
            True if placement successful
        """
        try:
            if not os.path.exists(logo_path):
                logger.error(f"Logo file not found: {logo_path}")
                return False
            
            abs_logo_path = os.path.abspath(logo_path)
            
            # Place the logo file
            placed_layer = doc.ArtLayers.Add()
            placed_layer.Name = "Logo"
            
            # Use place method to insert logo
            # Note: Photoshop COM doesn't have direct "place" equivalent
            # We'll use a workaround by opening logo as new document and copying
            
            # Open logo as separate document
            logo_doc = self.app.Open(abs_logo_path)
            
            # Select all and copy
            logo_doc.Selection.SelectAll()
            logo_doc.Selection.Copy()
            
            # Close logo document
            logo_doc.Close(2)
            
            # Paste into main document
            doc.Paste()
            
            # Get the pasted layer (should be the active layer)
            logo_layer = doc.ActiveLayer
            logo_layer.Name = "Logo"
            
            # Move to specified coordinates
            x_offset = coordinates['x']
            y_offset = coordinates['y']
            
            # Translate the layer
            logo_layer.Translate(x_offset, y_offset)
            
            # Resize if needed (optional)
            target_width = coordinates.get('width')
            target_height = coordinates.get('height')
            
            if target_width and target_height:
                # Get current bounds
                bounds = logo_layer.Bounds
                current_width = bounds[2] - bounds[0]
                current_height = bounds[3] - bounds[1]
                
                # Calculate scale factors
                scale_x = (target_width / current_width) * 100
                scale_y = (target_height / current_height) * 100
                
                # Resize layer
                logo_layer.Resize(scale_x, scale_y)
            
            logger.info(f"Logo placed at coordinates: x={x_offset}, y={y_offset}")
            return True
            
        except Exception as e:
            logger.error(f"Error placing logo: {e}")
            return False
    
    def _save_as_psd(self, doc, final_name: str) -> bool:
        """
        Save document as PSD file
        
        Args:
            doc: Photoshop document object
            final_name: Output filename
            
        Returns:
            True if save successful
        """
        try:
            # Ensure the filename has .psd extension
            if not final_name.lower().endswith('.psd'):
                final_name += '.psd'
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.getcwd(), 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # Full output path
            output_path = os.path.join(output_dir, final_name)
            abs_output_path = os.path.abspath(output_path)
            
            # Create Photoshop save options
            psd_options = win32com.client.Dispatch("Photoshop.PhotoshopSaveOptions")
            psd_options.EmbedColorProfile = True
            psd_options.AlphaChannels = True
            psd_options.Layers = True
            psd_options.SpotColors = True
            
            # Save the document
            doc.SaveAs(abs_output_path, psd_options, True)
            
            logger.info(f"Saved PSD file: {abs_output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving PSD: {e}")
            return False
    
    def close_photoshop(self):
        """Close Photoshop application"""
        try:
            if self.app:
                # Close all open documents
                while self.app.Documents.Count > 0:
                    self.app.Documents[0].Close(2)
                
                # Quit Photoshop (optional - comment out if you want to keep it open)
                # self.app.Quit()
                
                logger.info("Closed Photoshop documents")
        except Exception as e:
            logger.warning(f"Error closing Photoshop: {e}")
        finally:
            # Uninitialize COM
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    def create_new_document(self, width: int = 1920, height: int = 1080) -> bool:
        """
        Create a new document in Photoshop
        
        Args:
            width: Document width in pixels
            height: Document height in pixels
            
        Returns:
            True if creation successful
        """
        try:
            if not self.app:
                return False
            
            # Create new document
            doc = self.app.Documents.Add(width, height, 72, "New Document", 1)
            logger.info(f"Created new document: {width}x{height}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating new document: {e}")
            return False
    
    def get_photoshop_info(self) -> Dict:
        """
        Get information about Photoshop application
        
        Returns:
            Dictionary with Photoshop info
        """
        try:
            if not self.app:
                return {"status": "not_connected"}
            
            info = {
                "status": "connected",
                "version": str(self.app.Version),
                "name": str(self.app.Name),
                "open_documents": self.app.Documents.Count,
                "preferences_ruler_units": self.app.Preferences.RulerUnits
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting Photoshop info: {e}")
            return {"status": "error", "error": str(e)}
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'app') and self.app:
                # Close any open documents but don't quit Photoshop
                while self.app.Documents.Count > 0:
                    self.app.Documents[0].Close(2)
        except:
            pass