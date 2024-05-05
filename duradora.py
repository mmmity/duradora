'''
Main file with all endpoints
'''
from typing import Annotated, Optional, List

from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse

from src.responses import Success, Error

from src.db.user_controller import User
from src.auth import Auth, Token
from src.users import UserHandler

from src.db.track_controller import DBTrack
from src.tracks import TrackHandler, TrackWithFile, DBTrackWithFile, TrackUUID

from src.playlists import PlaylistHandler, PlaylistForCreation, PlaylistUUID, DBPlaylist


auth = Auth()
tracks = TrackHandler()
playlists = PlaylistHandler()
users = UserHandler()
app = FastAPI()

@app.post('/register', response_model=Success | Error)
async def register(user: User) -> Success | Error:
    '''
    Registers new user
    '''
    return await auth.register_user(user)

@app.post('/login', response_model=Token | Error)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token | Error:
    '''
    Attempts to login with username and password
    If succeeds, returns JWT token for authorization
    '''
    return await auth.login_user(User(username=form_data.username, password=form_data.password))

@app.post('/user/update', response_model=Success | Error)
async def update_user(executor: Annotated[User, Depends(auth.get_current_user)],
                      user: User) -> Success | Error:
    '''
    Attempts to update user. Is in authorized zone.
    Works only if executor is admin or if executor updates themself.
    If executor is not admin, they cannot make themselves admin.
    '''
    return await users.update_user(executor.username, user)

@app.post('/track/add', response_model=TrackUUID | Error)
async def add_track(executor: Annotated[User, Depends(auth.get_current_user)],
                    title: str | None = None, artists: str | None = None,
                    file: Annotated[UploadFile, File()] = None) -> TrackUUID | Error:
    '''
    Adds track to database. Can only be performed by admin
    '''
    return await tracks.add_track(executor.username,
                                  TrackWithFile(title=title, artists=artists, file=file))

@app.post('/track/update', response_model=TrackUUID | Error)
async def update_track(executor: Annotated[User, Depends(auth.get_current_user)],
                       uuid: str, title: str | None = None, artists: str | None = None,
                       file: Annotated[UploadFile, File()] = None) -> TrackUUID | Error:
    '''
    Updates track in database. Can only be performed by admin
    '''
    return await tracks.update_track(
        executor.username,
        DBTrackWithFile(uuid=uuid, title=title, artists=artists, file=file)
    )

@app.get('/track', response_model=DBTrack | Error)
async def get_track(uuid: str) -> DBTrack | Error:
    '''
    Returns track metadata by uuid
    '''
    return await tracks.get_track(uuid)

@app.get('/stream', response_model=None)
async def stream_track(uuid: str) -> StreamingResponse | Error:
    '''
    Streams track by uuid
    '''
    return await tracks.stream_track(uuid)

@app.post('/playlist', response_model=PlaylistUUID | Error)
async def create_playlist(executor: Annotated[User, Depends(auth.get_current_user)],
                          playlist: PlaylistForCreation) -> PlaylistUUID | Error:
    '''
    Creates playlist for user executor. Is in authorized zone
    '''
    return await playlists.create_playlist_for_user(executor.username, playlist)

@app.get('/playlist', response_model=DBPlaylist | Error)
async def get_playlist(executor: Annotated[User, Depends(auth.get_current_user)],
                       playlist_id: str) -> DBPlaylist | Error:
    '''
    Shows playlist by id. Is in authorized zone
    Does not show private playlists of others to non-admins
    '''
    return await playlists.get_playlist(executor.username, playlist_id)

@app.post('/playlist/add_track', response_model=Success | Error)
async def add_track_to_playlist(executor: Annotated[User, Depends(auth.get_current_user)],
                                playlist_id: str, track_id: str) -> Success | Error:
    '''
    Adds track to playlist
    Can only be performed by its creator or an admin
    '''
    return await playlists.add_track_to_playlist(executor.username, playlist_id, track_id)

@app.post('/playlist/remove_track', response_model=Success | Error)
async def remove_track_from_playlist(executor: Annotated[User, Depends(auth.get_current_user)],
                                     playlist_id: str, track_id: str) -> Success | Error:
    '''
    Removes track from playlist
    Can only be performed by its creator or an admin
    '''
    return await playlists.remove_track_from_playlist(executor.username, playlist_id, track_id)

@app.get('/user/{username}/playlists', response_model=List[DBPlaylist])
async def show_user_playlists(executor: Annotated[User, Depends(auth.get_current_user)],
                              username: str) -> List[DBPlaylist]:
    '''
    Shows playlist created by username
    If executor is not admin and not username, shows only public ones
    '''
    return await playlists.show_user_playlists(executor.username, username)

@app.get('/playlist/{playlist_id}/search', response_model=List[DBTrack])
async def search_playlist(executor: Annotated[User, Depends(auth.get_current_user)],
                          playlist_id: str, search_str: str) -> List[DBTrack]:
    '''
    Tries to search by track name in playlists
    '''
    return await playlists.search_playlist(executor.username, playlist_id, search_str)
