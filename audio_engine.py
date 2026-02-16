import wave
import io
import os
import subprocess
import shutil


class AudioStego:
    def _get_ffmpeg_path(self):
        """
        Smart detection for FFmpeg.
        """
        local_path = os.path.join(os.getcwd(), "ffmpeg.exe")
        if os.path.exists(local_path):
            return local_path
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        return "ffmpeg"

    def hide_data(self, audio_file_obj, secret_hex):
        ffmpeg_cmd = self._get_ffmpeg_path()
        temp_in = "temp_input_audio"
        temp_wav = "temp_clean.wav"

        try:
            # 1. WRITE: Save the uploaded file to disk
            with open(temp_in, "wb") as f:
                f.write(audio_file_obj.read())

            # 2. CONVERT: Force audio to 16-bit PCM WAV (Required for wave module)
            # -c:a pcm_s16le: Forces standard 16-bit audio (Critical fix)
            subprocess.run(
                [ffmpeg_cmd, "-y", "-i", temp_in, "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", "-f", "wav",
                 temp_wav],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 3. READ: Load the clean WAV data
            with wave.open(temp_wav, "rb") as song:
                params = song.getparams()
                frames = bytearray(song.readframes(song.getnframes()))

            # 4. ENCODE: Embed the secret hex string using LSB
            # Binary + 16-bit Terminator (1111111111111110)
            secret_bin = bin(int(secret_hex, 16))[2:].zfill(len(secret_hex) * 4) + '1111111111111110'

            if len(secret_bin) > len(frames):
                raise ValueError("Audio file is too short to hold this message.")

            # LSB Substitution
            for i in range(len(secret_bin)):
                frames[i] = (frames[i] & 254) | int(secret_bin[i])

            # 5. SAVE: Write to memory buffer
            output_buffer = io.BytesIO()
            with wave.open(output_buffer, 'wb') as fd:
                fd.setparams(params)
                fd.writeframes(frames)

            output_buffer.seek(0)  # Reset pointer to start
            self._cleanup()
            return output_buffer.getvalue()

        except subprocess.CalledProcessError:
            self._cleanup()
            raise Exception("FFmpeg failed. Please install FFmpeg or check input file.")
        except Exception as e:
            self._cleanup()
            raise Exception(f"Encryption Error: {str(e)}")

    def reveal_data(self, audio_file_obj):
        ffmpeg_cmd = self._get_ffmpeg_path()
        temp_in = "temp_decode_input.wav"  # Assume WAV first
        temp_converted = "temp_converted.wav"

        try:
            # 1. WRITE: Save uploaded file
            file_bytes = audio_file_obj.read()
            with open(temp_in, "wb") as f:
                f.write(file_bytes)

            frames = None

            # 2. ATTEMPT DIRECT READ (Critical Fix)
            # Try to read as WAV immediately. If it works, DO NOT use FFmpeg.
            # Using FFmpeg here would re-encode and destroy the LSBs.
            try:
                with wave.open(temp_in, "rb") as song:
                    frames = bytearray(song.readframes(song.getnframes()))
            except wave.Error:
                # 3. FALLBACK: Only convert if it's NOT a valid WAV (e.g. user uploaded mp3)
                # Note: Data hidden in MP3 is likely lost, but this prevents crashing.
                subprocess.run(
                    [ffmpeg_cmd, "-y", "-i", temp_in, "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", "-f", "wav",
                     temp_converted],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                with wave.open(temp_converted, "rb") as song:
                    frames = bytearray(song.readframes(song.getnframes()))

            if not frames:
                return None

            # 4. DECODE: Extract LSBs
            extracted_bin = ""
            terminator = "1111111111111110"

            for i in range(len(frames)):
                extracted_bin += str(frames[i] & 1)
                # Optimization: Check terminator every 16 bits to save time
                if len(extracted_bin) >= 16 and extracted_bin[-16:] == terminator:
                    extracted_bin = extracted_bin[:-16]  # Remove terminator
                    break
            else:
                # If loop finishes without break, terminator wasn't found
                self._cleanup()
                return None

            self._cleanup()

            # 5. Convert Binary to Hex
            if not extracted_bin: return None
            return hex(int(extracted_bin, 2))[2:]

        except Exception as e:
            self._cleanup()
            return None

    def _cleanup(self):
        """Removes temporary files."""
        temp_files = ["temp_input_audio", "temp_clean.wav", "temp_decode_input.wav", "temp_converted.wav"]
        for f in temp_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
