# exporter.py

import os
import subprocess
import platform
import shutil

def export_final_image(intermediate_image_path, job, settings):
    try:
        print("intermediate_image_path>>>>>>>>>>",intermediate_image_path)
        final_output_path = os.path.join(settings["output_folder"], job["Final Image Name"])
        jsx_script_path = os.path.abspath(os.path.join("src", "photoshop_bridge.jsx"))
        print("final_output_path>>>>>>>>>>>>>>",final_output_path)
        # Convert paths to forward slashes for JSX
        input_image_jsx = intermediate_image_path.replace("\\", "/")
        output_image_jsx = final_output_path.replace("\\", "/")
        jsx_script_jsx = jsx_script_path.replace("\\", "/")

        # Prepare Photoshop script arguments
        args = [
            "Photoshop",
            f'-r "var inputImagePath = \'{input_image_jsx}\';',
            f'var outputImagePath = \'{output_image_jsx}\';',
            f'$.evalFile(\'{jsx_script_jsx}\');"'
        ]

        # Construct full command
        command = " ".join(args)
        print(f"[Photoshop JSX] Running: {command}")

        if platform.system() == "Windows":
            subprocess.run(["cmd", "/c", command], check=True)
        else:
            raise EnvironmentError("This script currently supports only Windows + Photoshop scripting.")

        # Copy to thumbnails
        if os.path.exists(final_output_path):
            thumbnail_path = os.path.join(settings["thumbnail_folder"], job["Final Image Name"])
            shutil.copy(final_output_path, thumbnail_path)
            print(f"Exported & Copied Thumbnail: {thumbnail_path}")
        else:
            raise FileNotFoundError(f"Export failed: {final_output_path} not found")

    except Exception as e:
        print(f"Export error: {e}")
        raise

# # exporter.py

# import os
# import subprocess
# import platform
# import shutil

# def export_final_image(intermediate_image_path, job, settings):
#     try:
#         print("intermediate_image_path>>>>>>>>>>",intermediate_image_path)
#         final_output_path = os.path.join(settings["output_folder"], job["Final Image Name"])
#         jsx_script_path = os.path.abspath(os.path.join("src", "photoshop_bridge.jsx"))
#         print("final_output_path>>>>>>>>>>>>>>",final_output_path)
#         # Convert paths to forward slashes for JSX
#         input_image_jsx = intermediate_image_path.replace("\\", "/")
#         output_image_jsx = final_output_path.replace("\\", "/")
#         jsx_script_jsx = jsx_script_path.replace("\\", "/")

#         # Prepare Photoshop script arguments
#         args = [
#             "Photoshop",
#             f'-r "var inputImagePath = \'{input_image_jsx}\';',
#             f'var outputImagePath = \'{output_image_jsx}\';',
#             f'$.evalFile(\'{jsx_script_jsx}\');"'
#         ]

#         # Construct full command
#         command = " ".join(args)
#         print(f"[Photoshop JSX] Running: {command}")

#         if platform.system() == "Windows":
#             subprocess.run(["cmd", "/c", command], check=True)
#         else:
#             raise EnvironmentError("This script currently supports only Windows + Photoshop scripting.")

#         # Copy to thumbnails
#         if os.path.exists(final_output_path):
#             thumbnail_path = os.path.join(settings["thumbnail_folder"], job["Final Image Name"])
#             shutil.copy(final_output_path, thumbnail_path)
#             print(f"Exported & Copied Thumbnail: {thumbnail_path}")
#         else:
#             raise FileNotFoundError(f"Export failed: {final_output_path} not found")

#     except Exception as e:
#         print(f"Export error: {e}")
#         raise



# # exporter.py
# import os
# import subprocess
# from PIL import Image


# def export_final_image(intermediate_image_path, job, settings):
#     """
#     Triggers Photoshop JSX script to create PSD + JPG and generates a thumbnail.
#     """
#     final_name = job["Final Image Name"]
#     output_folder = settings["output_folder"]
#     thumbnail_folder = settings["thumbnail_folder"]
#     jsx_script_path = os.path.abspath("src/photoshop_bridge.jsx")

#     logo_position = job.get("logo_position", (100, 100))  # fallback
#     x, y = int(logo_position[0]), int(logo_position[1])

#     # Define export paths
#     input_image = os.path.abspath(intermediate_image_path)
#     logo_image = os.path.abspath(job["logo_path"])  # you need to set this in job object
#     output_psd_path = os.path.join(output_folder, final_name.replace(".jpg", ".psd"))
#     output_jpg_path = os.path.join(output_folder, final_name)

#     # Prepare the Photoshop command
#     ps_script = f"""
# var inputImage = "{input_image.replace("\\\\", "/")}";
# var logoImage = "{logo_image.replace("\\\\", "/")}";
# var x = {x};
# var y = {y};
# var outputPsd = "{output_psd_path.replace("\\\\", "/")}";
# var outputJpg = "{output_jpg_path.replace("\\\\", "/")}";
# $.evalFile("{jsx_script_path.replace("\\\\", "/")}");
# placeLogoAndExport(inputImage, logoImage, x, y, outputPsd, outputJpg);
# """

#     try:
#         temp_script_file = "temp_script.jsx"
#         with open(temp_script_file, "w") as f:
#             f.write(ps_script)

#         # Run Photoshop (assumes it's in PATH or hardcoded here)
#         subprocess.run(["photoshop", "-r", temp_script_file], check=True)

#         # Clean up
#         os.remove(temp_script_file)

#         # Generate thumbnail
#         if not os.path.exists(thumbnail_folder):
#             os.makedirs(thumbnail_folder)

#         thumbnail_path = os.path.join(thumbnail_folder, final_name)
#         with Image.open(output_jpg_path) as img:
#             img.thumbnail((300, 300))
#             img.save(thumbnail_path)

#         print(f"[✓] Exported PSD & JPG for: {final_name}")
#     except Exception as e:
#         print(f"[✗] Error exporting image: {final_name} | Error: {e}")
