import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class AgentWorkflowTests(unittest.TestCase):
    def test_folder_is_created_at_requested_path_only_after_download_click(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            (source / "example.txt").write_text("hello", encoding="utf-8")

            app_path = Path(__file__).parents[1] / "app.py"
            app = AppTest.from_file(str(app_path)).run(timeout=30)
            self.assertEqual(len(app.selectbox), 1)
            self.assertEqual(app.selectbox[0].value, "Fast (recommended)")
            app.text_input[0].set_value(str(source))
            app.text_input[1].set_value(str(root / "output"))
            app.checkbox[0].uncheck()
            app.button[0].click().run(timeout=30)

            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.button), 2)
            self.assertEqual(len(app.dataframe), 1)
            app.button[1].click().run(timeout=30)

            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("ready" in item.value for item in app.success))
            self.assertGreater(len(app.dataframe), 1)
            self.assertGreaterEqual(len(app.text_input), 2)
            self.assertTrue((root / "source" / "example.txt").exists())
            self.assertFalse((root / "output").exists())
            self.assertEqual(len(app.button), 3)
            self.assertEqual(app.button[2].label, "⬇️ Download folder")
            app.button[2].click().run(timeout=30)

            self.assertTrue(
                (root / "output" / "Documents" / "example.txt").is_file()
            )
            self.assertTrue((root / "source" / "example.txt").exists())
            self.assertTrue(
                any(
                    "downloaded successfully" in item.value
                    for item in app.success
                )
            )


if __name__ == "__main__":
    unittest.main()
