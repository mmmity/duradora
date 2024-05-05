'''
Base class for all DB controllers
'''
import sqlite3

class Controller:
    '''
    Base class for all DB controllers
    '''
    def __init__(self, database: str):
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
