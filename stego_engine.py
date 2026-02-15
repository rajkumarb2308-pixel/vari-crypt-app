from stegano import lsb
from PIL import Image, ImageDraw
import io
import random
import math
import requests  # Needed to fetch nature images


class StegoEngine:
    def _fetch_online_nature_image(self):
        """
        Attempts to fetch a random high-quality wildlife/nature image.
        Returns PIL Image or None if internet fails.
        """
        try:
            # Keywords to ensure we get nature shots
            keywords = random.choice(["wildlife", "tiger", "forest", "eagle", "ocean", "mountain"])
            # Request 800x600 image from LoremFlickr
            url = f"https://loremflickr.com/800/600/{keywords}"

            # 3-second timeout prevents hanging
            response = requests.get(url, timeout=3)

            if response.status_code == 200:
                img_bytes = io.BytesIO(response.content)
                return Image.open(img_bytes).convert("RGB")
            else:
                return None
        except Exception:
            return None  # Internet down or blocked

    def _generate_cosmic_fallback(self, width=600, height=600):
        """
        Fallback: Generates a starfield if we can't get a real photo.
        """
        img = Image.new('RGB', (width, height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Stars
        for _ in range(int(width * height * 0.002)):
            x, y = random.randint(0, width - 1), random.randint(0, height - 1)
            b = random.randint(150, 255)
            draw.point((x, y), fill=(b, b, b))

        # Nebulas
        for _ in range(5):
            x, y = random.randint(50, width - 50), random.randint(50, height - 50)
            r = random.randint(40, 150)
            color = random.choice([(20, 40, 80), (50, 20, 60), (20, 60, 40)])
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        return img

    def hide_data(self, image_input, secret_hex, auto_generate=False):
        """
        Universal Hide: Handles Uploads, Auto-Gen, and Resizing.
        """
        # --- STEP 1: ACQUIRE IMAGE ---
        if auto_generate:
            img = self._fetch_online_nature_image()
            if img is None:
                img = self._generate_cosmic_fallback()
        else:
            # Handle UploadedFile from Streamlit
            img = Image.open(image_input).convert("RGB")

        # --- STEP 2: SMART RESIZE ---
        # LSB needs space. We calculate if the image is big enough.
        current_pixels = img.width * img.height
        needed_pixels = len(secret_hex) * 4  # Safety margin

        if current_pixels < needed_pixels:
            scale = math.ceil(math.sqrt(needed_pixels / current_pixels))
            scale = max(scale, 1.1)  # Scale up at least 10%
            new_size = (int(img.width * scale), int(img.height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # --- STEP 3: HIDE DATA ---
        try:
            secret_img = lsb.hide(img, secret_hex)

            buf = io.BytesIO()
            secret_img.save(buf, format="PNG")
            return buf.getvalue()
        except Exception as e:
            raise ValueError(f"Steganography encoding failed: {str(e)}")

    def reveal_data(self, image_file):
        try:
            img = Image.open(image_file).convert("RGB")
            return lsb.reveal(img)
        except Exception:
            raise ValueError("No hidden data found in this image.")
