import os
import json
import traceback
from src.excel_parser import parse_excel_file
from src.logo_positioner import LogoPositioner
from src.exporter import export_final_image
from src.utils import setup_logging, log_error, create_output_dirs, is_back_location


def _count_files_with_ext(root_path, exts):
    count = 0
    for r, _, files in os.walk(root_path):
        for f in files:
            if f.lower().endswith(exts):
                count += 1
    return count


def _validate_and_fix_paths(image_folder, logo_folder):
    """
    Heuristic to detect if the user swapped image and logo folders.
    - If image_folder name contains 'logo' and logo_folder contains 'image', swap.
    - If image_folder has far fewer JPG/JPEG than logo_folder, and logo_folder has more PDFs/PNGs, do not swap.
      Otherwise, if logo_folder has more JPGs and image_folder almost none, swap.
    """
    img_norm = image_folder.lower()
    logo_norm = logo_folder.lower()

    should_swap = False

    if ("logo" in img_norm) and ("image" in logo_norm or "images" in logo_norm):
        should_swap = True
    else:
        img_jpgs = _count_files_with_ext(image_folder, (".jpg", ".jpeg"))
        logo_jpgs = _count_files_with_ext(logo_folder, (".jpg", ".jpeg"))
        # If image folder has almost no jpgs but logo folder has many, it's likely swapped
        if img_jpgs < 10 and logo_jpgs > img_jpgs * 5:
            should_swap = True

    if should_swap:
        print(f"[Warning] Detected swapped folders. Swapping image_folder and logo_folder.\n\timage_folder: {image_folder}\n\tlogo_folder: {logo_folder}")
        return logo_folder, image_folder

    return image_folder, logo_folder


def process_all_images(excel_file, image_folder, logo_folder, progress_callback=None):
    # Step 1: Setup
    log_path = setup_logging()

    # Step 2: Load config (resolve relative to project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    settings_path = os.path.join(project_root, "config", "settings.json")
    with open(settings_path, "r") as f:
        settings = json.load(f)

    # Ensure output dirs exist based on settings
    create_output_dirs(settings.get("output_folder", "./output/"), settings.get("thumbnail_folder", "./output/thumbnails/"))
    print(f"Logging to: {log_path}")

    # Validate folders and auto-fix if reversed
    image_folder, logo_folder = _validate_and_fix_paths(image_folder, logo_folder)

    try:
        job_data = parse_excel_file(excel_file)
        total = len(job_data)
        positioner = LogoPositioner(settings["template_folder"])

        for idx, job in enumerate(job_data):
            try:
                if not job.get("Supplier Name"):
                    raise ValueError(f"Missing Supplier Name for row {idx + 1}")

                print(f"Processing Job: {job['Final Image Name']}")

                # Place main logo
                intermediate_image_path, placement = positioner.place_logo_on_image(
                    job, settings, image_folder, logo_folder
                )

                # Also create front image if location is "FULL-BACK"
                if is_back_location(job["Location As per Word file"]):
                    front_job = job.copy()
                    front_job["Location As per Word file"] = "FULL-FRONT"
                    front_job["Final Image Name"] = "FRONT_" + job["Final Image Name"]
                    try:
                        positioner.place_logo_on_image(front_job, settings, image_folder, logo_folder)  # returns (path, placement) but we don't export front separately here
                    except Exception as fe:
                        log_error(
                            f"Front image placement failed for {front_job['Final Image Name']}: {fe}", log_path
                        )

                # Export final image: if Photoshop export is enabled on Windows, use placement data
                if settings.get("enable_photoshop_export", False):
                    try:
                        from src.exporter import export_with_photoshop
                        export_with_photoshop(placement, job, settings)
                    except Exception as ps_e:
                        log_error(f"Photoshop export failed for {job.get('Final Image Name', 'Unknown')}: {ps_e}", log_path)
                        export_final_image(intermediate_image_path, job, settings)
                else:
                    export_final_image(intermediate_image_path, job, settings)

            except Exception as e:
                error_msg = f"Failed Job: {job.get('Final Image Name', 'Unknown')} | Error: {str(e)}"
                log_error(error_msg, log_path)
                traceback.print_exc()

            if progress_callback and total > 0:
                progress_callback((idx + 1) * 100 // total)

    except Exception as e:
        log_error(f"Failed to process Excel: {str(e)}", log_path)
        traceback.print_exc()


if __name__ == "__main__":
    # For command line testing
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel = os.path.join(project_root, "input", "excel_files", "sample.xlsx")
    image_folder = os.path.join(project_root, "input", "assets")
    logo_folder = os.path.join(project_root, "input", "assets", "logos")
    process_all_images(excel, image_folder, logo_folder)
