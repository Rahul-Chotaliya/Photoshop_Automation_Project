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

            photoshop_exe = settings.get("photoshop_path") or "Photoshop"

            # Prepare Photoshop script arguments
            args = [
                photoshop_exe,
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


def export_with_photoshop(placement, job, settings):
    """
    Use Photoshop to place the logo as a separate layer at computed position and scale,
    then save PSD and JPG.
    placement: {
      base_image_path, logo_image_path, x, y, logo_width,
    }
    """
    if platform.system() != "Windows":
        raise EnvironmentError("Photoshop export is only supported on Windows.")

    photoshop_exe = settings.get("photoshop_path") or "Photoshop"
    jsx_script_path = os.path.abspath(os.path.join("src", "photoshop_bridge.jsx"))

    base = os.path.abspath(placement["base_image_path"]).replace("\\", "/")
    logo = os.path.abspath(placement["logo_image_path"]).replace("\\", "/")
    x = int(placement["x"]) if isinstance(placement["x"], (int, float)) else int(placement["x"][0])
    y = int(placement["y"]) if isinstance(placement["y"], (int, float)) else int(placement["y"][1])
    target_w = int(placement.get("logo_width", settings.get("default_logo_width", 150)))

    final_jpg = os.path.abspath(os.path.join(settings["output_folder"], job["Final Image Name"]))
    final_psd = final_jpg.replace(".jpg", ".psd").replace(".jpeg", ".psd")

    jsx = jsx_script_path.replace("\\", "/")

    # Build the -r code to set variables and eval the JSX
    runtime_code = (
        f"var inputImagePath=\"{base}\";"
        f" var logoImagePath=\"{logo}\";"
        f" var placeX={x}; var placeY={y}; var targetLogoWidth={target_w};"
        f" var outputPsdPath=\"{final_psd}\"; var outputJpgPath=\"{final_jpg}\";"
        f" $.evalFile(\"{jsx}\");"
    )

    cmd = [
        photoshop_exe,
        f'-r "{runtime_code}"'
    ]

    command = " ".join(cmd)
    print(f"[Photoshop JSX] Running: {command}")
    subprocess.run(["cmd", "/c", command], check=True)

    # Copy to thumbnails
    if os.path.exists(final_jpg):
        thumbnail_path = os.path.join(settings["thumbnail_folder"], job["Final Image Name"])
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        shutil.copy(final_jpg, thumbnail_path)
        print(f"Exported & Copied Thumbnail: {thumbnail_path}")
    else:
        raise FileNotFoundError(f"Export failed: {final_jpg} not found")
