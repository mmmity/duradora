'''
Module that contains some useful methods for handling users
'''

from src.db.user_controller import UserController, User
from src import config
from src.responses import Error, Success


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

    async def update_user(self, executor: str, user: User) -> Error | Success:
        '''
        Updates user with new data. Works only if executor is updated user of is admin
        If executor is not admin, they cannot make anyone admin
        '''
        try:
            if self.is_admin(executor):
                self.controller.update_user(user)
                return Success(success=True)

            if user.username == executor and not user.is_admin:
                self.controller.update_user(user)
                return Success(success=True)

            return Error(error="This user does not have rights to do this")
        except Exception as e:
            return Error(error=repr(e))
