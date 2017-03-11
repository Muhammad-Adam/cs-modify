'''
    test_app.py test the application's home page
'''
from paste.fixture import TestApp
from nose.tools import assert_equal
from app import APP
from components import session

class TestCode(object):
    '''
        This class runs the test cases to test app home page
    '''


    def __init__(self):
        '''
            Initialise testcode
        '''
        self.middleware = None
        self.test_app = None


    def setUp(self):
        '''
            Sets up the 'app.py' fixture
        '''
        self.middleware = []
        self.test_app = TestApp(APP.wsgifunc(*self.middleware))
        session.set_up(self.test_app)


    def tearDown(self):
        session.tear_down(self.test_app)


    def test_index_valid_response(self):
        '''
            Tests if user can access the index page without request errors.
        '''
        root = self.test_app.get('/')

        # checks if HTTP response code is 200 (= OK)
        assert_equal(root.status, 200)


    def test_goto_oversubscribed_modules(self):
        '''
            Tests if user can access the over subscribed page without request errors.
        '''
        root = self.test_app.get('/')

        response = root.click(linkid="home-page", href="/oversubscribedModules")

        assert_equal(response.status, 200)


    def test_goto_module_listing(self):
        '''
            Tests if user can access the module listing page without request errors.
        '''
        root = self.test_app.get('/')

        response = root.click(linkid="home-page", href="/modules")

        assert_equal(response.status, 200)


    def test_goto_fixed_module_mounting(self):
        '''
            Tests if user can access the fixed module mounting page without request errors.
        '''
        root = self.test_app.get('/')

        response = root.click(linkid="home-page", href="/moduleMountingFixed")

        assert_equal(response.status, 200)


    def test_goto_tentative_module_mounting(self):
        '''
            Tests if user can access the tentative module mounting page without request errors.
        '''
        root = self.test_app.get('/')

        response = root.click(linkid="home-page", href="/moduleMountingTentative")

        assert_equal(response.status, 200)


    def test_goto_student_enrollment(self):
        '''
            Tests if user can access the student enrollment page without request errors.
        '''
        root = self.test_app.get('/')

        response = root.click(linkid="home-page", href="/studentEnrollment")

        assert_equal(response.status, 200)

    def test_goto_overlapping_modules(self):
        '''
            Tests if user can access the overlapping modules page without request errors.
        '''
        root = self.test_app.get('/')

        response = root.click(linkid="home-page", href="/overlappingModules")

        assert_equal(response.status, 200)
