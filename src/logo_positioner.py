# logo_positioner.py
import os
import tempfile
import traceback

import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import mediapipe as mp


class LogoPositioner:
    def __init__(self, template_dir):
        self.template_dir = template_dir
        self.pose = mp.solutions.pose.Pose(static_image_mode=True)

    # ---------------------------
    # Human keypoint detection
    # ---------------------------
    def detect_human_keypoints(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise Exception("Image not found or unreadable: " + str(image_path))

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.pose.process(img_rgb)

            if not results.pose_landmarks:
                return None

            keypoints = {}
            h, w = img.shape[:2]
            for i, lm in enumerate(results.pose_landmarks.landmark):
                keypoints[i] = (int(lm.x * w), int(lm.y * h))
            return keypoints
        except Exception as e:
            print(f"[Keypoint Error] {e}")
            traceback.print_exc()
            return None

    # ---------------------------
    # Map location key to keypoint index
    # ---------------------------
    def get_logo_position(self, keypoints, location_key):
        try:
            location_map = {
                # (kept the same mapping you had — keys map to indexes)
                "FULL-BACK": 1,
                "FULL-FRONT": 2,
                "LEFT-BICEP": 3,
                "RIGHT-BICEP": 4,
                "LEFT-CHEST": 5,
                "RIGHT-CHEST": 6,
                "LEFT-COLLAR": 7,
                "RIGHT-COLLAR": 8,
                "LEFT-CUFF": 9,
                "RIGHT-CUFF": 10,
                "LEFT-HIP": 11,
                "RIGHT-HIP": 12,
                "LEFT-SLEEVE": 13,
                "RIGHT-SLEEVE": 14,
                "LEFT-THIGH-HIGH": 15,
                "RIGHT THIGH-HIGH": 16,
                "ON-POCKET": 17,

                "BACK-YOKE": 18,
                "FULL-BACK & FULL-FRONT": 19,
                "LEFT-BICEP-RIGHT-BICEP": 20,
                "LEFT-CHEST-LEFT-BICEP-RIGHT-BICEP": 21,
                "LEFT-CHEST-RIGHT-BICEP": 22,
                "LEFT-CHEST-RIGHT-SLEEVE": 23,
                "LEFT-SLEEVE-RIGHT-SLEEVE": 24,
                "RIGHT-CHEST-LEFT-BICEP": 25,
                "RIGHT-CHEST-LEFT-SLEEVE": 26,
                "RIGHT-CHEST-LFT-BICEP-RIGHT-BICEP": 27,
                "FULL-FRONT-FULL-BACK": 28,
                "LEFT-CHEST-FULL-BACK": 29,
                "RIGHT-CHEST-FULL-BACK": 30,

                "FRONT-CROWN": 31,
                "CAP-BACK": 32,
                "CAP-SIDE": 33,
                "CAP-FRONT-SIDE": 34,
                "LOWER-LEFT-CROWN": 35,
                "LOWER-RIGHT-CROWN": 36,
                "Corner-Angled-Towel": 37,
                "FRONT_CENTER": 38,
                "FRONT (ON BAG)": 39,
                "ON POCKET (ON BAG)": 40
            }

            if location_key is None:
                print("[DEBUG] location_key is None")
                return None

            print(f"[DEBUG] Requested Location Key: {location_key}")
            print(f"[DEBUG] Available Keypoints: {list(keypoints.keys())}")
            landmark_index = location_map.get(location_key.upper())
            print("landmark_index-------------", landmark_index)
            if landmark_index is None or landmark_index not in keypoints:
                return None
            return keypoints[landmark_index]
        except Exception as e:
            print(f"[Mapping Error] {e}")
            traceback.print_exc()
            return None

    # ---------------------------
    # Resize logo while preserving aspect ratio
    # ---------------------------
    def resize_logo(self, logo_img, target_width):
        try:
            if logo_img is None:
                return None
            h, w = logo_img.shape[:2]
            if w == 0:
                return logo_img
            scale_ratio = target_width / float(w)
            dim = (int(target_width), max(1, int(h * scale_ratio)))
            return cv2.resize(logo_img, dim, interpolation=cv2.INTER_AREA)
        except Exception as e:
            print(f"Error resizing logo: {e}")
            traceback.print_exc()
            return logo_img

    # ---------------------------
    # Basic background remove (simple threshold method)
    # ---------------------------
    def remove_background(self, image):
        try:
            if image is None:
                return image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
            # invert mask to keep non-white areas
            mask_inv = cv2.bitwise_not(mask)
            result = cv2.bitwise_and(image, image, mask=mask_inv)
            return result
        except Exception as e:
            print(f"Background removal failed: {e}")
            traceback.print_exc()
            return image

    # ---------------------------
    # Merge logo onto base image with alpha support (if present)
    # ---------------------------
    def merge_logo_on_image(self, base_image, logo_img, position):
        try:
            if base_image is None or logo_img is None or position is None:
                return base_image

            lx, ly = int(position[0]), int(position[1])

            # logo_img may be BGRA or BGR
            if logo_img.ndim == 3 and logo_img.shape[2] == 4:
                logo_bgr = logo_img[:, :, :3]
                alpha = logo_img[:, :, 3] / 255.0
            else:
                logo_bgr = logo_img
                # create alpha mask where non-white is opaque
                white_mask = np.all(logo_bgr >= 250, axis=2)
                alpha = (~white_mask).astype(float)

            lh, lw = logo_bgr.shape[:2]
            bh, bw = base_image.shape[:2]

            # Ensure we don't write outside base image boundaries
            if lx < 0:
                crop_x = -lx
                logo_bgr = logo_bgr[:, crop_x:]
                alpha = alpha[:, crop_x:]
                lx = 0
            if ly < 0:
                crop_y = -ly
                logo_bgr = logo_bgr[crop_y:, :]
                alpha = alpha[crop_y:, :]
                ly = 0

            # final region sizes
            lh, lw = logo_bgr.shape[:2]
            if lx + lw > bw:
                logo_bgr = logo_bgr[:, :bw - lx]
                alpha = alpha[:, :bw - lx]
            if ly + lh > bh:
                logo_bgr = logo_bgr[:bh - ly, :]
                alpha = alpha[:bh - ly, :]

            # region of interest
            roi = base_image[ly:ly + logo_bgr.shape[0], lx:lx + logo_bgr.shape[1]]

            # alpha blending
            alpha = alpha[..., np.newaxis]
            blended = (alpha * logo_bgr.astype(float) + (1 - alpha) * roi.astype(float)).astype(np.uint8)

            base_image[ly:ly + blended.shape[0], lx:lx + blended.shape[1]] = blended
            return base_image

        except Exception as e:
            print(f"Error merging logo: {e}")
            traceback.print_exc()
            return base_image

    # ---------------------------
    # Main entry - place logo
    # ---------------------------
    def place_logo_on_image(self, job_row, settings, image_root, logo_folder):
        """
        settings is expected to be a dict containing:
          - default_logo_width (int)
          - output_folder (str)
          - poppler_path (optional, str)  # used when converting PDFs on Windows
        """
        try:
            client_folder = os.path.join(image_root, job_row["Supplier Name"])
            image_name = f"{job_row['Supplier Part ID']} {job_row.get('Supplier Color', '')}".strip()
            product_img_path = self.find_image_file(client_folder, image_name)
            print("client_folder>>>>>>>>>>>>>", client_folder)
            print("image_name>>>>>>>>>>>", image_name)
            if not product_img_path:
                raise Exception(f"Image not found for {job_row['Supplier Part ID']} in {client_folder}")

            logo_img_path = self.find_logo_file(job_row, logo_folder)
            location_key = str(job_row.get("Location As per Word file", "")).strip()

            keypoints = self.detect_human_keypoints(product_img_path)
            if not keypoints:
                raise Exception("No keypoints found")

            print("keypointskeypointskeypoints>>>>>>>>>>>>>>>>>>>>>", keypoints)
            print("location_key>>>>>>>>>>>>>>>>>", location_key)
            position = self.get_logo_position(keypoints, location_key)
            if not position:
                raise Exception("Position not found")

            base_img = cv2.imread(product_img_path)
            if base_img is None:
                raise Exception("Failed to load base image: " + str(product_img_path))

            base_img = self.remove_background(base_img)

            # Load logo (pass poppler_path if provided in settings)
            poppler_path = settings.get("poppler_path") if isinstance(settings, dict) else None
            logo_img = self.load_logo_image(logo_img_path, poppler_path=poppler_path)
            print("logo_imglogo_img>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logo_img_path)
            if logo_img is None:
                raise Exception("Failed to load logo image: " + str(logo_img_path))

            resized_logo = self.resize_logo(logo_img, settings["default_logo_width"])
            merged_img = self.merge_logo_on_image(base_img, resized_logo, position)

            output_path = os.path.join(settings["output_folder"], job_row["Final Image Name"])
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, merged_img)
            print("output_pathoutput_path>>>>>>>>>>>>>>>>>", output_path)
            return output_path
        except Exception as e:
            print(f"Error placing logo: {e}")
            traceback.print_exc()
            raise

    # ---------------------------
    # Find logo file (png/jpg/pdf)
    # ---------------------------
    def find_logo_file(self, job_row, logo_folder):
        base_name = job_row.get("Decoration Code")
        if not base_name:
            raise FileNotFoundError("Decoration Code missing in job_row")
        expected_names = [
            f"{base_name}.png",
            f"{base_name}.jpg",
            f"{base_name}.jpeg",
            f"{base_name}.pdf"
        ]
        for name in expected_names:
            full_path = os.path.join(logo_folder, name)
            if os.path.exists(full_path):
                return full_path
        raise FileNotFoundError(f"Logo file not found for {base_name} in {logo_folder}")

    # ---------------------------
    # Find product image by searching filenames
    # ---------------------------
    def find_image_file(self, client_dir, supplier_part_id):
        if not os.path.isdir(client_dir):
            return None
        for root, _, files in os.walk(client_dir):
            for file in files:
                if str(supplier_part_id) in file and file.lower().endswith((".jpg", ".jpeg", ".png")):
                    return os.path.join(root, file)
        return None

    # ---------------------------
    # Helper: convert PIL -> cv2 and load files (PIL + pdf2image)
    # ---------------------------
    @staticmethod
    def pil_to_cv2(pil_img):
        arr = np.array(pil_img)
        if arr.ndim == 2:  # grayscale
            return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        if arr.shape[2] == 4:  # RGBA -> BGRA
            return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
        # RGB -> BGR
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    def load_logo_image(self, logo_path, poppler_path=None):
        """
        Returns an OpenCV image (BGR or BGRA) or None on failure.
        For PDFs: tries convert_from_path with explicit poppler_path fallback checks.
        """
        try:
            print("logo_path----------------------------------------", logo_path)
            if not logo_path:
                print("Empty logo_path provided")
                return None
            if not os.path.exists(logo_path):
                print(f"File not found: {logo_path}")
                return None

            ext = os.path.splitext(logo_path)[1].lower()
            print("Logo extension:", ext)

            # Helper: check if a candidate bin path contains pdftoppm/pdfinfo
            def has_poppler_bin(candidate):
                if not candidate:
                    return False
                # candidate may be path to 'bin' folder or to poppler root; check both
                possible = [
                    os.path.join(candidate, "pdftoppm.exe"),
                    os.path.join(candidate, "pdfinfo.exe"),
                    os.path.join(candidate, "Library", "bin", "pdftoppm.exe"),
                    os.path.join(candidate, "Library", "bin", "pdfinfo.exe"),
                ]
                for p in possible:
                    if os.path.exists(p):
                        return True
                return False

            # PDF handling
            if ext == ".pdf":
                # build list of poppler candidates to try
                candidates = []
                if poppler_path:
                    candidates.append(poppler_path)
                env_poppler = os.environ.get("POPPLER_PATH") or os.environ.get("POPPLER_BIN") or os.environ.get("PATH")
                if env_poppler:
                    # if PATH is given, don't treat as a single folder; we'll still try environment variable separately
                    # but also check env var specifically if it points to a folder
                    if os.path.isdir(env_poppler) and env_poppler not in candidates:
                        candidates.append(env_poppler)
                # common Windows install places (adjust if you installed elsewhere)
                common = [
                    r"C:\poppler\Library\bin",
                    r"C:\Program Files\poppler\bin",
                    r"C:\Program Files\poppler\Library\bin",
                    r"C:\tools\poppler\bin",
                ]
                for c in common:
                    if c not in candidates:
                        candidates.append(c)

                last_exc = None
                for cand in candidates:
                    if not cand:
                        continue
                    print(f"Trying poppler_path candidate: {cand}")
                    try:
                        pages = convert_from_path(logo_path, poppler_path=cand, dpi=300, fmt="jpeg")
                        if pages:
                            pil_img = pages[0].convert("RGBA")
                            logo_img = self.pil_to_cv2(pil_img)
                            print("PDF converted using poppler_path:", cand)
                            return logo_img
                    except Exception as e:
                        last_exc = e
                        print(f"convert_from_path failed with candidate {cand}: {e}")

                # If convert_from_path without explicit poppler_path sometimes works (rare), try it once more
                try:
                    print("Attempting convert_from_path without explicit poppler_path (last resort)...")
                    pages = convert_from_path(logo_path, dpi=300, fmt="jpeg")
                    if pages:
                        pil_img = pages[0].convert("RGBA")
                        logo_img = self.pil_to_cv2(pil_img)
                        print("PDF converted without explicit poppler_path")
                        return logo_img
                except Exception as e:
                    last_exc = e
                    print("convert_from_path without explicit poppler_path failed:", e)

                # nothing worked
                print("PDF -> image conversion failed. Tried candidates:", candidates)
                if last_exc:
                    print("Last exception:", last_exc)
                return None

            # Non-PDF: use PIL for better color profile handling
            try:
                pil_img = Image.open(logo_path)
                # Normalize modes
                if pil_img.mode == "CMYK":
                    pil_img = pil_img.convert("RGB")
                elif pil_img.mode in ("P", "L"):
                    pil_img = pil_img.convert("RGBA")
                if pil_img.mode not in ("RGB", "RGBA"):
                    pil_img = pil_img.convert("RGBA")

                logo_img = self.pil_to_cv2(pil_img)
                if logo_img is None:
                    print("PIL loaded image but conversion returned None")
                return logo_img

            except Exception as e:
                # Fallback to cv2.imread
                print("PIL open failed, falling back to cv2.imread:", e)
                try:
                    logo_img = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
                    if logo_img is None:
                        print(f"cv2.imread failed to read: {logo_path}")
                    return logo_img
                except Exception as e2:
                    print("cv2.imread also failed:", e2)
                    traceback.print_exc()
                    return None

        except Exception as e:
            print(f"Error loading logo image: {e}")
            traceback.print_exc()
            return None

    # def load_logo_image(self, logo_path, poppler_path=None):
    #     """
    #     Returns an OpenCV image (BGR or BGRA) or None on failure.
    #     If the file is a PDF, convert the first page using pdf2image.
    #     If you're on Windows and pdf2image raises poppler-related errors,
    #     pass poppler_path (path to poppler bin folder) in settings and it will be used.
    #     """
    #     try:
    #         print("logo_path----------------------------------------", logo_path)
    #         if not logo_path:
    #             print("Empty logo_path provided")
    #             return None
    #         if not os.path.exists(logo_path):
    #             print(f"File not found: {logo_path}")
    #             return None

    #         ext = os.path.splitext(logo_path)[1].lower()
    #         print("Logo extension:", ext)

    #         # PDF handling
    #         if ext == ".pdf":
    #             try:
    #                 convert_kwargs = {'dpi': 300, 'fmt': 'jpeg'}
    #                 if poppler_path:
    #                     pages = convert_from_path(logo_path, poppler_path=poppler_path, **convert_kwargs)
    #                 else:
    #                     pages = convert_from_path(logo_path, **convert_kwargs)

    #                 if not pages:
    #                     print(f"No pages returned when converting PDF: {logo_path}")
    #                     return None

    #                 pil_img = pages[0].convert("RGBA")
    #                 logo_img = self.pil_to_cv2(pil_img)
    #                 return logo_img
    #             except Exception as e:
    #                 print("PDF -> image conversion failed:", e)
    #                 traceback.print_exc()
    #                 return None

    #         # Non-PDF: use PIL for better color profile handling
    #         try:
    #             pil_img = Image.open(logo_path)
    #             # Normalize modes
    #             if pil_img.mode == "CMYK":
    #                 pil_img = pil_img.convert("RGB")
    #             elif pil_img.mode in ("P", "L"):
    #                 pil_img = pil_img.convert("RGBA")
    #             # keep RGB or RGBA as-is otherwise convert to RGBA for consistent alpha handling
    #             if pil_img.mode not in ("RGB", "RGBA"):
    #                 pil_img = pil_img.convert("RGBA")

    #             logo_img = self.pil_to_cv2(pil_img)
    #             if logo_img is None:
    #                 print("PIL loaded image but conversion returned None")
    #             return logo_img

    #         except Exception as e:
    #             # Fallback to cv2.imread
    #             print("PIL open failed, falling back to cv2.imread:", e)
    #             try:
    #                 logo_img = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    #                 if logo_img is None:
    #                     print(f"cv2.imread failed to read: {logo_path}")
    #                 return logo_img
    #             except Exception as e2:
    #                 print("cv2.imread also failed:", e2)
    #                 traceback.print_exc()
    #                 return None

    #     except Exception as e:
    #         print(f"Error loading logo image: {e}")
    #         traceback.print_exc()
    #         return None





# import cv2
# import numpy as np
# import os
# import tempfile
# from pdf2image import convert_from_path
# import mediapipe as mp

# class LogoPositioner:
#     def __init__(self, template_dir):
#         self.template_dir = template_dir
#         self.pose = mp.solutions.pose.Pose(static_image_mode=True)

#     def detect_human_keypoints(self, image_path):
#         try:
#             img = cv2.imread(image_path)
#             if img is None:
#                 raise Exception("Image not found or unreadable")

#             img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             results = self.pose.process(img_rgb)

#             if not results.pose_landmarks:
#                 return None

#             keypoints = {}
#             for i, lm in enumerate(results.pose_landmarks.landmark):
#                 h, w = img.shape[:2]
#                 keypoints[i] = (int(lm.x * w), int(lm.y * h))
#             return keypoints
#         except Exception as e:
#             print(f"[Keypoint Error] {e}")
#             return None

#     def get_logo_position(self, keypoints, location_key):
#         try:
#             location_map = {
#                 # 1200 x 1800 pxl - Single positions
#                 "FULL-BACK": 1,
#                 "FULL-FRONT": 2,
#                 "LEFT-BICEP": 3,
#                 "RIGHT-BICEP": 4,
#                 "LEFT-CHEST": 5,
#                 "RIGHT-CHEST": 6,
#                 "LEFT-COLLAR": 7,
#                 "RIGHT-COLLAR": 8,
#                 "LEFT-CUFF": 9,
#                 "RIGHT-CUFF": 10,
#                 "LEFT-HIP": 11,
#                 "RIGHT-HIP": 12,
#                 "LEFT-SLEEVE": 13,
#                 "RIGHT-SLEEVE": 14,
#                 "LEFT-THIGH-HIGH": 15,
#                 "RIGHT THIGH-HIGH": 16,
#                 "ON-POCKET": 17,

#                 # 1200 x 1800 pxl - Combined views
#                 "BACK-YOKE": 18,
#                 "FULL-BACK & FULL-FRONT": 19,
#                 "LEFT-BICEP-RIGHT-BICEP": 20,
#                 "LEFT-CHEST-LEFT-BICEP-RIGHT-BICEP": 21,
#                 "LEFT-CHEST-RIGHT-BICEP": 22,
#                 "LEFT-CHEST-RIGHT-SLEEVE": 23,
#                 "LEFT-SLEEVE-RIGHT-SLEEVE": 24,
#                 "RIGHT-CHEST-LEFT-BICEP": 25,
#                 "RIGHT-CHEST-LEFT-SLEEVE": 26,
#                 "RIGHT-CHEST-LFT-BICEP-RIGHT-BICEP": 27,
#                 "FULL-FRONT-FULL-BACK": 28,
#                 "LEFT-CHEST-FULL-BACK": 29,
#                 "RIGHT-CHEST-FULL-BACK": 30,

#                 # 1200 x 1200 pxl
#                 "FRONT-CROWN": 31,
#                 "CAP-BACK": 32,
#                 "CAP-SIDE": 33,
#                 "CAP-FRONT-SIDE": 34,
#                 "LOWER-LEFT-CROWN": 35,
#                 "LOWER-RIGHT-CROWN": 36,
#                 "Corner-Angled-Towel": 37,
#                 "FRONT_CENTER": 38,
#                 "FRONT (ON BAG)": 39,
#                 "ON POCKET (ON BAG)": 40
#             }



#             print(f"[DEBUG] Requested Location Key: {location_key}")
#             print(f"[DEBUG] Available Keypoints: {list(keypoints.keys())}")
#             landmark_index = location_map.get(location_key.upper())
#             print("landmark_index-------------",landmark_index)
#             if landmark_index is None or landmark_index not in keypoints:
#                 return None
#             return keypoints[landmark_index]
#         except Exception as e:
#             print(f"[Mapping Error] {e}")
#             return None

#     def resize_logo(self, logo_img, target_width):
#         try:
#             height, width = logo_img.shape[:2]
#             scale_ratio = target_width / float(width)
#             dim = (target_width, int(height * scale_ratio))
#             return cv2.resize(logo_img, dim, interpolation=cv2.INTER_AREA)
#         except Exception as e:
#             print(f"Error resizing logo: {e}")
#             return logo_img

#     def remove_background(self, image):
#         try:
#             gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#             _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
#             result = cv2.bitwise_not(image, image, mask=mask)
#             return result
#         except Exception as e:
#             print(f"Background removal failed: {e}")
#             return image

#     def merge_logo_on_image(self, base_image, logo_img, position):
#         try:
#             lx, ly = position
#             lh, lw = logo_img.shape[:2]
#             overlay = base_image.copy()
#             for y in range(lh):
#                 for x in range(lw):
#                     if lx + x >= base_image.shape[1] or ly + y >= base_image.shape[0]:
#                         continue
#                     pixel = logo_img[y, x]
#                     if not np.array_equal(pixel, [255, 255, 255]):  # Skip white
#                         overlay[ly + y, lx + x] = pixel
#             return overlay
#         except Exception as e:
#             print(f"Error merging logo: {e}")
#             return base_image

#     def place_logo_on_image(self, job_row, settings, image_root, logo_folder):
#         try:
#             client_folder = os.path.join(image_root, job_row["Supplier Name"])
#             image_name = job_row["Supplier Part ID"] + " "+job_row["Supplier Color"]
#             product_img_path = self.find_image_file(client_folder,image_name )
#             print("client_folder>>>>>>>>>>>>>",client_folder)
#             print("job_row['Supplier Part ID']>>>>>>>>>>>",image_name)
#             if not product_img_path:
#                 raise Exception(f"Image not found for {job_row['Supplier Part ID']} in {client_folder}")

#             logo_img_path = self.find_logo_file(job_row, logo_folder)
#             location_key = str(job_row["Location As per Word file"]).strip()

#             keypoints = self.detect_human_keypoints(product_img_path)
#             if not keypoints:
#                 raise Exception("No keypoints found")
#             print("keypointskeypointskeypoints>>>>>>>>>>>>>>>>>>>>>",keypoints)
#             print("location_key>>>>>>>>>>>>>>>>>",location_key)
#             position = self.get_logo_position(keypoints, location_key)
#             if not position:
#                 raise Exception("Position not found")

#             base_img = cv2.imread(product_img_path)
#             base_img = self.remove_background(base_img)

#             logo_img = self.load_logo_image(logo_img_path)
#             print("logo_imglogo_img>>>>>>>>>>>>>>>>>>>>>>>>>>>>",logo_img_path)
#             if logo_img is None:
#                 raise Exception("Failed to load logo image")

#             resized_logo = self.resize_logo(logo_img, settings["default_logo_width"])
#             merged_img = self.merge_logo_on_image(base_img, resized_logo, position)

#             output_path = os.path.join(settings["output_folder"], job_row["Final Image Name"])
#             os.makedirs(os.path.dirname(output_path), exist_ok=True)
#             cv2.imwrite(output_path, merged_img)

#             return output_path
#         except Exception as e:
#             print(f"Error placing logo: {e}")
#             raise

#     def find_logo_file(self, job_row, logo_folder):
#         base_name = job_row["Decoration Code"]
#         expected_names = [
#             f"{base_name}.png",
#             f"{base_name}.jpg",
#             f"{base_name}.jpeg",
#             f"{base_name}.pdf"
#         ]
#         for name in expected_names:
#             full_path = os.path.join(logo_folder, name)
#             if os.path.exists(full_path):
#                 return full_path
#         raise FileNotFoundError(f"Logo file not found for {base_name}")

#     def find_image_file(self, client_dir, supplier_part_id):
#         for root, _, files in os.walk(client_dir):
#             for file in files:
#                 # if supplier_part_id in file and file.lower().endswith((".jpg", ".jpeg", ".png")):
#                 if str(supplier_part_id) in file and file.lower().endswith((".jpg", ".jpeg", ".png")):
#                     return os.path.join(root, file)
#         return None
#     def load_logo_image(self, logo_path):
#         try:
#             print("logo_path----------------------------------------",logo_path)
#             if not os.path.exists(logo_path):
#                 print(f"File not found: {logo_path}")
#                 return None

#             ext = os.path.splitext(logo_path)[1].lower()

#             # Handle PDF files
#             if ext == ".pdf":
#                 images = convert_from_path(logo_path, dpi=300, fmt="jpeg")
#                 if not images:
#                     print(f"No pages found in PDF: {logo_path}")
#                     return None

#                 with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
#                     images[0].save(temp_file.name, "JPEG")
#                     logo_img = cv2.imread(temp_file.name)
#                     os.unlink(temp_file.name)  # Clean up temp file
#                     return logo_img

#             # Handle normal image files
#             else:
#                 logo_img = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
#                 if logo_img is None:
#                     print(f"Failed to load image: {logo_path}")
#                 return logo_img

#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             print(f"Error loading logo image: {e}")
#             return None
        
        
#####################################################################################  
        
        
        
        
        
    # def load_logo_image(self, logo_path):
    #     try:
    #         ext = os.path.splitext(logo_path)[1].lower()
    #         if ext == ".pdf":
    #             images = convert_from_path(logo_path, dpi=300, fmt="jpeg")
    #             print("images************************************",images)
    #             if images:
    #                 with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
    #                     images[0].save(temp_file.name, "JPEG")
    #                     logo_img = cv2.imread(temp_file.name)
    #                     os.unlink(temp_file.name)
    #                     return logo_img
    #             else:
    #                 print(f"No pages found in PDF: {logo_path}")
    #                 return None
    #         else:
    #             return cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    #     except Exception as e:
    #         print(f"Error loading logo image: {e}")
    #         return None



# import cv2
# import numpy as np
# import os
# import tempfile
# from pdf2image import convert_from_path
# import mediapipe as mp


# class LogoPositioner:
#     def __init__(self, template_dir):
#         self.template_dir = template_dir
#         self.pose = mp.solutions.pose.Pose(static_image_mode=True)

#     def detect_human_keypoints(self, image_path):
#         try:
#             print("image_path>>>>>>>>>>>>>>>>>>>>",image_path)
#             img = cv2.imread(image_path)
#             if img is None:
#                 raise Exception("Image not found or unreadable")

#             img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             results = self.pose.process(img_rgb)

#             if not results.pose_landmarks:
#                 return None

#             keypoints = {}
#             for i, lm in enumerate(results.pose_landmarks.landmark):
#                 h, w = img.shape[:2]
#                 keypoints[i] = (int(lm.x * w), int(lm.y * h))

#             return keypoints
#         except Exception as e:
#             print(f"[Keypoint Error] {e}")
#             return None

#     def get_logo_position(self, keypoints, location_key):
#         try:
#             location_map = {
#                 "RIGHT-ELBOW": 14,
#                 "LEFT-ELBOW": 13,
#                 "LEFT-CHEST": 11,
#                 "RIGHT-CHEST": 12,
#                 "FULL-FRONT": 0,
#                 "FULL-BACK": 24,
#                 "LEFT-BICEP": 11,
#                 "RIGHT-BICEP": 12,
#                 "CROWN": 0
#             }

#             landmark_index = location_map.get(location_key.upper())
#             if landmark_index is None or landmark_index not in keypoints:
#                 return None

#             return keypoints[landmark_index]
#         except Exception as e:
#             print(f"[Mapping Error] {e}")
#             return None

#     def resize_logo(self, logo_img, target_width):
#         try:
#             height, width = logo_img.shape[:2]
#             scale_ratio = target_width / float(width)
#             dim = (target_width, int(height * scale_ratio))
#             resized_logo = cv2.resize(logo_img, dim, interpolation=cv2.INTER_AREA)
#             return resized_logo
#         except Exception as e:
#             print(f"Error resizing logo: {e}")
#             return logo_img

#     def merge_logo_on_image(self, base_image, logo_img, position):
#         try:
#             lx, ly = position
#             lh, lw = logo_img.shape[:2]

#             overlay = base_image.copy()

#             for y in range(lh):
#                 for x in range(lw):
#                     if lx + x >= base_image.shape[1] or ly + y >= base_image.shape[0]:
#                         continue
#                     pixel = logo_img[y, x]
#                     if not np.array_equal(pixel, [255, 255, 255]):  # Skip white
#                         overlay[ly + y, lx + x] = pixel
#             return overlay
#         except Exception as e:
#             print(f"Error merging logo: {e}")
#             return base_image

#     def place_logo_on_image(self, job_row, settings, image_folder, logo_folder):
#         try:
#             product_img_path = os.path.join(image_folder, f"{job_row['Supplier Part ID']}.jpg")
#             logo_img_path = self.find_logo_file(job_row, logo_folder)
#             location_key = str(job_row["Location As per Word file"]).strip()

#             if not os.path.exists(product_img_path):
#                 raise Exception(f"Image not found: {product_img_path}")
#             if not os.path.exists(logo_img_path):
#                 raise Exception(f"Logo not found: {logo_img_path}")

#             keypoints = self.detect_human_keypoints(product_img_path)
#             if not keypoints:
#                 raise Exception("No keypoints found")

#             position = self.get_logo_position(keypoints, location_key)
#             if not position:
#                 raise Exception("Position not found")

#             base_img = cv2.imread(product_img_path)
#             logo_img = self.load_logo_image(logo_img_path)
#             if logo_img is None:
#                 raise Exception("Failed to load logo image")

#             resized_logo = self.resize_logo(logo_img, settings["default_logo_width"])
#             merged_img = self.merge_logo_on_image(base_img, resized_logo, position)

#             output_path = os.path.join(settings["output_folder"], job_row["Final Image Name"])
#             cv2.imwrite(output_path, merged_img)

#             return output_path
#         except Exception as e:
#             print(f"Error placing logo: {e}")
#             raise

#     def find_logo_file(self, job_row, logo_folder):
#         print("logo_folder>>>>>>>>>>>",logo_folder)
#         print("job_row>>>>>>>>>",job_row)
#         base_name = job_row["Decoration Code"]
#         color = job_row["Decoration Color"].replace(" ", "_")
#         expected_names = [
#             f"{base_name}.png",
#             f"{base_name}.jpg",
#             f"{base_name}.jpeg",
#             f"{base_name}.pdf"
#             # f"{base_name}_{color}.png",
#             # f"{base_name}_{color}.jpg",
#             # f"{base_name}_{color}.jpeg",
#             # f"{base_name}_{color}.pdf"
#         ]
#         for name in expected_names:
#             full_path = os.path.join(logo_folder, name)
#             if os.path.exists(full_path):
#                 return full_path
#         raise FileNotFoundError(f"Logo file not found for {base_name} ({color})")

#     def load_logo_image(self, logo_path):
#         try:
#             ext = os.path.splitext(logo_path)[1].lower()
#             if ext == ".pdf":
#                 images = convert_from_path(logo_path, dpi=300, fmt="jpeg")
#                 if images:
#                     with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
#                         images[0].save(temp_file.name, "JPEG")
#                         logo_img = cv2.imread(temp_file.name)
#                         os.unlink(temp_file.name)
#                         return logo_img
#                 else:
#                     print(f"No pages found in PDF: {logo_path}")
#                     return None
#             else:
#                 return cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
#         except Exception as e:
#             print(f"Error loading logo image: {e}")
#             return None


# # logo_positioner.py
# # Add at top
# from pdf2image import convert_from_path
# import tempfile
# import os
# import cv2
# import numpy as np
# import mediapipe as mp
# from PIL import Image

# class LogoPositioner:
#     def __init__(self, template_dir):
#         self.template_dir = template_dir
#         self.pose = mp.solutions.pose.Pose(static_image_mode=True)

#     def detect_human_keypoints(self, image_path):
#         try:
#             img = cv2.imread(image_path)
#             if img is None:
#                 raise Exception("Image not found or unreadable")

#             img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#             results = self.pose.process(img_rgb)

#             if not results.pose_landmarks:
#                 return None

#             keypoints = {}
#             for i, lm in enumerate(results.pose_landmarks.landmark):
#                 h, w = img.shape[:2]
#                 keypoints[i] = (int(lm.x * w), int(lm.y * h))

#             return keypoints
#         except Exception as e:
#             print(f"[Keypoint Error] {e}")
#             return None

#     def get_logo_position(self, keypoints, location_key):
#         try:
#             location_map = {
#                 "RIGHT-ELBOW": 14,
#                 "LEFT-ELBOW": 13,
#                 "LEFT-CHEST": 11,
#                 "RIGHT-CHEST": 12,
#                 "FULL-FRONT": 0,
#                 "FULL-BACK": 24,
#                 "LEFT-BICEP": 11,
#                 "RIGHT-BICEP": 12,
#                 "CROWN": 0
#             }

#             landmark_index = location_map.get(location_key.upper())
#             if landmark_index is None or landmark_index not in keypoints:
#                 return None

#             return keypoints[landmark_index]
#         except Exception as e:
#             print(f"[Mapping Error] {e}")
#             return None

#     def resize_logo(self, logo_img, target_width):
#         try:
#             height, width = logo_img.shape[:2]
#             scale_ratio = target_width / float(width)
#             dim = (target_width, int(height * scale_ratio))
#             resized_logo = cv2.resize(logo_img, dim, interpolation=cv2.INTER_AREA)
#             return resized_logo
#         except Exception as e:
#             print(f"Error resizing logo: {e}")
#             return logo_img

#     def merge_logo_on_image(self, base_image, logo_img, position):
#         try:
#             lx, ly = position
#             lh, lw = logo_img.shape[:2]

#             overlay = base_image.copy()

#             for y in range(lh):
#                 for x in range(lw):
#                     if lx + x >= base_image.shape[1] or ly + y >= base_image.shape[0]:
#                         continue
#                     pixel = logo_img[y, x]
#                     if not np.array_equal(pixel, [255, 255, 255]):  # Skip white
#                         overlay[ly + y, lx + x] = pixel
#             return overlay
#         except Exception as e:
#             print(f"Error merging logo: {e}")
#             return base_image

#     def place_logo_on_image(self, job_row, settings, image_folder, logo_folder):
#         try:
#             product_img_path = os.path.join(image_folder, f"{job_row['Supplier Part ID']}.jpg")
#             logo_img_path = self.find_logo_file(job_row, logo_folder)
#             location_key = str(job_row["Location As per Word file"]).strip()

#             if not os.path.exists(product_img_path):
#                 raise Exception(f"Image not found: {product_img_path}")
#             if not os.path.exists(logo_img_path):
#                 raise Exception(f"Logo not found: {logo_img_path}")

#             keypoints = self.detect_human_keypoints(product_img_path)
#             if not keypoints:
#                 raise Exception("No keypoints found")

#             position = self.get_logo_position(keypoints, location_key)
#             if not position:
#                 raise Exception("Position not found")

#             base_img = cv2.imread(product_img_path)
#             logo_img = cv2.imread(logo_img_path, cv2.IMREAD_UNCHANGED)
#             resized_logo = self.resize_logo(logo_img, settings["default_logo_width"])

#             merged_img = self.merge_logo_on_image(base_img, resized_logo, position)

#             output_path = os.path.join(settings["output_folder"], job_row["Final Image Name"])
#             cv2.imwrite(output_path, merged_img)

#             return output_path
#         except Exception as e:
#             print(f"Error placing logo: {e}")
#             raise

#     def find_logo_file(self, job_row, logo_folder):
#         base_name = job_row["Decoration Code"]
#         color = job_row["Decoration Color"].replace(" ", "_")
#         expected_names = [
#             f"{base_name}_{color}.png",
#             f"{base_name}_{color}.jpg"
#         ]
#         for name in expected_names:
#             full_path = os.path.join(logo_folder, name)
#             if os.path.exists(full_path):
#                 return full_path
#         raise FileNotFoundError(f"Logo file not found for {base_name} ({color})")










# # logo_positioner.py

# import cv2
# import numpy as np
# import os
# import mediapipe as mp

# class LogoPositioner:
#     def __init__(self, template_dir, default_logo_width=150):
#         self.template_dir = template_dir
#         self.default_logo_width = default_logo_width
#         self.pose = mp.solutions.pose.Pose(static_image_mode=True)

#     def detect_landmark(self, image_path, location_label):
#         """
#         Use MediaPipe to find human keypoints and map given label to coordinates.
#         E.g., "RIGHT-ELBOW" -> landmark 14
#         """
#         mp_landmarks = {
#             "LEFT-SHOULDER": 11,
#             "RIGHT-SHOULDER": 12,
#             "LEFT-ELBOW": 13,
#             "RIGHT-ELBOW": 14,
#             "LEFT-WRIST": 15,
#             "RIGHT-WRIST": 16,
#             "LEFT-HIP": 23,
#             "RIGHT-HIP": 24,
#         }

#         image = cv2.imread(image_path)
#         if image is None:
#             raise Exception(f"Image not found or unreadable: {image_path}")

#         image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         results = self.pose.process(image_rgb)

#         if not results.pose_landmarks:
#             raise Exception("No human landmarks detected")

#         h, w, _ = image.shape
#         landmark_id = mp_landmarks.get(location_label.upper().replace(" ", "-"))
#         if landmark_id is None:
#             raise Exception(f"Invalid location label: {location_label}")

#         landmark = results.pose_landmarks.landmark[landmark_id]
#         x_px = int(landmark.x * w)
#         y_px = int(landmark.y * h)
#         return (x_px, y_px)

#     def resize_logo(self, logo_img, target_width):
#         if logo_img is None:
#             raise ValueError("Invalid logo image")
#         height, width = logo_img.shape[:2]
#         scale = target_width / float(width)
#         new_dims = (target_width, int(height * scale))
#         return cv2.resize(logo_img, new_dims, interpolation=cv2.INTER_AREA)

#     def place_logo_on_image(self, job, settings, image_folder, logo_folder):
#         try:
#             image_name = job["Supplier Part ID"]
#             color = job["Supplier Color"]
#             logo_file = job["Decoration Code"]
#             logo_color = job["Decoration Color"]
#             location_label = job["Location As per Word file"]

#             image_filename = f"{image_name}_{color}.jpg".replace(" ", "_")
#             image_path = os.path.join(image_folder, image_filename)

#             logo_filename = f"{logo_file}_{logo_color}.png".replace(" ", "_")
#             logo_path = os.path.join(logo_folder, logo_filename)

#             if not os.path.exists(image_path):
#                 raise FileNotFoundError(f"Image not found: {image_path}")

#             if not os.path.exists(logo_path):
#                 raise FileNotFoundError(f"Logo not found: {logo_path}")

#             logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
#             image = cv2.imread(image_path)

#             if logo is None:
#                 raise Exception(f"Failed to read logo: {logo_path}")

#             if image is None:
#                 raise Exception(f"Failed to read image: {image_path}")

#             position = self.detect_landmark(image_path, location_label)
#             if position is None:
#                 raise Exception("Position not found")

#             resized_logo = self.resize_logo(logo, self.default_logo_width)
#             lx, ly = position

#             # Handle alpha transparency
#             if resized_logo.shape[2] == 4:
#                 alpha = resized_logo[:, :, 3] / 255.0
#                 for c in range(0, 3):
#                     y1 = ly
#                     y2 = ly + resized_logo.shape[0]
#                     x1 = lx
#                     x2 = lx + resized_logo.shape[1]

#                     if y2 > image.shape[0] or x2 > image.shape[1]:
#                         continue  # skip if out of bounds

#                     image[y1:y2, x1:x2, c] = (
#                         alpha * resized_logo[:, :, c] +
#                         (1 - alpha) * image[y1:y2, x1:x2, c]
#                     )
#             else:
#                 image[ly:ly + resized_logo.shape[0], lx:lx + resized_logo.shape[1]] = resized_logo

#             # Save intermediate file
#             output_path = os.path.join("output", "temp", job["Final Image Name"])
#             os.makedirs(os.path.dirname(output_path), exist_ok=True)
#             cv2.imwrite(output_path, image)

#             return output_path
#         except Exception as e:
#             print(f"Error placing logo: {e}")
#             raise
