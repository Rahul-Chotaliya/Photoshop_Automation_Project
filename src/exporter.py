# exporter.py

import os
import subprocess
import platform
import shutil


def export_final_image(intermediate_image_path, job, settings):
    """
    Export the final image. On Windows with Photoshop available, it will attempt to
    invoke the JSX bridge; on other platforms or when Photoshop is not available,
    it will simply ensure the intermediate image is used as the final output and
    copy it to the thumbnail folder.
    """
    try:
        print("intermediate_image_path>>>>>>>>>>", intermediate_image_path)
        final_output_path = os.path.join(settings["output_folder"], job["Final Image Name"])
        jsx_script_path = os.path.abspath(os.path.join("src", "photoshop_bridge.jsx"))
        print("final_output_path>>>>>>>>>>>>>>", final_output_path)

        # If the intermediate is already saved at the final path, nothing to do for export
        # except making the thumbnail. The current pipeline saves to final_output_path already.
        export_via_photoshop = False
        if platform.system() == "Windows":
            # Allow toggling Photoshop export via settings flag if desired in future
            export_via_photoshop = settings.get("enable_photoshop_export", False)

        if export_via_photoshop:
            # Convert paths to forward slashes for JSX
            input_image_jsx = intermediate_image_path.replace("\\", "/")
            output_image_jsx = final_output_path.replace("\\", "/")
            jsx_script_jsx = jsx_script_path.replace("\\", "/")

            # Prepare Photoshop script arguments
            args = [
                "Photoshop",
                f'-r "var inputImagePath = \"{input_image_jsx}\";'
                f' var outputImagePath = \"{output_image_jsx}\";'
                f' $.evalFile(\"{jsx_script_jsx}\");"'
            ]

            # Construct full command
            command = " ".join(args)
            print(f"[Photoshop JSX] Running: {command}")

            subprocess.run(["cmd", "/c", command], check=True)
        else:
            print("[Exporter] Skipping Photoshop export (non-Windows or disabled). Using intermediate image as final output.")
            # Ensure final output exists (copy if paths differ)
            os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
            if os.path.abspath(intermediate_image_path) != os.path.abspath(final_output_path):
                shutil.copyfile(intermediate_image_path, final_output_path)

        # Copy to thumbnails
        if os.path.exists(final_output_path):
            thumbnail_path = os.path.join(settings["thumbnail_folder"], job["Final Image Name"])
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            shutil.copy(final_output_path, thumbnail_path)
            print(f"Exported & Copied Thumbnail: {thumbnail_path}")
        else:
            raise FileNotFoundError(f"Export failed: {final_output_path} not found")

    except Exception as e:
        print(f"Export error: {e}")
        raise
