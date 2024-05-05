'''
Module for operating with playlists: adding/removing tracks, updating them, etc
'''
from typing import Optional, List
from pydantic import BaseModel

from src.db.playlist_controller import PlaylistController, Playlist, DBPlaylist, Access
from src.db.track_controller import TrackController, DBTrack
from src.users import UserHandler
from src.responses import Error, Success
from src import config


class PlaylistForCreation(BaseModel):
    '''
    Model that is accepted when new playlist is created
    '''
    creator: str
    title: str = "untitled"
    access: Access = Access.PUBLIC


class PlaylistUUID(BaseModel):
    '''
    Model containing playlist uuid. Is returned after creation
    '''
    uuid: str


class PlaylistHandler:
    '''
    Class that handles all operations with playlists
    '''
    def __init__(self):
        '''
        Initializes database controller
        '''
        self.controller = PlaylistController(config.DB_PATH)
        self.track_controller = TrackController(config.DB_PATH)
        self.user_handler = UserHandler()

    async def create_playlist_for_user(self, executor: str,
                                       playlist: PlaylistForCreation) -> PlaylistUUID | Error:
        '''
        Creates empty playlist for user playlist.username if executor is the new user
        Returns uuid of new playlist
        '''
        try:
            if executor != playlist.creator and not self.user_handler.is_admin(executor):
                return Error(error="This user has no permission to execute this command")

            new_playlist: Playlist = Playlist(
                title=playlist.title,
                creator=playlist.creator,
                access=playlist.access
            )

            return PlaylistUUID(uuid=self.controller.create_playlist(new_playlist))
        except Exception as e:
            return Error(error=repr(e))

    async def add_track_to_playlist(self, username: Optional[str],
                                    playlist_id: str,track_id: str) -> Success | Error:
        '''
        Adds track with track_id to playlist with playlist_id
        Returns Error if track already present or if no such playlist exists
        Also accepts username of user who tries to execute this
        If not creator or admin, returns Error
        Otherwise return Success
        '''
        try:
            playlist: DBPlaylist = self.controller.find_playlist(playlist_id)

            if playlist is None:
                return Error(error="No such playlist")
            if track_id in playlist.tracks:
                return Error(error="Track is already present")
            if playlist.creator != username and not self.user_handler.is_admin(username):
                return Error(error="This user has no rights to execute this command")

            playlist.tracks.append(track_id)
            self.controller.update_playlist(playlist)
        except Exception as e:
            return Error(error=repr(e))

        return Success(success=True)

    async def remove_track_from_playlist(self, username: str,
                                         playlist_id: str, track_id: str) -> Success | Error:
        '''
        Removes track with track_id from playlist with playlist_id
        Returns Error if no such track in playlist or if no such playlist exists
        Also accepts username of user who tries to execute this
        If not creator or admin, returns Error
        Otherwise returns Success
        '''
        try:
            playlist: DBPlaylist = self.controller.find_playlist(playlist_id)

            if playlist is None:
                return Error(error="No such playlist")
            if track_id not in playlist.tracks:
                return Error(error="No such track in playlist")
            if playlist.creator != username and not self.user_handler.is_admin(username):
                return Error(error="This user has no rights to execute this command")

            playlist.tracks.remove(track_id)
            self.controller.update_playlist(playlist)
        except Exception as e:
            return Error(error=repr(e))

        return Success(success=True)

    async def get_playlist(self, username: str, playlist_id: str) -> DBPlaylist | Error:
        '''
        Tries to get playlist by id.
        Accepts username of user who is executing this,
        then checks if he has rights to view this playlist
        Returns playlist or error
        '''
        try:
            playlist: DBPlaylist = self.controller.find_playlist(playlist_id)

            if playlist is None:
                return Error(error="No such playlist")
            if (playlist.access == int(Access.PRIVATE) and
                username != playlist.creator and
                not self.user_handler.is_admin(username)):
                return Error(error="This user has no rights to execute this command")

            return playlist
        except Exception as e:
            return Error(error=repr(e))

    async def show_user_playlists(self, executor: str, user: str) -> List[DBPlaylist]:
        '''
        Shows all playlists owned by user
        If executor is not user and not admin, shows only public ones
        '''
        try:
            playlists: List[DBPlaylist] = self.controller.user_playlists(user)
            if executor != user and not self.user_handler.is_admin(executor):
                playlists = list(filter(lambda p: p.access == Access.PUBLIC, playlists))
            return playlists
        except Exception as e:
            return Error(error=repr(e))

    async def search_playlist(self, username: str,
                              playlist_id: str, search_str: str) -> List[DBTrack] | Error:
        '''
        Searches tracks in playlist by title. Returns all tracks that match or error
        '''
        try:
            playlist: DBPlaylist | Error = await self.get_playlist(username, playlist_id)
            if isinstance(playlist, Error):
                return playlist

            def check_track(track_id: str) -> bool:
                track: Optional[DBTrack] = self.track_controller.find_track(track_id)
                if track is None:
                    return False
                return track.title.find(search_str) != -1

            out = list(filter(check_track, playlist.tracks))
            return out
        except Exception as e:
            return Error(error=repr(e))
