'''
Tests for user_controller module
'''
import unittest
from unittest.mock import MagicMock, patch

from src.db.user_controller import UserController, User

class TestUserController(unittest.TestCase):
    '''
    Tests UserController class
    '''
    @patch('sqlite3.connect')
    def test_init_del(self, mock_connect: MagicMock):
        '''
        Tests init and del magic methods
        '''
        _ = UserController('duradora.db')
        mock_connect.assert_called_once_with('duradora.db')

    @patch('sqlite3.connect')
    def test_create(self, _: MagicMock):
        '''
        Tests user creation
        '''
        controller = UserController('duradora.db')
        controller.create_user(User(username='mmmity', password='cringe', is_admin=True))
        controller.cur.execute.assert_called_once_with('INSERT INTO users VALUES(?, ?, ?)',
                                                       ('mmmity', 'cringe', True))
        controller.con.commit.assert_called_once()

    @patch('sqlite3.connect')
    def test_user_from_tuple(self, _):
        '''
        Tests converting tuple to User
        '''
        controller = UserController('duradora.db')
        user = controller.user_from_tuple(('mmmity', 'cringe', True))
        self.assertEqual(user.username, 'mmmity')
        self.assertEqual(user.password, 'cringe')
        self.assertEqual(user.is_admin, True)

    @patch('sqlite3.Cursor')
    @patch('sqlite3.Connection')
    @patch('sqlite3.connect')
    def test_find_user(self, mock_connect: MagicMock,
                       mock_connection: MagicMock, mock_cursor: MagicMock):
        '''
        Tests find_user method
        '''
        mock_cursor.fetchone.return_value = ('mmmity', 'cringe', True)
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        controller = UserController('duradora.db')
        output = controller.find_user('mmmity')
        self.assertEqual(output, User(username='mmmity', password='cringe', is_admin=True))

    @patch('sqlite3.connect')
    def test_update_user(self, _: MagicMock):
        '''
        Tests update_user method
        '''
        controller = UserController('duradora.db')
        controller.update_user(User(username='mmmity', password='flex', is_admin=False))

        arg_str = 'UPDATE users SET password = ?, is_admin = ? WHERE username = ?'
        controller.cur.execute.assert_called_once_with(arg_str, ('flex', False, 'mmmity'))
