'''
Tests for auth module
'''
import unittest
from unittest.mock import MagicMock
from jose import jwt

from src import config
from src.auth import Auth, Error, Success, Token
from src.db.user_controller import User
from src.hashes import SHA256Hasher


class MockAuth(Auth):
    '''
    Mock that replaces UserController to MagicMock
    '''
    def __init__(self):
        '''
        Initializes controller as MagicMock. Hasher is intact
        '''
        self.controller = MagicMock()
        self.hasher = SHA256Hasher(config.SALT)


class TestAuth(unittest.TestCase):
    '''
    Tests for Auth class
    '''
    def test_authenticate_user(self):
        '''
        Tests for authenticate_user method
        '''
        auth = MockAuth()
        test_user = User(username='mmmity', password=auth.hasher.hexdigest('cringe'), is_admin=True)
        auth.controller.find_user.return_value = test_user
        self.assertEqual(test_user, auth.authenticate_user('mmmity', 'cringe'))

        self.assertIsNone(auth.authenticate_user('mmmity', 'cringee'))
        auth.controller.find_user.return_value = None
        self.assertIsNone(auth.authenticate_user('mmmity', 'cringe'))

    def test_create_access_token(self):
        '''
        Tests for create_access_token method
        '''
        auth = MockAuth()
        token: str = auth.create_access_token({'flex': 'chill', 'cringe': True})
        decoded = jwt.decode(token, config.SECRET_KEY)

        self.assertEqual(decoded['flex'], 'chill')
        self.assertEqual(decoded['cringe'], True)
        self.assertIn('exp', decoded)


class TestAsyncs(unittest.IsolatedAsyncioTestCase):
    '''
    Tests for async methods of Auth
    '''
    async def test_get_current_user(self):
        '''
        Tests for get_current_user method
        '''
        auth = MockAuth()
        weird_token_res = await auth.get_current_user('anime')
        self.assertIsInstance(weird_token_res, Error)

        wrong_decoded_token = jwt.encode({'username': 'mmmity'}, key='anime')
        wrong_decoded_token_res = await auth.get_current_user(wrong_decoded_token)
        self.assertIsInstance(wrong_decoded_token_res, Error)

        wrong_composed_token = jwt.encode({'dora': 'dura'},
                                          key=config.SECRET_KEY,
                                          algorithm=config.ALGORITHM)
        wrong_composed_token_res = await auth.get_current_user(wrong_composed_token)
        self.assertIsInstance(wrong_composed_token_res, Error)

        test_user = User(username='mmmity', password='')
        auth.controller.find_user.return_value = test_user
        good_token = jwt.encode({'username': 'mmmity'},
                                key=config.SECRET_KEY,
                                algorithm=config.ALGORITHM)
        good_token_res = await auth.get_current_user(good_token)
        self.assertEqual(good_token_res, test_user)

    async def test_register_user(self):
        '''
        Tests for register_user method
        '''
        auth = MockAuth()
        auth.controller.find_user.return_value = True
        exists_res = await auth.register_user(User(username='mmmity', password=''))
        self.assertIsInstance(exists_res, Error)

        auth.controller.find_user.return_value = None
        good_res = await auth.register_user(User(username='mmmity', password=''))
        self.assertIsInstance(good_res, Success)

        auth.controller.create_user.side_effect = KeyError('anime')
        err_res = await auth.register_user(User(username='mmmity', password=''))
        self.assertIsInstance(err_res, Error)

    async def test_login_user(self):
        '''
        Tests for login_user method
        '''
        auth = MockAuth()
        user = User(username='mmmity', password='')

        auth.authenticate_user = MagicMock()
        auth.authenticate_user.return_value = None
        self.assertIsInstance(await auth.login_user(user), Error)

        auth.authenticate_user.return_value = user
        self.assertIsInstance(await auth.login_user(user), Token)
