import os
from pathlib import Path

from musync.models import Playlist, Song

from .base import ProviderClient

from ytmusicapi import YTMusic  # type: ignore


class YoutubeClient(ProviderClient):
    @classmethod
    def from_env(cls):
        return cls(auth_file=Path(os.getenv("YOUTUBE_BROWSER_AUTH_FILEPATH")))

    def __init__(self, auth_file: Path):
        self._client = YTMusic(str(auth_file))

    def find_song(self, song: Song) -> Song | None:
        search_results = self._client.search(
            query=f"{song.title} {song.artist}", filter="songs", limit=1
        )
        try:
            first_track_found = [
                track for track in search_results if track.get("videoId")
            ][0]
        except IndexError:
            return None
        else:
            album = (
                first_track_found["album"]["name"]
                if "album" in first_track_found
                else None
            )
            return Song(
                id=first_track_found["videoId"],
                title=first_track_found["title"],
                artist=first_track_found["artists"][0]["name"],
                album=album,
            )

    def get_user_playlists(self) -> list[Playlist]:
        playlists = self._client.get_library_playlists()
        return [
            Playlist(
                id=playlist["playlistId"],
                name=playlist["title"],
                songs=[
                    Song(
                        id=track["videoId"],
                        title=track["title"],
                        artist=track["artists"][0]["name"],
                        album=track["album"]["name"],
                    )
                    for track in self._client.get_playlist(playlist["playlistId"])[
                        "tracks"
                    ]
                ],
            )
            for playlist in playlists
        ]

    def create_playlist(self, name: str, songs: list[Song]) -> Playlist:
        playlist_id = self._client.create_playlist(
            title=name,
            description="Created by musync",
            video_ids=[song.id for song in songs],
        )
        return Playlist(
            id=playlist_id,
            name=name,
            songs=songs,
        )

    def user_playlist_exists(self, name: str) -> bool:
        return any(
            playlist["title"] == name
            for playlist in self._client.get_library_playlists()
        )
