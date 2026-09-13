import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.download_dataset import download_and_extract_plantvillage, download_plantvillage


class TestDownloadDatasetAPI(unittest.TestCase):
    def test_imports(self):
        """Verify download_and_extract_plantvillage and download_plantvillage can be imported cleanly."""
        self.assertTrue(callable(download_and_extract_plantvillage))
        self.assertTrue(callable(download_plantvillage))

    @patch("data.download_dataset.download_plantvillage")
    def test_download_and_extract_plantvillage_return_type(self, mock_download):
        """Verify download_and_extract_plantvillage returns Path to active_rgb_dir."""
        mock_download.return_value = {
            "source": "mohanty/PlantVillage",
            "status": "already_present",
            "active_rgb_dir": "data/raw/plantvillage/raw/color",
            "total_images": 54305,
        }
        res = download_and_extract_plantvillage()
        self.assertIsInstance(res, Path)
        self.assertEqual(res, ROOT / "data" / "raw" / "plantvillage" / "raw" / "color")
        mock_download.assert_called_once()


if __name__ == "__main__":
    unittest.main()
