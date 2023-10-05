import unittest
import requests
import sys
import os
from unittest.mock import patch
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from list_songs import (
    get_artist_id,
    api_call,
    top_songs_call,
    json_to_dataframe,
    songs_dataframe,
)

class MyModuleTest(unittest.TestCase):
    @patch('requests.get')
    def test_get_artist_id(self, mock_get):
        # Prepare mock response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'artists': {
                'items': [
                    {
                        'id': 'artist_id_123'
                    }
                ]
            }
        }

        # Test the function
        artist_id = get_artist_id('Artist Name')

        # Verify the result
        self.assertEqual(artist_id, 'artist_id_123')

    @patch('requests.get')
    def test_api_call(self, mock_get):
        # Prepare mock response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'artists': {
                # Mocked response data
            }
        }

        # Test the function
        result = api_call()

        # Verify the result
        # Add appropriate assertions

    @patch('requests.get')
    def test_top_songs_call(self, mock_get):
        # Prepare mock response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'tracks': [
                # Mocked response data
            ]
        }

        # Test the function
        result = top_songs_call('Artist Name')

        # Verify the result
        # Add appropriate assertions

    # Add more test methods for other functions


if __name__ == '__main__':
    unittest.main()
