from musync.models import Song

from musync.providers.spotify import SpotifyClient

import pytest

from unittest.mock import MagicMock


@pytest.fixture
def sp_client():
    return SpotifyClient.from_env()


def test_find_song(sp_client: SpotifyClient):
    song = Song(
        id="test_id",
        title="Wonderwall",
        artist="Oasis",
    )

    sp_client._client.search = MagicMock(
        return_value={
            "tracks": {
                "items": [
                    {
                        "id": "1qPbGZqppFwLwcBC1JQ6Vr",
                        "name": "Wonderwall",
                        "artists": [
                            {
                                "name": "Oasis",
                            }
                        ],
                        "album": {
                            "name": "What's the Story (Morning Glory)",
                        },
                    },
                    {
                        "id": "2qPbGZqppFwLwcBC1JQ6Vr",
                        "name": "Some Other Song",
                        "artists": [
                            {
                                "name": "Blur",
                            }
                        ],
                    },
                ]
            }
        }
    )

    sp_song = sp_client.find_song(song)

    assert sp_song is not None
    assert sp_song.id == "1qPbGZqppFwLwcBC1JQ6Vr"
    assert sp_song.title == song.title
    assert sp_song.artist == song.artist


def test_find_song_no_results(sp_client: SpotifyClient):
    song = Song(
        id="test_id",
        title="Wonderwall",
        artist="Oasis",
    )

    sp_client._client.search = MagicMock(return_value={"tracks": {"items": []}})

    sp_song = sp_client.find_song(song)

    assert sp_song is None
