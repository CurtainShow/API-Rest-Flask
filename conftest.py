try:
    from app import app
    import unittest
except Exception as e:
    print("Error: {e}")

class FlaskTest(unittest.TestCase):
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/", content_type="html/text")
        self.assertEqual(response.status_code, 200)
