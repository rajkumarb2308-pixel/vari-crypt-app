from stegano import lsb
from PIL import Image, ImageDraw
import io
import random

class StegoEngine:
    def generate_cosmic_carrier(self):
        """Generates a unique high-fidelity 500x500 nebula carrier."""
        img = Image.new('RGB', (500, 500), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        for _ in range(350):
            x, y = random.randint(0, 499), random.randint(0, 499)
            brightness = random.randint(180, 255)
            draw.point((x, y), fill=(brightness, brightness, brightness))
        for _ in range(6):
            center = (random.randint(50, 450), random.randint(50, 450))
            radius = random.randint(40, 160)
            color = random.choice([(15, 35, 70), (45, 15, 55), (20, 55, 45)])
            draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], fill=color)
        return img

    def hide_data(self, image_input, secret_hex, auto_generate=False):
        """Accepts PNG/JPG and hides data. Output is ALWAYS PNG for integrity."""
        if auto_generate:
            img = self.generate_cosmic_carrier()
        else:
            # .convert("RGB") ensures JPG and PNG follow the same pixel logic
            img = Image.open(image_input).convert("RGB")
            
        secret_img = lsb.hide(img, secret_hex)
        
        # We must save as PNG because JPG compression destroys LSB data
        buf = io.BytesIO()
        secret_img.save(buf, format="PNG")
        return buf.getvalue()

    def reveal_data(self, image_file):
        """Universal extraction for any supported format."""
        try:
            img = Image.open(image_file).convert("RGB")
            return lsb.reveal(img)
        except Exception:
            raise ValueError("No cosmic data found in this transmission.")
