import unittest
from main import app


class FlaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home_route(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_blog_route(self):
        response = self.app.get("/blog")
        self.assertEqual(response.status_code, 200)

    def test_visualizations_route(self):
        response = self.app.get("/visualizations")
        self.assertEqual(response.status_code, 200)
