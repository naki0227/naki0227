import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate import html_image_sources, validate  # noqa: E402


class ReadmeValidationTests(unittest.TestCase):
    def test_parses_image_source_and_alt(self):
        self.assertEqual(
            html_image_sources('<img alt="A project" width="100%" src="assets/a.svg" />'),
            [("assets/a.svg", "A project")],
        )

    def test_missing_alt_is_detectable(self):
        self.assertEqual(html_image_sources('<img src="a.svg"/>'), [("a.svg", "")])

    def test_current_repository_assets(self):
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()
