import numpy as np
from PIL import Image
import zlib
import hashlib
import math


class EnhancedImageStego:
    def hide_data(self, cover_path, secret_path, output_path, password):
        """Hides massive media files inside an image, auto-scaling if necessary."""
        with open(secret_path, "rb") as f:
            data = f.read()

        key = hashlib.sha256(password.encode()).digest()
        enc = bytearray(b ^ key[i % len(key)] for i, b in enumerate(data))
        payload = zlib.compress(enc, level=9) + b"==END=="

        # High-speed NumPy bit shifting
        chunks = np.zeros(len(payload) * 4, dtype=np.uint8)
        payload_arr = np.frombuffer(payload, dtype=np.uint8)
        chunks[0::4] = (payload_arr >> 6) & 3
        chunks[1::4] = (payload_arr >> 4) & 3
        chunks[2::4] = (payload_arr >> 2) & 3
        chunks[3::4] = payload_arr & 3

        img = Image.open(cover_path).convert("RGB")
        req_pixels = len(chunks)

        # DYNAMIC AUTO-SCALE: If the cover is too small, stretch it!
        if (img.width * img.height * 3) < req_pixels:
            new_side = math.ceil(math.sqrt(req_pixels / 3.0)) + 5
            img = img.resize((new_side, new_side), Image.Resampling.LANCZOS)

        pixels = np.array(img).flatten()

        # Inject payload
        pixels[:len(chunks)] = (pixels[:len(chunks)] & 252) | chunks

        new_img = Image.fromarray(pixels.reshape((img.height, img.width, 3)).astype(np.uint8))
        new_img.save(output_path, "PNG")

    def reveal_data(self, stego_path, password):
        """Extracts the massive file back out of the image matrix."""
        img = Image.open(stego_path).convert("RGB")
        pixels = np.array(img).flatten()

        # Fast extraction loop
        extracted = bytearray()
        for i in range(0, len(pixels), 4):
            if i + 3 >= len(pixels): break
            b = (pixels[i] & 3) << 6 | (pixels[i + 1] & 3) << 4 | (pixels[i + 2] & 3) << 2 | (pixels[i + 3] & 3)
            extracted.append(b)
            if extracted.endswith(b"==END=="):
                break

        try:
            dec = zlib.decompress(extracted[:-7])
            key = hashlib.sha256(password.encode()).digest()
            return bytes(b ^ key[i % len(key)] for i, b in enumerate(dec))
        except Exception:
            return None