'''
Tests for playlist_controller module
'''
import unittest
from unittest.mock import patch

from src.db.playlist_controller import PlaylistController, Playlist, DBPlaylist, Access

class TestPlaylistController(unittest.TestCase):
    '''
    Tests for PlaylistController class
    '''
    @patch('sqlite3.connect')
    def setUp(self, _):
        '''
        Sets up data for all tests
        '''
        self.controller = PlaylistController('.db')
        self.playlist = DBPlaylist(uuid='u',
                              title='t',
                              creator='c',
                              access=Access.PUBLIC,
                              tracks=['something']
                            )
        self.entry = ('u', 't', 'c', 0, '["something"]')

    def test_create_playlist(self):
        '''
        Tests adding playlist to database
        '''
        self.controller.create_playlist(Playlist(title='', creator=''))
        self.controller.cur.execute.assert_called_once()
        self.controller.con.commit.assert_called_once()

    def test_playlist_from_entry(self):
        '''
        Tests converting database entry into DBPlaylist
        '''

        self.assertEqual(self.playlist, self.controller.playlist_from_entry(self.entry))

    def test_find_playlist(self):
        '''
        Tests finding playlist by id
        '''
        self.controller.cur.fetchone.return_value = self.entry
        self.assertEqual(self.controller.find_playlist('u'), self.playlist)

        self.controller.cur.fetchone.return_value = None
        self.assertIsNone(self.controller.find_playlist('u'))

    def test_user_playlists(self):
        '''
        Tests getting all user playlists
        '''
        self.controller.cur.fetchall.return_value = [self.entry, self.entry]
        self.assertEqual(self.controller.user_playlists('u'), [self.playlist, self.playlist])

    def test_update_playlist(self):
        '''
        Tests updating playlist
        '''
        self.controller.update_playlist(self.playlist)
        self.controller.cur.execute.assert_called_once()
        self.controller.con.commit.assert_called_once()
