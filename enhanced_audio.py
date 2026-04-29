import wave
import subprocess
import os
import zlib
import hashlib
import math
import numpy as np


class EnhancedAudioStego:
    def hide_data(self, cover_path, secret_path, output_path, password):
        """Hides massive media files inside audio, auto-looping if necessary."""
        temp_wav = "temp_v2.wav"
        subprocess.run(["ffmpeg", "-y", "-i", cover_path, "-c:a", "pcm_s16le", "-f", "wav", temp_wav], check=True,
                       stderr=subprocess.DEVNULL)

        with open(secret_path, "rb") as f:
            data = f.read()

        key = hashlib.sha256(password.encode()).digest()
        enc = bytearray(b ^ key[i % len(key)] for i, b in enumerate(data))
        payload = zlib.compress(enc, level=9) + b"==END=="

        # Fast bit unpacking
        bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))

        with wave.open(temp_wav, "rb") as song:
            params = list(song.getparams())
            frames = bytearray(song.readframes(song.getnframes()))

        # DYNAMIC AUTO-LOOP: If audio is too short, duplicate it!
        if len(bits) > len(frames):
            multiplier = math.ceil(len(bits) / len(frames))
            frames = frames * multiplier
            params[3] = len(frames) // (params[0] * params[1])  # Update total frames count

        frames_arr = np.frombuffer(frames, dtype=np.uint8).copy()

        # Inject payload
        frames_arr[:len(bits)] = (frames_arr[:len(bits)] & 254) | bits

        with wave.open(output_path, "wb") as f:
            f.setparams(params)
            f.writeframes(frames_arr.tobytes())

        os.remove(temp_wav)

    def reveal_data(self, stego_path, password):
        """Extracts the massive file back out of the audio frequencies."""
        try:
            with wave.open(stego_path, "rb") as song:
                frames = bytearray(song.readframes(song.getnframes()))
        except Exception:
            return None

        frames_arr = np.frombuffer(frames, dtype=np.uint8)
        bits = frames_arr & 1

        # Pack bits back to bytes
        extracted = bytearray()
        for i in range(0, len(bits), 8):
            if i + 7 >= len(bits): break
            byte = (bits[i] << 7) | (bits[i + 1] << 6) | (bits[i + 2] << 5) | (bits[i + 3] << 4) | (
                        bits[i + 4] << 3) | (bits[i + 5] << 2) | (bits[i + 6] << 1) | bits[i + 7]
            extracted.append(byte)
            if extracted.endswith(b"==END=="): break

        try:
            dec = zlib.decompress(extracted[:-7])
            key = hashlib.sha256(password.encode()).digest()
            return bytes(b ^ key[i % len(key)] for i, b in enumerate(dec))
        except Exception:
            return None