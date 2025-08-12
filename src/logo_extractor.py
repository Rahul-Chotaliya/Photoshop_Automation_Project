"""
Logo extraction module for extracting logos from PDF files
"""

import os
import logging
from pathlib import Path
from typing import Optional
import tempfile

try:
    from pdf2image import convert_from_path
    import fitz  # PyMuPDF
    from PIL import Image
except ImportError as e:
    logging.error(f"Required libraries not installed: {e}")
    logging.error("Install with: pip install pdf2image PyMuPDF Pillow")

logger = logging.getLogger(__name__)


class LogoExtractor:
    """Handles extraction of logos from PDF files"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="logo_extraction_")
        logger.info(f"Created temporary directory: {self.temp_dir}")
    
    def extract_logo(self, logo_folder: str, decoration_code: str) -> Optional[str]:
        """
        Extract logo from PDF file based on decoration code
        
        Args:
            logo_folder: Root folder containing logo PDF files
            decoration_code: Code to identify the logo file
            
        Returns:
            Path to extracted logo image file, None if extraction fails
        """
        try:
            # Find the PDF file
            pdf_path = self._find_logo_pdf(logo_folder, decoration_code)
            if not pdf_path:
                logger.error(f"Logo PDF not found for decoration code: {decoration_code}")
                return None
            
            # Extract first page as image
            logo_image_path = self._extract_first_page(pdf_path, decoration_code)
            if not logo_image_path:
                logger.error(f"Failed to extract logo from PDF: {pdf_path}")
                return None
            
            logger.info(f"Successfully extracted logo: {logo_image_path}")
            return logo_image_path
            
        except Exception as e:
            logger.error(f"Error extracting logo: {e}")
            return None
    
    def _find_logo_pdf(self, logo_folder: str, decoration_code: str) -> Optional[str]:
        """
        Find PDF file based on decoration code
        
        Args:
            logo_folder: Root logo folder
            decoration_code: Decoration code to search for
            
        Returns:
            Path to PDF file if found
        """
        try:
            if not os.path.exists(logo_folder):
                logger.error(f"Logo folder not found: {logo_folder}")
                return None
            
            # Try exact match first
            pdf_filename = f"{decoration_code}.pdf"
            pdf_path = os.path.join(logo_folder, pdf_filename)
            
            if os.path.exists(pdf_path):
                logger.info(f"Found logo PDF: {pdf_path}")
                return pdf_path
            
            # Try fuzzy search
            fuzzy_path = self._fuzzy_search_pdf(logo_folder, decoration_code)
            if fuzzy_path:
                return fuzzy_path
            
            logger.error(f"PDF file not found for decoration code: {decoration_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding logo PDF: {e}")
            return None
    
    def _fuzzy_search_pdf(self, logo_folder: str, decoration_code: str) -> Optional[str]:
        """
        Perform fuzzy search for PDF files
        
        Args:
            logo_folder: Logo folder path
            decoration_code: Decoration code to search for
            
        Returns:
            Path to best matching PDF file
        """
        try:
            # Get all PDF files
            pdf_files = []
            for file in os.listdir(logo_folder):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(logo_folder, file))
            
            if not pdf_files:
                return None
            
            # Score PDFs based on similarity
            scored_pdfs = []
            decoration_code_lower = decoration_code.lower()
            
            for pdf_path in pdf_files:
                filename = os.path.basename(pdf_path).lower()
                
                score = 0
                if decoration_code_lower in filename:
                    score += 5
                
                # Check for partial matches
                words = decoration_code_lower.split()
                for word in words:
                    if len(word) > 2 and word in filename:
                        score += 2
                
                if score > 0:
                    scored_pdfs.append((score, pdf_path))
            
            if scored_pdfs:
                scored_pdfs.sort(reverse=True, key=lambda x: x[0])
                best_match = scored_pdfs[0][1]
                logger.info(f"Fuzzy match found for logo: {best_match}")
                return best_match
            
            return None
            
        except Exception as e:
            logger.error(f"Error in fuzzy search for PDF: {e}")
            return None
    
    def _extract_first_page(self, pdf_path: str, decoration_code: str) -> Optional[str]:
        """
        Extract first page from PDF as image
        
        Args:
            pdf_path: Path to PDF file
            decoration_code: Used for naming the output file
            
        Returns:
            Path to extracted image file
        """
        try:
            # Method 1: Try with PyMuPDF (faster)
            try:
                return self._extract_with_pymupdf(pdf_path, decoration_code)
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed: {e}")
            
            # Method 2: Fallback to pdf2image
            try:
                return self._extract_with_pdf2image(pdf_path, decoration_code)
            except Exception as e:
                logger.warning(f"pdf2image extraction failed: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting first page: {e}")
            return None
    
    def _extract_with_pymupdf(self, pdf_path: str, decoration_code: str) -> str:
        """Extract using PyMuPDF library"""
        doc = fitz.open(pdf_path)
        page = doc[0]  # First page
        
        # Get page as image
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
        pix = page.get_pixmap(matrix=mat)
        
        # Save as PNG
        output_path = os.path.join(self.temp_dir, f"{decoration_code}_logo.png")
        pix.save(output_path)
        
        doc.close()
        logger.info(f"Extracted logo using PyMuPDF: {output_path}")
        return output_path
    
    def _extract_with_pdf2image(self, pdf_path: str, decoration_code: str) -> str:
        """Extract using pdf2image library"""
        # Convert first page to image
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
        
        if not images:
            raise Exception("No images extracted from PDF")
        
        # Save the first (and only) image
        output_path = os.path.join(self.temp_dir, f"{decoration_code}_logo.png")
        images[0].save(output_path, 'PNG')
        
        logger.info(f"Extracted logo using pdf2image: {output_path}")
        return output_path
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup_temp_files()