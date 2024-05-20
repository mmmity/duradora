'''
Tests for tracks module
'''
import unittest
from unittest.mock import MagicMock, AsyncMock
import os
import shutil
import random

from src.tracks import TrackHandler, TrackUUID
from src.db.track_controller import DBTrack
from src.responses import Error

class MockTrackHandler(TrackHandler):
    '''
    Mocking TrackHandler so it uses separate storage path and does not connect to db
    '''
    def __init__(self):
        '''
        DB controller is now MagicMock, storage is random directory
        '''
        self.controller = MagicMock()
        self.storage = 'test_storage' + random.randbytes(5).hex()
        self.user_handler = MagicMock()
        os.makedirs(self.storage, exist_ok=True)

    def __del__(self):
        '''
        Removes storage directory
        '''
        shutil.rmtree(self.storage)


class MockDBTrackWithFile(DBTrack):
    '''
    Replacing UploadFile with str to simplify testing
    '''
    file: str


class TestTrackHandler(unittest.IsolatedAsyncioTestCase):
    '''
    Tests for TrackHandler class
    '''
    async def test_save_file(self):
        '''
        Tests for save_file method
        '''
        handler = MockTrackHandler()
        await handler.save_file('test_file', None)
        self.assertEqual(len(os.listdir(handler.storage)), 0)

        mock_file = AsyncMock()
        mock_file.read.return_value = b'contents'
        await handler.save_file('test_file', mock_file)

        self.assertTrue(os.path.exists(handler.storage + '/test_file'))
        with open(handler.storage + '/test_file', 'r') as f:
            self.assertEqual(f.read(), 'contents')

    async def test_add_track(self):
        '''
        Tests for add_track method
        '''
        handler = MockTrackHandler()
        mock_track = AsyncMock()
        mock_track.file.read.return_value = b'contents'
        handler.controller.create_track.return_value = 'lol'

        handler.user_handler.is_admin.return_value = False
        self.assertIsInstance(await handler.add_track(None, None), Error)
        handler.user_handler.is_admin.return_value = True

        uuid = await handler.add_track(None, mock_track)
        self.assertTrue(os.path.exists(handler.storage + '/lol.mp3'))
        with open(handler.storage + '/lol.mp3', 'r') as f:
            self.assertEqual(f.read(), 'contents')
        self.assertEqual(uuid, TrackUUID(uuid='lol'))

        handler.save_file = AsyncMock
        handler.save_file.side_effect = KeyError()
        self.assertIsInstance(await handler.add_track(None, mock_track), Error)

    async def test_update_track(self):
        '''
        Tests for update_track method
        '''
        handler = MockTrackHandler()
        track = MockDBTrackWithFile(uuid='u', artists='a', file='f')

        handler.user_handler.is_admin.return_value = False
        self.assertIsInstance(await handler.update_track(None, None), Error)
        handler.user_handler.is_admin.return_value = True

        handler.controller.find_track.return_value = None
        self.assertIsInstance(await handler.update_track(None, track), Error)

        mocktrack1 = MockDBTrackWithFile(uuid='u', title='t', file='f')
        mocktrack2 = MockDBTrackWithFile(uuid='u', title='t', artists='a', file='f')
        handler.controller.find_track.return_value = mocktrack1
        handler.save_file = AsyncMock()
        out = await handler.update_track(None, track)
        handler.controller.update_track.assert_called_with(mocktrack2)
        handler.save_file.assert_called_with('u.mp3', 'f')
        self.assertEqual(out.uuid, 'u')

        handler.controller.find_track.side_effect = KeyError()
        self.assertIsInstance(await handler.update_track(None, None), Error)
