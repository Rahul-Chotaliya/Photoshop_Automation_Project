#!/usr/bin/env python3
"""
Demo script for the Photoshop Automation Project (Simplified Version)
This demonstrates the core functionality without MediaPipe dependency
"""

import os
import json
import sys
from src.excel_parser import parse_excel_file
from src.logo_positioner_simple import SimpleLogoPositioner
from src.exporter import export_final_image
from src.utils import setup_logging, log_error, create_output_dirs

def create_sample_images():
    """Create sample images for demonstration"""
    import cv2
    import numpy as np
    
    print("🎨 Creating sample images for demonstration...")
    
    # Create sample product images
    suppliers = ["SupplierA", "SupplierB", "SupplierC", "SupplierD"]
    products = ["TSH001 Black", "TSH002 White", "CAP001 Red", "BAG001 Blue"]
    
    for i, (supplier, product) in enumerate(zip(suppliers, products)):
        # Create a simple t-shirt/cap image
        img = np.ones((800, 600, 3), dtype=np.uint8) * 255
        
        # Add some basic shape to represent clothing
        if "TSH" in product:
            # T-shirt shape
            cv2.rectangle(img, (200, 100), (400, 400), (200, 200, 200), -1)
            cv2.rectangle(img, (150, 150), (450, 350), (180, 180, 180), -1)
        elif "CAP" in product:
            # Cap shape
            cv2.ellipse(img, (300, 200), (150, 80), 0, 0, 180, (200, 200, 200), -1)
        elif "BAG" in product:
            # Bag shape
            cv2.rectangle(img, (150, 100), (450, 500), (200, 200, 200), -1)
        
        # Add text label
        cv2.putText(img, product, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, supplier, (50, 750), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Save image
        folder_path = f"input/assets/{supplier}"
        os.makedirs(folder_path, exist_ok=True)
        image_path = os.path.join(folder_path, f"{product}.png")
        cv2.imwrite(image_path, img)
        print(f"✅ Created: {image_path}")
    
    # Create sample logos
    logos = ["LOGO001", "LOGO002", "LOGO003", "LOGO004"]
    logo_folder = "input/assets/logos"
    os.makedirs(logo_folder, exist_ok=True)
    
    for logo in logos:
        # Create a simple logo
        logo_img = np.ones((200, 200, 4), dtype=np.uint8) * 255
        logo_img[:, :, 3] = 255  # Alpha channel
        
        # Add a simple shape
        cv2.circle(logo_img, (100, 100), 80, (0, 0, 255, 255), -1)
        cv2.putText(logo_img, logo, (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255, 255), 2)
        
        # Save as PNG
        logo_path = os.path.join(logo_folder, f"{logo}.png")
        cv2.imwrite(logo_path, logo_img)
        print(f"✅ Created: {logo_path}")

def demo_processing():
    """Demonstrate the processing workflow"""
    print("\n🚀 Starting Demo Processing...")
    
    # Load settings
    project_root = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(project_root, "config", "settings.json")
    
    with open(settings_path, "r") as f:
        settings = json.load(f)
    
    # Setup directories
    create_output_dirs(settings.get("output_folder", "./output/"), 
                      settings.get("thumbnail_folder", "./output/thumbnails/"))
    
    # Setup logging
    log_path = setup_logging()
    print(f"📝 Logging to: {log_path}")
    
    try:
        # Parse Excel file
        excel_path = os.path.join(project_root, "input", "excel_files", "sample.xlsx")
        job_data = parse_excel_file(excel_path)
        print(f"📊 Loaded {len(job_data)} jobs from Excel file")
        
        # Initialize logo positioner
        positioner = SimpleLogoPositioner(settings.get("template_folder"))
        
        # Process each job
        for idx, job in enumerate(job_data):
            try:
                print(f"\n🔄 Processing Job {idx + 1}/{len(job_data)}: {job['Final Image Name']}")
                
                # Place logo on image
                intermediate_image_path, placement = positioner.place_logo_on_image(
                    job, settings, 
                    os.path.join(project_root, "input", "assets"),
                    os.path.join(project_root, "input", "assets", "logos")
                )
                
                # Export final image
                export_final_image(intermediate_image_path, job, settings)
                
                print(f"✅ Completed: {job['Final Image Name']}")
                
            except Exception as e:
                error_msg = f"Failed Job: {job.get('Final Image Name', 'Unknown')} | Error: {str(e)}"
                log_error(error_msg, log_path)
                print(f"❌ {error_msg}")
        
        print(f"\n🎉 Demo completed! Check the output folder for results.")
        print(f"📁 Output folder: {settings['output_folder']}")
        print(f"📁 Thumbnails: {settings['thumbnail_folder']}")
        
    except Exception as e:
        error_msg = f"Demo failed: {str(e)}"
        log_error(error_msg, log_path)
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()

def main():
    """Main demo function"""
    print("🎯 Photoshop Automation Project - Demo")
    print("=" * 50)
    
    # Check if sample files exist
    excel_path = "input/excel_files/sample.xlsx"
    if not os.path.exists(excel_path):
        print("❌ Sample Excel file not found. Creating sample files...")
        create_sample_images()
    else:
        print("✅ Sample Excel file found")
    
    # Run demo
    demo_processing()

if __name__ == "__main__":
    main()