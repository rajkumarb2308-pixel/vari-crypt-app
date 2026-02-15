import io
import requests
import numpy as np
import random
from PIL import Image


class StegoEngine:
    def _get_wildlife_carrier(self):
        """
        Uses a bulletproof multi-source approach to ensure high-quality
        wildlife and nature images are always retrieved.
        """
        # A curated list of direct-link high-resolution wildlife and nature images.
        # Using direct IDs is much more reliable than 'random' endpoints.
        diverse_links = [
            "https://images.pexels.com/photos/33045/lion-wild-africa-african.jpg",
            "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg",
            "https://images.pexels.com/photos/1450353/pexels-photo-1450353.jpeg",
            "https://images.pexels.com/photos/358457/pexels-photo-358457.jpeg",
            "https://images.pexels.com/photos/52713/tiger-face-tiger-wild-animal-52713.jpeg",
            "https://images.pexels.com/photos/3408744/pexels-photo-3408744.jpeg",
            "https://images.pexels.com/photos/1624496/pexels-photo-1624496.jpeg",
            "https://images.pexels.com/photos/62627/pexels-photo-62627.jpeg"
        ]

        # We also keep a rotating "Random Nature" source as a secondary option
        random_nature_sources = [
            f"https://picsum.photos/800/600?nature={random.randint(1, 1000)}",
            f"https://loremflickr.com/800/600/wildlife?lock={random.randint(1, 1000)}"
        ]

        # Combine them for maximum variety
        all_sources = diverse_links + random_nature_sources
        random.shuffle(all_sources)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for url in all_sources:
            try:
                # Using a shorter timeout to cycle through sources quickly if one is blocked
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                    # Strict resizing to ensure the LSB math in app1.py remains perfect
                    return img.resize((800, 600))
            except Exception:
                continue

        # ULTIMATE FALLBACK: If internet is completely out, generate a high-quality
        # green/brown forest gradient that looks professional for a demo.
        r = np.linspace(20, 40, 600 * 800).reshape(600, 800).astype(np.uint8)
        g = np.linspace(60, 100, 600 * 800).reshape(600, 800).astype(np.uint8)
        b = np.linspace(20, 40, 600 * 800).reshape(600, 800).astype(np.uint8)
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
