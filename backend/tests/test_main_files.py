import unittest
from .app_test_client import app_test_client


class TestMainFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app_test_client

    @classmethod
    def tearDownClass(cls):
        cls.client.post("/api/logout")

    def test_upload_files(self):
        files = [
            ("files", ("test1.txt", b"File content 1", "text/plain")),
            ("files", ("test2.txt", b"File content 2", "text/plain")),
        ]

        response = self.client.post("/api/files", files=files)

        self.assertEqual(response.status_code, 200)

    def test_delete_file(self):
        files = [
            ("files", ("test3.txt", b"File content 3", "text/plain")),
        ]
        self.client.post("/api/files", files=files)
        
        response = self.client.delete("/api/files/test3.txt")

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
