# logo_positioner.py
import os
import tempfile
import traceback

import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import mediapipe as mp

try:
    import fitz  # PyMuPDF for robust PDF rasterization fallback
except Exception:  # pragma: no cover
    fitz = None


class LogoPositioner:
    def __init__(self, template_dir):
        self.template_dir = template_dir
        self.pose = mp.solutions.pose.Pose(static_image_mode=True)
        self.pose_landmark = mp.solutions.pose.PoseLandmark

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
    # Compute heuristic positions for locations
    # ---------------------------
    def get_logo_position(self, keypoints, location_key, image_shape=None):
        try:
            if not location_key:
                return None
            label = str(location_key).upper().strip()

            def get(idx):
                if not keypoints:
                    return None
                try:
                    index = int(idx.value)
                except AttributeError:
                    index = int(idx)
                return keypoints.get(index)

            # Helpful indices
            LM = self.pose_landmark
            nose = get(LM.NOSE)
            ls = get(LM.LEFT_SHOULDER)
            rs = get(LM.RIGHT_SHOULDER)
            le = get(LM.LEFT_ELBOW)
            re = get(LM.RIGHT_ELBOW)
            lw = get(LM.LEFT_WRIST)
            rw = get(LM.RIGHT_WRIST)
            lh = get(LM.LEFT_HIP)
            rh = get(LM.RIGHT_HIP)
            learp = get(LM.LEFT_EAR)
            rearp = get(LM.RIGHT_EAR)

            def midpoint(p1, p2):
                if not p1 or not p2:
                    return None
                return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)

            def dist(p1, p2):
                if not p1 or not p2:
                    return None
                return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

            def along(p1, p2, t):
                if not p1 or not p2:
                    return None
                return (int(p1[0] + t * (p2[0] - p1[0])), int(p1[1] + t * (p2[1] - p1[1])))

            shoulder_mid = midpoint(ls, rs)
            shoulder_span = dist(ls, rs) or 0

            # Default: center of image
            if image_shape is not None:
                img_h, img_w = image_shape[:2]
                default_center = (img_w // 2, img_h // 2)
            else:
                default_center = None

            # Chest positions
            if label in ("LEFT-CHEST", "RIGHT-CHEST", "FULL-FRONT", "FRONT_CENTER"):
                if shoulder_mid and shoulder_span:
                    # Place below shoulder line by ~22% of shoulder width
                    offset_y = int(0.22 * shoulder_span)
                    base = (shoulder_mid[0], shoulder_mid[1] + offset_y)
                    if label == "LEFT-CHEST" and ls and rs:
                        base = (int(shoulder_mid[0] - 0.18 * shoulder_span), base[1])
                    elif label == "RIGHT-CHEST" and ls and rs:
                        base = (int(shoulder_mid[0] + 0.18 * shoulder_span), base[1])
                    return base
                return default_center

            # Bicep/sleeve positions along upper arms
            if label in ("LEFT-BICEP", "LEFT-SLEEVE", "LEFT-CUFF"):
                if ls and le and lw:
                    if label == "LEFT-BICEP":
                        return along(ls, le, 0.55)
                    if label == "LEFT-SLEEVE":
                        return along(ls, le, 0.75)
                    if label == "LEFT-CUFF":
                        return along(le, lw, 0.85)
                return default_center

            if label in ("RIGHT-BICEP", "RIGHT-SLEEVE", "RIGHT-CUFF"):
                if rs and re and rw:
                    if label == "RIGHT-BICEP":
                        return along(rs, re, 0.55)
                    if label == "RIGHT-SLEEVE":
                        return along(rs, re, 0.75)
                    if label == "RIGHT-CUFF":
                        return along(re, rw, 0.85)
                return default_center

            # Collar / Yoke
            if label in ("LEFT-COLLAR", "RIGHT-COLLAR", "BACK-YOKE"):
                if shoulder_mid and shoulder_span:
                    offset_y = int(-0.05 * shoulder_span)
                    base = (shoulder_mid[0], shoulder_mid[1] + offset_y)
                    if label == "LEFT-COLLAR" and ls and rs:
                        base = (int(shoulder_mid[0] - 0.12 * shoulder_span), base[1])
                    if label == "RIGHT-COLLAR" and ls and rs:
                        base = (int(shoulder_mid[0] + 0.12 * shoulder_span), base[1])
                    return base
                return default_center

            # Hips
            if label == "LEFT-HIP" and lh:
                return lh
            if label == "RIGHT-HIP" and rh:
                return rh

            # Thigh-high approximations using hips -> knees aren't available reliably in all crops; fallback to hips
            if label in ("LEFT-THIGH-HIGH", "RIGHT THIGH-HIGH"):
                return lh or rh or default_center

            # Pocket
            if label in ("ON-POCKET", "ON POCKET (ON BAG)"):
                if shoulder_mid and shoulder_span:
                    return (shoulder_mid[0], int(shoulder_mid[1] + 0.35 * shoulder_span))
                return default_center

            # Bags/front generic
            if label in ("FRONT (ON BAG)",):
                return default_center

            # Crown / caps using ears/eyes/nose
            if label in ("FRONT-CROWN", "LOWER-LEFT-CROWN", "LOWER-RIGHT-CROWN", "CAP-FRONT-SIDE", "CAP-SIDE", "CAP-BACK"):
                head_mid = midpoint(learp, rearp) or nose or shoulder_mid or default_center
                if head_mid and learp and rearp:
                    head_w = dist(learp, rearp) or (shoulder_span * 0.6 if shoulder_span else 100)
                else:
                    head_w = 100
                # front crown just above forehead
                base = (head_mid[0], head_mid[1] - int(0.2 * head_w)) if head_mid else default_center
                if label == "LOWER-LEFT-CROWN":
                    base = (base[0] - int(0.2 * head_w), base[1] + int(0.1 * head_w)) if base else base
                if label == "LOWER-RIGHT-CROWN":
                    base = (base[0] + int(0.2 * head_w), base[1] + int(0.1 * head_w)) if base else base
                return base

            # Full front/back and combined: use chest center as anchor
            if label in (
                "FULL-FRONT", "FULL-BACK", "FULL-FRONT-FULL-BACK", "FULL-BACK & FULL-FRONT",
                "LEFT-CHEST-LEFT-BICEP-RIGHT-BICEP", "LEFT-SLEEVE-RIGHT-SLEEVE",
                "LEFT-CHEST-RIGHT-BICEP", "LEFT-CHEST-RIGHT-SLEEVE",
                "RIGHT-CHEST-LEFT-BICEP", "RIGHT-CHEST-LEFT-SLEEVE",
                "RIGHT-CHEST-LFT-BICEP-RIGHT-BICEP",
                "LEFT-CHEST-FULL-BACK", "RIGHT-CHEST-FULL-BACK"
            ):
                if shoulder_mid and shoulder_span:
                    return (shoulder_mid[0], shoulder_mid[1] + int(0.22 * shoulder_span))
                return default_center

            # If label unknown, return default center
            return default_center
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
                logo_bgr = logo_bgr[:, : bw - lx]
                alpha = alpha[:, : bw - lx]
            if ly + lh > bh:
                logo_bgr = logo_bgr[: bh - ly, :]
                alpha = alpha[: bh - ly, :]

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

            base_img = cv2.imread(product_img_path)
            if base_img is None:
                raise Exception("Failed to load base image: " + str(product_img_path))

            # Detect keypoints for AI placement
            keypoints = self.detect_human_keypoints(product_img_path)
            # Heuristic position with safe fallback to center
            position = self.get_logo_position(keypoints, location_key, image_shape=base_img.shape)
            if not position:
                h, w = base_img.shape[:2]
                position = (w // 2, h // 3)

            base_img = self.remove_background(base_img)

            # Load logo (pass poppler_path if provided in settings)
            poppler_path = settings.get("poppler_path") if isinstance(settings, dict) else None
            logo_img = self.load_logo_image(logo_img_path, poppler_path=poppler_path)
            print("logo_imglogo_img>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logo_img_path)
            if logo_img is None:
                raise Exception("Failed to load logo image: " + str(logo_img_path))

            target_width = int(settings.get("default_logo_width", 150))
            resized_logo = self.resize_logo(logo_img, target_width)
            merged_img = self.merge_logo_on_image(base_img, resized_logo, position)

            output_path = os.path.join(settings["output_folder"], job_row["Final Image Name"])
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, merged_img)
            print("output_pathoutput_path>>>>>>>>>>>>>>>>>", output_path)

            # Prepare Photoshop placement data for optional export
            placement = {
                "base_image_path": product_img_path,
                "logo_image_path": logo_img_path,
                "x": int(position[0]),
                "y": int(position[1]),
                "logo_width": target_width,
            }
            # Return output path (composited image) and placement info
            return output_path, placement
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
    # Find product image by searching filenames (robust matching)
    # ---------------------------
    def find_image_file(self, client_dir, supplier_part_and_color):
        if not os.path.isdir(client_dir):
            return None

        # Normalize tokens (split into part id and optional color)
        tokens = [t for t in supplier_part_and_color.replace("_", " ").replace("-", " ").split(" ") if t]
        tokens_lower = [t.lower() for t in tokens]

        best_match = None
        best_score = -1

        for root, _, files in os.walk(client_dir):
            for file in files:
                if not file.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                fname = file.lower().replace("_", " ").replace("-", " ")

                # Score match: count how many tokens appear
                score = sum(1 for t in tokens_lower if t in fname)
                # Fallback: if only part id present (first token), still accept
                if score > best_score or (score == best_score and best_match is None):
                    best_match = os.path.join(root, file)
                    best_score = score

                # Perfect match if both tokens found
                if best_score >= max(1, len(tokens_lower)):
                    return best_match

        # Return best available candidate (may be based on part id only)
        return best_match

    # ---------------------------
    # Helper: convert PIL -> cv2 and load files (PIL + pdf2image + PyMuPDF fallback)
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
        For PDFs: tries convert_from_path with explicit poppler_path then falls back to PyMuPDF.
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

            # PDF handling
            if ext == ".pdf":
                # Try pdf2image with poppler
                last_exc = None
                if poppler_path:
                    try:
                        pages = convert_from_path(logo_path, poppler_path=poppler_path, dpi=300, fmt="jpeg")
                        if pages:
                            pil_img = pages[0].convert("RGBA")
                            return self.pil_to_cv2(pil_img)
                    except Exception as e:
                        last_exc = e
                        print(f"convert_from_path with poppler_path failed: {e}")
                # Try without explicit poppler (if configured in PATH on system)
                try:
                    pages = convert_from_path(logo_path, dpi=300, fmt="jpeg")
                    if pages:
                        pil_img = pages[0].convert("RGBA")
                        return self.pil_to_cv2(pil_img)
                except Exception as e:
                    last_exc = e
                    print("convert_from_path without explicit poppler_path failed:", e)
                # Fallback to PyMuPDF if available
                if fitz is not None:
                    try:
                        with fitz.open(logo_path) as doc:
                            page = doc.load_page(0)
                            pix = page.get_pixmap(dpi=300, alpha=True)
                            img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
                            return self.pil_to_cv2(img)
                    except Exception as e:
                        last_exc = e
                        print("PyMuPDF conversion failed:", e)
                print("PDF -> image conversion failed. Last exception:", last_exc)
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
