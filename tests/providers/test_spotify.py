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


def test_get_songs_from_playlist(sp_client: SpotifyClient):
    sp_client._client.playlist_tracks = MagicMock(
        return_value={
            "items": [
                {
                    "track": {
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
                    }
                }
            ],
            "next": None,
        }
    )

    songs = sp_client.get_songs_from_playlist("test_playlist_id")

    assert len(songs) == 1
    assert songs[0].id == "1qPbGZqppFwLwcBC1JQ6Vr"
    assert songs[0].title == "Wonderwall"
    assert songs[0].artist == "Oasis"
    assert songs[0].album == "What's the Story (Morning Glory)"


def test_get_songs_from_playlist_multiple_pages(sp_client: SpotifyClient):
    sp_client._client.playlist_tracks = MagicMock(
        side_effect=[
            {
                "items": [
                    {
                        "track": {
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
                        }
                    }
                ],
                "next": "http://example.com",
            },
        ]
    )

    sp_client._client.next = MagicMock(
        side_effect=[
            {
                "items": [
                    {
                        "track": {
                            "id": "2qPbGZqppFwLwcBC1JQ6Vr",
                            "name": "Some Other Song",
                            "artists": [
                                {
                                    "name": "Blur",
                                }
                            ],
                            "album": {
                                "name": "Some Album",
                            },
                        }
                    }
                ],
                "next": "http://example.com",
            },
            {
                "items": [
                    {
                        "track": {
                            "id": "3qPbGZqppFwLwcBC1JQ6Vr",
                            "name": "Some Other Song 2",
                            "artists": [
                                {
                                    "name": "Blur",
                                }
                            ],
                            "album": {
                                "name": "Some Album",
                            },
                        }
                    }
                ],
                "next": None,
            },
        ]
    )

    songs = sp_client.get_songs_from_playlist("test_playlist_id")

    assert len(songs) == 3
    assert songs[0].id == "1qPbGZqppFwLwcBC1JQ6Vr"
    assert songs[0].title == "Wonderwall"
    assert songs[0].artist == "Oasis"
    assert songs[0].album == "What's the Story (Morning Glory)"
    assert songs[1].id == "2qPbGZqppFwLwcBC1JQ6Vr"
    assert songs[1].title == "Some Other Song"
    assert songs[1].artist == "Blur"
    assert songs[1].album == "Some Album"
    assert songs[2].id == "3qPbGZqppFwLwcBC1JQ6Vr"
    assert songs[2].title == "Some Other Song 2"
    assert songs[2].artist == "Blur"
    assert songs[2].album == "Some Album"
