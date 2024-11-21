import os
from musync.models import Song, Playlist
from musync.providers.base import ProviderClient

from spotipy import Spotify, SpotifyOAuth  # type: ignore


SCOPES = [
    "user-follow-read",
    "user-library-read",
    "user-top-read",
    "user-read-private",
]


class SpotifyClient(ProviderClient):
    @classmethod
    def from_env(cls):
        return cls(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        )

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self._client = Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=" ".join(SCOPES),
            )
        )

    def find_song(self, song: Song) -> Song | None:
        results = self._client.search(q=f"{song.title} {song.artist}", limit=1)
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

    def get_songs_from_playlist(self, playlist_id: str) -> list[Song]:
        results = self._client.playlist_tracks(playlist_id)
        songs = results["items"]
        while results["next"]:
            results = self._client.next(results)
            songs.extend(results["items"])

        return [
            Song(
                id=track["track"]["id"],
                title=track["track"]["name"],
                artist=track["track"]["artists"][0]["name"],
                album=track["track"]["album"]["name"],
            )
            for track in songs
        ]

    def get_user_playlists(self) -> list[Playlist]:
        results = self._client.current_user_playlists()
        playlists = results["items"]
        while results["next"]:
            results = self._client.next(results)
            playlists.extend(results["items"])

        return [
            Playlist(
                id=playlist["id"],
                name=playlist["name"],
                songs=self.get_songs_from_playlist(playlist["id"]),
            )
            for playlist in playlists
        ]

    def create_playlist(self, name: str, songs: list[Song]) -> Playlist:
        playlist = self._client.user_playlist_create(
            user=self._client.me()["id"],
            name=name,
        )

        self._client.playlist_add_items(
            playlist_id=playlist["id"],
            items=[song.id for song in songs],
        )

        return Playlist(
            id=playlist["id"],
            name=playlist["name"],
            songs=songs,
        )

    def user_playlist_exists(self, name: str):
        playlists = self._client.current_user_playlists()["items"]
        return any(playlist["name"] == name for playlist in playlists)
