import unittest
from .app_test_client import app_test_client


class TestMainApp(unittest.TestCase):
    """Test the main FastAPI app."""

    @classmethod
    def setUpClass(cls):
        cls.client = app_test_client

    def test_config_get(self):
        """Test the /api/config endpoint."""
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        self.assertIn("version", response.json().keys())


if __name__ == "__main__":
    unittest.main()
