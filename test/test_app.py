from paste.fixture import TestApp
from nose.tools import *
from modules import app
import os

class TestCode():
    def test_index(self):
        middleware = []
        testApp = TestApp(app.wsgifunc(*middleware))
        root = testApp.get('/')
        assert_equal(root.status, 200)
        root.mustcontain('All Modules')