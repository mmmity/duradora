'''
Tests for users module
'''
import unittest
from unittest.mock import MagicMock

from src.users import UserHandler, User
from src.responses import Success, Error


class MockUserHandler(UserHandler):
    '''
    Mocking UserHandler so it does not connect to db
    '''
    def __init__(self):
        '''
        controller is now MagicMock
        '''
        self.controller = MagicMock()


class TestUserHandler(unittest.TestCase):
    '''
    Tests for UserHandler class
    '''
    def test_is_admin(self):
        '''
        Tests for is_admin method
        '''
        handler = MockUserHandler()

        handler.controller.find_user.return_value = None
        self.assertFalse(handler.is_admin('u'))

        handler.controller.find_user.return_value = User(username='u', password='p')
        self.assertFalse(handler.is_admin('u'))

        handler.controller.find_user.return_value.is_admin = True
        self.assertTrue(handler.is_admin('u'))


class TestUserHandlerAsync(unittest.IsolatedAsyncioTestCase):
    '''
    Tests for async methods of UserHandler class
    '''
    async def test_update_user(self):
        '''
        Tests for update_user method
        '''
        handler = MockUserHandler()
        handler.is_admin = MagicMock()

        handler.is_admin.return_value = True
        self.assertIsInstance(await handler.update_user('u', None), Success)
        handler.is_admin.return_value = False

        user = User(username='u', password='p')
        self.assertIsInstance(await handler.update_user('u', user), Success)

        user = User(username='u', password='p', is_admin=True)
        self.assertIsInstance(await handler.update_user('u', user), Error)

        handler.is_admin.side_effect = KeyError()
        self.assertIsInstance(await handler.update_user('u', None), Error)
