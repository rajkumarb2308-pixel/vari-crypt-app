import random


class AquaticCoverEngine:
    def generate_cover(self, required_size=1080):
        """
        Fetches a limitless, random real aquatic image directly from the internet.
        Dynamically requests the resolution needed to fit the payload.
        """
        # A random cache-buster ensures you never get the same image twice
        cache_buster = random.randint(1, 1000000)

        # We cap the internet request size at 2500px so the download doesn't time out.
        # If the payload is massive (e.g., 50MB), your Stego engine will automatically
        # stretch this downloaded image the rest of the way.
        fetch_size = min(required_size, 2500)

        # Limitless direct internet fetch based on aquatic keywords
        url = f"https://loremflickr.com/{fetch_size}/{fetch_size}/ocean,underwater,reef?random={cache_buster}"

        return url