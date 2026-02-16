import io
import requests
import numpy as np
import random
from PIL import Image


class StegoEngine:
    def _get_wildlife_carrier(self):
        """
        Fetches a beautiful nature/wildlife image using a robust list of
        direct, high-speed source URLs. This avoids API blocking issues.
        """
        # A massive list of high-quality, direct-link images (Nature & Wildlife).
        # These include pre-set width parameters (?w=800) for faster loading.
        reliable_sources = [
            # --- Wildlife (Lions, Tigers, Wolves, Eagles) ---
            "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800&q=80",  # Lion
            "https://images.unsplash.com/photo-1533730717864-73f74546b88f?w=800&q=80",  # Tiger
            "https://images.unsplash.com/photo-1474511320721-79a0c259c277?w=800&q=80",  # Fox
            "https://images.unsplash.com/photo-1452570053594-1b985d6ea82e?w=800&q=80",  # Bird
            "https://images.unsplash.com/photo-1437622368342-7a3d73a34c8f?w=800&q=80",  # Turtle
            "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800&q=80",  # Panda
            "https://images.unsplash.com/photo-1504006833117-8886a36e6bf3?w=800&q=80",  # Elephant
            "https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=800&q=80",  # Leopard
            "https://images.unsplash.com/photo-1495360019602-e001921678fe?w=800&q=80",  # Owl

            # --- Landscapes (Mountains, Forests, Oceans) ---
            "https://images.unsplash.com/photo-1470093851219-69951fcbb533?w=800&q=80",  # Forest
            "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&q=80",  # Lake
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",  # Mountains
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&q=80",  # Canyon
            "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=800&q=80",  # Hills
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",  # Beach
            "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&q=80",  # Snow
            "https://images.unsplash.com/photo-1500829248997-712c73d07f67?w=800&q=80",  # Jungle

            # --- Pexels Backups ---
            "https://images.pexels.com/photos/414612/pexels-photo-414612.jpeg?auto=compress&cs=tinysrgb&w=800",
            "https://images.pexels.com/photos/3225517/pexels-photo-3225517.jpeg?auto=compress&cs=tinysrgb&w=800",
            "https://images.pexels.com/photos/15286/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=800"
        ]

        # Randomly shuffle the list to ensure variety every time
        random.shuffle(reliable_sources)

        # User-Agent to look like a real browser (prevents 403 blocks)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Try up to 3 random images from the list before giving up
        for i in range(3):
            try:
                url = reliable_sources[i]  # Pick the next one in the shuffled list
                response = requests.get(url, headers=headers, timeout=5)

                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                    # Strict resize to 800x600 to ensure app.py compatibility
                    return img.resize((800, 600))
            except Exception:
                continue  # If one fails, loop to the next immediately

        # FALLBACK: If user has ZERO internet, generate a clean gradient
        # This prevents the app from crashing.
        r = np.linspace(20, 50, 600 * 800).reshape(600, 800).astype(np.uint8)
        g = np.linspace(60, 120, 600 * 800).reshape(600, 800).astype(np.uint8)
        b = np.linspace(20, 50, 600 * 800).reshape(600, 800).astype(np.uint8)
        return Image.fromarray(np.stack([r, g, b], axis=-1))

    def hide_data(self, image_file, hex_payload, use_wildlife=False):
        """Standard LSB embedding logic used in the Vari-Crypt project."""
        if use_wildlife:
            img = self._get_wildlife_carrier()
        elif image_file is None:
            img = Image.fromarray(np.zeros((600, 800, 3), dtype=np.uint8))
        else:
            img = Image.open(image_file).convert("RGB")
            img = img.resize((800, 600))

        pixels = np.array(img)
        orig_shape = pixels.shape
        flat_pixels = pixels.flatten()

        binary_data = bin(int(hex_payload, 16))[2:].zfill(len(hex_payload) * 4)
        binary_data += '1111111111111110'

        if len(binary_data) > len(flat_pixels):
            raise ValueError("Payload too large for carrier capacity.")

        for i in range(len(binary_data)):
            flat_pixels[i] = (flat_pixels[i] & 254) | int(binary_data[i])

        new_pixels = flat_pixels.reshape(orig_shape)
        result_img = Image.fromarray(new_pixels.astype(np.uint8))

        buf = io.BytesIO()
        result_img.save(buf, format="PNG")  # Lossless PNG is mandatory for LSB
        return buf.getvalue()

    def reveal_data(self, image_file):
        """LSB recovery logic to extract the hidden hex data."""
        img = Image.open(image_file).convert("RGB")
        pixels = np.array(img).flatten()
        binary_data = ""
        for p in pixels:
            binary_data += str(p & 1)
            if binary_data.endswith('1111111111111110'):
                break
        clean_bin = binary_data[:-16]
        return hex(int(clean_bin, 2))[2:] if clean_bin else ""
