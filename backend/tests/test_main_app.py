import unittest
from fastapi.testclient import TestClient


class TestMainApp(unittest.TestCase):
    """Test the main FastAPI app."""
    @classmethod
    def setUpClass(cls):
        from main import app
        cls.client = TestClient(app)

    def test_config_get(self):
        """Test the /api/config endpoint."""
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        self.assertIn("version", response.json().keys())


if __name__ == "__main__":
    unittest.main()
