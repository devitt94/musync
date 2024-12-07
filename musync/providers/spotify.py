import functools
import itertools
import os

from musync.models import Song, Playlist
from musync.models.artist import Artist
from musync.providers.base import ProviderClient

from spotipy import Spotify, SpotifyOAuth  # type: ignore


SCOPES = [
    "user-follow-read",
    "user-library-read",
    "user-library-modify",
    "user-top-read",
    "user-read-private",
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
    "playlist-read-collaborative",
    "user-follow-modify",
]


class SpotifyClient(ProviderClient):
    @classmethod
    def from_env(cls, read_only: bool = False):
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

        if not client_id or not client_secret or not redirect_uri:
            raise ValueError(
                "SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and SPOTIFY_REDIRECT_URI environment variables must be set"
            )

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            read_only=read_only,
        )

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        read_only: bool = False,
    ):
        self._client = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=" ".join(SCOPES),
            )
        )
        self.read_only = read_only

    @property
    def provider_name(self) -> str:
        return "Spotify"

    @functools.cached_property
    def user_id(self) -> str:
        return self._client.me()["id"]

    def find_song(self, song: Song) -> Song | None:
        results = self._client.search(
            q=f"{song.title} {song.artist}", type="track", limit=10
        )
        try:
            track = results["tracks"]["items"][0]
        except IndexError:
            return None
        else:
            return Song(
                id=track["id"],
                title=track["name"],
                artist=track["artists"][0]["name"],
                album=track["album"]["name"],
            )

    def find_artist(self, artist: Artist) -> Artist | None:
        results = self._client.search(q=artist.name, type="artist", limit=10)

        for found_artist in results["artists"]["items"]:
            if found_artist["name"].lower() == artist.name.lower():
                return Artist(
                    id=found_artist["id"],
                    name=found_artist["name"],
                )

        return None

    def get_followed_artists(self) -> list[Artist]:
        results = self._client.current_user_followed_artists()["artists"]
        artists = results["items"]
        while results["next"]:
            results = self._client.next(results)["artists"]
            artists.extend(results["items"])

        return [Artist(id=artist["id"], name=artist["name"]) for artist in artists]

    def follow_artist(self, artist: Artist) -> None:
        if not self.read_only:
            self._client.user_follow_artists([artist.id])

    def get_songs_from_playlist(self, playlist_id: str) -> list[Song]:
        results = self._client.playlist_tracks(playlist_id)
        songs = results["items"]
        while results["next"]:
            results = self._client.next(results)
            songs.extend(results["items"])

        return [
            Song(
                id=track["track"]["id"] or track["track"]["uri"],
                title=track["track"]["name"],
                artist=track["track"]["artists"][0]["name"],
                album=track["track"]["album"]["name"],
            )
            for track in songs
        ]

    def __is_self_authored_playlist(self, playlist: dict) -> bool:
        return playlist["owner"]["id"] == self.user_id

    def __get_playlists(self, is_user_authored: bool) -> list[Playlist]:
        if is_user_authored:

            def filter_fn(x):
                return x is not None and self.__is_self_authored_playlist(x)
        else:

            def filter_fn(x):
                return x is not None and not self.__is_self_authored_playlist(x)

        results = self._client.current_user_playlists()

        playlists = results["items"]
        while results["next"]:
            results = self._client.next(results)
            playlists.extend(results["items"])

        filtered_playlists = filter(filter_fn, playlists)

        return [
            Playlist(
                id=playlist["id"],
                name=playlist["name"],
                songs=self.get_songs_from_playlist(playlist["id"]),
            )
            for playlist in filtered_playlists
        ]

    def get_user_playlists(self) -> list[Playlist]:
        return self.__get_playlists(is_user_authored=True)

    def create_playlist(self, name: str, songs: list[Song]) -> Playlist:
        if not self.read_only:
            playlist = self._client.user_playlist_create(
                user=self.user_id,
                name=name,
            )

            for batch in itertools.batched(songs, 100):
                self._client.playlist_add_items(
                    playlist_id=playlist["id"],
                    items=[song.id for song in batch],
                )

            playlist_id = playlist["id"]
        else:
            playlist_id = "read_only_playlist"

        return Playlist(
            id=playlist_id,
            name=name,
            songs=songs,
        )

    def user_playlist_exists(self, name: str):
        playlists = self._client.current_user_playlists()["items"]
        return any(playlist == name for playlist in playlists)

    def get_followed_playlists(self) -> list[Playlist]:
        return self.__get_playlists(is_user_authored=False)

    def delete_playlist(self, playlist: Playlist) -> None:
        if not self.read_only:
            self._client.current_user_unfollow_playlist(playlist.id)
