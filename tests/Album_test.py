import unittest
from unittest.mock import patch, MagicMock
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from make_album import create_playlist

class CreatePlaylistTest(unittest.TestCase):
    @patch('list_songs.create_playlist.sp')
    def test_create_playlist(self, mock_sp):
        # Prepare mock objects and data
        username = 'test_user'
        playlist_name = 'test_playlist'
        songs = [
            {'uri': 'spotify:track:123456'},
            {'uri': 'spotify:track:789012'}
        ]

        mock_sp.user.return_value = MagicMock()
        mock_sp.user_playlist_create.return_value = {'id': 'test_playlist_id'}
        mock_sp.playlist_add_items.return_value = MagicMock()

        # Call the function under test
        create_playlist(username, playlist_name, songs)

        # Verify the interactions and assertions
        mock_sp.user.assert_called_once_with(username)
        mock_sp.user_playlist_create.assert_called_once_with(
            username,
            playlist_name,
            public=True,
            collaborative=False,
            description='recs'
        )
        mock_sp.playlist_add_items.assert_called_once_with(
            'test_playlist_id',
            ['spotify:track:123456', 'spotify:track:789012']
        )

