'''
Initializes database if it is not already initialized
'''
import sqlite3
from src.db.user_controller import UserController
from src.config import config

con = sqlite3.connect(config['db_path'])
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS users(
                username STRING PRIMARY KEY,
                password STRING,
                is_admin BOOLEAN
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS tracks(
                uuid STRING PRIMARY KEY,
                title STRING,
                artists STRING
)''')

cur.execute('''CREATE TABLE IF NOT EXISTS playlists(
                uuid STRING PRIMARY KEY,
                title STRING,
                creator STRING,
                access INTEGER,
                tracks STRING
)''')

userController = UserController('duradora.db')

print(cur.fetchall())
