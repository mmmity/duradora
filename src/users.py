'''
Module that contains some useful methods for handling users
'''

from src.db.user_controller import UserController, User
from src import config


class UserHandler:
    '''
    Class that implements some userful methods for handling users
    '''
    def __init__(self):
        '''
        Initializes database
        '''
        self.controller = UserController(config.DB_PATH)

    def is_admin(self, username: str) -> bool:
        '''
        Returns True if user with username exists and is admin, otherwise False
        '''
        user: User = self.controller.find_user(username)
        if user is None:
            return False
        return user.is_admin
