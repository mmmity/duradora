from fastapi import FastAPI, Depends, UploadFile, Form, File
from fastapi.responses import StreamingResponse
from typing import Annotated, Optional

from src.db.user_controller import User, UserController
from src.auth import Auth

from src.db.track_controller import TrackController, Track
from src.tracks import TrackHandler, TrackWithFile, DBTrackWithFile

from pydantic import BaseModel

auth = Auth()
tracks = TrackHandler()
app = FastAPI()

class Error(BaseModel):
    error: str

@app.post('/register')
async def register(user: User):
    return auth.register_user(user)

@app.post('/login')
async def login(user: User):
    return await auth.login_user(user)

@app.get('/me', response_model=User | Error)
async def get_user(current_user: Annotated[User, Depends(auth.get_current_user)]):
    if 'error' in current_user.model_fields.keys():
        return current_user
    try:
        controller = UserController('duradora.db')
        user = controller.find_user(current_user.username)
        if user is None:
            return {'error': 'No such user'}
        return user
    except Exception as e:
        return {'error': str(e)}

@app.post('/user/update')
async def update_user(user: User):
    try:
        controller = UserController('duradora.db')
        controller.update_user(user)
    except Exception as e:
        return {'error': str(e)}
    return {'success': True}

@app.post('/track/add')
async def add_track(title: str | None = None, artists: str | None = None, file: Annotated[UploadFile, File()] = None):
    return await tracks.add_track(TrackWithFile(title=title, artists=artists, file=file))

@app.post('/track/update')
async def update_track(uuid: str, title: str | None = None, artists: str | None = None, file: Annotated[UploadFile, File()] = None):
    return await tracks.update_track(DBTrackWithFile(uuid=uuid, title=title, artists=artists, file=file))

@app.get('/track')
async def get_track(uuid: str):
    return await tracks.get_track(uuid)

@app.get('/stream')
async def stream_track(uuid: str):
    return await tracks.stream_track(uuid)
