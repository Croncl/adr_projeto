import unittest
from main import app


class BasicTestCase(unittest.TestCase):
    def test_true(self):
        self.assertTrue(True)


class FlaskAppTestCase(unittest.TestCase):
    def test_home_route_exists(self):
        tester = app.test_client(self)
        response = tester.get("/")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
