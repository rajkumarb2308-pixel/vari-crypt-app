from stegano import lsb
from PIL import Image, ImageDraw
import io
import random


class StegoEngine:
    def generate_cosmic_carrier(self):
        """Generates a 500x500 Interstellar-style nebula from scratch."""
        img = Image.new('RGB', (500, 500), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw Stars
        for _ in range(350):
            x, y = random.randint(0, 499), random.randint(0, 499)
            brightness = random.randint(180, 255)
            draw.point((x, y), fill=(brightness, brightness, brightness))

        # Draw Nebula Gas
        for _ in range(6):
            center = (random.randint(50, 450), random.randint(50, 450))
            radius = random.randint(40, 160)
            color = random.choice([(15, 35, 70), (45, 15, 55), (20, 55, 45)])
            draw.ellipse([center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius], fill=color)

        return img

    def hide_data(self, image_input, secret_hex, auto_generate=False):
        """Hides hex data in either an uploaded or generated image."""
        if auto_generate:
            img = self.generate_cosmic_carrier()
        else:
            img = Image.open(image_input)

        secret_img = lsb.hide(img, secret_hex)
        buf = io.BytesIO()
        secret_img.save(buf, format="PNG")
        return buf.getvalue()

    def reveal_data(self, image_file):
        """Reveals hex data hidden in an image."""
        try:
            img = Image.open(image_file)
            return lsb.reveal(img)
        except Exception:
            raise ValueError("No cosmic data found in this transmission.")