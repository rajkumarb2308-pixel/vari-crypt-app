import wave
import io
import os
import subprocess
import shutil


class AudioStego:
    def _get_ffmpeg_path(self):
        """
        Smart detection:
        1. Checks for 'ffmpeg.exe' in the current folder (for your Laptop/Windows).
        2. Falls back to system 'ffmpeg' (for Render/Cloud/Linux).
        """
        local_path = os.path.join(os.getcwd(), "ffmpeg.exe")

        # Priority 1: Use the local file if it exists (Windows Local)
        if os.path.exists(local_path):
            return local_path

        # Priority 2: Use the system command (Cloud / Linux)
        if shutil.which("ffmpeg"):
            return "ffmpeg"

        # Fallback: Just try the command and hope for the best
        return "ffmpeg"

    def hide_data(self, audio_file_obj, secret_hex):
        ffmpeg_cmd = self._get_ffmpeg_path()

        try:
            # 1. WRITE: Save the uploaded file to disk so FFmpeg can read it
            with open("temp_input_audio", "wb") as f:
                f.write(audio_file_obj.getbuffer())

            # 2. CONVERT: Use FFmpeg to clean the audio and convert to WAV
            # -y: Overwrite output
            # -ar 44100: Standard CD quality sample rate
            # -ac 2: Stereo
            # -f wav: Force WAV format
            subprocess.run(
                [ffmpeg_cmd, "-y", "-i", "temp_input_audio", "-ar", "44100", "-ac", "2", "-f", "wav", "temp_clean.wav"],
                check=True,
                stdout=subprocess.DEVNULL,  # Silence the logs
                stderr=subprocess.DEVNULL
            )

            # 3. READ: Load the clean WAV data
            with wave.open("temp_clean.wav", "rb") as song:
                params = song.getparams()
                frames = bytearray(song.readframes(song.getnframes()))

            # 4. ENCODE: Embed the secret hex string using LSB Steganography
            # Add a terminator sequence so we know when the message stops
            secret_bin = bin(int(secret_hex, 16))[2:].zfill(len(secret_hex) * 4) + '1111111111111110'

            if len(secret_bin) > len(frames):
                raise ValueError(
                    f"Audio file is too short! Needs {len(secret_bin)} bits, but only has {len(frames)} frames.")

            for i in range(len(secret_bin)):
                # Replace the Last Significant Bit (LSB) with our secret bit
                frames[i] = (frames[i] & 254) | int(secret_bin[i])

            # 5. SAVE: Write the modified frames to a memory buffer
            output_buffer = io.BytesIO()
            with wave.open(output_buffer, 'wb') as fd:
                fd.setparams(params)
                fd.writeframes(frames)

            # 6. CLEANUP: Delete temp files
            self._cleanup()

            return output_buffer.getvalue()

        except subprocess.CalledProcessError:
            self._cleanup()
            raise Exception("FFmpeg conversion failed. The audio file might be corrupt.")
        except Exception as e:
            self._cleanup()
            raise Exception(f"Encryption Error: {str(e)}")

    def reveal_data(self, audio_file_obj):
        ffmpeg_cmd = self._get_ffmpeg_path()
        try:
            # 1. WRITE: Save uploaded file
            with open("temp_decode_input", "wb") as f:
                f.write(audio_file_obj.getbuffer())

            # 2. CONVERT: Standardize to WAV (fixes issues with different encodings)
            subprocess.run(
                [ffmpeg_cmd, "-y", "-i", "temp_decode_input", "-ar", "44100", "-ac", "2", "-f", "wav",
                 "temp_decode.wav"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 3. READ: Load frames
            with wave.open("temp_decode.wav", "rb") as song:
                frames = bytearray(song.readframes(song.getnframes()))

            # 4. DECODE: Extract LSBs until terminator is found
            extracted = ""
            for i in range(len(frames)):
                extracted += str(frames[i] & 1)
                if extracted.endswith('1111111111111110'):
                    break

            # 5. CLEANUP & RETURN
            self._cleanup()

            # Remove terminator and convert binary back to hex
            bits = extracted[:-16]
            if not bits: return None

            return hex(int(bits, 2))[2:]

        except Exception:
            self._cleanup()
            return None

    def _cleanup(self):
        """Removes temporary files to keep the server clean."""
        temp_files = ["temp_input_audio", "temp_clean.wav", "temp_decode_input", "temp_decode.wav"]
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass