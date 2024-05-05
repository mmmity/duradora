'''
A higher-level API for SQL table "users"
'''
from typing import Optional, Tuple

import sqlite3
from pydantic import BaseModel

from src.db.controller import Controller


class User(BaseModel):
    '''
    Pydantic model representing user
    '''
    username: str
    password: str
    is_admin: bool = False


class UserController(Controller):
    '''
    Class that provides higher-level API for SQL table "users"
    '''
    def __init__(self, database: str):
        '''
        Initializes base controller
        '''
        super().__init__(database)

    def create_user(self, user: User):
        '''
        Inserts new user into table "users"
        '''
        self.cur.execute('INSERT INTO users VALUES(?, ?, ?)',
                         (user.username, user.password, user.is_admin))
        self.con.commit()

    def user_from_tuple(self, t: Tuple[str, str, bool]) -> User:
        '''
        Converts unnamed tuple with values in right order into user
        '''
        return User(**{key: t[i] for i, key in enumerate(User.model_fields.keys())})

    def find_user(self, username: str) -> Optional[User]:
        '''
        Tries to find user with such username
        Returns User if found, otherwise None
        '''
        self.cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        out: Optional[Tuple[str, str, bool]] = self.cur.fetchone()
        if out is not None:
            return self.user_from_tuple(out)
        return None

    def update_user(self, user: User):
        '''
        Updates user with user.username with new values
        '''
        self.cur.execute('UPDATE users SET password = ?, is_admin = ? WHERE username = ?',
                         (user.password, user.is_admin, user.username))
        self.con.commit()
