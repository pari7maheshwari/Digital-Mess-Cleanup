import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
from PIL import Image, ImageDraw
from imagehash import ImageHash

from digital_mess_cleanup.config import SIMILARITY_THRESHOLD
from digital_mess_cleanup.organizer import _hash_bands, scan_and_organize


class SimilarityIndexTests(unittest.TestCase):
    def test_similar_hashes_share_at_least_one_index_band(self):
        rng = random.Random(2026)
        band_count = SIMILARITY_THRESHOLD + 1

        for _ in range(100):
            bits = rng.getrandbits(64)
            changed_bits = rng.sample(
                range(64), k=SIMILARITY_THRESHOLD
            )
            similar_bits = bits
            for bit in changed_bits:
                similar_bits ^= 1 << bit

            first_hash = ImageHash(
                np.array(
                    [bool(bits & (1 << bit)) for bit in range(63, -1, -1)],
                    dtype=bool,
                ).reshape((8, 8))
            )
            second_hash = ImageHash(
                np.array(
                    [
                        bool(similar_bits & (1 << bit))
                        for bit in range(63, -1, -1)
                    ],
                    dtype=bool,
                ).reshape((8, 8))
            )
            first_bands = set(_hash_bands(first_hash, band_count))
            second_bands = set(_hash_bands(second_hash, band_count))

            self.assertLessEqual(first_hash - second_hash, SIMILARITY_THRESHOLD)
            self.assertTrue(first_bands & second_bands)

    def test_scan_detects_reencoded_similar_images(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "images"
            source.mkdir()

            image = Image.new("RGB", (256, 256), "white")
            draw = ImageDraw.Draw(image)
            draw.rectangle((30, 30, 200, 190), fill="#2266aa")
            draw.ellipse((75, 65, 180, 170), fill="#efaa22")
            image.save(source / "first.png")
            image.save(source / "similar.jpg", quality=94)

            with (
                patch(
                    "digital_mess_cleanup.organizer.st.progress",
                    return_value=Mock(),
                ),
                patch(
                    "digital_mess_cleanup.organizer.st.empty",
                    return_value=Mock(),
                ),
            ):
                _, rows = scan_and_organize(
                    source, root / "output", False, 0.2
                )

            statuses = {row["File Name"]: row["Status"] for row in rows}
            self.assertEqual(statuses["first.png"], "Organized")
            self.assertEqual(statuses["similar.jpg"], "Similar Image")


if __name__ == "__main__":
    unittest.main()
