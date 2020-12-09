import unittest
import time
from app import app, db
from app.config import TestConfig


class TestHueApi(unittest.TestCase):

    def setUp(self):
        # run before each test
        #app.config.from_object(TestConfig)
        self.app = app.test_client()


    def test_get_lights(self):
        r = self.app.get('/api/hue/getlights/')
        self.assertEqual(r.status_code, 200)

    def get_light_names(self):
        r = self.app.get('api/hue/getlights/')
        return r.json['names']

    def test_set_light(self):
        #test default settings
        r = self.app.get('/api/hue/setlight/')
        self.assertNotEqual(r.status_code, 200)
        #test with parameters
        names = self.get_light_names()

        params = {'name': names[1], 'on': True, 'bri' : 0}
        r = self.app.get('/api/hue/setlight/', query_string=params)
        self.assertEqual(r.status_code, 200)

        params = {'name': names[1], 'transitiontime' : 0, 'bri' : 240}
        r = self.app.get('/api/hue/setlight/', query_string=params)
        self.assertEqual(r.status_code, 200)

        time.sleep(0.1)
        params = {'name': names[1], 'transitiontime' : 0, 'bri' : 100}
        r = self.app.get('/api/hue/setlight/', query_string=params)
        self.assertEqual(r.status_code, 200)

        params = {'name': names[1], 'transitiontime' : 30, 'on': False}
        r = self.app.get('/api/hue/setlight/', query_string=params)
        self.assertEqual(r.status_code, 200)

