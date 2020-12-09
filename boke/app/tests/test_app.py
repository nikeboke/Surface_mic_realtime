
import unittest
from app import app, db
from app.config import TestConfig

class TestApp(unittest.TestCase):

    def setUp(self):
        # run before each test
        #app.config.from_object(TestConfig)
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        pass

    def test_login(self):
        pass
