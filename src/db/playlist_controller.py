'''
A higher-level API for SQL table "playlists"
'''
from typing import List, Tuple, Optional
import uuid
from enum import IntEnum
import json

from pydantic import BaseModel

from src.db.controller import Controller


class Access(IntEnum):
    '''
    Enum for playlist access modifier
    '''
    PUBLIC = 0
    LINK = 1
    PRIVATE = 2


class Playlist(BaseModel):
    '''
    Pydantic model representing playlist
    '''
    title: str = "untitled"
    creator: str
    access: Access = Access.PUBLIC
    tracks: List[str] = []


class DBPlaylist(Playlist):
    '''
    Pydantic model representing playlist stored in database
    '''
    uuid: str


class PlaylistController(Controller):
    '''
    Class that provides higher-level API for SQL table "playlists"
    '''

    def create_playlist(self, playlist: Playlist) -> str:
        '''
        Inserts new playlist into table "playlists"
        Returns uuid of new playlist
        '''
        playlist_id: str = str(uuid.uuid4())
        self.cur.execute('INSERT INTO playlists VALUES(?, ?, ?, ?, ?)',
                         (playlist_id,
                          playlist.title,
                          playlist.creator,
                          int(playlist.access),
                          json.dumps(playlist.tracks)))
        self.con.commit()
        return playlist_id

    def playlist_from_entry(self, t: Tuple[str, str, str, int, str]) -> DBPlaylist:
        '''
        Converts database entry into DBPlaylist
        '''
        return DBPlaylist(
            uuid=t[0],
            title=t[1],
            creator=t[2],
            access=Access(t[3]),
            tracks=json.loads(t[4])
        )

    def find_playlist(self, uuid_str: str) -> Optional[DBPlaylist]:
        '''
        Tries to find playilst by uuid
        Returns DBPlaylist if found, otherwise None
        '''
        self.cur.execute('SELECT * FROM playlists WHERE uuid = ?', (uuid_str,))
        out: Optional[Tuple[str, str, str, int, str]] = self.cur.fetchone()
        if out is not None:
            return self.playlist_from_entry(out)
        return None

    def user_playlists(self, username: str) -> List[DBPlaylist]:
        '''
        Returns all playlists with creator == username as list
        '''
        self.cur.execute('SELECT * FROM playlists WHERE creator = ?', (username,))
        out: List[Tuple[str, str, str, int, str]] = self.cur.fetchall()
        return list(map(self.playlist_from_entry, out))

    def update_playlist(self, playlist: DBPlaylist):
        '''
        Updates dbplaylist with playlist.uuid with new values
        '''
        self.cur.execute(
            'UPDATE playlists SET title = ?, creator = ?, access = ?, tracks = ? WHERE uuid = ?',
            (
                playlist.title,
                playlist.creator,
                int(playlist.access),
                json.dumps(playlist.tracks),
                playlist.uuid
            )
        )
        self.con.commit()
