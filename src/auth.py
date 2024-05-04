'''
Contains functions for working with authorization
'''
from typing import Optional, Annotated
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from src.db.user_controller import UserController, User
from src import config
from src.hashes import SHA256Hasher
from src.responses import Error, Success


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

class Token(BaseModel):
    '''
    Model for returning token from login
    '''
    access_token: str
    token_type: str


class TokenData(BaseModel):
    '''
    Model that contains decrypted token 
    '''
    username: str | None = None


class Auth:
    '''
    Class for handling user authorization via JWT
    '''
    def __init__(self):
        '''
        Initializes user db controller and hasher
        '''
        self.controller = UserController(config.DB_PATH)
        self.hasher = SHA256Hasher(config.SALT)

    def get_user(self, username: str) -> Optional[User]:
        '''
        Tries to find user from database by username
        '''
        return self.controller.find_user(username)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        '''
        Checks if user with such password exists. If does, returns User, otherwise None
        '''
        user: Optional[User] = self.get_user(username)
        if user is None:
            return None
        if not self.hasher.verify(password, user.password):
            return None
        return user

    def create_access_token(self, data: dict) -> str:
        '''
        Creates JWT from dictionary and signs it
        '''
        to_encode: dict = data.copy()
        expires: datetime = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({'exp': expires})
        encoded_jwt: str = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]) -> User | Error:
        '''
        Tries to extract user from given JWT. Returns user or credentials error
        '''
        creds_error = Error(error='invalid credentials')
        try:
            payload: dict = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            username: str = payload.get('username')
            if username is None:
                return creds_error
        except JWTError:
            return creds_error

        user: Optional[User] = self.get_user(username)
        if user is None:
            return creds_error
        return user

    async def register_user(self, user: User) -> Success | Error:
        '''
        Tries to add user into database
        '''
        try:
            if self.controller.find_user(user.username) is not None:
                return Error(error='user with such username already exists')

            user.password = self.hasher.hexdigest(user.password)
            self.controller.create_user(user)
        except Exception as e:
            return Error(error=repr(e))

        return Success(success=True)

    async def login_user(self, user: User) -> Token | Error:
        '''
        Tries to authorize user with password. If succeeds, returns token for user
        '''
        auth: Optional[User] = self.authenticate_user(user.username, user.password)
        if auth is None:
            return Error(error='incorrect username or password')
        token = self.create_access_token(data={'username': user.username})
        return Token(access_token=token, token_type='bearer')
