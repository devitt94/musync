from abc import ABC, abstractmethod
from typing import Self

from musync.models import Song, Playlist

class ProviderClient(ABC):

    @classmethod
    @abstractmethod
    def from_env(cls):
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