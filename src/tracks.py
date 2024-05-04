'''
Module for operating with tracks: files, databases, etc
'''
import os
from typing import Optional

from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from src.db.track_controller import TrackController, Track, DBTrack, TrackUUID
from src.responses import Error, Success
from src import config

class TrackWithFile(Track):
    '''
    Pydantic model representing track with file
    '''
    file: UploadFile | None = None


class DBTrackWithFile(DBTrack):
    '''
    Pydantic model representing track with file and uuid
    '''
    file: UploadFile | None = None


class TrackHandler:
    '''
    Class that handles all operations with tracks
    '''
    def __init__(self):
        '''
        Initializes database and storage path
        '''
        self.controller = TrackController(config.DB_PATH)
        self.storage: str = config.STORAGE_PATH
        os.makedirs(self.storage, exist_ok=True)


    async def save_file(self, filename: str, file: UploadFile):
        '''
        Saves file to self.storage/filename
        '''
        if file is None:
            return
        contents: bytes  = await file.read()
        with open(self.storage + '/' + filename, 'wb') as newfile:
            newfile.write(contents)

    async def add_track(self, track: TrackWithFile) -> TrackUUID | Success:
        '''
        Tries to add track to storage. Returns error or success
        '''
        try:
            uuid: str = self.controller.create_track(track)
            await self.save_file(uuid + '.mp3', track.file)
        except Exception as e:
            return Error(error=repr(e))

        return TrackUUID(uuid=uuid)

    async def update_track(self, track: DBTrackWithFile) -> TrackUUID | Success:
        '''
        Tries to update track with track.uuid. Returns error or success
        '''
        try:
            existing_track = self.controller.find_track(track.uuid)
            if existing_track is None:
                return Error(error="No such track exists")

            for key in track.model_fields.keys():
                if track.__dict__[key] is None:
                    track.__dict__[key] = existing_track.__dict__.get(key, None)

            self.controller.update_track(track)
            if track.file is not None:
                await self.save_file(track.uuid + '.mp3', track.file)

        except Exception as e:
            return Error(error=repr(e))

        return TrackUUID(uuid=track.uuid)

    async def get_track(self, uuid: str) -> Optional[DBTrack]:
        '''
        Returns track metadata by uuid
        '''
        return self.controller.find_track(uuid)

    def stream_track(self, uuid: str) -> Optional[StreamingResponse]:
        '''
        Streams track with uuid if its file exists
        '''
        if not os.path.exists(self.storage + '/' + uuid + '.mp3'):
            return None

        def iterfile():
            with open(self.storage + '/' + uuid + '.mp3', 'rb') as stream:
                yield from stream

        return StreamingResponse(iterfile(), media_type='audio/mp3')
