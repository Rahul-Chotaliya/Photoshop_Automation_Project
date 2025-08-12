import os
import json
import traceback
from src.excel_parser import parse_excel_file
from src.logo_positioner import LogoPositioner
from src.exporter import export_final_image
from src.utils import setup_logging, log_error, create_output_dirs, is_back_location

def process_all_images(excel_file, image_folder, logo_folder, progress_callback=None):
    # Step 1: Setup
    log_path = setup_logging()
    create_output_dirs()
    print(f"Logging to: {log_path}")

    # Step 2: Load config
    with open("config/settings.json", "r") as f:
        settings = json.load(f)

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
                intermediate_image_path = positioner.place_logo_on_image(
                    job, settings, image_folder, logo_folder
                )

                # Also create front image if location is "FULL-BACK"
                if is_back_location(job["Location As per Word file"]):
                    front_job = job.copy()
                    front_job["Location As per Word file"] = "FULL-FRONT"
                    front_job["Final Image Name"] = "FRONT_" + job["Final Image Name"]
                    try:
                        positioner.place_logo_on_image(front_job, settings, image_folder, logo_folder)
                    except Exception as fe:
                        log_error(
                            f"Front image placement failed for {front_job['Final Image Name']}: {fe}", log_path
                        )

                # Export final image (Photoshop export is skipped on non-Windows or when disabled)
                export_final_image(intermediate_image_path, job, settings)

            except Exception as e:
                error_msg = f"Failed Job: {job.get('Final Image Name', 'Unknown')} | Error: {str(e)}"
                log_error(error_msg, log_path)
                traceback.print_exc()

            if progress_callback:
                progress_callback((idx + 1) * 100 // total)

    except Exception as e:
        log_error(f"Failed to process Excel: {str(e)}", log_path)
        traceback.print_exc()

if __name__ == "__main__":
    # For command line testing
    excel = "input/excel_files/sample.xlsx"
    image_folder = "input/assets/"
    logo_folder = "input/assets/logos/"
    process_all_images(excel, image_folder, logo_folder)


# # main.py

# import os
# import json
# import traceback
# from src.excel_parser import parse_excel_file
# from src.logo_positioner import LogoPositioner
# from src.exporter import export_final_image
# from src.utils import setup_logging, log_error, create_output_dirs, is_back_location, is_front_location

# def process_all_images(excel_file, image_folder, logo_folder, progress_callback=None):
#     # Step 1: Setup
#     log_path = setup_logging()
#     create_output_dirs()
#     print(f"Logging to: {log_path}")

#     # Step 2: Load config
#     with open("config/settings.json", "r") as f:
#         settings = json.load(f)

#     try:
#         job_data = parse_excel_file(excel_file)
#         total = len(job_data)
#         positioner = LogoPositioner(settings["template_folder"])

#         for idx, job in enumerate(job_data):
#             print(f"Processing Job: {job['Final Image Name']}")
#             try:
#                 # Place main logo
#                 intermediate_image_path = positioner.place_logo_on_image(job, settings, image_folder, logo_folder)

#                 # If "FULL-BACK", also generate front image automatically
#                 if is_back_location(job["Location As per Word file"]):
#                     front_job = job.copy()
#                     front_job["Location As per Word file"] = "2. FULL-FRONT"
#                     front_job["Final Image Name"] = "FRONT_" + job["Final Image Name"]
#                     try:
#                         positioner.place_logo_on_image(front_job, settings, image_folder, logo_folder)
#                     except Exception as fe:
#                         log_error(f"Front image placement failed for {front_job['Final Image Name']}: {fe}", log_path)

#                 # Export image via Photoshop
#                 export_final_image(intermediate_image_path, job, settings)

#             except Exception as e:
#                 error_msg = f"Failed Job: {job['Final Image Name']} | Error: {str(e)}"
#                 log_error(error_msg, log_path)
#                 traceback.print_exc()

#             if progress_callback:
#                 progress_callback((idx + 1) * 100 // total)

#     except Exception as e:
#         log_error(f"Failed to process Excel: {str(e)}", log_path)
#         traceback.print_exc()

# if __name__ == "__main__":
#     # Used for testing outside the GUI
#     excel = "input/excel_files/sample.xlsx"
#     img_folder = "input/assets/"
#     logo_folder = "input/assets/logos/"
#     process_all_images(excel, img_folder, logo_folder)



# import os
# import json
# import traceback
# from src.excel_parser import parse_excel_file
# from src.logo_positioner import LogoPositioner
# from src.exporter import export_final_image
# from src.utils import setup_logging, log_error, create_output_dirs

# def process_all_images(excel_file, image_folder, logo_folder, progress_callback=None):
#     log_path = setup_logging()
#     create_output_dirs()

#     with open("config/settings.json", "r") as f:
#         settings = json.load(f)

#     try:
#         print(f"Processing Excel: {excel_file}")
#         job_data = parse_excel_file(excel_file)

#         positioner = LogoPositioner(settings["template_folder"])

#         for idx, job in enumerate(job_data):
#             print(f"\tProcessing Job: {job['Final Image Name']}")
#             try:
#                 intermediate_image_path = positioner.place_logo_on_image(
#                     job, settings, image_folder, logo_folder
#                 )
#                 export_final_image(intermediate_image_path, job, settings)
#             except Exception as e:
#                 error_msg = f"Failed Job: {job['Final Image Name']} | Error: {str(e)}"
#                 log_error(error_msg)
#                 traceback.print_exc()
#             if progress_callback:
#                 progress = int((idx + 1) / len(job_data) * 100)
#                 progress_callback(progress)

#     except Exception as e:
#         log_error(f"Failed to parse Excel {excel_file}: {str(e)}")
#         traceback.print_exc()

# if __name__ == "__main__":
#     # This is only for CLI testing, not used by GUI
#     excel_file = "input/excel_files/sample.xlsx"
#     image_folder = "input/assets"
#     logo_folder = "input/assets/logos"
#     process_all_images(excel_file, image_folder, logo_folder)
