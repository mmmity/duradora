'''
A higher-level API for SQL table "users"
'''
import sqlite3
from pydantic import BaseModel
from typing import Optional, Tuple

class User(BaseModel):
    '''
    Pydantic model representing user
    '''
    username: str
    password: str
    is_admin: bool = False

class UserController:
    '''
    Class that provides higher-level API for SQL table "users"
    '''
    def __init__(self, database):
        '''
        Opens connection to database and saves cursor
        '''
        self.con: sqlite3.Connection = sqlite3.connect(database)
        self.cur: sqlite3.Cursor = self.con.cursor()

    def __del__(self):
        '''
        Closes the connection when object is deleted
        '''
        self.con.close()

    def create_user(self, user: User):
        '''
        Inserts new user into table "users"
        '''
        self.cur.execute('INSERT INTO users VALUES(?, ?, ?)', (user.username, user.password, user.is_admin))
        self.con.commit()
    
    def user_from_tuple(self, t: Tuple[str, str, bool]):
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
        out = self.cur.fetchone()
        if out is not None:
            return self.user_from_tuple(out)

    def update_user(self, user: User):
        '''
        Updates user with user.username with new values
        '''
        self.cur.execute('UPDATE users SET password = ?, is_admin = ? WHERE username = ?', (user.password, user.is_admin, user.username))
        self.con.commit()
