from abc import ABC, abstractmethod

from musync.models import Song, Playlist
from musync.models.artist import Artist


class ProviderClient(ABC):
    @classmethod
    @abstractmethod
    def from_env(cls, read_only: bool = False):
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def user_id(self) -> str:
        pass

    @property
    @abstractmethod
    def username(self) -> str:
        pass

    @abstractmethod
    def find_song(self, song: Song) -> Song | None:
        pass

    @abstractmethod
    def find_artist(self, artist: Artist) -> Artist | None:
        pass

    @abstractmethod
    def get_followed_artists(self) -> list[Artist]:
        pass

    @abstractmethod
    def follow_artist(self, artist: Artist) -> None:
        pass

    @abstractmethod
    def get_user_playlists(self) -> list[Playlist]:
        pass

    @abstractmethod
    def create_playlist(self, name: str, songs: list[Song]) -> Playlist:
        pass

    @abstractmethod
    def user_playlist_exists(self, name: str) -> bool:
        pass

    @abstractmethod
    def get_followed_playlists(self) -> list[Playlist]:
        pass

    @abstractmethod
    def delete_playlist(self, playlist: Playlist) -> None:
        pass

    @abstractmethod
    def get_playlist_by_name(self, name: str) -> Playlist | None:
        pass

    @abstractmethod
    def add_songs_to_playlist(self, playlist: Playlist, songs: list[Song]) -> Playlist:
        pass
