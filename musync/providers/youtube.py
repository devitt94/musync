import functools
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

    @property
    def provider_name(self) -> str:
        return "YouTube"

    @functools.cached_property
    def user_id(self) -> str:
        endpoint = "account/account_menu"
        response = self._client._send_request(endpoint, {})
        return response["actions"][0]["openPopupAction"]["popup"][
            "multiPageMenuRenderer"
        ]["sections"][0]["multiPageMenuSectionRenderer"]["items"][0][
            "compactLinkRenderer"
        ]["navigationEndpoint"]["browseEndpoint"]["browseId"]

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

    def __is_self_authored_playlist(self, playlist: dict) -> bool:
        authors = playlist.get("author")
        if not authors:
            return False
        return any(author["id"] == self.user_id for author in authors)

    def __get_playlists(self, is_user_authored: bool) -> list[Playlist]:
        if is_user_authored:
            filter_fn = self.__is_self_authored_playlist
        else:

            def filter_fn(x):
                return not self.__is_self_authored_playlist(x)

        playlists = self._client.get_library_playlists()

        filtered_playlists = filter(filter_fn, playlists)

        return [
            Playlist(
                id=playlist["playlistId"],
                name=playlist["title"],
                songs=[
                    Song(
                        id=track["videoId"],
                        title=track["title"],
                        artist=track["artists"][0]["name"],
                        album=None,
                    )
                    for track in self._client.get_playlist(playlist["playlistId"])[
                        "tracks"
                    ]
                ],
            )
            for playlist in filtered_playlists
        ]

    def get_user_playlists(self) -> list[Playlist]:
        return self.__get_playlists(is_user_authored=True)

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

    def get_followed_playlists(self) -> list[Playlist]:
        return self.__get_playlists(is_user_authored=False)
