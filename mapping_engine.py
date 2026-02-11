import random
import string
import hashlib


class MappingEngine:
    def __init__(self):
        self.base_pool = self._generate_symbol_universe()

    def _generate_symbol_universe(self):
        pool = list(string.ascii_letters + string.digits)

        # Greek letters
        greek = [chr(code) for code in range(0x0391, 0x03A9)]
        pool.extend(greek)

        # Math symbols
        math_syms = [
            '∀','∂','∃','∅','∇','∈','∉','∋','∏','∑','−','∗',
            '√','∝','∞','∠','∫','≈','≠','≡','≤','≥'
        ]
        pool.extend(math_syms)

        # Fill until 256
        start = 0x2600
        while len(pool) < 256:
            char = chr(start)
            if char.isprintable() and char not in pool:
                pool.append(char)
            start += 1

        return pool[:256]

    def _stable_seed(self, password: str):
        digest = hashlib.sha256(password.encode()).hexdigest()
        return int(digest, 16)

    def generate_map(self, password: str):
        working = self.base_pool.copy()
        random.Random(self._stable_seed(password)).shuffle(working)
        return working

    def map_ciphertext(self, ciphertext: bytes, password: str):
        symbol_map = self.generate_map(password)
        return "".join(symbol_map[b] for b in ciphertext)

    def unmap_ciphertext(self, visual_string: str, password: str):
        symbol_map = self.generate_map(password)
        reverse_map = {char: idx for idx, char in enumerate(symbol_map)}

        byte_arr = bytearray()
        for ch in visual_string:
            if ch not in reverse_map:
                raise ValueError("Corrupted data or wrong password.")
            byte_arr.append(reverse_map[ch])

        return bytes(byte_arr)