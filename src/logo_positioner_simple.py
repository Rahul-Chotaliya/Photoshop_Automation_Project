# Simplified logo positioner without MediaPipe dependency
import os
import tempfile
import traceback
import cv2
import numpy as np
from PIL import Image

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

try:
    import fitz  # PyMuPDF for robust PDF rasterization fallback
except Exception:
    fitz = None


class SimpleLogoPositioner:
    def __init__(self, template_dir=None):
        self.template_dir = template_dir

    def get_logo_position(self, location_key, image_shape):
        """Simple heuristic positioning without AI"""
        try:
            if not location_key:
                return None
            label = str(location_key).upper().strip()
            
            h, w = image_shape[:2]
            
            # Simple positioning based on location
            if "FRONT" in label:
                return (w // 2, h // 3)  # Center front
            elif "BACK" in label:
                return (w // 2, h // 2)  # Center back
            elif "LEFT" in label:
                return (w // 4, h // 3)  # Left side
            elif "RIGHT" in label:
                return (3 * w // 4, h // 3)  # Right side
            elif "CHEST" in label:
                return (w // 2, h // 4)  # Upper chest
            elif "SLEEVE" in label:
                return (w // 2, h // 2)  # Sleeve area
            else:
                return (w // 2, h // 3)  # Default center
                
        except Exception as e:
            print(f"[Position Error] {e}")
            h, w = image_shape[:2]
            return (w // 2, h // 3)  # Safe fallback

    def resize_logo(self, logo_img, target_width):
        """Resize logo while preserving aspect ratio"""
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
            return logo_img

    def remove_background(self, image):
        """Simple background removal"""
        try:
            if image is None:
                return image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            result = cv2.bitwise_and(image, image, mask=mask_inv)
            return result
        except Exception as e:
            print(f"Background removal failed: {e}")
            return image

    def merge_logo_on_image(self, base_image, logo_img, position):
        """Merge logo onto base image"""
        try:
            if base_image is None or logo_img is None or position is None:
                return base_image

            lx, ly = int(position[0]), int(position[1])

            # Handle logo alpha channel
            if logo_img.ndim == 3 and logo_img.shape[2] == 4:
                logo_bgr = logo_img[:, :, :3]
                alpha = logo_img[:, :, 3] / 255.0
            else:
                logo_bgr = logo_img
                # Create alpha mask where non-white is opaque
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

            # Final region sizes
            lh, lw = logo_bgr.shape[:2]
            if lx + lw > bw:
                logo_bgr = logo_bgr[:, : bw - lx]
                alpha = alpha[:, : bw - lx]
            if ly + lh > bh:
                logo_bgr = logo_bgr[: bh - ly, :]
                alpha = alpha[: bh - ly, :]

            # Region of interest
            roi = base_image[ly:ly + logo_bgr.shape[0], lx:lx + logo_bgr.shape[1]]

            # Alpha blending
            alpha = alpha[..., np.newaxis]
            blended = (alpha * logo_bgr.astype(float) + (1 - alpha) * roi.astype(float)).astype(np.uint8)

            base_image[ly:ly + blended.shape[0], lx:lx + blended.shape[1]] = blended
            return base_image

        except Exception as e:
            print(f"Error merging logo: {e}")
            return base_image

    def place_logo_on_image(self, job_row, settings, image_root, logo_folder):
        """Main method to place logo on image"""
        try:
            client_folder = os.path.join(image_root, job_row["Supplier Name"])
            image_name = f"{job_row['Supplier Part ID']} {job_row.get('Supplier Color', '')}".strip()
            product_img_path = self.find_image_file(client_folder, image_name)
            
            print(f"Looking for image: {image_name} in {client_folder}")
            
            if not product_img_path:
                raise Exception(f"Image not found for {job_row['Supplier Part ID']} in {client_folder}")

            logo_img_path = self.find_logo_file(job_row, logo_folder)
            location_key = str(job_row.get("Location As per Word file", "")).strip()

            base_img = cv2.imread(product_img_path)
            if base_img is None:
                raise Exception("Failed to load base image: " + str(product_img_path))

            # Get position using simple heuristics
            position = self.get_logo_position(location_key, base_img.shape)
            if not position:
                h, w = base_img.shape[:2]
                position = (w // 2, h // 3)

            base_img = self.remove_background(base_img)

            # Load logo
            logo_img = self.load_logo_image(logo_img_path)
            if logo_img is None:
                raise Exception("Failed to load logo image: " + str(logo_img_path))

            target_width = int(settings.get("default_logo_width", 150))
            resized_logo = self.resize_logo(logo_img, target_width)
            merged_img = self.merge_logo_on_image(base_img, resized_logo, position)

            output_path = os.path.join(settings["output_folder"], job_row["Final Image Name"])
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, merged_img)
            print(f"Saved output: {output_path}")

            # Prepare placement data
            placement = {
                "base_image_path": product_img_path,
                "logo_image_path": logo_img_path,
                "x": int(position[0]),
                "y": int(position[1]),
                "logo_width": target_width,
            }
            
            return output_path, placement
            
        except Exception as e:
            print(f"Error placing logo: {e}")
            traceback.print_exc()
            raise

    def find_logo_file(self, job_row, logo_folder):
        """Find logo file by decoration code"""
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

    def find_image_file(self, client_dir, supplier_part_and_color):
        """Find product image file"""
        if not os.path.isdir(client_dir):
            return None

        # Normalize tokens
        tokens = [t for t in supplier_part_and_color.replace("_", " ").replace("-", " ").split(" ") if t]
        tokens_lower = [t.lower() for t in tokens]

        best_match = None
        best_score = -1

        for root, _, files in os.walk(client_dir):
            for file in files:
                if not file.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                fname = file.lower().replace("_", " ").replace("-", " ")

                # Score match
                score = sum(1 for t in tokens_lower if t in fname)
                if score > best_score or (score == best_score and best_match is None):
                    best_match = os.path.join(root, file)
                    best_score = score

                if best_score >= max(1, len(tokens_lower)):
                    return best_match

        return best_match

    @staticmethod
    def pil_to_cv2(pil_img):
        """Convert PIL image to OpenCV format"""
        arr = np.array(pil_img)
        if arr.ndim == 2:  # grayscale
            return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        if arr.shape[2] == 4:  # RGBA -> BGRA
            return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGRA)
        # RGB -> BGR
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    def load_logo_image(self, logo_path):
        """Load logo image from file"""
        try:
            if not logo_path or not os.path.exists(logo_path):
                print(f"Logo file not found: {logo_path}")
                return None

            ext = os.path.splitext(logo_path)[1].lower()
            print(f"Loading logo: {logo_path} (extension: {ext})")

            # PDF handling
            if ext == ".pdf":
                if convert_from_path:
                    try:
                        pages = convert_from_path(logo_path, dpi=300, fmt="jpeg")
                        if pages:
                            pil_img = pages[0].convert("RGBA")
                            return self.pil_to_cv2(pil_img)
                    except Exception as e:
                        print(f"PDF conversion failed: {e}")
                
                if fitz:
                    try:
                        with fitz.open(logo_path) as doc:
                            page = doc.load_page(0)
                            pix = page.get_pixmap(dpi=300, alpha=True)
                            img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
                            return self.pil_to_cv2(img)
                    except Exception as e:
                        print(f"PyMuPDF conversion failed: {e}")
                
                print("PDF conversion not available")
                return None

            # Image handling
            try:
                pil_img = Image.open(logo_path)
                if pil_img.mode == "CMYK":
                    pil_img = pil_img.convert("RGB")
                elif pil_img.mode in ("P", "L"):
                    pil_img = pil_img.convert("RGBA")
                if pil_img.mode not in ("RGB", "RGBA"):
                    pil_img = pil_img.convert("RGBA")

                return self.pil_to_cv2(pil_img)

            except Exception as e:
                print(f"PIL failed, trying cv2: {e}")
                try:
                    return cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
                except Exception as e2:
                    print(f"cv2 also failed: {e2}")
                    return None

        except Exception as e:
            print(f"Error loading logo: {e}")
            return None