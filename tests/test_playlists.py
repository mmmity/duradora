'''
Tests for playlists module
'''
import unittest
from unittest.mock import MagicMock, AsyncMock

from src.playlists import PlaylistHandler, PlaylistForCreation, PlaylistUUID
from src.db.playlist_controller import DBPlaylist, Access
from src.db.track_controller import Track
from src.responses import Error, Success


class MockPlaylistHandler(PlaylistHandler):
    '''
    Mocking playlist handler so it does not connect to db
    '''
    def __init__(self):
        '''
        DB controllers and user_handler are now MagicMocks
        '''
        self.controller = MagicMock()
        self.track_controller = MagicMock()
        self.user_handler = MagicMock()


class TestPlaylistHandler(unittest.IsolatedAsyncioTestCase):
    '''
    Tests for PlaylistHandler class
    '''
    async def test_create_playlist_for_user(self):
        '''
        Tests for create_playlist_for_user method
        '''
        handler = MockPlaylistHandler()
        playlist = PlaylistForCreation(creator='mmmity')
        handler.controller.create_playlist.return_value = 'uuid'

        handler.user_handler.is_admin.return_value = False
        self.assertIsInstance(await handler.create_playlist_for_user('leha', playlist), Error)
        self.assertIsInstance(await handler.create_playlist_for_user('mmmity', playlist),
                              PlaylistUUID)
        handler.user_handler.is_admin.return_value = True
        self.assertIsInstance(await handler.create_playlist_for_user('leha', playlist),
                              PlaylistUUID)

        handler.user_handler.is_admin.side_effect = KeyError()
        self.assertIsInstance(await handler.create_playlist_for_user('leha', playlist), Error)

    async def test_add_track_to_playlist(self):
        '''
        Tests for add_track_to_playlist method
        '''
        handler = MockPlaylistHandler()
        handler.user_handler.is_admin.return_value = False

        handler.controller.find_playlist.return_value = None
        self.assertIsInstance(await handler.add_track_to_playlist('u', 'p', 't'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='u', tracks=['t'], uuid='u'
        )
        self.assertIsInstance(await handler.add_track_to_playlist('u', 'p', 't'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='not_u', tracks=[], uuid='u'
        )
        self.assertIsInstance(await handler.add_track_to_playlist('u', 'p', 't'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='u', tracks=[], uuid='u'
        )
        self.assertIsInstance(await handler.add_track_to_playlist('u', 'p', 't'), Success)
        handler.controller.update_playlist.assert_called_once()

        handler.controller.find_playlist.side_effect = KeyError
        self.assertIsInstance(await handler.add_track_to_playlist('u', 'p', 't'), Error)

    async def test_remove_track_from_playlist(self):
        '''
        Tests for remove_track_from_playlist method
        '''
        handler = MockPlaylistHandler()
        handler.user_handler.is_admin.return_value = False

        handler.controller.find_playlist.return_value = None
        self.assertIsInstance(await handler.remove_track_from_playlist('u', 'p', 't'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='u', tracks=[], uuid='u'
        )
        self.assertIsInstance(await handler.remove_track_from_playlist('u', 'p', 't'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='not_u', tracks=['t'], uuid='u'
        )
        self.assertIsInstance(await handler.remove_track_from_playlist('u', 'p', 't'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='u', tracks=['t'], uuid='u'
        )
        self.assertIsInstance(await handler.remove_track_from_playlist('u', 'p', 't'), Success)
        handler.controller.update_playlist.assert_called_once()

        handler.controller.find_playlist.side_effect = KeyError
        self.assertIsInstance(await handler.remove_track_from_playlist('u', 'p', 't'), Error)

    async def test_get_playlist(self):
        '''
        Tests for get_playlist method
        '''
        handler = MockPlaylistHandler()
        handler.user_handler.is_admin.return_value = False

        handler.controller.find_playlist.return_value = None
        self.assertIsInstance(await handler.get_playlist('u', 'p'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='not u', uuid='u', access=Access.PRIVATE
        )
        self.assertIsInstance(await handler.get_playlist('u', 'p'), Error)

        handler.controller.find_playlist.return_value = DBPlaylist(
            creator='not u', uuid='u', access=Access.PUBLIC
        )
        self.assertIsInstance(await handler.get_playlist('u', 'p'), DBPlaylist)

        handler.controller.find_playlist.side_effect = KeyError()
        self.assertIsInstance(await handler.get_playlist('u', 'p'), Error)

    async def test_show_user_playlists(self):
        '''
        Tests for show_user_playlists method
        '''
        handler = MockPlaylistHandler()
        handler.user_handler.is_admin.return_value = False
        handler.controller.user_playlists.return_value = [
            DBPlaylist(creator='c', access=Access.LINK, uuid='u'),
            DBPlaylist(creator='c', access=Access.PUBLIC, uuid='u')
        ]

        list1 = await handler.show_user_playlists('u', 'u')
        list2 = await handler.show_user_playlists('u', 'not u')
        self.assertEqual(len(list1), 2)
        self.assertEqual(len(list2), 1)

        handler.controller.user_playlists.side_effect = KeyError()
        self.assertIsInstance(await handler.show_user_playlists('u', 'u'), Error)

    async def test_search_playlist(self):
        '''
        Tests for search_playlist method
        '''
        handler = MockPlaylistHandler()
        handler.get_playlist = AsyncMock()

        handler.get_playlist.return_value = Error(error='error')
        self.assertIsInstance(await handler.search_playlist('', '', ''), Error)

        handler.track_controller.find_track.return_value = Track(title='Doradura')
        handler.get_playlist.return_value = DBPlaylist(creator='c', uuid='u', tracks=['a', 'b'])

        self.assertEqual(len(await handler.search_playlist('', '', 'Dora')), 2)
        self.assertEqual(len(await handler.search_playlist('', '', 'Oora')), 0)
