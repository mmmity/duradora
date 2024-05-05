'''
Tests for users module
'''
import unittest
from unittest.mock import MagicMock

from src.users import UserHandler, User


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
