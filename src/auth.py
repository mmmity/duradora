'''
Contains functions for working with authorization
'''
from src.db.user_controller import UserController, User
from src import config
from src.hashes import SHA256Hasher

from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, Annotated

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class Error(BaseModel):
    error: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

hasher = SHA256Hasher(config.SALT)

def get_user(username: str):
    controller = UserController(config.DB_PATH)
    return controller.find_user(username)

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user(username)

    if user is None:
        return False
    if not hasher.verify(password, user.password):
        return False
    return user

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expires})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User | Error:
    creds_error = Error(error='invalid credentials')
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get('username')
        if username is None:
            return creds_error
    except JWTError:
        return creds_error

    user = get_user(username)
    if user is None:
        return creds_error
    return user

async def register_user(user: User):
    try:
        controller = UserController('duradora.db')
        if controller.find_user(user.username) is not None:
            return Error(error='user with such username already exists')
        
        user.password = hasher.hexdigest(user.password)
        controller.create_user(user)
    except Exception as e:
        return {'error': repr(e)}
    
    return {'success': True}

async def login_user(user: User):
    auth = authenticate_user(user.username, user.password)
    if not auth:
        return Error(error='incorrect username or password')
    token = create_access_token(data={'username': user.username})
    return Token(access_token=token, token_type='bearer')
