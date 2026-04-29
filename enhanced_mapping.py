import zlib
import hashlib
import random


class EnhancedMapping:
    def __init__(self):
        # Your exact requested multi-language and emoji pool
        pool_str = (
                "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" +
                "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщ" +
                "ÄÖÜäöüßÑñ¿¡áéíóúÁÉÍÓÚ!@#$%^&*()_+-=[]{}|;:,.<>?/~`" +
                "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψω" +
                "😀🚀🔒🔑💻📱📡🛡️📂📈⚙️🔥⚡🧠🌍🛑👽👻🤖👾🎃👍👎✌️🤞🖖🤘🤙🖐️👌🤌🤏"
        )
        # Force exactly 256 unique characters
        pool = []
        for c in pool_str:
            if c not in pool: pool.append(c)
        while len(pool) < 256:
            pool.append(chr(len(pool) + 1000))

        self.base_pool = pool[:256]

    def compress_and_map(self, file_path, password):
        """Encrypts whole media files into a polymorphic multi-language cipher."""
        with open(file_path, "rb") as f:
            data = f.read()

        # XOR Encryption
        key = hashlib.sha256(password.encode()).digest()
        enc = bytearray(b ^ key[i % len(key)] for i, b in enumerate(data))
        comp = zlib.compress(enc, level=9)

        # Polymorphic Shuffling (Unique to password)
        seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        working_pool = self.base_pool.copy()
        random.Random(seed).shuffle(working_pool)

        # High-speed list comprehension for massive files
        return "".join([working_pool[b] for b in comp])

    def unmap_and_decompress(self, cipher_text, password):
        """Reverses the heavy cipher back into the original media file."""
        seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        working_pool = self.base_pool.copy()
        random.Random(seed).shuffle(working_pool)

        rev_map = {c: i for i, c in enumerate(working_pool)}

        try:
            b_array = bytearray(rev_map[c] for c in cipher_text if c in rev_map)
            dec = zlib.decompress(b_array)

            key = hashlib.sha256(password.encode()).digest()
            return bytes(b ^ key[i % len(key)] for i, b in enumerate(dec))
        except Exception:
            return None