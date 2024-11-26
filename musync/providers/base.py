from abc import ABC, abstractmethod

from musync.models import Song, Playlist


class ProviderClient(ABC):
    @classmethod
    @abstractmethod
    def from_env(cls, read_only: bool = False):
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def find_song(self, song: Song) -> Song | None:
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
