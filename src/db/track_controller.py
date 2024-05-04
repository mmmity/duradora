'''
A higher-level API for SQL table "tracks"
'''
from typing import List, Tuple, Optional
import uuid

import sqlite3
from pydantic import BaseModel


class Track(BaseModel):
    '''
    Pydantic model representing track
    '''
    title: str | None = None
    artists: str | None = None


class DBTrack(Track):
    '''
    Pydantic model representing track stored in Database
    '''
    uuid: str


class TrackUUID(BaseModel):
    '''
    Pydantic model representing track UUOD
    '''
    uuid: str


class TrackController:
    '''
    Class that provides higher-level API for SQL table "tracks"
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

    def create_track(self, track: Track) -> str:
        '''
        Inserts new track into table "tracks"
        Returns uuid of new track
        '''
        track_id: str = str(uuid.uuid4())
        self.cur.execute('INSERT INTO tracks VALUES(?, ?, ?)',
                         (track_id, track.title, track.artists))
        self.con.commit()
        return track_id

    def track_from_entry(self, t: Tuple[str, str, str]) -> DBTrack:
        '''
        Converts database entry into Track
        '''
        return DBTrack(uuid=t[0], title=t[1], artists=t[2])

    def find_track(self, uuid_str: str) -> Optional[DBTrack]:
        '''
        Tries to find track by uuid
        Returns DBTrack if found, otherwise None
        '''
        self.cur.execute('SELECT * FROM tracks WHERE uuid = ?', (uuid_str,))
        out: Optional[Tuple[str, str, str]] = self.cur.fetchone()
        if out is not None:
            return self.track_from_entry(out)
        return None

    def update_track(self, track: DBTrack):
        '''
        Updates dbtrack with track.uuid with new values
        '''
        self.cur.execute('UPDATE tracks SET title = ?, artists = ? WHERE uuid = ?',
                         (track.title, track.artists, track.uuid))
        self.con.commit()
