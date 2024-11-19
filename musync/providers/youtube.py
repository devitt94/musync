import os
from pathlib import Path

from pydantic import BaseModel

from musync.models import Playlist, Song

from .base import ProviderClient

from ytmusicapi import YTMusic


class YoutubeClient(ProviderClient):

    @classmethod
    def from_env(cls):
        return cls(auth_file=Path(os.getenv("YOUTUBE_BROWSER_AUTH_FILEPATH")))
    
    def __init__(self, auth_file: Path):
        self._client = YTMusic(str(auth_file))

    def find_song(self, song: Song) -> Song | None:
        try:
            search_results = self._client.search(query=f"{song.title} {song.artist}")
        except Exception as e:
            print(f"Error searching for {song.title} by {song.artist}: {e}")
            return None

        try:
            track = search_results[0]
        except IndexError:
            return None
        else:
            return Song(
                id=track['videoId'],
                title=track['title'],
                artist=track['artists'][0]['name'],
                album=track['album']['name'],
            )
        
    
    def get_user_playlists(self) -> list[Playlist]:
        playlists = self._client.get_library_playlists()
        return [
            Playlist(
                id=playlist['playlistId'],
                name=playlist['title'],
                songs=[
                    Song(
                        id=track['videoId'],
                        title=track['title'],
                        artist=track['artists'][0]['name'],
                        album=track['album']['name'],
                    )
                    for track in self._client.get_playlist(playlist['playlistId'])['tracks']
                ]
            )
            for playlist in playlists
        ]