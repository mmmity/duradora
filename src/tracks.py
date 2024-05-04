'''
Module for operating with tracks: files, databases, etc
'''
import os
from typing import Optional

from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from src.db.track_controller import TrackController, Track, DBTrack
from responses import Error, Success

class TrackWithFile(Track):
    '''
    Pydantic model representing track with file
    '''
    file: UploadFile | None


class DBTrackWithFile(DBTrack):
    '''
    Pydantic model representing track with file and uuid
    '''
    file: UploadFile | None


class TrackHandler:
    '''
    Class that handles all operations with tracks
    '''
    def __init__(self, db: str, storage: str):
        '''
        Initializes database and storage path
        '''
        self.controller = TrackController(db)
        self.storage: str = storage

    async def save_file(self, filename: str, file: UploadFile):
        '''
        Saves file to self.storage/filename
        '''
        if file is None:
            return
        contents: bytes  = await file.read()
        with open(self.storage + '/' + filename, 'wb') as newfile:
            newfile.write(contents)

    async def add_track(self, track: TrackWithFile) -> Error | Success:
        '''
        Tries to add track to storage. Returns error or success
        '''
        try:
            uuid: str = self.controller.create_track(track)
            await self.save_file(uuid + '.mp3', track.file)
        except Exception as e:
            return Error(error=repr(e))

        return Success(success=True)

    async def update_track(self, track: DBTrackWithFile) -> Error | Success:
        '''
        Tries to update track with track.uuid. Returns error or success
        '''
        try:
            self.controller.update_track(track)
            await self.save_file(track.uuid + '.mp3', track.file)
        except Exception as e:
            return Error(error=repr(e))

        return Success(success=True)

    async def get_track(self, uuid: str) -> Optional[DBTrack]:
        '''
        Returns track metadata by uuid
        '''
        return self.controller.find_track(uuid)

    async def stream_track(self, uuid: str) -> Optional[StreamingResponse]:
        '''
        Streams track with uuid if its file exists
        '''
        if not os.path.exists(self.storage + '/' + uuid + '.mp3'):
            return None

        def iterfile():
            with open(self.storage + '/' + uuid + '.mp3', 'rb') as stream:
                yield from stream

        return StreamingResponse(iterfile, media_type='audio/mp3')
