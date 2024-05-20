'''
Tests for track_controller module
'''
import unittest
from unittest.mock import patch, MagicMock
from src.db.track_controller import Track, TrackController, DBTrack


class TestTrackController(unittest.TestCase):
    '''
    Tests for TrackController class
    '''
    @patch('sqlite3.connect')
    def test_init_del(self, mock_connect: MagicMock):
        '''
        Tests initialization and destruction
        '''
        controller = TrackController('duradora.db')
        mock_connect.assert_called_once_with('duradora.db')
        connection: MagicMock = controller.con
        del controller
        connection.close.assert_called_once()

    @patch('sqlite3.connect')
    def test_create_track(self, _):
        '''
        Tests adding tracks to database
        '''
        controller = TrackController('duradora.db')
        track = Track(title='title', artists='artists')
        controller.create_track(track)
        controller.cur.execute.assert_called_once()
        controller.con.commit.assert_called_once()

    @patch('sqlite3.connect')
    def test_track_from_entry(self, _):
        '''
        Tests converting tuple to DBTrack
        '''
        track = DBTrack(title='t', artists='a', uuid='u')
        controller = TrackController('duradora.db')
        out = controller.track_from_entry(('u', 't', 'a'))
        self.assertEqual(track, out)

    @patch('sqlite3.connect')
    def test_find_track(self, _):
        '''
        Tests searching for track in DB
        '''
        controller = TrackController('duradora.db')
        controller.cur.fetchone.return_value = None
        self.assertIsNone(controller.find_track('u'))
        controller.cur.fetchone.return_value = ('u', 't', 'a')
        self.assertEqual(controller.find_track('u'), controller.track_from_entry(('u', 't', 'a')))

    @patch('sqlite3.connect')
    def test_update_track(self, _):
        '''
        Tests updating track
        '''
        controller = TrackController('duradora.db')
        controller.update_track(DBTrack(title='t', artists='a', uuid='u'))
        controller.con.commit.assert_called_once()
        controller.cur.execute.assert_called_once()
