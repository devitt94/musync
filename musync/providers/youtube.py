import functools
import os
from pathlib import Path

from musync.models import Playlist, Song
from musync.models.artist import Artist

from .base import ProviderClient

from ytmusicapi import YTMusic  # type: ignore


class YoutubeClient(ProviderClient):
    @classmethod
    def from_env(cls, read_only: bool = False):
        filepath = os.getenv("YOUTUBE_BROWSER_AUTH_FILEPATH")
        if not filepath:
            raise ValueError(
                "'YOUTUBE_BROWSER_AUTH_FILEPATH' environment variable is not set"
            )

        return cls(
            auth_file=Path(filepath),
            read_only=read_only,
        )

    def __init__(self, auth_file: Path, read_only: bool = False):
        self._client = YTMusic(str(auth_file))
        self.read_only = read_only

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

        try:
            album = first_track_found["album"]["name"]
        except (KeyError, TypeError):
            album = None

        return Song(
            id=first_track_found["videoId"],
            title=first_track_found["title"],
            artist=first_track_found["artists"][0]["name"],
            album=album,
        )

    def find_artist(self, artist: Artist) -> Artist | None:
        search_results = self._client.search(
            query=artist.name, filter="artists", limit=10
        )

        for found_artist in search_results:
            if found_artist["artist"].lower() == artist.name.lower():
                return Artist(
                    id=found_artist["browseId"],
                    name=found_artist["artist"],
                )

        return None

    def get_followed_artists(self) -> list[Artist]:
        followed_artists = self._client.get_library_subscriptions()
        return [
            Artist(
                id=artist["browseId"],
                name=artist["artist"],
            )
            for artist in followed_artists
        ]

    def follow_artist(self, artist: Artist) -> None:
        if not self.read_only:
            self._client.subscribe_artists([artist.id])

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

        playlists = self._client.get_library_playlists(limit=None)

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
        if not self.read_only:
            playlist_id = self._client.create_playlist(
                title=name,
                description="Created by musync",
                video_ids=[song.id for song in songs],
            )
        else:
            playlist_id = "read_only_playlist"

        return Playlist(
            id=playlist_id,
            name=name,
            songs=songs,
        )

    def user_playlist_exists(self, name: str) -> bool:
        return any(
            playlist["title"] == name
            for playlist in self._client.get_library_playlists(limit=None)
        )

    def get_followed_playlists(self) -> list[Playlist]:
        return self.__get_playlists(is_user_authored=False)

    def delete_playlist(self, playlist: Playlist) -> None:
        if not self.read_only:
            self._client.delete_playlist(playlist.id)

    def get_playlist_by_name(self, name: str) -> Playlist | None:
        for playlist in self._client.get_library_playlists(limit=None):
            if playlist["title"] == name:
                tracks = self._client.get_playlist(playlist["playlistId"])["tracks"]
                return Playlist(
                    id=playlist["playlistId"],
                    name=playlist["title"],
                    songs=[
                        Song(
                            id=track["videoId"],
                            title=track["title"],
                            artist=track["artists"][0]["name"],
                            album=None,
                        )
                        for track in tracks
                    ],
                )

        return None

    def add_songs_to_playlist(self, playlist: Playlist, songs: list[Song]) -> Playlist:
        if not self.read_only:
            self._client.add_playlist_items(playlist.id, [song.id for song in songs])

        playlist.songs.extend(songs)
        return playlist
